"""
Retrieval-Augmented Generation (RAG) service.
Provides functionality for indexing documents and retrieving relevant context.
"""

from personal_automation_bot.services.rag.vector_store import (
    VectorStore,
    FAISSVectorStore,
    ChromaVectorStore,
    get_vector_store
)
from personal_automation_bot.services.rag.indexer import DocumentIndexer
from personal_automation_bot.services.rag.retriever import DocumentRetriever

__all__ = [
    'VectorStore',
    'FAISSVectorStore',
    'ChromaVectorStore',
    'get_vector_store',
    'DocumentIndexer',
    'DocumentRetriever',
]
