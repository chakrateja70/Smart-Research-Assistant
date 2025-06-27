import streamlit as st
import sys
import os

backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_path)

from backend.upload import process_uploaded_files
from backend.generate_response import answer_question, generate_challenge_questions, evaluate_answer, generate_summary, evaluate_challenge_response
from backend.utils import load_documents

st.set_page_config(
    page_title="Smart Assistant for Research Summarization",
    page_icon="📚",
    layout="wide"
)

# --- SIDEBAR ---
with st.sidebar:
    st.title("📄 Smart Assistant for Research Summarization")
    st.markdown("""
    **Objective:**
    > Develop an AI assistant that not only reads content from documents but can also understand and reason through it.
    
    **Problem:**
    Reading large documents (research papers, legal files, technical manuals) is time-consuming. Traditional tools lack deep comprehension and logical reasoning.
        
    **How to use this assistant:**
    1. Upload your document(s) using the uploader below.
    2. After upload, a summary of your document will be displayed.
    3. Choose an interaction mode:
       - **Ask Anything:** Type any question about your document and get a grounded, referenced answer.
       - **Challenge Me:** Receive logic/comprehension questions based on your document, answer them, and get feedback.
    4. You can switch between modes at any time using the buttons provided.
    """)
    st.markdown("---")
    st.subheader("🔧 System Status")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    if google_api_key:
        st.success("✅ Google API Key configured")
    else:
        st.error("❌ Google API Key missing")
    if pinecone_api_key:
        st.success("✅ Pinecone API Key configured")
    else:
        st.error("❌ Pinecone API Key missing")

# --- MAIN PAGE ---

st.title("📚 Smart Assistant for Research Summarization")
st.markdown("Upload your documents and store them in a vector database for AI-powered search and retrieval.")

st.subheader("📁 Upload Documents")

# Track uploaded files in session state for display
if 'vector_files' not in st.session_state:
    st.session_state.vector_files = []

# Disable upload button after successful upload
upload_disabled = False  # Always keep upload enabled

