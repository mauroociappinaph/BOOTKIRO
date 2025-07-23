"""
Tests for the vector store implementation.
"""
import os
import shutil
import tempfile
import unittest
import numpy as np

from personal_automation_bot.services.rag.vector_store import (
    FAISSVectorStore,
    ChromaVectorStore,
    get_vector_store
)
from personal_automation_bot.services.rag.indexer import DocumentIndexer
from personal_automation_bot.services.rag.retriever import DocumentRetriever

class TestVectorStore(unittest.TestCase):
    """Test vector store functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for vector store
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_faiss_vector_store(self):
        """Test FAISS vector store."""
        try:
            import faiss
        except ImportError:
            self.skipTest("FAISS not installed")

        # Create vector store
        store = FAISSVectorStore(self.temp_dir, dimension=128)

        # Test adding documents
        docs = [
            {"id": "1", "text": "This is a test document about AI"},
            {"id": "2", "text": "Another document about machine learning"},
            {"id": "3", "text": "This document is about databases"}
        ]

        # Create random embeddings for testing
        embeddings = np.random.rand(3, 128).astype('float32').tolist()

        # Add documents
        ids = store.add_documents(docs, embeddings)
        self.assertEqual(len(ids), 3)

        # Test search
        query_embedding = np.random.rand(128).astype('float32').tolist()
        results = store.search(query_embedding, top_k=2)
        self.assertEqual(len(results), 2)

        # Test persistence
        store.persist()

        # Create new store and load
        new_store = FAISSVectorStore(self.temp_dir, dimension=128)
        self.assertEqual(len(new_store.doc_ids), 3)

        # Test deletion
        new_store.delete([ids[0]])
        self.assertEqual(len(new_store.doc_ids), 2)

    def test_chroma_vector_store(self):
        """Test ChromaDB vector store."""
        try:
            import chromadb
        except ImportError:
            self.skipTest("ChromaDB not installed")

        # Create vector store
        store = ChromaVectorStore(self.temp_dir, collection_name="test")

        # Test adding documents
        docs = [
            {"id": "1", "text": "This is a test document about AI"},
            {"id": "2", "text": "Another document about machine learning"},
            {"id": "3", "text": "This document is about databases"}
        ]

        # Create random embeddings for testing
        embeddings = np.random.rand(3, 768).astype('float32').tolist()

        # Add documents
        ids = store.add_documents(docs, embeddings)
        self.assertEqual(len(ids), 3)

        # Test search
        query_embedding = np.random.rand(768).astype('float32').tolist()
        results = store.search(query_embedding, top_k=2)
        self.assertEqual(len(results), 2)

        # Test deletion
        store.delete([ids[0]])
        results = store.search(query_embedding, top_k=3)
        self.assertEqual(len(results), 2)

    def test_factory_function(self):
        """Test vector store factory function."""
        # Test FAISS
        try:
            store = get_vector_store("faiss", self.temp_dir)
            self.assertIsInstance(store, FAISSVectorStore)
        except ImportError:
            pass

        # Test ChromaDB
        try:
            store = get_vector_store("chroma", self.temp_dir)
            self.assertIsInstance(store, ChromaVectorStore)
        except ImportError:
            pass

        # Test invalid type
        with self.assertRaises(ValueError):
            get_vector_store("invalid", self.temp_dir)


class TestDocumentIndexer(unittest.TestCase):
    """Test document indexer functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for vector store
        self.temp_dir = tempfile.mkdtemp()

        # Skip if sentence-transformers not available
        try:
            import sentence_transformers
        except ImportError:
            self.skipTest("sentence-transformers not installed")

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_document_processing(self):
        """Test document processing."""
        # Create indexer with mock vector store
        class MockVectorStore:
            def __init__(self):
                self.documents = []
                self.embeddings = []
                self.store_path = "mock_path"

            def add_documents(self, documents, embeddings):
                self.documents.extend(documents)
                self.embeddings.extend(embeddings)
                return [f"id_{i}" for i in range(len(documents))]

        mock_store = MockVectorStore()

        # Create indexer with small model for testing
        indexer = DocumentIndexer(
            vector_store=mock_store,
            embedding_model="all-MiniLM-L6-v2",
            chunk_size=100,
            chunk_overlap=20
        )

        # Test document chunking
        document = {
            "id": "test_doc",
            "title": "Test Document",
            "text": "This is a test document. " * 20  # ~400 characters
        }

        # Index document
        chunk_ids = indexer.index_document(document)

        # Check that document was chunked
        self.assertGreater(len(mock_store.documents), 1)

        # Check that embeddings were generated
        self.assertEqual(len(mock_store.documents), len(mock_store.embeddings))


class TestDocumentRetriever(unittest.TestCase):
    """Test document retriever functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for vector store
        self.temp_dir = tempfile.mkdtemp()

        # Skip if sentence-transformers not available
        try:
            import sentence_transformers
        except ImportError:
            self.skipTest("sentence-transformers not installed")

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_search(self):
        """Test search functionality."""
        # Create mock indexer and vector store
        class MockVectorStore:
            def search(self, query_embedding, top_k=5):
                return [
                    {"id": "1", "text": "Document 1", "score": 0.9, "source": "test"},
                    {"id": "2", "text": "Document 2", "score": 0.8, "source": "test"},
                    {"id": "3", "text": "Document 3", "score": 0.7, "source": "other"}
                ][:top_k]

        class MockIndexer:
            def generate_embeddings(self, texts):
                return [[0.1] * 128 for _ in texts]

        mock_store = MockVectorStore()
        mock_indexer = MockIndexer()

        # Create retriever
        retriever = DocumentRetriever(
            indexer=mock_indexer,
            vector_store=mock_store
        )

        # Test search
        results = retriever.search("test query", top_k=2)
        self.assertEqual(len(results), 2)

        # Test filtering
        results = retriever.search("test query", filters={"source": "test"})
        self.assertEqual(len(results), 2)

        results = retriever.search("test query", filters={"source": "other"})
        self.assertEqual(len(results), 1)

        # Test context retrieval
        context, sources = retriever.get_relevant_context("test query", top_k=2)
        self.assertIn("Document 1", context)
        self.assertIn("Document 2", context)
        self.assertEqual(len(sources), 2)


if __name__ == "__main__":
    unittest.main()
