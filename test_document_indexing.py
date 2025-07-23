"""
Tests for the document indexing system.
"""
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from personal_automation_bot.services.rag.document_processors.base import DocumentProcessor
from personal_automation_bot.services.rag.document_processors.text import TextProcessor
from personal_automation_bot.services.rag.document_processors.factory import get_document_processor, register_processor
from personal_automation_bot.services.rag.document_indexer import DocumentIndexingService

class TestDocumentProcessors(unittest.TestCase):
    """Test document processors."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()

        # Create test files
        self.text_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.text_file, "w") as f:
            f.write("This is a test document.\\nIt has multiple lines.\\nEnd of document.")

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_text_processor(self):
        """Test text processor."""
        processor = TextProcessor()

        # Test can_process
        self.assertTrue(processor.can_process(self.text_file))
        self.assertFalse(processor.can_process(os.path.join(self.temp_dir, "nonexistent.pdf")))

        # Test extract_text
        text = processor.extract_text(self.text_file)
        self.assertEqual(text, "This is a test document.\\nIt has multiple lines.\\nEnd of document.")

        # Test extract_metadata
        metadata = processor.extract_metadata(self.text_file)
        self.assertEqual(metadata["filename"], "test.txt")
        self.assertEqual(metadata["extension"], ".txt")
        self.assertEqual(metadata["file_type"], "text")
        self.assertEqual(metadata["mime_type"], "text/plain")

        # Test process_file
        result = processor.process_file(self.text_file)
        self.assertEqual(result["text"], "This is a test document.\\nIt has multiple lines.\\nEnd of document.")
        self.assertEqual(result["metadata"]["filename"], "test.txt")
        self.assertEqual(result["source"], self.text_file)
        self.assertEqual(result["processor"], "TextProcessor")

    def test_factory(self):
        """Test document processor factory."""
        # Test get_document_processor
        processor = get_document_processor(self.text_file)
        self.assertIsInstance(processor, TextProcessor)

        # Test with unsupported file
        unsupported_file = os.path.join(self.temp_dir, "test.xyz")
        with open(unsupported_file, "w") as f:
            f.write("Test")

        processor = get_document_processor(unsupported_file)
        self.assertIsNone(processor)

        # Test register_processor
        class CustomProcessor(DocumentProcessor):
            def can_process(self, file_path):
                return file_path.endswith(".xyz")

            def extract_text(self, file_path, **kwargs):
                return "Custom processor text"

            def extract_metadata(self, file_path, **kwargs):
                return {"custom": True}

        register_processor(CustomProcessor)

        processor = get_document_processor(unsupported_file)
        self.assertIsInstance(processor, CustomProcessor)


class TestDocumentIndexingService(unittest.TestCase):
    """Test document indexing service."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.temp_dir, "cache")

        # Create test files
        self.text_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.text_file, "w") as f:
            f.write("This is a test document.\\nIt has multiple lines.\\nEnd of document.")

        # Create mock indexer
        self.mock_indexer = MagicMock()
        self.mock_indexer.index_document.return_value = ["chunk1", "chunk2"]

        # Create indexing service
        self.indexing_service = DocumentIndexingService(
            indexer=self.mock_indexer,
            cache_dir=self.cache_dir
        )

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_process_document(self):
        """Test processing a document."""
        # Process document
        document = self.indexing_service.process_document(self.text_file)

        # Check result
        self.assertEqual(document["text"], "This is a test document.\\nIt has multiple lines.\\nEnd of document.")
        self.assertEqual(document["metadata"]["filename"], "test.txt")
        self.assertEqual(document["source"], self.text_file)

        # Check cache
        self.assertIn(os.path.abspath(self.text_file), self.indexing_service.document_cache)

        # Process again (should use cache)
        document2 = self.indexing_service.process_document(self.text_file)
        self.assertEqual(document["id"], document2["id"])

        # Force reprocessing
        document3 = self.indexing_service.process_document(self.text_file, force=True)
        self.assertEqual(document["id"], document3["id"])

    def test_index_document(self):
        """Test indexing a document."""
        # Index document
        chunk_ids = self.indexing_service.index_document(self.text_file)

        # Check result
        self.assertEqual(chunk_ids, ["chunk1", "chunk2"])

        # Verify indexer was called
        self.mock_indexer.index_document.assert_called_once()

        # Index again (should use cache and call indexer again)
        self.indexing_service.index_document(self.text_file)
        self.assertEqual(self.mock_indexer.index_document.call_count, 2)

    def test_index_directory(self):
        """Test indexing a directory."""
        # Create subdirectory with more files
        subdir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(subdir)

        with open(os.path.join(subdir, "test2.txt"), "w") as f:
            f.write("Another test document.")

        with open(os.path.join(subdir, "test3.log"), "w") as f:
            f.write("Log file.")

        # Index directory
        results = self.indexing_service.index_directory(self.temp_dir)

        # Check results (should include both .txt files but not .log)
        self.assertEqual(len(results), 2)
        self.assertIn(self.text_file, results)
        self.assertIn(os.path.join(subdir, "test2.txt"), results)
        self.assertNotIn(os.path.join(subdir, "test3.log"), results)

        # Test non-recursive
        results = self.indexing_service.index_directory(self.temp_dir, recursive=False)
        self.assertEqual(len(results), 1)
        self.assertIn(self.text_file, results)

        # Test exclude patterns
        results = self.indexing_service.index_directory(
            self.temp_dir,
            exclude_patterns=["test*.txt"]
        )
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
