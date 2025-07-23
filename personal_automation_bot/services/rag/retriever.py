"""
Retrieval functionality for the RAG system.
Handles semantic search and context retrieval.
"""
import logging
from typing import List, Dict, Any, Optional, Union, Tuple

from personal_automation_bot.services.rag.indexer import DocumentIndexer
from personal_automation_bot.services.rag.vector_store import VectorStore, get_vector_store

logger = logging.getLogger(__name__)

class DocumentRetriever:
    """Handles retrieving relevant documents for RAG."""

    def __init__(
        self,
        indexer: Optional[DocumentIndexer] = None,
        vector_store: Optional[VectorStore] = None,
        vector_store_type: str = "faiss",
        vector_store_path: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """
        Initialize the document retriever.

        Args:
            indexer: Document indexer instance (if None, one will be created)
            vector_store: Vector store instance (if None, one will be created)
            vector_store_type: Type of vector store to create if none provided
            vector_store_path: Path for vector store data
            embedding_model: Name of the sentence transformer model to use
        """
        # Initialize vector store if not provided
        self.vector_store = vector_store or get_vector_store(
            store_type=vector_store_type,
            store_path=vector_store_path
        )

        # Initialize indexer if not provided
        self.indexer = indexer or DocumentIndexer(
            vector_store=self.vector_store,
            embedding_model=embedding_model
        )

    def search(self, query: str, top_k: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for documents relevant to a query.

        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional filters to apply to results

        Returns:
            List of relevant documents with similarity scores
        """
        # Generate embedding for query
        query_embedding = self.indexer.generate_embeddings([query])[0]

        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=top_k)

        # Apply filters if provided
        if filters and results:
            filtered_results = []
            for result in results:
                if self._matches_filters(result, filters):
                    filtered_results.append(result)
            results = filtered_results

        logger.info(f"Found {len(results)} results for query: {query[:50]}...")
        return results

    def _matches_filters(self, document: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if a document matches the given filters."""
        for key, value in filters.items():
            if key not in document:
                return False

            if isinstance(value, list):
                if document[key] not in value:
                    return False
            elif document[key] != value:
                return False

        return True

    def get_relevant_context(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        max_tokens: Optional[int] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Get relevant context for a query, formatted for use in RAG.

        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional filters to apply to results
            max_tokens: Maximum number of tokens to include in context

        Returns:
            Tuple of (formatted context string, list of source documents)
        """
        # Search for relevant documents
        results = self.search(query, top_k=top_k, filters=filters)

        # Format context
        context_parts = []
        for i, result in enumerate(results):
            text = result.get("text", "")
            source = result.get("source", "Unknown")
            score = result.get("score", 0.0)

            context_parts.append(f"[Document {i+1}] (Source: {source}, Relevance: {score:.2f})\n{text}\n")

        context = "\n".join(context_parts)

        # Truncate if needed (simple character-based truncation)
        if max_tokens and len(context) > max_tokens * 4:  # Rough approximation
            context = context[:max_tokens * 4] + "..."

        return context, results
