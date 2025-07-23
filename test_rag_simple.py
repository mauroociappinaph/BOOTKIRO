"""
Simple test for the RAG generation system.
"""
import os
import tempfile
import shutil
import unittest
from unittest.mock import MagicMock, patch

class TestRAGGeneration(unittest.TestCase):
    """Test RAG generation functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()

        # Create test files
        self.text_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.text_file, "w") as f:
            f.write("This is a test document about RAG systems.\\n"
                   "RAG stands for Retrieval-Augmented Generation.\\n"
                   "It combines retrieval and generation for better results.")

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_citation_class(self):
        """Test Citation class."""
        try:
            from personal_automation_bot.services.content.rag_generator import Citation

            # Create citation
            citation = Citation(
                source_id="doc1",
                source_path="/path/to/doc.txt",
                source_title="Test Document",
                relevance_score=0.85
            )

            # Test to_dict
            data = citation.to_dict()
            self.assertEqual(data["source_id"], "doc1")
            self.assertEqual(data["source_path"], "/path/to/doc.txt")
            self.assertEqual(data["source_title"], "Test Document")
            self.assertEqual(data["relevance_score"], 0.85)

            # Test from_dict
            citation2 = Citation.from_dict(data)
            self.assertEqual(citation2.source_id, "doc1")
            self.assertEqual(citation2.source_path, "/path/to/doc.txt")
            self.assertEqual(citation2.source_title, "Test Document")
            self.assertEqual(citation2.relevance_score, 0.85)

            # Test string representation
            self.assertEqual(str(citation), "[Test Document](/path/to/doc.txt)")

            print("✅ Citation class tests passed")
        except ImportError as e:
            self.skipTest(f"Required module not available: {e}")

    def test_rag_response_class(self):
        """Test RAGResponse class."""
        try:
            from personal_automation_bot.services.content.rag_generator import RAGResponse, Citation

            # Create citations
            citation1 = Citation(source_id="doc1", source_path="/path/to/doc1.txt", source_title="Doc 1", relevance_score=0.9)
            citation2 = Citation(source_id="doc2", source_path="/path/to/doc2.txt", source_title="Doc 2", relevance_score=0.8)

            # Create response
            response = RAGResponse(
                text="This is a generated response about RAG.",
                citations=[citation1, citation2],
                context_used="Context information about RAG...",
                prompt="What is RAG?"
            )

            # Test to_dict
            data = response.to_dict()
            self.assertEqual(data["text"], "This is a generated response about RAG.")
            self.assertEqual(len(data["citations"]), 2)
            self.assertEqual(data["prompt"], "What is RAG?")

            # Test from_dict
            response2 = RAGResponse.from_dict(data)
            self.assertEqual(response2.text, "This is a generated response about RAG.")
            self.assertEqual(len(response2.citations), 2)
            self.assertEqual(response2.prompt, "What is RAG?")

            # Test formatted text
            formatted = response.get_formatted_text_with_citations()
            self.assertIn("This is a generated response about RAG.", formatted)
            self.assertIn("Sources:", formatted)
            self.assertIn("[Doc 1](/path/to/doc1.txt)", formatted)
            self.assertIn("[Doc 2](/path/to/doc2.txt)", formatted)

            print("✅ RAGResponse class tests passed")
        except ImportError as e:
            self.skipTest(f"Required module not available: {e}")

    def test_mock_rag_generator(self):
        """Test RAG generator with mocks."""
        try:
            from personal_automation_bot.services.content.rag_generator import RAGGenerator, RAGResponse
            from personal_automation_bot.services.content.text_generator import TextGenerator

            # Create mock retriever
            mock_retriever = MagicMock()
            mock_retriever.get_relevant_context.return_value = (
                "RAG stands for Retrieval-Augmented Generation.",
                [
                    {"id": "doc1", "source": self.text_file, "score": 0.9, "text": "RAG stands for Retrieval-Augmented Generation."}
                ]
            )

            # Create mock text generator
            class MockTextGenerator(TextGenerator):
                def generate(self, prompt, **kwargs):
                    return f"Generated text for: {prompt}"

                def generate_with_context(self, prompt, context, **kwargs):
                    return f"RAG is Retrieval-Augmented Generation, which combines retrieval and generation."

            # Create RAG generator
            rag_generator = RAGGenerator(
                retriever=mock_retriever,
                generator=MockTextGenerator()
            )

            # Generate text
            response = rag_generator.generate(query="What is RAG?")

            # Check response
            self.assertIsInstance(response, RAGResponse)
            self.assertEqual(response.prompt, "What is RAG?")
            self.assertIn("RAG is Retrieval-Augmented Generation", response.text)
            self.assertEqual(len(response.citations), 1)
            self.assertEqual(response.citations[0].source_path, self.text_file)

            print("✅ RAG generator tests passed")
        except ImportError as e:
            self.skipTest(f"Required module not available: {e}")

if __name__ == "__main__":
    unittest.main()
