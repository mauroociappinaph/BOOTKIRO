"""
Document indexing functionality for the RAG system.
Handles processing documents and creating embeddings.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Union, Callable
import hashlib
import json

# For embedding generation
try:
    import sentence_transformers
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from personal_automation_bot.services.rag.vector_store import get_vector_store, VectorStore

logger = logging.getLogger(__name__)

class DocumentIndexer:
    """Handles indexing documents for RAG."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        vector_store_type: str = "faiss",
        vector_store_path: Optional[str] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        """
        Initialize the document indexer.

        Args:
            vector_store: Vector store instance (if None, one will be created)
            vector_store_type: Type of vector store to create if none provided
            vector_store_path: Path for vector store data
            embedding_model: Name of the sentence transformer model to use
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
        """
        # Initialize vector store
        self.vector_store = vector_store or get_vector_store(
            store_type=vector_store_type,
            store_path=vector_store_path
        )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Initialize embedding model
        self._init_embedding_model(embedding_model)

        # Cache for document hashes to avoid reprocessing
        self.document_cache_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "..", "data", "vector_store", "document_cache.json"
        )
        self.document_cache = self._load_document_cache()

    def _init_embedding_model(self, model_name: str) -> None:
        """Initialize the embedding model."""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Install it with 'pip install sentence-transformers'"
            )

        try:
            self.embedding_model = sentence_transformers.SentenceTransformer(model_name)
            self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
            logger.info(f"Initialized embedding model {model_name} with dimension {self.embedding_dimension}")
        except Exception as e:
            logger.error(f"Failed to load embedding model {model_name}: {e}")
            raise

    def _load_document_cache(self) -> Dict[str, str]:
        """Load document cache from disk."""
        if os.path.exists(self.document_cache_path):
            try:
                with open(self.document_cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load document cache: {e}")

        return {}

    def _save_document_cache(self) -> None:
        """Save document cache to disk."""
        os.makedirs(os.path.dirname(self.document_cache_path), exist_ok=True)
        try:
            with open(self.document_cache_path, 'w') as f:
                json.dump(self.document_cache, f)
        except Exception as e:
            logger.warning(f"Failed to save document cache: {e}")

    def _compute_document_hash(self, document: Dict[str, Any]) -> str:
        """Compute a hash for a document to detect changes."""
        # Extract content for hashing
        content = document.get("text", "") or document.get("content", "") or str(document)
        return hashlib.md5(content.encode()).hexdigest()

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap."""
        if not text:
            return []

        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk:
                chunks.append(chunk)

        return chunks

    def _process_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a document into chunks with metadata."""
        # Extract content
        content = document.get("text", "") or document.get("content", "") or str(document)

        # Create chunks
        chunks = self._chunk_text(content)

        # Create processed chunks with metadata
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            # Create a new document for each chunk
            chunk_doc = document.copy()
            chunk_doc["text"] = chunk
            chunk_doc["chunk_index"] = i
            chunk_doc["total_chunks"] = len(chunks)

            # Remove duplicate content field if present
            if "content" in chunk_doc and "text" in chunk_doc:
                del chunk_doc["content"]

            processed_chunks.append(chunk_doc)

        return processed_chunks

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []

        embeddings = self.embedding_model.encode(texts)
        return embeddings.tolist()

    def index_document(self, document: Dict[str, Any]) -> List[str]:
        """
        Index a single document.

        Args:
            document: Document to index

        Returns:
            List of chunk IDs
        """
        # Check if document has changed
        doc_hash = self._compute_document_hash(document)
        doc_id = document.get("id", str(hash(str(document))))

        if doc_id in self.document_cache and self.document_cache[doc_id] == doc_hash:
            logger.info(f"Document {doc_id} hasn't changed, skipping indexing")
            return []

        # Process document into chunks
        chunks = self._process_document(document)
        if not chunks:
            logger.warning(f"Document {doc_id} produced no chunks")
            return []

        # Generate embeddings
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.generate_embeddings(texts)

        # Add to vector store
        chunk_ids = self.vector_store.add_documents(chunks, embeddings)

        # Update cache
        self.document_cache[doc_id] = doc_hash
        self._save_document_cache()

        logger.info(f"Indexed document {doc_id} into {len(chunk_ids)} chunks")
        return chunk_ids

    def index_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Index multiple documents.

        Args:
            documents: List of documents to index

        Returns:
            List of all chunk IDs
        """
        all_chunk_ids = []
        for document in documents:
            chunk_ids = self.index_document(document)
            all_chunk_ids.extend(chunk_ids)

        return all_chunk_ids

    def delete_document(self, doc_id: str) -> None:
        """
        Delete a document from the index.

        Args:
            doc_id: Document ID to delete
        """
        # In a real implementation, we would need to track which chunks belong to which document
        # For simplicity, we'll just remove from the cache
        if doc_id in self.document_cache:
            del self.document_cache[doc_id]
            self._save_document_cache()
            logger.info(f"Removed document {doc_id} from cache")

    def clear_index(self) -> None:
        """Clear the entire index."""
        # Create a new vector store
        store_type = self.vector_store.__class__.__name__
        if "FAISS" in store_type:
            self.vector_store = get_vector_store("faiss", self.vector_store.store_path)
        elif "Chroma" in store_type:
            self.vector_store = get_vector_store("chroma", self.vector_store.store_path)

        # Clear cache
        self.document_cache = {}
        self._save_document_cache()

        logger.info("Cleared document index")
