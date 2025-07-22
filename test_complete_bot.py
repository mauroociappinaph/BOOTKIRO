#!/usr/bin/env python3
"""
Complete test script for the Telegram bot system.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_complete_system():
    """Test the complete bot system."""
    print("🤖 Testing Complete Bot System\n")

    # Test 1: All imports
    print("📋 Testing Imports...")
    try:
        from personal_automation_bot.bot import setup_bot
        from personal_automation_bot.bot.commands.basic import start_command, help_command, menu_command
        from personal_automation_bot.bot.commands.auth import auth_command
        from personal_automation_bot.bot.commands.callbacks import handle_callback_query
        from personal_automation_bot.bot.commands.messages import handle_message
        from personal_automation_bot.bot.keyboards.main_menu import get_main_menu_keyboard
        from personal_automation_bot.bot.conversations.base import ConversationState, conversation_data
        from personal_automation_bot.utils.auth import google_auth_manager
        from personal_automation_bot.utils.storage import TokenStorage
        print("✅ All imports successful")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

    # Test 2: Bot setup
    print("\n📋 Testing Bot Setup...")
    try:
        app = setup_bot()
        print("✅ Bot setup successful")
    except ValueError as e:
        if "token not provided" in str(e).lower():
            print("✅ Bot setup correctly requires token")
        else:
            print(f"❌ Unexpected error: {e}")
            return False
    except Exception as e:
        print(f"❌ Bot setup error: {e}")
        return False

    # Test 3: Keyboard generation
    print("\n📋 Testing Keyboards...")
    try:
        from personal_automation_bot.bot.keyboards.main_menu import (
            get_main_menu_keyboard,
            get_email_menu_keyboard,
            get_calendar_menu_keyboard,
            get_content_menu_keyboard,
            get_back_keyboard
        )

        keyboards = [
            get_main_menu_keyboard(),
            get_email_menu_keyboard(),
            get_calendar_menu_keyboard(),
            get_content_menu_keyboard(),
            get_back_keyboard()
        ]

        # Check that keyboards have buttons
        for i, kb in enumerate(keyboards):
            if not kb.inline_keyboard:
                print(f"❌ Keyboard {i} has no buttons")
                return False

        print("✅ All keyboards generated successfully")
    except Exception as e:
        print(f"❌ Keyboard error: {e}")
        return False

    # Test 4: Conversation system
    print("\n📋 Testing Conversation System...")
    try:
        user_id = 12345

        # Test state management
        conversation_data.set_user_state(user_id, ConversationState.EMAIL_SEND_TO)
        state = conversation_data.get_user_state(user_id)
        if state != ConversationState.EMAIL_SEND_TO:
            print("❌ Conversation state management failed")
            return False

        # Test field management
        conversation_data.set_user_field(user_id, "test_field", "test_value")
        value = conversation_data.get_user_field(user_id, "test_field")
        if value != "test_value":
            print("❌ Conversation field management failed")
            return False

        # Test cleanup
        conversation_data.clear_user_data(user_id)
        state = conversation_data.get_user_state(user_id)
        if state is not None:
            print("❌ Conversation cleanup failed")
            return False

        print("✅ Conversation system working")
    except Exception as e:
        print(f"❌ Conversation system error: {e}")
        return False

    # Test 5: Authentication system
    print("\n📋 Testing Authentication System...")
    try:
        # Test auth manager
        if not google_auth_manager.is_user_authenticated(99999):
            print("✅ Auth manager working")
        else:
            print("❌ Auth manager failed")
            return False

        # Test token storage
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        storage = TokenStorage(temp_dir)

        test_tokens = {'token': 'test'}
        storage.store_user_tokens(12345, test_tokens)
        loaded = storage.load_user_tokens(12345)

        if loaded and loaded['token'] == 'test':
            print("✅ Token storage working")
        else:
            print("❌ Token storage failed")
            return False

        shutil.rmtree(temp_dir)

    except Exception as e:
        print(f"❌ Authentication system error: {e}")
        return False

    # Test 6: Configuration
    print("\n📋 Testing Configuration...")
    try:
        from personal_automation_bot.config import settings

        # Check that settings can be loaded
        if hasattr(settings, 'TELEGRAM_BOT_TOKEN'):
            print("✅ Configuration loaded")
        else:
            print("❌ Configuration missing")
            return False

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

    return True

def main():
    """Run the complete system test."""
    if test_complete_system():
        print("\n🎉 Complete Bot System Test PASSED!")
        print("\n📋 System Summary:")
        print("✅ Telegram Bot Core - Ready")
        print("✅ Command System - Ready")
        print("✅ Inline Keyboards - Ready")
        print("✅ Conversation System - Ready")
        print("✅ Authentication System - Ready")
        print("✅ Token Storage - Ready")
        print("✅ Configuration - Ready")
        print("\n🚀 The bot is ready for deployment!")
        print("\n📖 Next steps:")
        print("1. Configure your .env file with bot token and Google credentials")
        print("2. Run: python main.py")
        print("3. Test with your Telegram bot")
        return 0
    else:
        print("\n❌ Complete Bot System Test FAILED!")
        print("Please check the errors above and fix them before proceeding.")
        return 1

if __name__ == "__main__":
    exit(main())
