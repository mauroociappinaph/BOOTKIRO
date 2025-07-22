#!/usr/bin/env python3
"""
Test script for Gmail authentication diagnosis.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_credentials_file():
    """Test if credentials.json exists and is valid."""
    print("🔍 Testing credentials.json file...")

    credentials_path = "credentials.json"

    if not os.path.exists(credentials_path):
        print(f"❌ credentials.json not found at {credentials_path}")
        return False

    try:
        import json
        with open(credentials_path, 'r') as f:
            creds = json.load(f)

        # Check if it has the required structure
        if 'web' in creds:
            web_creds = creds['web']
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']

            for field in required_fields:
                if field not in web_creds:
                    print(f"❌ Missing required field: {field}")
                    return False
                else:
                    print(f"✅ Found {field}")

            print("✅ credentials.json structure is valid")
            return True
        else:
            print("❌ credentials.json missing 'web' section")
            return False

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in credentials.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        return False

def test_google_auth_imports():
    """Test if Google Auth libraries are properly installed."""
    print("\n🔍 Testing Google Auth imports...")

    try:
        from google.auth.transport.requests import Request
        print("✅ google.auth.transport.requests imported")

        from google.oauth2.credentials import Credentials
        print("✅ google.oauth2.credentials imported")

        from google_auth_oauthlib.flow import InstalledAppFlow
        print("✅ google_auth_oauthlib.flow imported")

        from googleapiclient.discovery import build
        print("✅ googleapiclient.discovery imported")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_oauth_flow():
    """Test OAuth flow setup."""
    print("\n🔍 Testing OAuth flow setup...")

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow

        # Gmail API scopes
        SCOPES = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify'
        ]

        credentials_path = "credentials.json"

        if not os.path.exists(credentials_path):
            print("❌ credentials.json not found")
            return False

        # Try to create the flow
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, SCOPES
        )

        print("✅ OAuth flow created successfully")
        print(f"✅ Redirect URI: {flow.redirect_uri}")

        return True

    except Exception as e:
        print(f"❌ OAuth flow error: {e}")
        return False

def test_user_data_directory():
    """Test user data directory creation."""
    print("\n🔍 Testing user data directory...")

    try:
        from personal_automation_bot.utils.storage import get_user_data_path

        test_user_id = "test_user"
        user_data_path = get_user_data_path(test_user_id)

        print(f"✅ User data path: {user_data_path}")

        # Try to create the directory
        os.makedirs(user_data_path, exist_ok=True)

        if os.path.exists(user_data_path):
            print("✅ User data directory created successfully")
            return True
        else:
            print("❌ Failed to create user data directory")
            return False

    except Exception as e:
        print(f"❌ User data directory error: {e}")
        return False

def main():
    """Run all diagnostic tests."""
    print("🧪 Gmail Authentication Diagnostic\n")

    tests = [
        ("Credentials File", test_credentials_file),
        ("Google Auth Imports", test_google_auth_imports),
        ("OAuth Flow Setup", test_oauth_flow),
        ("User Data Directory", test_user_data_directory)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"--- {test_name} ---")
        if test_func():
            print(f"✅ {test_name} PASSED\n")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED\n")

    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All diagnostic tests passed!")
        print("\n💡 Possible solutions for authentication errors:")
        print("1. Make sure no other instances of the bot are running")
        print("2. Try the authentication process again")
        print("3. Check that port 8080 is available")
        print("4. Ensure your Google Cloud Console project has Gmail API enabled")
        return 0
    else:
        print("\n💥 Some diagnostic tests failed!")
        print("\n🔧 Recommended fixes:")
        if not test_credentials_file():
            print("- Download credentials.json from Google Cloud Console")
        if not test_google_auth_imports():
            print("- Install missing dependencies: pip install google-auth google-auth-oauthlib google-api-python-client")
        return 1

if __name__ == "__main__":
    sys.exit(main())
