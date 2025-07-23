"""
Factory for content generators.
"""
import os
import logging
from typing import Optional, Dict, Any

from personal_automation_bot.services.content.generators.base import ContentGenerator
from personal_automation_bot.services.content.generators.groq_generator import GroqGenerator
from personal_automation_bot.services.content.generators.local_generator import LocalGenerator

logger = logging.getLogger(__name__)

def get_content_generator(
    generator_type: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> ContentGenerator:
    """
    Get an appropriate content generator.

    Args:
        generator_type: Type of generator ('groq', 'local', or None for auto-detect)
        config: Configuration dictionary

    Returns:
        Content generator instance
    """
    config = config or {}

    # If type is specified, try to create that specific generator
    if generator_type == 'groq':
        generator = GroqGenerator(config)
        if generator.is_available():
            logger.info("Using Groq generator")
            return generator
        else:
            logger.warning("Groq generator requested but not available, falling back to local")

    elif generator_type == 'local':
        generator = LocalGenerator(config)
        logger.info("Using local generator")
        return generator

    # Auto-detect best available generator
    logger.info("Auto-detecting best available content generator")

    # Try Groq first (if API key is available)
    if os.getenv('GROQ_API_KEY') or config.get('groq', {}).get('api_key'):
        groq_config = config.get('groq', {})
        if not groq_config.get('api_key'):
            groq_config['api_key'] = os.getenv('GROQ_API_KEY')

        generator = GroqGenerator(groq_config)
        if generator.is_available():
            logger.info("Auto-selected Groq generator")
            return generator

    # Fall back to local generator
    local_config = config.get('local', {})
    generator = LocalGenerator(local_config)
    logger.info("Auto-selected local generator")
    return generator

def get_available_generators() -> Dict[str, bool]:
    """
    Get information about available generators.

    Returns:
        Dictionary with generator availability
    """
    availability = {}

    # Check Groq
    groq_gen = GroqGenerator()
    availability['groq'] = groq_gen.is_available()

    # Check local
    local_gen = LocalGenerator()
    availability['local'] = local_gen.is_available()

    return availability
