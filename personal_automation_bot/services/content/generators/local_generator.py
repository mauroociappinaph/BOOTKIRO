"""
Local content generator using free/local models.
"""
import logging
import re
from typing import Dict, Any, List, Optional

from personal_automation_bot.services.content.generators.base import (
    ContentGenerator,
    GenerationRequest,
    GenerationResponse
)

logger = logging.getLogger(__name__)

class LocalGenerator(ContentGenerator):
    """Content generator using local/free models."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize local generator.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config)

        # Check available local models
        self.has_transformers = self._check_transformers()
        self.has_ollama = self._check_ollama()

        # Configuration
        self.model_name = config.get('model_name', 'microsoft/DialoGPT-medium')
        self.max_length = config.get('max_length', 500)
        self.temperature = config.get('temperature', 0.7)

        # Initialize model if available
        if self.has_transformers:
            self._initialize_transformers_model()

    def _check_transformers(self) -> bool:
        """Check if transformers library is available."""
        try:
            import transformers
            import torch
            return True
        except ImportError:
            return False

    def _check_ollama(self) -> bool:
        """Check if Ollama is available."""
        try:
            import requests
            # Try to ping Ollama API
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            return response.status_code == 200
        except:
            return False

    def _initialize_transformers_model(self):
        """Initialize transformers model."""
        if not self.has_transformers:
            return

        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch

            # Use a smaller, free model for text generation
            model_name = "microsoft/DialoGPT-small"  # Smaller model for better performance

            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)

            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            logger.info(f"Initialized local model: {model_name}")

        except Exception as e:
            logger.error(f"Failed to initialize transformers model: {e}")
            self.tokenizer = None
            self.model = None

    def is_available(self) -> bool:
        """Check if local generator is available."""
        return (
            (self.has_transformers and hasattr(self, 'model') and self.model is not None) or
            self.has_ollama
        )

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """
        Generate content using local models.

        Args:
            request: Generation request

        Returns:
            Generation response
        """
        if not self.is_available():
            # Fallback to template-based generation
            return self._generate_template_based(request)

        if self.has_ollama:
            return self._generate_with_ollama(request)
        elif self.has_transformers and hasattr(self, 'model') and self.model is not None:
            return self._generate_with_transformers(request)
        else:
            return self._generate_template_based(request)

    def _generate_with_ollama(self, request: GenerationRequest) -> GenerationResponse:
        """Generate content using Ollama."""
        try:
            import requests

            # Prepare prompt
            prompt = self._prepare_prompt(request)

            # Make request to Ollama
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama2',  # Default model
                    'prompt': prompt,
                    'stream': False
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get('response', '')

                # Extract citations
                sources_used = request.sources or []
                citations = self.extract_citations(content, sources_used)

                return GenerationResponse(
                    content=content,
                    sources_used=sources_used,
                    metadata={'model': 'ollama-llama2'},
                    citations=citations
                )
            else:
                raise Exception(f"Ollama API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Error with Ollama generation: {e}")
            return self._generate_template_based(request)

    def _generate_with_transformers(self, request: GenerationRequest) -> GenerationResponse:
        """Generate content using transformers."""
        try:
            import torch

            # Prepare prompt
            prompt = self._prepare_prompt(request)

            # Tokenize
            inputs = self.tokenizer.encode(prompt, return_tensors='pt', max_length=512, truncation=True)

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + self.max_length,
                    temperature=self.temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Decode
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract only the new content (remove the prompt)
            content = generated_text[len(prompt):].strip()

            # Extract citations
            sources_used = request.sources or []
            citations = self.extract_citations(content, sources_used)

            return GenerationResponse(
                content=content,
                sources_used=sources_used,
                metadata={'model': 'transformers-local'},
                citations=citations
            )

        except Exception as e:
            logger.error(f"Error with transformers generation: {e}")
            return self._generate_template_based(request)

    def _generate_template_based(self, request: GenerationRequest) -> GenerationResponse:
        """Generate content using template-based approach (fallback)."""
        logger.info("Using template-based generation as fallback")

        # Simple template-based response
        if request.context and request.sources:
            # Extract key information from context
            context_summary = self._summarize_context(request.context)

            content = f"Basándome en la información proporcionada:\\n\\n{context_summary}\\n\\n"
            content += f"En respuesta a tu pregunta: {request.prompt}\\n\\n"
            content += "La información disponible sugiere que este tema está relacionado con los documentos proporcionados. "
            content += "Para obtener una respuesta más detallada, recomiendo revisar las fuentes citadas."

            # Add source references
            if request.sources:
                content += "\\n\\nFuentes consultadas:\\n"
                for i, source in enumerate(request.sources, 1):
                    content += f"[{i}] {source.get('source', 'Fuente desconocida')}\\n"
        else:
            content = f"Para responder a tu pregunta '{request.prompt}', necesitaría más contexto o información específica. "
            content += "Por favor, proporciona más detalles o documentos relevantes."

        # Extract citations
        sources_used = request.sources or []
        citations = self.extract_citations(content, sources_used)

        return GenerationResponse(
            content=content,
            sources_used=sources_used,
            metadata={'model': 'template-based'},
            citations=citations
        )

    def _prepare_prompt(self, request: GenerationRequest) -> str:
        """Prepare prompt for generation."""
        prompt_parts = []

        if request.context and request.sources:
            formatted_context = self.format_context(request.context, request.sources)
            prompt_parts.append(formatted_context)
            prompt_parts.append("")

        prompt_parts.append(f"Pregunta: {request.prompt}")
        prompt_parts.append("Respuesta:")

        return "\\n".join(prompt_parts)

    def _summarize_context(self, context: str, max_sentences: int = 3) -> str:
        """Summarize context to key points."""
        # Simple extractive summarization
        sentences = re.split(r'[.!?]+', context)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Take first few sentences as summary
        summary_sentences = sentences[:max_sentences]
        return '. '.join(summary_sentences) + '.' if summary_sentences else context[:200] + '...'
