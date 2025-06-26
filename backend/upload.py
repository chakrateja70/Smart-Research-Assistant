import os
import sys
import tempfile
from typing import List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import (
    load_documents,
    split_chunks,
    convert_to_embeddings,
    add_embeddings_to_pinecone,
)
from config.pinecone import pinecone_connection


def process_uploaded_files(uploaded_files) -> dict:
    """
    Process uploaded files through the complete pipeline:
    1. Load documents
    2. Split into chunks
    3. Convert to embeddings
    4. Store in Pinecone vector database

    Args:
        uploaded_files: List of uploaded file objects from Streamlit

    Returns:
        dict: Result containing success status and metadata
    """
    try:
        pinecone_connection()

        with tempfile.TemporaryDirectory() as tmpdirname:
            file_paths = []
            for uploaded_file in uploaded_files:
                file_path = os.path.join(tmpdirname, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_paths.append(file_path)

            # Step 1: Load documents
            pages = load_documents(tmpdirname)
            if not pages:
                return {
                    "success": False,
                    "message": "No valid documents found in uploaded files",
                    "documents_processed": 0,
                    "chunks_created": 0,
                    "vectors_stored": 0,
                }

            # Step 2: Split documents into chunks
            chunks = split_chunks(pages)
            if not chunks:
                return {
                    "success": False,
                    "message": "Failed to create chunks from documents",
                    "documents_processed": len(pages),
                    "chunks_created": 0,
                    "vectors_stored": 0,
                }

            # Step 3: Convert chunks to embeddings
            embeddings = convert_to_embeddings(chunks)
            if not embeddings:
                return {
                    "success": False,
                    "message": "Failed to create embeddings from chunks",
                    "documents_processed": len(pages),
                    "chunks_created": len(chunks),
                    "vectors_stored": 0,
                }

            # Step 4: Store embeddings in Pinecone
            add_embeddings_to_pinecone(embeddings)

            return {
                "success": True,
                "message": "Documents successfully processed and stored in vector database",
                "documents_processed": len(pages),
                "chunks_created": len(chunks),
                "vectors_stored": len(embeddings),
                "files_processed": [
                    uploaded_file.name for uploaded_file in uploaded_files
                ],
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing files: {str(e)}",
            "documents_processed": 0,
            "chunks_created": 0,
            "vectors_stored": 0,
        }


def get_processing_status():
    """
    Get the current status of document processing
    """
    return {"status": "ready"}
