"""
Embeddings configuration for RAG vector store.

Supports multiple embedding providers, fully configurable via environment
variables (no code changes required to swap models):
  - EMBEDDING_PROVIDER=ollama  -> uses OLLAMA_EMBEDDING_MODEL (default nomic-embed-text)
  - EMBEDDING_PROVIDER=openai  -> uses OPENAI_EMBEDDING_MODEL via OPENAI_API_KEY
  - EMBEDDING_PROVIDER=chroma  -> uses ChromaDB built-in ONNX (all-MiniLM-L6-v2)
"""
from app.config.settings import settings


class _ChromaEmbeddingWrapper:
    """Thin adapter that wraps a ChromaDB EmbeddingFunction into the
    LangChain ``Embeddings`` interface (``embed_documents`` / ``embed_query``).
    Used only when ``EMBEDDING_PROVIDER=chroma``."""

    def __init__(self, chroma_fn):
        self._fn = chroma_fn

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._fn(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._fn([text])[0]


def get_embeddings():
    """Get the LangChain embedding function based on configured provider."""
    provider = settings.embedding_provider.lower()

    if provider == "ollama":
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(
            model=settings.embedding_model,
            base_url=settings.ollama_base_url,
        )

    if provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
        )

    # Default: ChromaDB built-in ONNX embeddings wrapped for LangChain
    from chromadb.utils import embedding_functions
    return _ChromaEmbeddingWrapper(embedding_functions.DefaultEmbeddingFunction())

