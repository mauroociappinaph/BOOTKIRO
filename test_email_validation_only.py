#!/usr/bin/env python3
"""
Test script for email validation functionality only.
"""
import re

def _is_valid_email(email: str) -> bool:
    """
    Validate email address with enhanced checks.

    Args:
        email: Email address to validate

    Returns:
        bool: True if valid, False otherwise
    """
    # Basic format check
    if not email or '@' not in email or '.' not in email:
        return False

    # Check for consecutive dots
    if '..' in email:
        return False

    # Check for dots at start or end of local part
    local_part = email.split('@')[0]
    if local_part.startswith('.') or local_part.endswith('.'):
        return False

    # Enhanced regex pattern
    email_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._+%-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$'

    return bool(re.match(email_pattern, email))

def test_email_validation():
    """Test email validation function."""
    print("Testing email validation...")

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

def main():
    """Run the test."""
    print("🧪 Testing Email Validation\n")

    if test_email_validation():
        print("\n✅ Email validation test PASSED")
        print("🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Email validation test FAILED")
        return 1

if __name__ == "__main__":
    exit(main())
