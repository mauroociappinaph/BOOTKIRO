#!/usr/bin/env python3
"""
Test script for Gmail API integration.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from personal_automation_bot.services.email import GmailClient, EmailService


def test_gmail_client():
    """Test Gmail client authentication and basic functionality."""
    print("🧪 Testing Gmail Client...")

    # Test user ID (you can use any string)
    test_user_id = "test_user_123"

    try:
        # Create Gmail client
        client = GmailClient(test_user_id)
        print("✅ Gmail client created successfully")

        # Test authentication
        print("\n🔐 Testing authentication...")
        auth_success = client.authenticate()

        if auth_success:
            print("✅ Authentication successful!")

            # Test getting profile
            print("\n👤 Getting user profile...")
            profile = client.get_profile()
            if profile:
                print(f"✅ Profile: {profile['email']}")
                print(f"📧 Total messages: {profile['messages_total']}")

            # Test getting recent emails
            print("\n📧 Getting recent emails...")
            emails = client.get_recent_emails(max_results=5)
            print(f"✅ Found {len(emails)} recent emails")

            for i, email in enumerate(emails[:3], 1):
                print(f"  {i}. {email['subject'][:50]}... - {email['sender'][:30]}")

        else:
            print("❌ Authentication failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True


def test_email_service():
    """Test high-level email service."""
    print("\n🧪 Testing Email Service...")

    test_user_id = "test_user_123"

    try:
        # Create email service
        service = EmailService()
        print("✅ Email service created successfully")

        # Test authentication
        print("\n🔐 Testing service authentication...")
        success, message = service.authenticate_user(test_user_id)
        print(f"{'✅' if success else '❌'} {message}")

        if success:
            # Test getting recent emails
            print("\n📧 Testing get recent emails...")
            success, emails, message = service.get_recent_emails(test_user_id, count=3)
            print(f"{'✅' if success else '❌'} {message}")

            if success and emails:
                print("\n📋 Email summaries:")
                for email in emails:
                    formatted = service.format_email_summary(email)
                    print(f"\n{formatted}")
                    print("-" * 50)

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True


def main():
    """Main test function."""
    print("🚀 Gmail Integration Test")
    print("=" * 50)

    # Check if credentials file exists
    creds_path = os.getenv('GOOGLE_CLIENT_SECRETS_PATH', 'credentials.json')
    if not os.path.exists(creds_path):
        print(f"❌ Credentials file not found: {creds_path}")
        print("Please make sure you have downloaded credentials.json from Google Cloud Console")
        return

    print(f"✅ Credentials file found: {creds_path}")

    # Test Gmail client
    client_success = test_gmail_client()

    if client_success:
        # Test email service
        service_success = test_email_service()

        if service_success:
            print("\n🎉 All tests passed! Gmail integration is working correctly.")
        else:
            print("\n❌ Email service tests failed.")
    else:
        print("\n❌ Gmail client tests failed.")

    print("\n" + "=" * 50)
    print("Test completed.")


if __name__ == "__main__":
    main()
