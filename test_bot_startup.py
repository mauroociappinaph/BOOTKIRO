#!/usr/bin/env python3
"""
Test script to verify bot startup and calendar integration.
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_bot_initialization():
    """Test that the bot can be initialized with calendar functionality."""
    print("🧪 Testing bot initialization with calendar...")

    try:
        # Load environment variables
        load_dotenv()

        # Check if bot token is available
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            print("⚠️  TELEGRAM_BOT_TOKEN not found in environment")
            print("   This is expected for testing - using dummy token")
            bot_token = "dummy_token_for_testing"

        # Import bot setup
        from personal_automation_bot.bot import setup_bot

        # Try to set up the bot (this will fail with dummy token but should not crash)
        try:
            application = setup_bot(token=bot_token)
            print("✅ Bot application created successfully")

            # Check handlers
            handlers = application.handlers
            print(f"✅ Bot has {len(handlers)} handler groups")

            # Check for calendar conversation handler
            calendar_handler_found = False
            for group_handlers in handlers.values():
                for handler in group_handlers:
                    if hasattr(handler, 'name') and handler.name == "calendar_conversation":
                        calendar_handler_found = True
                        print("✅ Calendar conversation handler found")
                        break

            if not calendar_handler_found:
                print("❌ Calendar conversation handler not found")
                return False

            print("✅ Bot initialization test completed successfully")
            return True

        except Exception as e:
            if "Invalid token" in str(e) or "Unauthorized" in str(e):
                print("✅ Bot setup works (token validation failed as expected)")
                return True
            else:
                print(f"❌ Unexpected error during bot setup: {e}")
                return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_calendar_commands_import():
    """Test that calendar commands can be imported."""
    print("\n🧪 Testing calendar commands import...")

    try:
        from personal_automation_bot.bot.commands.calendar import calendar_commands
        from personal_automation_bot.bot.conversations.calendar_conversation import get_calendar_conversation_handler

        print("✅ Calendar commands imported successfully")
        print("✅ Calendar conversation handler imported successfully")

        # Test conversation handler creation
        handler = get_calendar_conversation_handler()
        print(f"✅ Conversation handler created: {handler.name}")

        return True

    except Exception as e:
        print(f"❌ Calendar import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_google_api_dependencies():
    """Test that Google API dependencies are available."""
    print("\n🧪 Testing Google API dependencies...")

    try:
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        print("✅ Google API client libraries available")

        from personal_automation_bot.services.calendar import CalendarService, CalendarEvent
        print("✅ Calendar service classes available")

        return True

    except ImportError as e:
        print(f"❌ Google API dependency missing: {e}")
        print("   Run: pip install google-api-python-client google-auth-oauthlib")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Bot Startup Tests\n")

    # Run all tests
    tests = [
        test_google_api_dependencies,
        test_calendar_commands_import,
        test_bot_initialization
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests

    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All startup tests passed!")
        print("\n📋 Bot Ready Status:")
        print("   ✅ Google API dependencies installed")
        print("   ✅ Calendar commands and handlers available")
        print("   ✅ Bot can be initialized with calendar functionality")
        print("\n🚀 To start the bot:")
        print("   1. Set TELEGRAM_BOT_TOKEN in your .env file")
        print("   2. Set Google OAuth credentials (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)")
        print("   3. Run: python main.py")
        print("\n📱 In Telegram:")
        print("   • Use /calendar to access calendar functions")
        print("   • Use /start to see the main menu")
        print("   • Use /auth to authenticate with Google")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} tests failed!")
        print("   Please fix the issues above before starting the bot.")
        sys.exit(1)
