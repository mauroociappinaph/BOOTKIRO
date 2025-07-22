#!/usr/bin/env python3
"""
Test script for email sending functionality.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_email_validation():
    """Test email validation function."""
    print("Testing email validation...")

    try:
        # Import the validation function
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "messages",
            "personal_automation_bot/bot/commands/messages.py"
        )
        messages_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(messages_module)

        _is_valid_email = messages_module._is_valid_email

        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@test.com",
            "user_name@example-domain.com"
        ]

        # Invalid emails
        invalid_emails = [
            "invalid",
            "@example.com",
            "user@",
            "user@domain",
            "user@.com",
            "user..name@example.com",
            "user@domain..com",
            ".user@example.com",
            "user.@example.com"
        ]

        # Test valid emails
        for email in valid_emails:
            if not _is_valid_email(email):
                print(f"❌ Valid email failed: {email}")
                return False
            else:
                print(f"✅ Valid email passed: {email}")

        # Test invalid emails
        for email in invalid_emails:
            if _is_valid_email(email):
                print(f"❌ Invalid email passed: {email}")
                return False
            else:
                print(f"✅ Invalid email rejected: {email}")

        return True

    except Exception as e:
        print(f"❌ Error testing email validation: {e}")
        return False

def test_conversation_states():
    """Test that conversation states are properly defined."""
    print("Testing conversation states...")

    try:
        # Import without telegram dependencies
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "base",
            "personal_automation_bot/bot/conversations/base.py"
        )
        base_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(base_module)

        ConversationState = base_module.ConversationState

        # Check that all email states exist
        required_states = [
            'EMAIL_SEND_TO',
            'EMAIL_SEND_SUBJECT',
            'EMAIL_SEND_BODY',
            'EMAIL_SEND_CONFIRM'
        ]

        for state in required_states:
            if hasattr(ConversationState, state):
                print(f"✅ {state} state exists")
            else:
                print(f"❌ {state} state missing")
                return False

        return True

    except Exception as e:
        print(f"❌ Error testing conversation states: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Email Send Functionality\n")

    tests = [
        ("Email Validation", test_email_validation),
        ("Conversation States", test_conversation_states)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
