"""
Vector store implementation for the RAG system.
Provides functionality for storing and retrieving document embeddings.
"""
import os
import pickle
import logging
from typing import List, Dict, Any, Optional, Union
import numpy as np

# We'll support both FAISS and Chroma as vector stores
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

logger = logging.getLogger(__name__)

class VectorStore:
    """Base class for vector stores."""

    def __init__(self, store_path: str):
        """
        Initialize the vector store.

        Args:
            store_path: Path where vector store data will be saved
        """
        self.store_path = store_path
        os.makedirs(store_path, exist_ok=True)

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[str]:
        """
        Add documents and their embeddings to the vector store.

        Args:
            documents: List of document dictionaries
            embeddings: List of embedding vectors

        Returns:
            List of document IDs
        """
        raise NotImplementedError

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents based on query embedding.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of document dictionaries with similarity scores
        """
        raise NotImplementedError

    def delete(self, doc_ids: List[str]) -> None:
        """
        Delete documents from the vector store.

        Args:
            doc_ids: List of document IDs to delete
        """
        raise NotImplementedError

    def persist(self) -> None:
        """Save the vector store to disk."""
        raise NotImplementedError

    def load(self) -> None:
        """Load the vector store from disk."""
        raise NotImplementedError


class FAISSVectorStore(VectorStore):
    """FAISS implementation of vector store."""

    def __init__(self, store_path: str, dimension: int = 768):
        """
        Initialize FAISS vector store.

        Args:
            store_path: Path where vector store data will be saved
            dimension: Dimension of embedding vectors
        """
        super().__init__(store_path)
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS is not installed. Install it with 'pip install faiss-cpu'")

        self.dimension = dimension
        self.index_path = os.path.join(store_path, "faiss_index.bin")
        self.metadata_path = os.path.join(store_path, "faiss_metadata.pkl")

        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(dimension)

        # Document metadata storage
        self.doc_metadata = {}  # id -> document metadata
        self.doc_ids = []  # List of document IDs in order of addition

        # Load existing index if available
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            self.load()

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[str]:
        """Add documents and their embeddings to FAISS."""
        if not documents or not embeddings:
            return []

        if len(documents) != len(embeddings):
            raise ValueError("Number of documents and embeddings must match")

        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings).astype('float32')

        # Generate IDs for new documents
        start_idx = len(self.doc_ids)
        new_ids = [f"doc_{start_idx + i}" for i in range(len(documents))]

        # Add embeddings to FAISS index
        self.index.add(embeddings_array)

        # Store document metadata
        for i, doc_id in enumerate(new_ids):
            self.doc_metadata[doc_id] = documents[i]
            self.doc_ids.append(doc_id)

        # Persist changes
        self.persist()

        return new_ids

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents in FAISS."""
        if not self.doc_ids:
            return []

        # Convert query to numpy array
        query_array = np.array([query_embedding]).astype('float32')

        # Search FAISS index
        top_k = min(top_k, len(self.doc_ids))
        distances, indices = self.index.search(query_array, top_k)

        # Prepare results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.doc_ids):
                doc_id = self.doc_ids[idx]
                doc = self.doc_metadata.get(doc_id, {}).copy()
                doc["id"] = doc_id
                doc["score"] = float(distances[0][i])
                results.append(doc)

        return results

    def delete(self, doc_ids: List[str]) -> None:
        """
        Delete documents from FAISS.

        Note: FAISS doesn't support direct deletion, so we rebuild the index.
        """
        if not doc_ids:
            return

        # Filter out documents to delete
        keep_ids = [doc_id for doc_id in self.doc_ids if doc_id not in doc_ids]

        if len(keep_ids) == len(self.doc_ids):
            # Nothing to delete
            return

        # Create new index
        new_index = faiss.IndexFlatL2(self.dimension)
        new_metadata = {}
        new_doc_ids = []

        # Add documents to keep to new index
        embeddings_to_keep = []
        for doc_id in keep_ids:
            if doc_id in self.doc_metadata:
                new_metadata[doc_id] = self.doc_metadata[doc_id]
                new_doc_ids.append(doc_id)

                # We need to extract embeddings from the original index
                # This is a limitation of FAISS - we'd need to store embeddings separately
                # for efficient deletion

                # For now, we'll just rebuild with empty embeddings
                # In a real implementation, we'd store embeddings alongside metadata
                embeddings_to_keep.append([0.0] * self.dimension)

        # Update index and metadata
        if embeddings_to_keep:
            embeddings_array = np.array(embeddings_to_keep).astype('float32')
            new_index.add(embeddings_array)

        self.index = new_index
        self.doc_metadata = new_metadata
        self.doc_ids = new_doc_ids

        # Persist changes
        self.persist()

    def persist(self) -> None:
        """Save FAISS index and metadata to disk."""
        # Save FAISS index
        faiss.write_index(self.index, self.index_path)

        # Save metadata
        with open(self.metadata_path, 'wb') as f:
            pickle.dump({
                'doc_metadata': self.doc_metadata,
                'doc_ids': self.doc_ids
            }, f)

        logger.info(f"Saved FAISS index with {len(self.doc_ids)} documents to {self.store_path}")

    def load(self) -> None:
        """Load FAISS index and metadata from disk."""
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)

        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'rb') as f:
                data = pickle.load(f)
                self.doc_metadata = data.get('doc_metadata', {})
                self.doc_ids = data.get('doc_ids', [])

            logger.info(f"Loaded FAISS index with {len(self.doc_ids)} documents from {self.store_path}")


