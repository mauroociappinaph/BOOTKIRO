#!/usr/bin/env python3
"""
Basic test script for the Telegram bot functionality.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all bot components can be imported."""
    try:
        from personal_automation_bot.bot import setup_bot
        print("✅ Bot core import successful")

        from personal_automation_bot.bot.commands.basic import start_command, help_command, menu_command
        print("✅ Basic commands import successful")

        from personal_automation_bot.bot.commands.callbacks import handle_callback_query
        print("✅ Callback handlers import successful")

        from personal_automation_bot.bot.commands.messages import handle_message
        print("✅ Message handlers import successful")

        from personal_automation_bot.bot.keyboards.main_menu import get_main_menu_keyboard
        print("✅ Keyboards import successful")

        from personal_automation_bot.bot.conversations.base import ConversationState, conversation_data
        print("✅ Conversation system import successful")

        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_bot_setup():
    """Test bot setup without token (should raise ValueError)."""
    try:
        from personal_automation_bot.bot import setup_bot
        setup_bot()
        print("❌ Bot setup should have failed without token")
        return False
    except ValueError as e:
        if "token not provided" in str(e).lower():
            print("✅ Bot setup correctly requires token")
            return True
        else:
            print(f"❌ Unexpected error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_keyboards():
    """Test keyboard generation."""
    try:
        from personal_automation_bot.bot.keyboards.main_menu import (
            get_main_menu_keyboard,
            get_email_menu_keyboard,
            get_calendar_menu_keyboard,
            get_content_menu_keyboard,
            get_back_keyboard
        )

        # Test that keyboards can be generated
        main_kb = get_main_menu_keyboard()
        email_kb = get_email_menu_keyboard()
        calendar_kb = get_calendar_menu_keyboard()
        content_kb = get_content_menu_keyboard()
        back_kb = get_back_keyboard()

        print("✅ All keyboards generated successfully")
        return True
    except Exception as e:
        print(f"❌ Keyboard generation error: {e}")
        return False

def test_conversation_system():
    """Test conversation data management."""
    try:
        from personal_automation_bot.bot.conversations.base import conversation_data, ConversationState

        # Test user data management
        user_id = 12345
        conversation_data.set_user_state(user_id, ConversationState.EMAIL_SEND_TO)
        state = conversation_data.get_user_state(user_id)

        if state == ConversationState.EMAIL_SEND_TO:
            print("✅ Conversation state management working")
        else:
            print("❌ Conversation state management failed")
            return False

        # Test field management
        conversation_data.set_user_field(user_id, "test_field", "test_value")
        value = conversation_data.get_user_field(user_id, "test_field")

        if value == "test_value":
            print("✅ Conversation field management working")
        else:
            print("❌ Conversation field management failed")
            return False

        # Test data clearing
        conversation_data.clear_user_data(user_id)
        state = conversation_data.get_user_state(user_id)

        if state is None:
            print("✅ Conversation data clearing working")
            return True
        else:
            print("❌ Conversation data clearing failed")
            return False

    except Exception as e:
        print(f"❌ Conversation system error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Telegram Bot Components\n")

    tests = [
        ("Import Tests", test_imports),
        ("Bot Setup Test", test_bot_setup),
        ("Keyboard Tests", test_keyboards),
        ("Conversation System Tests", test_conversation_system)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The bot system is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
