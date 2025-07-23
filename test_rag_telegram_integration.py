"""
Test script for RAG Telegram integration.
This script simulates Telegram interactions to test the RAG functionality.
"""
import os
import sys
import logging
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.abspath('.'))

class MockTelegramUpdate:
    """Mock Telegram Update object."""

    def __init__(self, message_text=None, callback_data=None, user_id=12345):
        self.effective_user = MagicMock()
        self.effective_user.id = user_id
        self.effective_user.first_name = "Test User"

        # Set up message or callback query
        if message_text:
            self.message = AsyncMock()
            self.message.text = message_text
            self.message.reply_text = AsyncMock()
            self.callback_query = None
        elif callback_data:
            self.callback_query = AsyncMock()
            self.callback_query.data = callback_data
            self.callback_query.answer = AsyncMock()
            self.callback_query.edit_message_text = AsyncMock()
            self.message = None
        else:
            self.message = AsyncMock()
            self.message.reply_text = AsyncMock()
            self.callback_query = None

    def get_response_text(self):
        """Get the text of the response."""
        if self.message and self.message.reply_text.call_args:
            # Get first positional argument
            args = self.message.reply_text.call_args[0]
            if args:
                return args[0]
        elif self.callback_query and self.callback_query.edit_message_text.call_args:
            # Get keyword argument 'text' or first positional argument
            kwargs = self.callback_query.edit_message_text.call_args[1]
            if 'text' in kwargs:
                return kwargs['text']
            args = self.callback_query.edit_message_text.call_args[0]
            if args:
                return args[0]
        return None

class MockTelegramContext:
    """Mock Telegram Context object."""

    def __init__(self):
        self.bot = AsyncMock()
        self.bot.get_file = AsyncMock()
        self.bot.get_file.return_value = AsyncMock()
        self.bot.get_file.return_value.download_to_drive = AsyncMock()

        self.user_data = {}
        self.chat_data = {}
        self.args = []

async def test_rag_command():
    """Test the /rag command."""
    logger.info("Testing /rag command...")

    # Import the command handler
    from personal_automation_bot.bot.commands.rag import rag_command

    # Create mock update and context
    update = MockTelegramUpdate()
    context = MockTelegramContext()

    # Call the command handler
    result = await rag_command(update, context)

    # Check the result
    response_text = update.get_response_text()
    logger.info(f"Response: {response_text}")

    if "Sistema RAG" in response_text:
        logger.info("✅ /rag command test passed")
    else:
        logger.error("❌ /rag command test failed")

    return result

async def test_rag_help_command():
    """Test the /raghelp command."""
    logger.info("Testing /raghelp command...")

    # Import the command handler
    from personal_automation_bot.bot.commands.rag import rag_help

    # Create mock update and context
    update = MockTelegramUpdate()
    context = MockTelegramContext()

    # Call the command handler
    await rag_help(update, context)

    # Check the result
    response_text = update.get_response_text()
    logger.info(f"Response: {response_text}")

    if "Comandos RAG" in response_text:
        logger.info("✅ /raghelp command test passed")
    else:
        logger.error("❌ /raghelp command test failed")

async def test_rag_button_ask():
    """Test the RAG button for asking a question."""
    logger.info("Testing RAG 'ask' button...")

    # Import the button handler
    from personal_automation_bot.bot.conversations.rag_conversation import rag_button, RAG_STATES

    # Create mock update with callback data
    update = MockTelegramUpdate(callback_data="rag_ask")
    context = MockTelegramContext()

    # Call the button handler
    result = await rag_button(update, context)

    # Check the result
    response_text = update.get_response_text()
    logger.info(f"Response: {response_text}")

    if "escribe tu pregunta" in response_text.lower():
        logger.info("✅ RAG 'ask' button test passed")
    else:
        logger.error("❌ RAG 'ask' button test failed")

    # Check the state
    if result == RAG_STATES["WAITING_FOR_QUESTION"]:
        logger.info("✅ State transition correct")
    else:
        logger.error(f"❌ Incorrect state transition: {result}")

    return result

