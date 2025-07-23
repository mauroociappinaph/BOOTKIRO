"""
Test script for Groq generator.
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.abspath('.'))

# Load environment variables
load_dotenv()

def test_groq_generator():
    """Test Groq generator."""
    try:
        from personal_automation_bot.services.content.generators.groq_generator import GroqGenerator
        from personal_automation_bot.services.content.generators.base import GenerationRequest

        # Create Groq generator
        generator = GroqGenerator()

        # Check if Groq is available
        if not generator.is_available():
            logger.error("Groq generator is not available. Check if the Groq library is installed and API key is set.")
            return False

        logger.info("Groq generator is available.")
        logger.info(f"Using model: {generator.model}")

        # Create a simple request
        request = GenerationRequest(
            prompt="¿Qué es RAG (Retrieval-Augmented Generation)?",
            max_tokens=100,
            temperature=0.7
        )

        # Generate response
        logger.info("Generating response...")
        response = generator.generate(request)

        # Print response
        logger.info(f"Generated text: {response.content}")
        logger.info(f"Metadata: {response.metadata}")

        return True
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure all required packages are installed.")
        return False
    except Exception as e:
        logger.error(f"Error testing Groq generator: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    logger.info("Testing Groq generator...")

    # Check if Groq API key is set
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.error("GROQ_API_KEY environment variable is not set.")
        return

    logger.info("GROQ_API_KEY is set.")

    # Test Groq generator
    success = test_groq_generator()

    if success:
        logger.info("✅ Groq generator test passed!")
    else:
        logger.error("❌ Groq generator test failed!")

if __name__ == "__main__":
    main()