# Hide upload UI if summary is present
if not st.session_state.get("document_summary"):
    uploaded_files = st.file_uploader(
        "Choose PDF, DOCX, or TXT files", 
        type=["pdf", "docx", "txt"], 
        accept_multiple_files=True,
        help="You can upload multiple files at once. Supported formats: PDF, DOCX, TXT",
        disabled=upload_disabled
    )
    if uploaded_files:
        with st.expander("View selected files"):
            for file in uploaded_files:
                st.write(f"• {file.name} ({file.size/1024:.1f} KB)")
        if st.button("Process and Upload to Vector Database", type="primary", disabled=upload_disabled):
            progress_bar = st.progress(0)
            status_text = st.empty()
            with st.spinner("🔄 Processing documents..."):
                status_text.text("📖 Loading documents...")
                progress_bar.progress(25)
                status_text.text("✂️ Splitting into chunks...")
                progress_bar.progress(50)
                status_text.text("🧠 Creating embeddings...")
                progress_bar.progress(75)
                status_text.text("💾 Storing in vector database...")
                result = process_uploaded_files(uploaded_files)
                progress_bar.progress(100)
            progress_bar.empty()
            status_text.empty()
            st.session_state.processing_complete = True
            if result["success"]:
                st.session_state.processing_success = True
                st.session_state.vector_files = result.get("files_processed", [])
                st.success("✅ Documents successfully processed and stored!")
                # After successful processing, show auto summary
                import tempfile
                with tempfile.TemporaryDirectory() as tmpdirname:
                    file_paths = []
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(tmpdirname, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_paths.append(file_path)
                    # Load all pages from all uploaded files
                    pages = load_documents(tmpdirname)
                    # Combine all page contents for summary
                    context = "\n".join([str(page["page"].page_content) for page in pages])
                    with st.spinner("Generating summary..."):
                        summary = generate_summary(context)
                    st.session_state["document_summary"] = summary
            else:
                st.session_state.processing_success = False
                st.error("❌ Processing failed. Please try again.")

# Show files in vector database after upload
if st.session_state.get("processing_success") and st.session_state.get("vector_files") and not st.session_state.get("document_summary"):
    st.markdown("**Files in Vector Database:**")
    for fname in st.session_state.vector_files:
        st.markdown(f"- `{fname}`")

# Lazy loader for summary
if st.session_state.get("processing_success") and st.session_state.get("document_summary"):
    st.markdown(
        """
        <div style='background-color: #222; border-radius: 8px; padding: 1em; margin-bottom: 1em; border: 1px solid #444;'>
        <b>📝 Document Summary:</b><br>
        <span style='color: #ccc;'>""" + st.session_state["document_summary"] + "</span></div>", unsafe_allow_html=True
    )

st.markdown("---")

if 'active_mode' not in st.session_state:
    st.session_state.active_mode = None

interaction_col1, interaction_col2 = st.columns(2)

with interaction_col1:
    st.subheader("🤖 Ask Anything")
    ask_btn = st.button("Activate Ask Anything", key="activate_ask_anything")
    if ask_btn:
        st.session_state.active_mode = "ask_anything"
        # Deactivate challenge questions state
        if "challenge_questions" in st.session_state:
            del st.session_state["challenge_questions"]
        if "challenge_answers" in st.session_state:
            del st.session_state["challenge_answers"]
        if "challenge_feedback" in st.session_state:
            del st.session_state["challenge_feedback"]
    if st.session_state.active_mode == "ask_anything":
        user_query = st.text_input("Your question:", key="ask_anything_query")
        if "ask_anything_answer" not in st.session_state:
            st.session_state.ask_anything_answer = None
        # Clear previous answer when user types a new question
        if user_query == "" and st.session_state.ask_anything_answer is not None:
            st.session_state.ask_anything_answer = None
        if st.button("Ask", key="ask_anything_btn") and user_query:
            st.session_state.ask_anything_answer = None  # Clear previous answer and source
            with st.spinner("Thinking..."):
                result = answer_question(user_query)
            st.session_state.ask_anything_answer = result
        if st.session_state.ask_anything_answer:
            answer = st.session_state.ask_anything_answer.get("answer", "")
            sources = st.session_state.ask_anything_answer.get("sources", [])
            st.markdown(f"**Answer:** {answer}")
            # Only show source if answer is not a fallback/no-answer message
            if sources:
                st.markdown(f"<span style='font-size: 0.9em; color: #888;'>Source: {', '.join(sources)}</span>", unsafe_allow_html=True)
    else:
        st.info("Click 'Activate Ask Anything' to use this mode.")

with interaction_col2:
    st.subheader("🎯 Challenge Me")
    challenge_btn = st.button("Activate Challenge Me", key="activate_challenge_me")
    if challenge_btn:
        st.session_state.active_mode = "challenge_me"
        # Deactivate ask anything state
        if "ask_anything_query" in st.session_state:
            del st.session_state["ask_anything_query"]
    if st.session_state.active_mode == "challenge_me":
        if "challenge_questions" not in st.session_state:
            with st.spinner("Generating questions..."):
                st.session_state.challenge_questions = generate_challenge_questions()
            st.session_state.challenge_answers = ["" for _ in range(3)]
            st.session_state.challenge_feedback = [None for _ in range(3)]
        st.markdown("**Try to answer these questions based on your document:**")
        for i, q in enumerate(st.session_state.challenge_questions):
            st.markdown(f"**Q{i+1}: {q}**")
            st.session_state.challenge_answers[i] = st.text_input(
                f"Your answer to Q{i+1}",
                value=st.session_state.challenge_answers[i],
                key=f"challenge_answer_{i}"
            )
        if st.button("Submit Answers", key="submit_challenge_btn"):
            st.session_state.challenge_feedback = []
            st.session_state.challenge_justification = []
            st.session_state.challenge_score = []
            for i, q in enumerate(st.session_state.challenge_questions):
                user_ans = st.session_state.challenge_answers[i]
                with st.spinner(f"Evaluating Q{i+1}..."):
                    result = evaluate_challenge_response(q, user_ans)
                st.session_state.challenge_feedback.append(result["feedback"])
                st.session_state.challenge_justification.append(result["justification"])
                st.session_state.challenge_score.append(result["score"])
        # Show feedback if available
        if any(st.session_state.get("challenge_feedback", [])):
            st.markdown("---")
            st.markdown("**Feedback:**")
            for i in range(len(st.session_state.get("challenge_feedback", []))):
                feedback = st.session_state.challenge_feedback[i]
                justification = st.session_state.challenge_justification[i]
                score = st.session_state.challenge_score[i]
                if feedback:
                    st.markdown(f"**Q{i+1} Feedback:** {feedback}")
                    st.markdown(f"**Justification:** {justification}")
                    st.markdown(f"**Similarity Score:** {score} / 100")
        if st.button("🔄 New Challenge", key="new_challenge_btn"):
            del st.session_state["challenge_questions"]
            del st.session_state["challenge_answers"]
            del st.session_state["challenge_feedback"]
            del st.session_state["challenge_justification"]
            del st.session_state["challenge_score"]
            st.rerun()
    else:
        st.info("Click 'Activate Challenge Me' to use this mode.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>🚀 EZ Task - Powered by LangChain, Google AI, and Pinecone</div>", 
    unsafe_allow_html=True
)