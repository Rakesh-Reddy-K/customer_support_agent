"""
Vector store setup for RAG using LangChain's Chroma wrapper.

The embedding provider is fully configurable via env vars:
  EMBEDDING_PROVIDER  - ollama | openai | chroma
  EMBEDDING_MODEL     - model name (e.g. nomic-embed-text, text-embedding-3-small)
  OLLAMA_BASE_URL     - Ollama server URL (default http://host.docker.internal:11434)
"""
import os
from app.rag.documents import load_documents
from app.rag.embeddings import get_embeddings
from app.config.settings import settings

_vectorstore = None


def get_vectorstore():
    """Get or initialize the LangChain Chroma vector store."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    persist_dir = settings.chroma_persist_dir
    embedding_fn = get_embeddings()

    from langchain_community.vectorstores import Chroma

    # When using Ollama / OpenAI embeddings (LangChain Embeddings objects),
    # wrap them via LangChain Chroma.  For native ChromaDB ONNX embeddings
    # we also go through LangChain Chroma so everything is consistent.
    _vectorstore = Chroma(
        collection_name="techkart_policies",
        embedding_function=embedding_fn,
        persist_directory=persist_dir,
    )

    # Seed documents if the collection is empty
    if _vectorstore._collection.count() == 0:
        docs = load_documents()
        if docs:
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(docs)
            _vectorstore.add_documents(chunks)
            print(f"Seeded {len(chunks)} chunks into ChromaDB")
        else:
            print("No RAG documents found to seed")

    return _vectorstore