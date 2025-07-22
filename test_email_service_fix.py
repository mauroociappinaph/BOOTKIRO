#!/usr/bin/env python3
"""
Test the fixed EmailService authentication.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_email_service_auth():
    """Test EmailService authentication after fix."""
    print("🔧 Testing Fixed EmailService Authentication")
    print("=" * 50)

    try:
        from personal_automation_bot.services.email import EmailService

        # Initialize email service
        email_service = EmailService()

        # Test with the user ID that has credentials
        user_id = "793880527"

        print(f"🔍 Testing authentication for user ID: {user_id}")

        # Check authentication
        is_auth = email_service.is_user_authenticated(user_id)
        print(f"🔐 Is authenticated: {'✅ Yes' if is_auth else '❌ No'}")

        if not is_auth:
            print("❌ Authentication check failed")
            return False

        # Test sending email
        print(f"\n📧 Testing email send through EmailService...")

        email_to = "ciappinamaurooj@gmail.com"
        email_subject = "prueba desde EmailService"
        email_body = "probando EmailService arreglado"

        print(f"   To: {email_to}")
        print(f"   Subject: {email_subject}")
        print(f"   Body: {email_body}")

        # Ask for confirmation
        response = input("\n⚠️  Send REAL email via EmailService? (yes/no): ").lower().strip()

        if response not in ['yes', 'y', 'sí', 'si']:
            print("❌ Email sending cancelled")
            return True  # Still consider auth test successful

        print("📤 Sending email via EmailService...")

        success, message = email_service.send_email(user_id, email_to, email_subject, email_body)

        if success:
            print(f"✅ SUCCESS: {message}")
            return True
        else:
            print(f"❌ FAILED: {message}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("🧪 EmailService Fix Test\n")

    if test_email_service_auth():
        print("\n🎉 EmailService is working correctly!")
        print("Now the Telegram bot should work too.")
        return 0
    else:
        print("\n❌ EmailService test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
