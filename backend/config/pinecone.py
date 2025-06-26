from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os

load_dotenv(override=True)

pc = Pinecone(os.getenv("PINECONE_API_KEY"))

def pinecone_connection():
    """
    Connect to Pinecone and create an index if it doesn't exist.
    """
    index_name = "nabla-rag-poc"
    try:
        if not pc.has_index(index_name):
            pc.create_index(
                name=index_name,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
    except Exception as e:
        print(f"Error connecting to Pinecone or creating index: {e}")

# Create index connection for global use
index = pc.Index("nabla-rag-poc")
