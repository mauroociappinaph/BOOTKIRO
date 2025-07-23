"""
Tests for the RAG generation system.
"""
import unittest
from unittest.mock import MagicMock, patch
import tempfile
import os

from personal_automation_bot.services.content.generators.base import (
    ContentGenerator,
    GenerationRequest,
    GenerationResponse
)
from personal_automation_bot.services.content.generators.local_generator import LocalGenerator
from personal_automation_bot.services.content.generators.factory import get_content_generator
from personal_automation_bot.services.content.rag_service import RAGService, RAGRequest

class TestContentGenerators(unittest.TestCase):
    """Test content generators."""

    def test_local_generator_template_based(self):
        """Test local generator with template-based fallback."""
        generator = LocalGenerator()

        # Test basic generation
        request = GenerationRequest(
            prompt="¿Qué es la inteligencia artificial?",
            context="La inteligencia artificial es una tecnología que permite a las máquinas aprender y tomar decisiones.",
            sources=[{"source": "test.txt", "title": "AI Basics"}]
        )

        response = generator.generate(request)

        self.assertIsInstance(response, GenerationResponse)
        self.assertIsInstance(response.content, str)
        self.assertGreater(len(response.content), 0)
        self.assertEqual(len(response.sources_used), 1)
.assertIn('template-based', response.metadata.get('model', ''))

    def test_generation_request_response(self):
        """Test generation request and response data classes."""
        # Test GenerationRequest
        request = GenerationRequest(
            prompt="Test prompt",
            context="Test context",
            max_tokens=100,
            temperature=0.7
        )

        self.assertEqual(request.prompt, "Test prompt")
        self.assertEqual(request.context, "Test context")
        self.assertEqual(request.max_tokens, 100)
        self.assertEqual(request.temperature, 0.7)

        # Test GenerationResponse
        response = GenerationResponse(
            content="Test response",
            sources_used=[{"source": "test.txt"}],
            metadata={"model": "test"},
            citations=["[1] test.txt"]
        )

        self.assertEqual(response.content, "Test response")
        self.assertEqual(len(response.sources_used), 1)
        self.assertEqual(response.metadata["model"], "test")
        self.assertEqual(len(response.citations), 1)

    def test_content_generator_factory(self):
        """Test content generator factory."""
        # Test local generator
        generator = get_content_generator(generator_type='local')
        self.assertIsInstance(generator, LocalGenerator)

        # Test auto-detection (should return local since OpenAI key not available)
        generator = get_content_generator()
        self.assertIsInstance(generator, ContentGenerator)


class TestRAGService(unittest.TestCase):
    """Test RAG service."""

    def setUp(self):
        """Set up test environment."""
        # Create mock retriever
        self.mock_retriever = MagicMock()
        self.mock_retriever.search.return_value = [
            {
                'id': 'doc1',
                'text': 'This is a test document about artificial intelligence.',
                'source': 'test1.txt',
                'score': 0.9,
                'metadata': {'filename': 'test1.txt', 'file_type': 'text'}
            },
            {
                'id': 'doc2',
                'text': 'AI is transforming many industries.',
                'source': 'test2.txt',
                'score': 0.8,
                'metadata': {'filename': 'test2.txt', 'file_type': 'text'}
            }
        ]

        # Create mock content generator
        self.mock_generator = MagicMock(spec=ContentGenerator)
        self.mock_generator.generate.return_value = GenerationResponse(
            content="Based on the provided documents, artificial intelligence is a transformative technology. [1] [2]",
            sources_used=[],
            metadata={'model': 'mock'},
            citations=['[1] test1.txt', '[2] test2.txt']
        )

        # Create RAG service
        self.rag_service = RAGService(
            retriever=self.mock_retriever,
            content_generator=self.mock_generator
        )

    def test_rag_generation_with_context(self):
        """Test RAG generation with retrieved context."""
        request = RAGRequest(
            query="What is artificial intelligence?",
            max_sources=2
        )

        response = self.rag_service.generate(request)

        # Verify retriever was called
        self.mock_retriever.search.assert_called_once_with("What is artificial intelligence?", top_k=2)

        # Verify generator was called
        self.mock_generator.generate.assert_called_once()

        # Verify response
        self.assertIsInstance(response.answer, str)
        self.assertEqual(len(response.sources), 2)
        self.assertEqual(len(response.citations), 2)
        self.assertGreater(response.confidence_score, 0)
        self.assertEqual(response.metadata['num_sources'], 2)

    def test_rag_generation_no_context(self):
        """Test RAG generation when no relevant documents are found."""
        # Mock retriever to return no results
        self.mock_retriever.search.return_value = []

        request = RAGRequest(
            query="What is quantum computing?",
            max_sources=2
        )

        response = self.rag_service.generate(request)

        # Verify response
        self.assertIsInstance(response.answer, str)
        self.assertEqual(len(response.sources), 0)
        self.assertEqual(len(response.citations), 0)
        self.assertEqual(response.confidence_score, 0.1)  # Low confidence
        self.assertTrue(response.metadata.get('no_context', False))

    def test_rag_generation_with_relevance_filter(self):
        """Test RAG generation with relevance score filtering."""
        # Mock retriever to return documents with low scores
        self.mock_retriever.search.return_value = [
            {
                'id': 'doc1',
                'text': 'Low relevance document.',
                'source': 'test1.txt',
                'score': 0.2,  # Below threshold
                'metadata': {'filename': 'test1.txt'}
            }
        ]

        request = RAGRequest(
            query="What is AI?",
            max_sources=2,
            min_relevance_score=0.5  # High threshold
        )

        response = self.rag_service.generate(request)

        # Should trigger no-context response due to low relevance
        self.assertEqual(len(response.sources), 0)
        self.assertTrue(response.metadata.get('no_context', False))

    def test_confidence_score_calculation(self):
        """Test confidence score calculation."""
        # Test with high relevance documents
        high_relevance_docs = [
            {'score': 0.9},
            {'score': 0.8}
        ]

        mock_response = GenerationResponse(
            content="Test response with citations [1] [2]",
            sources_used=[],
            metadata={},
            citations=['[1] source1', '[2] source2']
        )

        confidence = self.rag_service._calculate_confidence_score(high_relevance_docs, mock_response)
        self.assertGreater(confidence, 0.8)  # Should be high

        # Test with low relevance documents
        low_relevance_docs = [
            {'score': 0.3},
            {'score': 0.2}
        ]

        mock_response_no_citations = GenerationResponse(
            content="Test response without citations",
            sources_used=[],
            metadata={},
            citations=[]
        )

        confidence = self.rag_service._calculate_confidence_score(low_relevance_docs, mock_response_no_citations)
        self.assertLess(confidence, 0.5)  # Should be low


if __name__ == "__main__":
    unittest.main()