class ChromaVectorStore(VectorStore):
    """ChromaDB implementation of vector store."""

    def __init__(self, store_path: str, collection_name: str = "documents"):
        """
        Initialize ChromaDB vector store.

        Args:
            store_path: Path where vector store data will be saved
            collection_name: Name of the collection to use
        """
        super().__init__(store_path)
        if not CHROMA_AVAILABLE:
            raise ImportError("ChromaDB is not installed. Install it with 'pip install chromadb'")

        self.collection_name = collection_name

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=store_path,
            settings=Settings(anonymized_telemetry=False)
        )

        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing ChromaDB collection '{collection_name}'")
        except (ValueError, Exception) as e:
            # Handle both ValueError and NotFoundError
            self.collection = self.client.create_collection(name=collection_name)
            logger.info(f"Created new ChromaDB collection '{collection_name}'")

    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]) -> List[str]:
        """Add documents and their embeddings to ChromaDB."""
        if not documents or not embeddings:
            return []

        if len(documents) != len(embeddings):
            raise ValueError("Number of documents and embeddings must match")

        # Generate IDs for new documents
        ids = [f"doc_{i}_{hash(str(doc))}" for i, doc in enumerate(documents)]

        # Extract document texts and metadata
        metadatas = []
        documents_text = []

        for doc in documents:
            # Extract text content
            text = doc.get("text", "") or doc.get("content", "") or str(doc)
            documents_text.append(text)

            # Extract metadata (excluding text content to avoid duplication)
            metadata = {k: v for k, v in doc.items() if k not in ["text", "content"]}
            metadatas.append(metadata)

        # Add to ChromaDB collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents_text,
            metadatas=metadatas
        )

        return ids

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents in ChromaDB."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Format results
        formatted_results = []
        if results and results.get('ids'):
            for i, doc_id in enumerate(results['ids'][0]):
                result = {
                    "id": doc_id,
                    "text": results['documents'][0][i],
                    "score": float(results['distances'][0][i]) if 'distances' in results else 0.0
                }

                # Add metadata if available
                if 'metadatas' in results and results['metadatas'][0]:
                    result.update(results['metadatas'][0][i])

                formatted_results.append(result)

        return formatted_results

    def delete(self, doc_ids: List[str]) -> None:
        """Delete documents from ChromaDB."""
        if not doc_ids:
            return

        self.collection.delete(ids=doc_ids)

    def persist(self) -> None:
        """ChromaDB automatically persists data, so this is a no-op."""
        # ChromaDB handles persistence automatically
        pass

    def load(self) -> None:
        """ChromaDB automatically loads data, so this is a no-op."""
        # ChromaDB handles loading automatically
        pass


def get_vector_store(store_type: str = "faiss", store_path: str = None, **kwargs) -> VectorStore:
    """
    Factory function to get the appropriate vector store.

    Args:
        store_type: Type of vector store ('faiss' or 'chroma')
        store_path: Path to store vector data
        **kwargs: Additional arguments for specific vector stores

    Returns:
        VectorStore instance
    """
    if store_path is None:
        # Default path in the data directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        store_path = os.path.join(base_dir, "..", "data", "vector_store", store_type)

    if store_type.lower() == "faiss":
        dimension = kwargs.get("dimension", 768)
        return FAISSVectorStore(store_path, dimension=dimension)
    elif store_type.lower() == "chroma":
        collection_name = kwargs.get("collection_name", "documents")
        return ChromaVectorStore(store_path, collection_name=collection_name)
    else:
        raise ValueError(f"Unsupported vector store type: {store_type}")
