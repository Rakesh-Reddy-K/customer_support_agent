"""
Retriever for RAG - wraps the LangChain Chroma vector store as a retriever.
"""
from app.rag.vectorstore import get_vectorstore


def get_retriever(k: int = 4):
    """Get a retriever for policy/FAQ documents."""
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": k})