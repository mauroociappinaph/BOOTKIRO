"""
Simple test for Groq API.
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

# Load environment variables
load_dotenv()

def test_groq_api():
    """Test Groq API directly."""
    try:
        import groq

        # Get API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.error("GROQ_API_KEY environment variable is not set.")
            return False

        # Initialize client
        client = groq.Client(api_key=api_key)

        # Test API
        logger.info("Testing Groq API...")

        # Make a simple completion request
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is RAG (Retrieval-Augmented Generation)?"}
            ],
            max_tokens=100,
            temperature=0.7
        )

        # Print response
        logger.info(f"Response: {response.choices[0].message.content}")
        logger.info(f"Model: {response.model}")
        logger.info(f"Usage: {response.usage}")

        return True
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure the groq package is installed.")
        return False
    except Exception as e:
        logger.error(f"Error testing Groq API: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    logger.info("Testing Groq API directly...")

    # Test Groq API
    success = test_groq_api()

    if success:
        logger.info("✅ Groq API test passed!")
    else:
        logger.error("❌ Groq API test failed!")

if __name__ == "__main__":
    main()
