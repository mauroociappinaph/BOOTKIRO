#!/usr/bin/env python3
"""
Test real email sending functionality.
This script will actually send an email using the authenticated Gmail account.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_real_email_send():
    """Test sending a real email."""
    print("📧 Testing Real Email Send")
    print("=" * 40)

    try:
        from personal_automation_bot.services.email import EmailService

        # Initialize email service
        email_service = EmailService()

        # Test with different possible user IDs
        possible_user_ids = ["793880527", "7938805278", "123456789"]

        authenticated_user_id = None

        print("🔍 Checking authentication for different user IDs...")
        for user_id in possible_user_ids:
            is_auth = email_service.is_user_authenticated(user_id)
            print(f"   User ID {user_id}: {'✅ Authenticated' if is_auth else '❌ Not authenticated'}")
            if is_auth:
                authenticated_user_id = user_id
                break

        if not authenticated_user_id:
            print("\n❌ No authenticated user found!")
            print("Available user directories:")
            if os.path.exists("data/users"):
                for user_dir in os.listdir("data/users"):
                    creds_file = f"data/users/{user_dir}/gmail_credentials.pickle"
                    exists = "✅" if os.path.exists(creds_file) else "❌"
                    print(f"   {exists} {user_dir}")
            return False

        print(f"\n🎯 Using authenticated user ID: {authenticated_user_id}")

        # Email details (same as your request)
        email_to = "ciappinamaurooj@gmail.com"
        email_subject = "prueba"
        email_body = "probando"

        print(f"\n📧 Email Details:")
        print(f"   From: ciappinamaurooj@gmail.com (authenticated account)")
        print(f"   To: {email_to}")
        print(f"   Subject: {email_subject}")
        print(f"   Body: {email_body}")

        # Ask for confirmation
        print(f"\n⚠️  This will send a REAL email!")
        response = input("Do you want to proceed? (yes/no): ").lower().strip()

        if response not in ['yes', 'y', 'sí', 'si']:
            print("❌ Email sending cancelled by user")
            return False

        print(f"\n📤 Sending email...")

        # Send the email
        success, message = email_service.send_email(
            authenticated_user_id,
            email_to,
            email_subject,
            email_body
        )

        if success:
            print(f"✅ SUCCESS: {message}")
            print(f"\n🎉 Email sent successfully!")
            print(f"📧 Check your inbox at {email_to}")
            return True
        else:
            print(f"❌ FAILED: {message}")
            return False

    except Exception as e:
        print(f"❌ Error during email send test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_email_validation():
    """Test email validation separately."""
    print("\n🔍 Testing Email Validation...")

    try:
        # Import validation function
        import re

        def _is_valid_email(email: str) -> bool:
            if not email or '@' not in email or '.' not in email:
                return False
            if '..' in email:
                return False
            local_part = email.split('@')[0]
            if local_part.startswith('.') or local_part.endswith('.'):
                return False
            email_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._+%-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$'
            return bool(re.match(email_pattern, email))

        test_email = "ciappinamaurooj@gmail.com"
        is_valid = _is_valid_email(test_email)

        print(f"   Email: {test_email}")
        print(f"   Valid: {'✅ Yes' if is_valid else '❌ No'}")

        return is_valid

    except Exception as e:
        print(f"❌ Email validation error: {e}")
        return False

def main():
    """Main function."""
    print("🤖 Personal Automation Bot - Real Email Test")
    print("This script will test the actual email sending functionality.\n")

    # Test email validation first
    if not test_email_validation():
        print("❌ Email validation failed, stopping test")
        return 1

    # Test real email sending
    if test_real_email_send():
        print("\n🎉 All tests passed!")
        print("The email sending functionality is working correctly.")
        return 0
    else:
        print("\n❌ Email sending test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
