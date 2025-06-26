from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config.pinecone import index
import os

# STEP1: Load documents
def load_documents(folder_path: str) -> List[Dict[str, Any]]:
    """
    Load documents from a specified folder.
    Supports PDF, DOCX, and TXT file types.

    Args:
        folder_path (str): Path to the folder containing documents

    Returns:
        List[Dict[str, Any]]: List of dictionaries with 'page' and 'filename' keys
    """
    pages = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif filename.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
            elif filename.endswith(".txt"):
                loader = TextLoader(file_path)
            else:
                print(f"Unsupported file type: {filename}")
                continue
            loaded_pages = loader.load()
            for page in loaded_pages:
                pages.append({"page": page, "filename": filename})
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    return pages


# STEP2: Split documents into chunks
def split_chunks(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Split documents into chunks of text.

    Args:
        pages (List[Dict[str, Any]]): List of dictionaries with 'page' and 'filename'

    Returns:
        List[Dict[str, Any]]: List of dictionaries with 'chunk' and 'filename'
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = []
    for item in pages:
        page = item["page"]
        filename = item["filename"]
        split_page_chunks = text_splitter.split_documents([page])
        for chunk in split_page_chunks:
            chunks.append({"chunk": chunk, "filename": filename})
    return chunks


# STEP3: Convert text chunks to embeddings
def convert_to_embeddings(split_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert a list of text chunks into embeddings using GoogleGenerativeAIEmbeddings.

    Args:
        split_docs (List[Dict[str, Any]]): List of dictionaries with 'chunk' and 'filename'.

    Returns:
        List[Dict[str, Any]]: List of dictionaries containing embeddings and metadata.
    """
    import os

    embed_docs = []
    try:
        if not os.environ.get("GOOGLE_API_KEY"):
            os.environ["GOOGLE_API_KEY"]

        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        for i, item in enumerate(split_docs):
            split_doc = (
                item["chunk"].page_content
                if hasattr(item["chunk"], "page_content")
                else str(item["chunk"])
            )
            filename = item["filename"]
            try:
                embed = embeddings.embed_query(split_doc)
                embed_docs.append(
                    {
                        "id": f"doc_{i}",
                        "values": embed,
                        "metadata": {"text": split_doc, "source": filename},
                    }
                )
            except Exception as e:
                print(f"Error embedding document {i}: {e}")
    except Exception as e:
        print(f"Error initializing embeddings: {e}")
    return embed_docs


# STEP4: add embeddings to Pinecone
def add_embeddings_to_pinecone(embed_docs: List[Dict[str, Any]]):
    """
    Add embedding documents to Pinecone index.

    Args:
        embed_docs (List[Dict[str, Any]]): List of dictionaries containing embeddings and metadata.
    """
    vectors = [(doc["id"], doc["values"], doc["metadata"]) for doc in embed_docs]
    try:
        index.upsert(vectors, namespace="EZTask")
        print(f"Successfully upserted {len(vectors)} vectors to Pinecone.")
    except Exception as e:
        print(f"Error upserting to Pinecone: {e}")

def retreive_relavant_chunks(query: str, top_k: int = 8) -> List[Document]:
    """
    Retrieve relevant chunks from Pinecone index based on a query.

    Args:
        query (str): The query string to search for.
        top_k (int): The number of top results to return.

    Returns:
        List[Document]: List of relevant documents.
    """
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    query_embedding = embeddings.embed_query(query)
    try:
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace="EZTask",
            include_metadata=True
        )
        return [Document(page_content=res['metadata']['text'], metadata=res['metadata']) for res in results['matches']]
    except Exception as e:
        print(f"Error retrieving relevant chunks: {e}")
        return []

