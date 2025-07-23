"""
Factory for content generators.
"""
import os
import logging
from typing import Optional, Dict, Any

from personal_automation_bot.services.content.generators.base import ContentGenerator
from personal_automation_bot.services.content.generators.openai_generator import OpenAIGenerator
from personal_automation_bot.services.content.generators.local_generator import LocalGenerator

logger = logging.getLogger(__name__)

def get_content_generator(
    generator_type: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> ContentGenerator:
    """
    Get an appropriate content generator.

    Args:
        generator_type: Type of generator ('openai', 'local', or None for auto-detect)
        config: Configuration dictionary

    Returns:
        Content generator instance
    """
    config = config or {}

    # If type is specified, try to create that specific generator
    if generator_type == 'openai':
        generator = OpenAIGenerator(config)
        if generator.is_available():
            logger.info("Using OpenAI generator")
            return generator
        else:
            logger.warning("OpenAI generator requested but not available, falling back to local")

    elif generator_type == 'local':
        generator = LocalGenerator(config)
        logger.info("Using local generator")
        return generator

    # Auto-detect best available generator
    logger.info("Auto-detecting best available content generator")

    # Try OpenAI first (if API key is available)
    if os.getenv('OPENAI_API_KEY') or config.get('openai', {}).get('api_key'):
        openai_config = config.get('openai', {})
        if not openai_config.get('api_key'):
            openai_config['api_key'] = os.getenv('OPENAI_API_KEY')

        generator = OpenAIGenerator(openai_config)
        if generator.is_available():
            logger.info("Auto-selected OpenAI generator")
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

    # Check OpenAI
    openai_gen = OpenAIGenerator()
    availability['openai'] = openai_gen.is_available()

    # Check local
    local_gen = LocalGenerator()
    availability['local'] = local_gen.is_available()

    return availability
