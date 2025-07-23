"""
RAG (Retrieval-Augmented Generation) service.
Combines document retrieval with text generation.
"""
import os
import logging
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass

from personal_automation_bot.services.content.text_generator import TextGenerator, get_text_generator
from personal_automation_bot.services.rag.retriever import DocumentRetriever

logger = logging.getLogger(__name__)

@dataclass
class Citation:
    """Citation information for a source document."""

    source_id: str
    source_path: str
    source_title: Optional[str] = None
    relevance_score: float = 0.0
    start_char: Optional[int] = None
    end_char: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_id": self.source_id,
            "source_path": self.source_path,
            "source_title": self.source_title,
            "relevance_score": self.relevance_score,
            "start_char": self.start_char,
            "end_char": self.end_char
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Citation':
        """Create from dictionary."""
        return cls(
            source_id=data["source_id"],
            source_path=data["source_path"],
            source_title=data.get("source_title"),
            relevance_score=data.get("relevance_score", 0.0),
            start_char=data.get("start_char"),
            end_char=data.get("end_char")
        )

    def __str__(self) -> str:
        """String representation."""
        title = self.source_title or os.path.basename(self.source_path)
        return f"[{title}]({self.source_path})"


@dataclass
class RAGResponse:
    """Response from the RAG generator."""

    text: str
    citations: List[Citation]
    context_used: str
    prompt: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "citations": [c.to_dict() for c in self.citations],
            "context_used": self.context_used,
            "prompt": self.prompt
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RAGResponse':
        """Create from dictionary."""
        return cls(
            text=data["text"],
            citations=[Citation.from_dict(c) for c in data["citations"]],
            context_used=data["context_used"],
            prompt=data["prompt"]
        )

    def get_formatted_text_with_citations(self) -> str:
        """Get text with citations formatted as markdown."""
        text = self.text

        # Add footnotes at the end
        if self.citations:
            text += "\n\n**Sources:**\n"
            for i, citation in enumerate(self.citations):
                text += f"{i+1}. {str(citation)}\n"

        return text


class RAGGenerator:
    """RAG (Retrieval-Augmented Generation) generator."""

    def __init__(
        self,
        retriever: Optional[DocumentRetriever] = None,
        generator: Optional[TextGenerator] = None,
        generator_provider: str = "openai",
        generator_model: Optional[str] = None,
        max_context_tokens: int = 2000,
        citation_threshold: float = 0.6
    ):
        """
        Initialize RAG generator.

        Args:
            retriever: Document retriever
            generator: Text generator
            generator_provider: Provider for text generator if not provided
            generator_model: Model for text generator if not provided
            max_context_tokens: Maximum number of tokens to use for context
            citation_threshold: Minimum relevance score for citations
        """
        self.retriever = retriever
        self.generator = generator or get_text_generator(
            provider=generator_provider,
            model=generator_model
        )
        self.max_context_tokens = max_context_tokens
        self.citation_threshold = citation_threshold

    def generate(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> RAGResponse:
        """
        Generate text based on query and retrieved context.

        Args:
            query: Query to generate text for
            top_k: Number of documents to retrieve
            filters: Filters for document retrieval
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional arguments for the generator

        Returns:
            RAGResponse with generated text and citations
        """
        if not self.retriever:
            raise ValueError("No retriever provided")

        # Retrieve relevant context
        context, sources = self.retriever.get_relevant_context(
            query=query,
            top_k=top_k,
            filters=filters,
            max_tokens=self.max_context_tokens
        )

        # Generate text with context
        generated_text = self.generator.generate_with_context(
            prompt=query,
            context=context,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

        # Create citations for relevant sources
        citations = []
        for source in sources:
            if source.get("score", 0) >= self.citation_threshold:
                citation = Citation(
                    source_id=source.get("id", "unknown"),
                    source_path=source.get("source", "unknown"),
                    source_title=source.get("title", os.path.basename(source.get("source", ""))),
                    relevance_score=source.get("score", 0.0)
                )
                citations.append(citation)

        # Create response
        response = RAGResponse(
            text=generated_text,
            citations=citations,
            context_used=context,
            prompt=query
        )

        return response

    def generate_with_explicit_context(
        self,
        query: str,
        context: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text with explicitly provided context.

        Args:
            query: Query to generate text for
            context: Context to use for generation
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation
            **kwargs: Additional arguments for the generator

        Returns:
            Generated text
        """
        return self.generator.generate_with_context(
            prompt=query,
            context=context,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
