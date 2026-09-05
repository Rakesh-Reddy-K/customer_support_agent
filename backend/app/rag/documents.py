"""
RAG documents - loading and processing policy documents.
"""
import os
from langchain_core.documents import Document


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")


def load_documents() -> list[Document]:
    """Load all policy and FAQ documents."""
    docs = []
    policies_dir = os.path.join(DATA_DIR, "policies")
    faq_dir = os.path.join(DATA_DIR, "faq")
    
    for d in [policies_dir, faq_dir]:
        if not os.path.exists(d):
            continue
        for fname in os.listdir(d):
            if fname.endswith(".md"):
                filepath = os.path.join(d, fname)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                source_type = "policy" if "policies" in d else "faq"
                doc_name = fname.replace(".md", "").replace("_", " ").title()
                docs.append(Document(
                    page_content=content,
                    metadata={"source": source_type, "filename": fname, "title": doc_name},
                ))
    return docs