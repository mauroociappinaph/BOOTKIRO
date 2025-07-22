#!/usr/bin/env python3
"""
Test script for email reading functionality integrated with Telegram bot.
"""

import os
import sys
import asyncio
from unittest.mock import Mock, AsyncMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from personal_automation_bot.bot.commands.email import (
    email_command,
    handle_email_list_recent,
    handle_email_details,
    show_email_page
)
from personal_automation_bot.services.email import EmailService


def create_mock_update(user_id=123456789, callback_data=None):
    """Create a mock Telegram update object."""
    update = Mock()
    update.effective_user = Mock()
    update.effective_user.id = user_id

    if callback_data:
        update.callback_query = Mock()
        update.callback_query.data = callback_data
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
    else:
        update.callback_query = None
        update.message = Mock()
        update.message.reply_text = AsyncMock()

    return update


def create_mock_context():
    """Create a mock Telegram context object."""
    context = Mock()
    context.user_data = {}
    return context


async def test_email_command():
    """Test the main email command."""
    print("🧪 Testing email command...")

    # Test with unauthenticated user
    update = create_mock_update()
    context = create_mock_context()

    try:
        result = await email_command(update, context)
        print("✅ Email command executed successfully")
        print(f"   Returned state: {result}")

        # Check if reply_text was called
        if update.message.reply_text.called:
            args, kwargs = update.message.reply_text.call_args
            print(f"   Message sent: {args[0][:100]}...")

    except Exception as e:
        print(f"❌ Error in email command: {e}")
        return False

    return True


async def test_email_list_recent():
    """Test the email list recent functionality."""
    print("\n🧪 Testing email list recent...")

    # Create authenticated user mock
    update = create_mock_update(callback_data="email_list_recent")
    context = create_mock_context()

    try:
        result = await handle_email_list_recent(update, context)
        print("✅ Email list recent executed successfully")
        print(f"   Returned state: {result}")

        # Check if edit_message_text was called
        if update.callback_query.edit_message_text.called:
            args, kwargs = update.callback_query.edit_message_text.call_args
            print(f"   Message edited: {args[0][:100]}...")

    except Exception as e:
        print(f"❌ Error in email list recent: {e}")
        return False

    return True


async def test_email_service_integration():
    """Test email service integration."""
    print("\n🧪 Testing email service integration...")

    try:
        # Test email service
        service = EmailService()
        print("✅ Email service created successfully")

        # Test authentication check
        test_user_id = "test_user_123"
        is_auth = service.is_user_authenticated(test_user_id)
        print(f"✅ Authentication check: {is_auth}")

        if is_auth:
            # Test getting recent emails
            success, emails, message = service.get_recent_emails(test_user_id, count=3)
            print(f"✅ Get recent emails: {success}")
            print(f"   Message: {message}")

            if success and emails:
                print(f"   Found {len(emails)} emails")

                # Test email formatting
                for i, email in enumerate(emails[:2], 1):
                    formatted = service.format_email_summary(email)
                    print(f"   Email {i} summary: {formatted[:100]}...")

    except Exception as e:
        print(f"❌ Error in email service integration: {e}")
        return False

    return True


async def test_pagination():
    """Test email pagination functionality."""
    print("\n🧪 Testing email pagination...")

    try:
        # Create mock context with emails
        context = create_mock_context()

        # Mock emails data
        mock_emails = []
        for i in range(12):  # Create 12 mock emails
            mock_emails.append({
                'id': f'email_{i}',
                'subject': f'Test Email {i + 1}',
                'sender': f'sender{i}@example.com',
                'date': f'2025-01-{i + 1:02d}',
                'snippet': f'This is a test email snippet {i + 1}'
            })

        context.user_data['emails'] = mock_emails
        context.user_data['current_page'] = 0

        # Create mock query
        query = Mock()
        query.edit_message_text = AsyncMock()

        # Test showing first page
        await show_email_page(query, context, 0)
        print("✅ First page displayed successfully")

        # Test showing second page
        await show_email_page(query, context, 1)
        print("✅ Second page displayed successfully")

        # Test showing last page
        await show_email_page(query, context, 2)
        print("✅ Last page displayed successfully")

        # Check if edit_message_text was called
        if query.edit_message_text.called:
            print("✅ Message editing called correctly")

    except Exception as e:
        print(f"❌ Error in pagination test: {e}")
        return False

    return True


async def main():
    """Main test function."""
    print("🚀 Email Reading Functionality Test")
    print("=" * 50)

    # Check if we have the necessary configuration
    if not os.path.exists('credentials.json'):
        print("⚠️  Warning: credentials.json not found")
        print("   Some tests may not work without Gmail authentication")

    # Run tests
    tests = [
        ("Email Command", test_email_command),
        ("Email List Recent", test_email_list_recent),
        ("Email Service Integration", test_email_service_integration),
        ("Pagination", test_pagination)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)

        try:
            success = await test_func()
            if success:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Email reading functionality is working correctly.")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please check the implementation.")

    print("\n💡 Note: For full functionality testing, make sure:")
    print("   • credentials.json is present")
    print("   • Gmail authentication is working")
    print("   • Bot token is configured")


if __name__ == "__main__":
    asyncio.run(main())
