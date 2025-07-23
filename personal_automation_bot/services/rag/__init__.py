"""
Retrieval-Augmented Generation (RAG) service.
Provides functionality for indexing documents and retrieving relevant context.
"""

# Import document processors (these don't require heavy dependencies)
from personal_automation_bot.services.rag.document_processors import (
    DocumentProcessor,
    TextProcessor,
    PDFProcessor,
    DocxProcessor,
    HTMLProcessor,
    get_document_processor
)

# Try to import vector store components (require numpy, faiss, etc.)
try:
    from personal_automation_bot.services.rag.vector_store import (
        VectorStore,
        FAISSVectorStore,
        ChromaVectorStore,
        get_vector_store
    )
    from personal_automation_bot.services.rag.indexer import DocumentIndexer
    from personal_automation_bot.services.rag.retriever import DocumentRetriever
    from personal_automation_bot.services.rag.document_indexer import DocumentIndexingService

    __all__ = [
        'VectorStore',
        'FAISSVectorStore',
        'ChromaVectorStore',
        'get_vector_store',
        'DocumentIndexer',
        'DocumentRetriever',
        'DocumentIndexingService',
        'DocumentProcessor',
        'TextProcessor',
        'PDFProcessor',
        'DocxProcessor',
        'HTMLProcessor',
        'get_document_processor',
    ]
except ImportError as e:
    # If vector store dependencies are missing, only export document processors
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Vector store dependencies not available: {e}")

    __all__ = [
        'DocumentProcessor',
        'TextProcessor',
        'PDFProcessor',
        'DocxProcessor',
        'HTMLProcessor',
        'get_document_processor',
    ]
