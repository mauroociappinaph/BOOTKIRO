#!/usr/bin/env python3
"""
Direct Gmail client test.
Test Gmail functionality directly without the EmailService wrapper.
"""
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gmail_client_direct():
    """Test Gmail client directly."""
    print("🔍 Testing Gmail Client Directly")
    print("=" * 40)

    try:
        from personal_automation_bot.services.email.gmail_client import GmailClient

        # Test with the user ID that has credentials
        user_id = "793880527"

        print(f"📁 Testing with user ID: {user_id}")

        # Check if credentials file exists
        creds_path = f"data/users/{user_id}/gmail_credentials.pickle"
        print(f"🔑 Credentials path: {creds_path}")
        print(f"🔑 Credentials exist: {'✅ Yes' if os.path.exists(creds_path) else '❌ No'}")

        if not os.path.exists(creds_path):
            print("❌ Credentials file not found!")
            return False

        # Create Gmail client
        gmail_client = GmailClient(user_id)

        # Check authentication
        is_auth = gmail_client.is_authenticated()
        print(f"🔐 Is authenticated: {'✅ Yes' if is_auth else '❌ No'}")

        if not is_auth:
            print("🔄 Attempting to authenticate...")
            auth_success = gmail_client.authenticate()
            print(f"🔐 Authentication result: {'✅ Success' if auth_success else '❌ Failed'}")

            if not auth_success:
                return False

        # Test getting profile
        print("👤 Getting Gmail profile...")
        profile = gmail_client.get_profile()

        if profile:
            print(f"✅ Profile retrieved:")
            print(f"   📧 Email: {profile['email']}")
            print(f"   📊 Messages: {profile['messages_total']}")
        else:
            print("❌ Failed to get profile")
            return False

        # Test sending email
        print(f"\n📧 Testing email send...")

        email_to = "ciappinamaurooj@gmail.com"
        email_subject = "prueba"
        email_body = "probando"

        print(f"   To: {email_to}")
        print(f"   Subject: {email_subject}")
        print(f"   Body: {email_body}")

        # Ask for confirmation
        response = input("\n⚠️  Send REAL email? (yes/no): ").lower().strip()

        if response not in ['yes', 'y', 'sí', 'si']:
            print("❌ Email sending cancelled")
            return True  # Still consider test successful

        print("📤 Sending email...")

        send_success = gmail_client.send_email(email_to, email_subject, email_body)

        if send_success:
            print("✅ Email sent successfully!")
            return True
        else:
            print("❌ Email sending failed")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print("🧪 Direct Gmail Client Test\n")

    if test_gmail_client_direct():
        print("\n🎉 Gmail client test completed successfully!")
        return 0
    else:
        print("\n❌ Gmail client test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
