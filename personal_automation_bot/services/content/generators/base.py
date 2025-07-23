"""
Base class for content generators.
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class GenerationRequest:
    """Request for content generation."""
    prompt: str
    context: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    system_prompt: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None

@dataclass
class GenerationResponse:
    """Response from content generation."""
    content: str
    sources_used: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    citations: List[str]

class ContentGenerator(ABC):
    """Base class for content generators."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the content generator.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """
        Generate content based on the request.

        Args:
            request: Generation request

        Returns:
            Generation response
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the generator is available and properly configured.

        Returns:
            True if available, False otherwise
        """
        pass

    def format_context(self, context: str, sources: List[Dict[str, Any]]) -> str:
        """
        Format context with sources for the prompt.

        Args:
            context: Raw context text
            sources: List of source documents

        Returns:
            Formatted context string
        """
        if not context or not sources:
            return context or ""

        formatted_parts = []
        formatted_parts.append("Contexto relevante:")
        formatted_parts.append(context)
        formatted_parts.append("\\nFuentes:")

        for i, source in enumerate(sources, 1):
            source_info = f"[{i}] {source.get('source', 'Fuente desconocida')}"
            if source.get('title'):
                source_info += f" - {source['title']}"
            formatted_parts.append(source_info)

        return "\\n".join(formatted_parts)

    def extract_citations(self, content: str, sources: List[Dict[str, Any]]) -> List[str]:
        """
        Extract citations from generated content.

        Args:
            content: Generated content
            sources: Source documents

        Returns:
            List of citations
        """
        citations = []
        for i, source in enumerate(sources, 1):
            # Look for references to this source in the content
            if f"[{i}]" in content or str(i) in content:
                citation = f"[{i}] {source.get('source', 'Fuente desconocida')}"
                if source.get('title'):
                    citation += f" - {source['title']}"
                citations.append(citation)

        return citations
