"""
Simple RAG service for testing purposes.
"""
import logging
from typing import Dict, Any, Optional
from personal_automation_bot.services.content.text_generator import get_text_generator

logger = logging.getLogger(__name__)

class SimpleRAGService:
    """Simple RAG service for testing"""

    def __init__(self):
        """Initialize the simple RAG service"""
        self.vector_store = {}  # Simple in-memory storage
        self.text_generator = get_text_generator(provider="groq")

    async def index_document(self, content: str, title: str, metadata: Dict[str, Any] = None) -> str:
        """Index a document for RAG"""
        doc_id = f"doc_{len(self.vector_store)}"
        self.vector_store[doc_id] = {
            'content': content,
            'title': title,
            'metadata': metadata or {}
        }
        logger.info(f"Indexed document: {title}")
        return doc_id

    async def generate_with_context(self, query: str) -> str:
        """Generate response using RAG"""
        # Simple context retrieval - just use all documents
        context = ""
        for doc_id, doc_data in self.vector_store.items():
            context += f"Document: {doc_data['title']}\n{doc_data['content']}\n\n"

        if not context:
            return "No documents available for context."

        # Generate response with context
        response = self.text_generator.generate_with_context(
            prompt=query,
            context=context,
            max_tokens=200
        )

        return response
