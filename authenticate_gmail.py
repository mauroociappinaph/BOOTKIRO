#!/usr/bin/env python3
"""
Gmail Authentication Script
Authenticate with Gmail API and save credentials for the bot.
"""
import os
import pickle
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def authenticate_gmail():
    """Authenticate with Gmail API and save credentials."""
    print("🔐 Gmail Authentication Setup")
    print("=" * 40)

    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        # Gmail API scopes
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify'
        ]

        credentials_path = "credentials.json"

        if not os.path.exists(credentials_path):
            print(f"❌ Error: {credentials_path} not found")
            print("Please download it from Google Cloud Console")
            return False

        print(f"✅ Found {credentials_path}")

        # Create user data directory
        user_id = "793880527"  # Your Telegram user ID from the logs
        user_data_dir = f"data/users/{user_id}"
        os.makedirs(user_data_dir, exist_ok=True)

        token_path = os.path.join(user_data_dir, "gmail_credentials.pickle")

        print(f"📁 User data directory: {user_data_dir}")
        print(f"🔑 Token will be saved to: {token_path}")

        credentials = None

        # Check if we already have valid credentials
        if os.path.exists(token_path):
            print("🔍 Checking existing credentials...")
            with open(token_path, 'rb') as token:
                credentials = pickle.load(token)

        # If there are no valid credentials, start OAuth flow
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print("🔄 Refreshing expired credentials...")
                credentials.refresh(Request())
            else:
                print("🚀 Starting OAuth flow...")
                print("\n📋 What will happen:")
                print("1. Your browser will open")
                print("2. Sign in with your Gmail account: ciappinamaurooj@gmail.com")
                print("3. Grant the requested permissions")
                print("4. Return here when done")

                input("\nPress Enter to continue...")

                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )

                # Try different ports
                ports_to_try = [8080, 8081, 8082, 8083]

                for port in ports_to_try:
                    try:
                        print(f"🌐 Starting OAuth server on port {port}...")
                        credentials = flow.run_local_server(
                            port=port,
                            open_browser=True,
                            success_message='✅ Authentication successful! You can close this window and return to the terminal.'
                        )
                        break
                    except OSError as e:
                        if "Address already in use" in str(e):
                            print(f"⚠️  Port {port} is busy, trying next port...")
                            if port == ports_to_try[-1]:
                                raise e
                            continue
                        else:
                            raise e

        # Save the credentials
        with open(token_path, 'wb') as token:
            pickle.dump(credentials, token)

        print("💾 Credentials saved successfully!")

        # Test the credentials
        print("🧪 Testing Gmail API connection...")
        service = build('gmail', 'v1', credentials=credentials)

        # Get profile info
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress')

        print(f"✅ Successfully connected to Gmail!")
        print(f"📧 Email: {email_address}")
        print(f"📊 Total messages: {profile.get('messagesTotal', 'Unknown')}")

        print("\n🎉 Gmail authentication completed!")
        print("Now you can use the bot to send emails.")

        return True

    except Exception as e:
        print(f"❌ Authentication failed: {e}")

        # Provide specific error guidance
        if "redirect_uri_mismatch" in str(e).lower():
            print("\n🔧 Fix: Add http://localhost:8080/ to authorized redirect URIs in Google Cloud Console")
        elif "access_denied" in str(e).lower():
            print("\n🔧 Fix: Make sure to grant all requested permissions during OAuth")
        elif "invalid_client" in str(e).lower():
            print("\n🔧 Fix: Check that your credentials.json is correct")

        return False

def main():
    """Main function."""
    print("🤖 Personal Automation Bot - Gmail Setup")
    print("This script will authenticate your Gmail account for the bot.\n")

    if authenticate_gmail():
        print("\n✅ Setup complete! You can now:")
        print("1. Use /email in the Telegram bot")
        print("2. Send emails without additional authentication")
        print("3. The bot will use your authenticated Gmail account")
        return 0
    else:
        print("\n❌ Setup failed. Please check the errors above and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
