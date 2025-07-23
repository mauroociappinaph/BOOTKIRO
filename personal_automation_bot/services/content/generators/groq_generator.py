"""
Groq content generator.
"""
import os
import logging
from typing import Dict, Any, List, Optional

from personal_automation_bot.services.content.generators.base import (
    ContentGenerator,
    GenerationRequest,
    GenerationResponse
)

logger = logging.getLogger(__name__)

class GroqGenerator(ContentGenerator):
    """Content generator using Groq API."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Groq generator.

        Args:
            config: Configuration dictionary with API key and settings
        """
        super().__init__(config)

        # Check if Groq is available
        self.has_groq = self._check_groq()

        if self.has_groq:
            self.api_key = config.get('api_key') or os.getenv('GROQ_API_KEY')
            self.model = config.get('model', 'llama3-70b-8192')
            self.max_tokens = config.get('max_tokens', 1000)
            self.temperature = config.get('temperature', 0.7)

            if self.api_key:
                self._initialize_client()
        else:
            logger.warning("Groq library not available")

    def _check_groq(self) -> bool:
        """Check if Groq library is available."""
        try:
            import groq
            return True
        except ImportError:
            return False

    def _initialize_client(self):
        """Initialize Groq client."""
        if not self.has_groq:
            return

        try:
            import groq
            self.client = groq.Client(api_key=self.api_key)
            logger.info("Groq client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.client = None

    def is_available(self) -> bool:
        """Check if Groq generator is available."""
        return (
            self.has_groq and
            self.api_key is not None and
            hasattr(self, 'client') and
            self.client is not None
        )

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """
        Generate content using Groq API.

        Args:
            request: Generation request

        Returns:
            Generation response
        """
        if not self.is_available():
            raise ValueError("Groq generator is not available")

        # Prepare messages
        messages = []

        # Add system prompt
        system_prompt = request.system_prompt or self._get_default_system_prompt()
        messages.append({"role": "system", "content": system_prompt})

        # Format user prompt with context
        user_prompt = request.prompt
        if request.context and request.sources:
            formatted_context = self.format_context(request.context, request.sources)
            user_prompt = f"{formatted_context}\\n\\nPregunta: {request.prompt}"

        messages.append({"role": "user", "content": user_prompt})

        try:
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=request.max_tokens or self.max_tokens,
                temperature=request.temperature or self.temperature
            )

            # Extract content
            content = response.choices[0].message.content

            # Extract citations
            sources_used = request.sources or []
            citations = self.extract_citations(content, sources_used)

            # Prepare metadata
            metadata = {
                "model": self.model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0,
                "finish_reason": response.choices[0].finish_reason if hasattr(response.choices[0], 'finish_reason') else None
            }

            return GenerationResponse(
                content=content,
                sources_used=sources_used,
                metadata=metadata,
                citations=citations
            )

        except Exception as e:
            logger.error(f"Error generating content with Groq: {e}")
            raise

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for RAG."""
        return """Eres un asistente útil que responde preguntas basándose en el contexto proporcionado.

Instrucciones:
1. Usa únicamente la información del contexto proporcionado para responder
2. Si la información no está en el contexto, indica que no tienes suficiente información
3. Cita las fuentes usando números entre corchetes [1], [2], etc.
4. Sé preciso y conciso en tus respuestas
5. Si hay múltiples fuentes que respaldan un punto, menciona todas las relevantes"""
