#!/usr/bin/env python3
"""
Test script for the authentication system.
"""
import sys
import os
import tempfile
import shutil

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_token_storage():
    """Test the token storage system."""
    try:
        from personal_automation_bot.utils.storage import TokenStorage

        # Create temporary directory for testing
        temp_dir = tempfile.mkdtemp()
        storage = TokenStorage(temp_dir)

        # Test storing tokens
        user_id = 12345
        test_tokens = {
            'token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret'
        }

        storage.store_user_tokens(user_id, test_tokens)
        print("✅ Token storage successful")

        # Test loading tokens
        loaded_tokens = storage.load_user_tokens(user_id)
        if loaded_tokens and loaded_tokens['token'] == 'test_access_token':
            print("✅ Token loading successful")
        else:
            print("❌ Token loading failed")
            return False

        # Test user has tokens check
        if storage.user_has_tokens(user_id):
            print("✅ User has tokens check successful")
        else:
            print("❌ User has tokens check failed")
            return False

        # Test listing users
        users = storage.list_users_with_tokens()
        if user_id in users:
            print("✅ List users with tokens successful")
        else:
            print("❌ List users with tokens failed")
            return False

        # Test deleting tokens
        if storage.delete_user_tokens(user_id):
            print("✅ Token deletion successful")
        else:
            print("❌ Token deletion failed")
            return False

        # Verify tokens are deleted
        if not storage.user_has_tokens(user_id):
            print("✅ Token deletion verification successful")
        else:
            print("❌ Token deletion verification failed")
            return False

        # Clean up
        shutil.rmtree(temp_dir)
        return True

    except Exception as e:
        print(f"❌ Token storage test error: {e}")
        return False

def test_auth_manager():
    """Test the Google Auth Manager."""
    try:
        from personal_automation_bot.utils.auth import GoogleAuthManager

        # Create auth manager
        auth_manager = GoogleAuthManager()
        print("✅ Auth manager creation successful")

        # Test user authentication check (should be False for non-existent user)
        user_id = 99999
        if not auth_manager.is_user_authenticated(user_id):
            print("✅ User authentication check successful")
        else:
            print("❌ User authentication check failed")
            return False

        # Test auth status summary
        status = auth_manager.get_auth_status_summary(user_id)
        if not status['authenticated']:
            print("✅ Auth status summary successful")
        else:
            print("❌ Auth status summary failed")
            return False

        # Test cleanup of expired sessions
        auth_manager.cleanup_expired_auth_sessions()
        print("✅ Cleanup expired sessions successful")

        return True

    except Exception as e:
        print(f"❌ Auth manager test error: {e}")
        return False

def test_auth_imports():
    """Test that all auth components can be imported."""
    try:
        from personal_automation_bot.utils.auth import GoogleAuthManager, google_auth_manager
        print("✅ Auth manager import successful")

        from personal_automation_bot.utils.storage import TokenStorage
        print("✅ Token storage import successful")

        from personal_automation_bot.bot.commands.auth import (
            auth_command,
            handle_auth_callback,
            handle_auth_code_message
        )
        print("✅ Auth commands import successful")

        return True

    except ImportError as e:
        print(f"❌ Auth import error: {e}")
        return False

def test_bot_with_auth():
    """Test that the bot can be set up with auth components."""
    try:
        from personal_automation_bot.bot import setup_bot

        # Test that bot setup works with auth components (may succeed if token is available)
        try:
            app = setup_bot()
            print("✅ Bot setup with auth components successful")
            return True
        except ValueError as e:
            if "token not provided" in str(e).lower():
                print("✅ Bot setup correctly requires token (auth components working)")
                return True
            else:
                print(f"❌ Unexpected error: {e}")
                return False

    except Exception as e:
        print(f"❌ Bot with auth test error: {e}")
        return False

def main():
    """Run all authentication tests."""
    print("🔐 Testing Authentication System\n")

    tests = [
        ("Auth Imports", test_auth_imports),
        ("Token Storage", test_token_storage),
        ("Auth Manager", test_auth_manager),
        ("Bot with Auth", test_bot_with_auth)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All authentication tests passed! The auth system is ready.")
        return 0
    else:
        print("❌ Some authentication tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