async def test_process_question():
    """Test processing a question."""
    logger.info("Testing question processing...")

    # Import the question handler
    from personal_automation_bot.bot.conversations.rag_conversation import process_question

    # Create mock update with question text
    update = MockTelegramUpdate(message_text="What is RAG?")
    context = MockTelegramContext()

    # Mock the RAG generator
    with patch('personal_automation_bot.bot.conversations.rag_conversation.get_rag_generator') as mock_get_generator:
        # Create mock generator
        mock_generator = MagicMock()
        mock_generator.generate.return_value = MagicMock(
            text="RAG stands for Retrieval-Augmented Generation.",
            citations=[],
            get_formatted_text_with_citations=lambda: "RAG stands for Retrieval-Augmented Generation."
        )
        mock_get_generator.return_value = mock_generator

        # Call the question handler
        result = await process_question(update, context)

    # Check the responses
    # There should be two responses: "Buscando información..." and the answer
    calls = update.message.reply_text.call_args_list
    if len(calls) >= 2:
        first_call = calls[0][0][0]
        second_call = calls[1][0][0]

        logger.info(f"First response: {first_call}")
        logger.info(f"Second response: {second_call}")

        if "Buscando información" in first_call and "Respuesta" in second_call:
            logger.info("✅ Question processing test passed")
        else:
            logger.error("❌ Question processing test failed")
    else:
        logger.error(f"❌ Expected at least 2 responses, got {len(calls)}")

    return result

async def test_rag_button_docs():
    """Test the RAG button for viewing documents."""
    logger.info("Testing RAG 'docs' button...")

    # Import the button handler
    from personal_automation_bot.bot.conversations.rag_conversation import rag_button, RAG_STATES

    # Create mock update with callback data
    update = MockTelegramUpdate(callback_data="rag_docs")
    context = MockTelegramContext()

    # Mock the vector store
    with patch('personal_automation_bot.bot.conversations.rag_conversation.get_vector_store') as mock_get_store:
        # Create mock vector store
        mock_store = MagicMock()
        mock_store.doc_ids = ["doc1", "doc2", "doc3"]
        mock_get_store.return_value = mock_store

        # Call the button handler
        result = await rag_button(update, context)

    # Check the result
    response_text = update.get_response_text()
    logger.info(f"Response: {response_text}")

    if "Documentos indexados" in response_text:
        logger.info("✅ RAG 'docs' button test passed")
    else:
        logger.error("❌ RAG 'docs' button test failed")

    # Check the state
    if result == RAG_STATES["SHOWING_DOCUMENTS"]:
        logger.info("✅ State transition correct")
    else:
        logger.error(f"❌ Incorrect state transition: {result}")

    return result

async def test_rag_button_index():
    """Test the RAG button for indexing a document."""
    logger.info("Testing RAG 'index' button...")

    # Import the button handler
    from personal_automation_bot.bot.conversations.rag_conversation import rag_button, RAG_STATES

    # Create mock update with callback data
    update = MockTelegramUpdate(callback_data="rag_index")
    context = MockTelegramContext()

    # Call the button handler
    result = await rag_button(update, context)

    # Check the result
    response_text = update.get_response_text()
    logger.info(f"Response: {response_text}")

    if "envía un archivo" in response_text.lower():
        logger.info("✅ RAG 'index' button test passed")
    else:
        logger.error("❌ RAG 'index' button test failed")

    # Check the state
    if result == RAG_STATES["WAITING_FOR_FILE"]:
        logger.info("✅ State transition correct")
    else:
        logger.error(f"❌ Incorrect state transition: {result}")

    return result

async def test_conversation_handler():
    """Test the RAG conversation handler."""
    logger.info("Testing RAG conversation handler...")

    # Import the conversation handler
    from personal_automation_bot.bot.commands.rag import get_rag_conversation_handler

    # Get the conversation handler
    conversation_handler = get_rag_conversation_handler()

    # Check that it's properly configured
    if conversation_handler:
        entry_points = conversation_handler.entry_points
        states = conversation_handler.states
        fallbacks = conversation_handler.fallbacks

        logger.info(f"Entry points: {len(entry_points)}")
        logger.info(f"States: {len(states)}")
        logger.info(f"Fallbacks: {len(fallbacks)}")

        if entry_points and states and fallbacks:
            logger.info("✅ Conversation handler is properly configured")
        else:
            logger.error("❌ Conversation handler is missing components")
    else:
        logger.error("❌ Failed to get conversation handler")

async def run_tests():
    """Run all tests."""
    logger.info("Starting RAG Telegram integration tests...")

    try:
        # Test commands
        await test_rag_command()
        await test_rag_help_command()

        # Test conversation flow
        await test_rag_button_ask()
        await test_process_question()
        await test_rag_button_docs()
        await test_rag_button_index()

        # Test conversation handler
        await test_conversation_handler()

        logger.info("All tests completed!")
    except Exception as e:
        logger.error(f"Error during tests: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_tests())
