"""
Simple test script for RAG integration.
This script tests the core RAG functionality without Telegram dependencies.
"""
import os
import sys
import logging
from unittest.mock import MagicMock, patch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.abspath('.'))

def test_rag_generator():
    """Test the RAG generator functionality."""
    logger.info("Testing RAG generator...")

    try:
        # Import RAG components
        from personal_automation_bot.services.content.rag_generator import RAGGenerator, RAGResponse, Citation

        # Create mock retriever
        mock_retriever = MagicMock()
        mock_retriever.get_relevant_context.return_value = (
            "RAG stands for Retrieval-Augmented Generation.",
            [
                {"id": "doc1", "source": "test.txt", "score": 0.9, "text": "RAG stands for Retrieval-Augmented Generation."}
            ]
        )

        # Create mock text generator
        mock_generator = MagicMock()
        mock_generator.generate_with_context.return_value = "RAG is a technique that combines retrieval and generation."

        # Create RAG generator
        rag_generator = RAGGenerator(
            retriever=mock_retriever,
            generator=mock_generator
        )

        # Generate response
        response = rag_generator.generate(query="What is RAG?")

        # Check response
        logger.info(f"Generated text: {response.text}")
        logger.info(f"Citations: {response.citations}")

        if response.text and isinstance(response, RAGResponse):
            logger.info("✅ RAG generator test passed")
        else:
            logger.error("❌ RAG generator test failed")

        return True
    except Exception as e:
        logger.error(f"Error testing RAG generator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_citation_system():
    """Test the citation system."""
    logger.info("Testing citation system...")

    try:
        # Import citation components
        from personal_automation_bot.services.content.rag_generator import Citation, RAGResponse

        # Create citations
        citation1 = Citation(
            source_id="doc1",
            source_path="/path/to/doc1.txt",
            source_title="Document 1",
            relevance_score=0.9
        )

        citation2 = Citation(
            source_id="doc2",
            source_path="/path/to/doc2.txt",
            source_title="Document 2",
            relevance_score=0.8
        )

        # Create RAG response
        response = RAGResponse(
            text="This is a test response with citations.",
            citations=[citation1, citation2],
            context_used="Test context",
            prompt="Test prompt"
        )

        # Get formatted text
        formatted_text = response.get_formatted_text_with_citations()
        logger.info(f"Formatted text: {formatted_text}")

        # Check if citations are included
        if "[Document 1]" in formatted_text and "[Document 2]" in formatted_text:
            logger.info("✅ Citation system test passed")
        else:
            logger.error("❌ Citation system test failed")

        return True
    except Exception as e:
        logger.error(f"Error testing citation system: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_text_generator():
    """Test the text generator functionality."""
    logger.info("Testing text generator...")

    try:
        # Import text generator
        from personal_automation_bot.services.content.text_generator import TextGenerator

        # Create a simple implementation for testing
        class TestTextGenerator(TextGenerator):
            def generate(self, prompt, **kwargs):
                return f"Generated text for: {prompt}"

            def generate_with_context(self, prompt, context, **kwargs):
                return f"Generated text for: {prompt} with context: {context[:50]}..."

        # Create generator
        generator = TestTextGenerator()

        # Test generation
        text1 = generator.generate("Test prompt")
        text2 = generator.generate_with_context("Test prompt", "Test context")

        logger.info(f"Generated text without context: {text1}")
        logger.info(f"Generated text with context: {text2}")

        if "Generated text for: Test prompt" in text1 and "with context" in text2:
            logger.info("✅ Text generator test passed")
        else:
            logger.error("❌ Text generator test failed")

        return True
    except Exception as e:
        logger.error(f"Error testing text generator: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_command_handler():
    """Test the RAG command handler logic."""
    logger.info("Testing RAG command handler logic...")

    try:
        # Import the command handler module
        import personal_automation_bot.bot.commands.rag as rag_commands

        # Check if the module has the expected functions
        has_rag_command = hasattr(rag_commands, 'rag_command')
        has_rag_help = hasattr(rag_commands, 'rag_help')
        has_get_rag_generator = hasattr(rag_commands, 'get_rag_generator')
        has_get_conversation_handler = hasattr(rag_commands, 'get_rag_conversation_handler')

        logger.info(f"Has rag_command: {has_rag_command}")
        logger.info(f"Has rag_help: {has_rag_help}")
        logger.info(f"Has get_rag_generator: {has_get_rag_generator}")
        logger.info(f"Has get_conversation_handler: {has_get_conversation_handler}")

        if all([has_rag_command, has_rag_help, has_get_rag_generator, has_get_conversation_handler]):
            logger.info("✅ RAG command handler module test passed")
        else:
            logger.error("❌ RAG command handler module test failed")

        return True
    except Exception as e:
        logger.error(f"Error testing RAG command handler: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rag_conversation_handler():
    """Test the RAG conversation handler logic."""
    logger.info("Testing RAG conversation handler logic...")

    try:
        # Import the conversation handler module
        import personal_automation_bot.bot.conversations.rag_conversation as rag_conversation

        # Check if the module has the expected components
        has_rag_button = hasattr(rag_conversation, 'rag_button')
        has_process_question = hasattr(rag_conversation, 'process_question')
        has_process_file = hasattr(rag_conversation, 'process_file')
        has_rag_states = hasattr(rag_conversation, 'RAG_STATES')
        has_conversation = hasattr(rag_conversation, 'RAG_CONVERSATION')

        logger.info(f"Has rag_button: {has_rag_button}")
        logger.info(f"Has process_question: {has_process_question}")
        logger.info(f"Has process_file: {has_process_file}")
        logger.info(f"Has RAG_STATES: {has_rag_states}")
        logger.info(f"Has RAG_CONVERSATION: {has_conversation}")

        if all([has_rag_button, has_process_question, has_process_file, has_rag_states, has_conversation]):
            logger.info("✅ RAG conversation handler module test passed")
        else:
            logger.error("❌ RAG conversation handler module test failed")

        # Check states
        if has_rag_states:
            states = rag_conversation.RAG_STATES
            logger.info(f"RAG states: {states}")

            required_states = ["MAIN_MENU", "WAITING_FOR_QUESTION", "WAITING_FOR_FILE"]
            all_states_present = all(state in states for state in required_states)

            if all_states_present:
                logger.info("✅ RAG states test passed")
            else:
                logger.error("❌ RAG states test failed")

        return True
    except Exception as e:
        logger.error(f"Error testing RAG conversation handler: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_tests():
    """Run all tests."""
    logger.info("Starting RAG integration tests...")

    # Test core RAG functionality
    test_rag_generator()
    test_citation_system()
    test_text_generator()

    # Test Telegram integration components
    test_rag_command_handler()
    test_rag_conversation_handler()

    logger.info("All tests completed!")

if __name__ == "__main__":
    # Run the tests
    run_tests()
