"""
Text generation service.
Provides functionality for generating text using various AI services.
"""
import os
import logging
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)

class TextGenerator(ABC):
    """Base class for text generators."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text based on a prompt.

        Args:
            prompt: The prompt to generate text from
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation (higher = more creative)
            **kwargs: Additional arguments for the specific generator

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    def generate_with_context(
        self,
        prompt: str,
        context: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text based on a prompt and additional context.

        Args:
            prompt: The prompt to generate text from
            context: Additional context to inform the generation
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation (higher = more creative)
            **kwargs: Additional arguments for the specific generator

        Returns:
            Generated text
        """
        pass


class GroqTextGenerator(TextGenerator):
    """Text generator using Groq API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama3-70b-8192",
        organization: Optional[str] = None
    ):
        """
        Initialize Groq text generator.

        Args:
            api_key: Groq API key (if None, will use GROQ_API_KEY env var)
            model: Model to use for generation
            organization: Groq organization ID
        """
        self.model = model

        # Get API key from env var if not provided
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("No Groq API key provided. Text generation will not work.")

        self.organization = organization

        # Initialize Groq client if available
        try:
            import groq
            self.client = groq.Client(
                api_key=self.api_key
            )
            self.available = True
        except ImportError:
            logger.warning("Groq package not installed. Install with 'pip install groq'")
            self.available = False
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
            self.available = False

    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using Groq API."""
        if not self.available:
            raise RuntimeError("Groq client not available")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text with Groq: {e}")
            raise

    def generate_with_context(
        self,
        prompt: str,
        context: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text with context using Groq API."""
        if not self.available:
            raise RuntimeError("Groq client not available")

        # Combine prompt and context
        system_message = f"Use the following information to answer the user's question. If the information doesn't contain the answer, say you don't know.\\n\\nContext information:\\n{context}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text with Groq: {e}")
            raise


class HuggingFaceTextGenerator(TextGenerator):
    """Text generator using Hugging Face models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "google/flan-t5-base",
        local_model: bool = False
    ):
        """
        Initialize Hugging Face text generator.

        Args:
            api_key: Hugging Face API key (if None, will use HF_API_KEY env var)
            model: Model to use for generation
            local_model: Whether to use a local model (True) or the API (False)
        """
        self.model_name = model
        self.local_model = local_model

        # Get API key from env var if not provided and using API
        self.api_key = None
        if not local_model:
            self.api_key = api_key or os.environ.get("HF_API_KEY")
            if not self.api_key:
                logger.warning("No Hugging Face API key provided. API-based text generation will not work.")

        # Initialize client based on mode
        if local_model:
            self._init_local_model()
        else:
            self._init_api_client()

    def _init_local_model(self):
        """Initialize local Hugging Face model."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.available = True

            logger.info(f"Loaded local model: {self.model_name}")
        except ImportError:
            logger.warning("Transformers package not installed. Install with 'pip install transformers'")
            self.available = False
        except Exception as e:
            logger.error(f"Error loading local model {self.model_name}: {e}")
            self.available = False

    def _init_api_client(self):
        """Initialize Hugging Face API client."""
        try:
            import requests
            self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
            self.headers = {"Authorization": f"Bearer {self.api_key}"}
            self.available = True

            logger.info(f"Using Hugging Face API with model: {self.model_name}")
        except ImportError:
            logger.warning("Requests package not installed. Install with 'pip install requests'")
            self.available = False
        except Exception as e:
            logger.error(f"Error initializing Hugging Face API client: {e}")
            self.available = False

    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using Hugging Face."""
        if not self.available:
            raise RuntimeError("Hugging Face client not available")

        if self.local_model:
            return self._generate_local(prompt, max_tokens, temperature, **kwargs)
        else:
            return self._generate_api(prompt, max_tokens, temperature, **kwargs)

    def _generate_local(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using local Hugging Face model."""
        try:
            import torch

            inputs = self.tokenizer(prompt, return_tensors="pt")

            gen_kwargs = {
                "max_length": max_tokens,
                "temperature": temperature,
                "do_sample": temperature > 0,
                **kwargs
            }

            with torch.no_grad():
                output = self.model.generate(**inputs, **gen_kwargs)

            return self.tokenizer.decode(output[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Error generating text with local model: {e}")
            raise

    def _generate_api(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using Hugging Face API."""
        import requests

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        }

        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()

            result = response.json()

            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                if "generated_text" in result[0]:
                    return result[0]["generated_text"]
                else:
                    return str(result[0])
            elif isinstance(result, dict) and "generated_text" in result:
                return result["generated_text"]
            else:
                return str(result)
        except Exception as e:
            logger.error(f"Error generating text with Hugging Face API: {e}")
            raise

    def generate_with_context(
        self,
        prompt: str,
        context: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text with context using Hugging Face."""
        # Combine prompt and context
        combined_prompt = f"Context: {context}\\n\\nQuestion: {prompt}\\n\\nAnswer:"

        return self.generate(combined_prompt, max_tokens, temperature, **kwargs)


def get_text_generator(
    provider: str = "groq",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> TextGenerator:
    """
    Get a text generator based on the provider.

    Args:
        provider: Provider to use ('groq' or 'huggingface')
        api_key: API key for the provider
        model: Model to use
        **kwargs: Additional arguments for the specific generator

    Returns:
        TextGenerator instance
    """
    if provider.lower() == "groq":
        default_model = "llama3-70b-8192"
        return GroqTextGenerator(api_key=api_key, model=model or default_model, **kwargs)
    elif provider.lower() in ["huggingface", "hf"]:
        default_model = "google/flan-t5-base"
        return HuggingFaceTextGenerator(api_key=api_key, model=model or default_model, **kwargs)
    else:
        raise ValueError(f"Unsupported provider: {provider}")
