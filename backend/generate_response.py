from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from utils import retreive_relavant_chunks
import google.generativeai as genai
from typing import List
import os
import re
from difflib import SequenceMatcher

# Configure API key (should be set via environment variable in production)
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash")

# Prompt for answering user questions
answer_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template = """
        You are a helpful, honest, and reliable AI assistant designed to read research documents and answer questions accurately.

        Your job is to:
        - Use the provided **context only** (do not use external knowledge).
        - Never guess or make up facts — answer only if the answer is clearly supported in the context.
        - If the answer is not found in the context, respond with:
        "I'm sorry, I don't have enough information in the provided document to answer that."
        - Do **not** answer questions related to medical, legal, financial advice, or anything harmful or unsafe.
        - Maintain a clear, respectful, and professional tone at all times.

        Your answer must:
        - Be **concise** and **factual**
        - Provide a **justification**, like: “This is supported by section/paragraph X.”

        Context:
        {context}

        Question:
        {question}

        Answer (with justification):
    """

)

# Prompt for generating challenge questions
challenge_prompt = PromptTemplate(
    input_variables=["context"],
    template="""
        You are an AI assistant. Based only on the following document context, generate three logic-based or comprehension-focused questions that test understanding of the material. Do not use external knowledge. Number each question.
        Context:
        {context}
        Questions:
    """
)

# Prompt for evaluating user answers
evaluate_prompt = PromptTemplate(
    input_variables=["context", "question", "user_answer"],
    template="""
        You are an AI tutor. Given the document context, a question, and a user's answer, evaluate the answer for correctness.
        Provide a short, simple feedback (2-3 sentences) and a brief justification, referencing the context (e.g., "This is supported by section/paragraph X").
        Avoid long explanations. Be concise and easy to understand.
        Context:
        {context}
        Question:
        {question}
        User's Answer:
        {user_answer}
        Feedback (with justification):
    """
)

# Prompt for generating a concise summary (≤ 150 words)
summary_prompt = PromptTemplate(
    input_variables=["context"],
    template="""
        You are a helpful assistant. Summarize the following document in no more than 150 words. Only use the provided content. Do not add any information or make up facts.
        Document:
        {context}
        Summary (≤ 150 words):
    """
)

def answer_question(query: str) -> dict:
    results = retreive_relavant_chunks(query=query, top_k=5)
    context = "\n".join([doc.page_content for doc in results])
    chain = answer_prompt | llm
    response = chain.invoke({
        "context": context,
        "question": query
    })
    answer_text = response.content.strip()
    # Post-processing: check for justification
    justification_patterns = [
        r"section[\s\w\d]*[\.:]", r"paragraph[\s\w\d]*[\.:]", r"quote[\s\w\d]*[\.:]", r"supported by", r"according to", r"as stated in"
    ]
    if not any(re.search(pattern, answer_text, re.IGNORECASE) for pattern in justification_patterns):
        answer_text += "\n\nNote: The answer could not be verified with a document-based justification."
    # Collect unique source filenames from metadata
    sources = list({doc.metadata.get('source') for doc in results if doc.metadata.get('source')})
    return {"answer": answer_text, "sources": sources}


def generate_challenge_questions() -> List[str]:
    # Use a generic prompt to get relevant context
    context_query = "main ideas, logic, and comprehension points"
    results = retreive_relavant_chunks(query=context_query, top_k=8)
    context = "\n".join([doc.page_content for doc in results])
    chain = challenge_prompt | llm
    response = chain.invoke({
        "context": context
    })
    # Split into questions (assuming numbered list)
    questions = []
    for line in response.content.split("\n"):
        if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith("-") ):
            # Remove number or dash
            q = line.strip().lstrip("0123456789.- ")
            if q:
                questions.append(q)
    # Fallback: if not split, just return up to 3 lines
    if not questions:
        questions = [q.strip() for q in response.content.split("\n") if q.strip()][:3]
    return questions[:3]


def evaluate_answer(question: str, user_answer: str) -> str:
    # Use the question as the query to get relevant context
    results = retreive_relavant_chunks(query=question, top_k=5)
    context = "\n".join([doc.page_content for doc in results])
    chain = evaluate_prompt | llm
    response = chain.invoke({
        "context": context,
        "question": question,
        "user_answer": user_answer
    })
    return response.content  # Only display the feedback content

def compute_similarity_score(user_answer: str, actual_answer: str) -> int:
    """Compute a similarity score (0-100) between user and actual answer."""
    matcher = SequenceMatcher(None, user_answer.lower(), actual_answer.lower())
    return int(matcher.ratio() * 100)

def evaluate_challenge_response(question: str, user_answer: str) -> dict:
    """
    Evaluate user answer, provide feedback, justification, and a similarity score.
    """
    # Get actual answer from LLM
    results = retreive_relavant_chunks(query=question, top_k=5)
    context = "\n".join([doc.page_content for doc in results])
    chain = answer_prompt | llm
    actual_response = chain.invoke({
        "context": context,
        "question": question
    }).content.strip()
    # Evaluate user answer
    feedback = evaluate_answer(question, user_answer)
    # Compute similarity score
    score = compute_similarity_score(user_answer, actual_response)
    return {
        "feedback": feedback,
        "justification": actual_response,
        "score": score
    }

def generate_summary(context: str) -> str:
    chain = summary_prompt | llm
    response = chain.invoke({"context": context})
    return response.content.strip()
