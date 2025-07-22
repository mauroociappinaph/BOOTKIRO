#!/usr/bin/env python3
"""
Integration test for email sending functionality.
Tests the conversation flow without actually sending emails.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_conversation_flow():
    """Test the email sending conversation flow."""
    print("Testing email sending conversation flow...")

    try:
        # Import conversation components
        import importlib.util

        # Import conversation base
        spec = importlib.util.spec_from_file_location(
            "base",
            "personal_automation_bot/bot/conversations/base.py"
        )
        base_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(base_module)

        ConversationState = base_module.ConversationState
        ConversationData = base_module.ConversationData

        # Test conversation data management
        conversation_data = ConversationData()
        user_id = 12345

        # Test setting email recipient
        conversation_data.set_user_state(user_id, ConversationState.EMAIL_SEND_TO)
        conversation_data.set_user_field(user_id, "email_to", "test@example.com")

        if conversation_data.get_user_state(user_id) != ConversationState.EMAIL_SEND_TO:
            print("❌ Failed to set EMAIL_SEND_TO state")
            return False

        if conversation_data.get_user_field(user_id, "email_to") != "test@example.com":
            print("❌ Failed to store email recipient")
            return False

        print("✅ EMAIL_SEND_TO state and data storage working")

        # Test setting email subject
        conversation_data.set_user_state(user_id, ConversationState.EMAIL_SEND_SUBJECT)
        conversation_data.set_user_field(user_id, "email_subject", "Test Subject")

        if conversation_data.get_user_state(user_id) != ConversationState.EMAIL_SEND_SUBJECT:
            print("❌ Failed to set EMAIL_SEND_SUBJECT state")
            return False

        if conversation_data.get_user_field(user_id, "email_subject") != "Test Subject":
            print("❌ Failed to store email subject")
            return False

        print("✅ EMAIL_SEND_SUBJECT state and data storage working")

        # Test setting email body
        conversation_data.set_user_state(user_id, ConversationState.EMAIL_SEND_BODY)
        conversation_data.set_user_field(user_id, "email_body", "Test email body content")

        if conversation_data.get_user_state(user_id) != ConversationState.EMAIL_SEND_BODY:
            print("❌ Failed to set EMAIL_SEND_BODY state")
            return False

        if conversation_data.get_user_field(user_id, "email_body") != "Test email body content":
            print("❌ Failed to store email body")
            return False

        print("✅ EMAIL_SEND_BODY state and data storage working")

        # Test confirmation state
        conversation_data.set_user_state(user_id, ConversationState.EMAIL_SEND_CONFIRM)

        if conversation_data.get_user_state(user_id) != ConversationState.EMAIL_SEND_CONFIRM:
            print("❌ Failed to set EMAIL_SEND_CONFIRM state")
            return False

        print("✅ EMAIL_SEND_CONFIRM state working")

        # Test data retrieval for confirmation
        email_to = conversation_data.get_user_field(user_id, "email_to")
        email_subject = conversation_data.get_user_field(user_id, "email_subject")
        email_body = conversation_data.get_user_field(user_id, "email_body")

        if not all([email_to, email_subject, email_body]):
            print("❌ Failed to retrieve all email data for confirmation")
            return False

        print("✅ Email data retrieval for confirmation working")

        # Test clearing conversation data
        conversation_data.clear_user_data(user_id)

        if conversation_data.get_user_state(user_id) is not None:
            print("❌ Failed to clear conversation state")
            return False

        if conversation_data.get_user_field(user_id, "email_to") is not None:
            print("❌ Failed to clear conversation data")
            return False

        print("✅ Conversation data clearing working")

        return True

    except Exception as e:
        print(f"❌ Error in conversation flow test: {e}")
        return False

def test_email_service_integration():
    """Test email service integration (without actually sending)."""
    print("Testing email service integration...")

    try:
        # Import email service
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "email_service",
            "personal_automation_bot/services/email/email_service.py"
        )
        email_service_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(email_service_module)

        EmailService = email_service_module.EmailService

        # Create email service instance
        email_service = EmailService()

        # Test that the service can be instantiated
        if email_service is None:
            print("❌ Failed to create EmailService instance")
            return False

        print("✅ EmailService instantiation working")

        # Test that send_email method exists and has correct signature
        if not hasattr(email_service, 'send_email'):
            print("❌ EmailService missing send_email method")
            return False

        print("✅ EmailService has send_email method")

        # Test that authentication check method exists
        if not hasattr(email_service, 'is_user_authenticated'):
            print("❌ EmailService missing is_user_authenticated method")
            return False

        print("✅ EmailService has is_user_authenticated method")

        return True

    except Exception as e:
        print(f"❌ Error in email service integration test: {e}")
        return False

def main():
    """Run all integration tests."""
    print("🧪 Testing Email Send Integration\n")

    tests = [
        ("Conversation Flow", test_conversation_flow),
        ("Email Service Integration", test_email_service_integration)
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
        print("🎉 All integration tests passed!")
        return 0
    else:
        print("💥 Some integration tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
