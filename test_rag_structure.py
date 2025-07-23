"""
Test script for RAG structure.
This script checks the structure of the RAG implementation without importing modules.
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def check_file_exists(file_path):
    """Check if a file exists."""
    exists = os.path.exists(file_path)
    if exists:
        logger.info(f"✅ File exists: {file_path}")
    else:
        logger.error(f"❌ File does not exist: {file_path}")
    return exists

def check_file_content(file_path, expected_content):
    """Check if a file contains expected content."""
    if not os.path.exists(file_path):
        logger.error(f"❌ File does not exist: {file_path}")
        return False

    with open(file_path, 'r') as f:
        content = f.read()

    all_found = True
    for item in expected_content:
        if item in content:
            logger.info(f"✅ Found in {os.path.basename(file_path)}: {item}")
        else:
            logger.error(f"❌ Not found in {os.path.basename(file_path)}: {item}")
            all_found = False

    return all_found

def test_rag_generator_structure():
    """Test the structure of the RAG generator."""
    logger.info("Testing RAG generator structure...")

    # Check if files exist
    files_to_check = [
        "personal_automation_bot/services/content/rag_generator.py",
        "personal_automation_bot/services/content/text_generator.py",
        "personal_automation_bot/services/content/__init__.py",
        "personal_automation_bot/services/content/README.md"
    ]

    all_exist = True
    for file_path in files_to_check:
        if not check_file_exists(file_path):
            all_exist = False

    if all_exist:
        # Check content of rag_generator.py
        rag_generator_content = [
            "class RAGGenerator",
            "class Citation",
            "class RAGResponse",
            "def generate",
            "def generate_with_explicit_context"
        ]
        check_file_content("personal_automation_bot/services/content/rag_generator.py", rag_generator_content)

        # Check content of text_generator.py
        text_generator_content = [
            "class TextGenerator",
            "class OpenAITextGenerator",
            "class HuggingFaceTextGenerator",
            "def generate",
            "def generate_with_context"
        ]
        check_file_content("personal_automation_bot/services/content/text_generator.py", text_generator_content)

    return all_exist

def test_telegram_integration_structure():
    """Test the structure of the Telegram integration."""
    logger.info("Testing Telegram integration structure...")

    # Check if files exist
    files_to_check = [
        "personal_automation_bot/bot/commands/rag.py",
        "personal_automation_bot/bot/conversations/rag_conversation.py"
    ]

    all_exist = True
    for file_path in files_to_check:
        if not check_file_exists(file_path):
            all_exist = False

    if all_exist:
        # Check content of rag.py
        rag_py_content = [
            "def rag_command",
            "def rag_help",
            "def get_rag_generator",
            "def get_rag_conversation_handler"
        ]
        check_file_content("personal_automation_bot/bot/commands/rag.py", rag_py_content)

        # Check content of rag_conversation.py
        rag_conversation_content = [
            "RAG_STATES",
            "def rag_button",
            "def process_question",
            "def process_file",
            "RAG_CONVERSATION"
        ]
        check_file_content("personal_automation_bot/bot/conversations/rag_conversation.py", rag_conversation_content)

    return all_exist

def test_core_integration():
    """Test the integration with the bot core."""
    logger.info("Testing core integration...")

    # Check if core.py exists
    if not check_file_exists("personal_automation_bot/bot/core.py"):
        return False

    # Check if core.py contains RAG imports and handlers
    core_content = [
        "from personal_automation_bot.bot.commands.rag import",
        "get_rag_conversation_handler"
    ]
    return check_file_content("personal_automation_bot/bot/core.py", core_content)

def run_tests():
    """Run all tests."""
    logger.info("Starting RAG structure tests...")

    # Test RAG generator structure
    test_rag_generator_structure()

    # Test Telegram integration structure
    test_telegram_integration_structure()

    # Test core integration
    test_core_integration()

    logger.info("All structure tests completed!")

if __name__ == "__main__":
    # Run the tests
    run_tests()
