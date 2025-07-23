"""
RAG (Retrieval-Augmented Generation) service.
Combines document retrieval with content generation.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from personal_automation_bot.services.content.generators.base import (
    ContentGenerator,
    GenerationRequest,
    GenerationResponse
)
from personal_automation_bot.services.content.generators.factory import get_content_generator

logger = logging.getLogger(__name__)

@dataclass
class RAGRequest:
    """Request for RAG generation."""
    query: str
    max_sources: int = 5
    min_relevance_score: float = 0.0
    generator_type: Optional[str] = None
    generator_config: Optional[Dict[str, Any]] = None
    system_prompt: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

@dataclass
class RAGResponse:
    """Response from RAG generation."""
    answer: str
    sources: List[Dict[str, Any]]
    citations: List[str]
    metadata: Dict[str, Any]
    confidence_score: float

class RAGService:
    """Service for Retrieval-Augmented Generation."""

    def __init__(
        self,
        retriever=None,
        content_generator: Optional[ContentGenerator] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize RAG service.

        Args:
            retriever: Document retriever instance
            content_generator: Content generator instance
            config: Configuration dictionary
        """
        self.retriever = retriever
        self.content_generator = content_generator
        self.config = config or {}

        # Initialize content generator if not provided
        if not self.content_generator:
            generator_config = self.config.get('generator', {})
            self.content_generator = get_content_generator(config=generator_config)

    def generate(self, request: RAGRequest) -> RAGResponse:
        """
        Generate answer using RAG.

        Args:
            request: RAG request

        Returns:
            RAG response
        """
        if not self.retriever:
            raise ValueError("No retriever provided")

        # Step 1: Retrieve relevant documents
        logger.info(f"Retrieving documents for query: {request.query}")
        retrieved_docs = self.retriever.search(
            request.query,
            top_k=request.max_sources
        )

        # Filter by relevance score
        relevant_docs = [
            doc for doc in retrieved_docs
            if doc.get('score', 0) >= request.min_relevance_score
        ]

        if not relevant_docs:
            logger.warning("No relevant documents found")
            return self._generate_no_context_response(request)

        logger.info(f"Found {len(relevant_docs)} relevant documents")

        # Step 2: Prepare context
        context, formatted_sources = self._prepare_context(relevant_docs)

        # Step 3: Generate content
        generation_request = GenerationRequest(
            prompt=request.query,
            context=context,
            sources=formatted_sources,
            system_prompt=request.system_prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )

        # Use specific generator if requested
        if request.generator_type or request.generator_config:
            generator = get_content_generator(
                generator_type=request.generator_type,
                config=request.generator_config or {}
            )
        else:
            generator = self.content_generator

        logger.info(f"Generating content using {generator.__class__.__name__}")
        generation_response = generator.generate(generation_request)

        # Step 4: Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            relevant_docs,
            generation_response
        )

        # Step 5: Prepare final response
        return RAGResponse(
            answer=generation_response.content,
            sources=formatted_sources,
            citations=generation_response.citations,
            metadata={
                'num_sources': len(relevant_docs),
                'avg_relevance_score': sum(doc.get('score', 0) for doc in relevant_docs) / len(relevant_docs),
                'generator_metadata': generation_response.metadata,
                'generator_type': generator.__class__.__name__
            },
            confidence_score=confidence_score
        )

    def _prepare_context(self, documents: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Prepare context from retrieved documents.

        Args:
            documents: List of retrieved documents

        Returns:
            Tuple of (context_text, formatted_sources)
        """
        context_parts = []
        formatted_sources = []

        for i, doc in enumerate(documents, 1):
            # Extract text
            text = doc.get('text', '')
            if len(text) > 500:  # Truncate long texts
                text = text[:500] + '...'

            context_parts.append(f"Documento {i}: {text}")

            # Format source information
            source_info = {
                'id': doc.get('id', f'doc_{i}'),
                'source': doc.get('source', 'Fuente desconocida'),
                'title': doc.get('title', ''),
                'score': doc.get('score', 0.0),
                'text': text
            }

            # Add metadata if available
            if 'metadata' in doc:
                metadata = doc['metadata']
                if metadata.get('filename'):
                    source_info['filename'] = metadata['filename']
                if metadata.get('file_type'):
                    source_info['file_type'] = metadata['file_type']

            formatted_sources.append(source_info)

        context_text = '\\n\\n'.join(context_parts)
        return context_text, formatted_sources

    def _calculate_confidence_score(
        self,
        documents: List[Dict[str, Any]],
        generation_response: GenerationResponse
    ) -> float:
        """
        Calculate confidence score for the generated response.

        Args:
            documents: Retrieved documents
            generation_response: Generated response

        Returns:
            Confidence score between 0 and 1
        """
        if not documents:
            return 0.0

        # Base score from document relevance
        avg_relevance = sum(doc.get('score', 0) for doc in documents) / len(documents)

        # Boost score if citations are present
        citation_boost = 0.1 if generation_response.citations else 0.0

        # Boost score based on number of sources
        source_boost = min(len(documents) * 0.05, 0.2)

        # Combine scores
        confidence = min(avg_relevance + citation_boost + source_boost, 1.0)

        return confidence

    def _generate_no_context_response(self, request: RAGRequest) -> RAGResponse:
        """
        Generate response when no relevant context is found.

        Args:
            request: RAG request

        Returns:
            RAG response
        """
        # Generate without context
        generation_request = GenerationRequest(
            prompt=request.query,
            system_prompt="Responde de manera útil pero indica que no tienes información específica sobre el tema.",
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )

        generator = self.content_generator
        if request.generator_type or request.generator_config:
            generator = get_content_generator(
                generator_type=request.generator_type,
                config=request.generator_config or {}
            )

        generation_response = generator.generate(generation_request)

        return RAGResponse(
            answer=generation_response.content,
            sources=[],
            citations=[],
            metadata={
                'num_sources': 0,
                'generator_metadata': generation_response.metadata,
                'generator_type': generator.__class__.__name__,
                'no_context': True
            },
            confidence_score=0.1  # Low confidence without context
        )

    def get_available_generators(self) -> Dict[str, bool]:
        """
        Get information about available content generators.

        Returns:
            Dictionary with generator availability
        """
        from personal_automation_bot.services.content.generators.factory import get_available_generators
        return get_available_generators()
