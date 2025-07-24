"""
Configuration validation utilities for the Simplified Google Bot.
"""

import os
import sys
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from simplified_google_bot.config import settings


def validate_environment() -> Tuple[bool, Dict[str, str]]:
    """
    Validate the environment configuration.

    Returns:
        Tuple[bool, Dict[str, str]]: (is_valid, errors)
    """
    errors = settings.validate_config()
    return len(errors) == 0, errors


def check_directory_permissions() -> Tuple[bool, List[str]]:
    """
    Check if the application has proper permissions for required directories.

    Returns:
        Tuple[bool, List[str]]: (all_permissions_ok, error_messages)
    """
    directories_to_check = [
        settings.DATA_DIR,
        settings.TOKENS_DIR,
        settings.USERS_DIR
    ]

    errors = []

    for directory in directories_to_check:
        # Check if directory exists
        if not directory.exists():
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Could not create directory {directory}: {str(e)}")
                continue

        # Check write permissions
        try:
            test_file = directory / ".permission_test"
            with open(test_file, "w") as f:
                f.write("test")
            test_file.unlink()
        except Exception as e:
            errors.append(f"No write permission for directory {directory}: {str(e)}")

    return len(errors) == 0, errors


def print_validation_results(is_valid: bool, errors: Dict[str, str]) -> None:
    """
    Print validation results in a user-friendly format.

    Args:
        is_valid (bool): Whether the configuration is valid
        errors (Dict[str, str]): Dictionary of errors
    """
    if is_valid:
        print("✅ Configuration is valid!")
        return

    print("❌ Configuration validation failed:")
    for key, message in errors.items():
        print(f"  - {key}: {message}")

    print("\nPlease set the required environment variables:")
    if "bot_token" in errors:
        print("  export TELEGRAM_BOT_TOKEN='your_telegram_bot_token'")
    if "google_client_id" in errors:
        print("  export GOOGLE_CLIENT_ID='your_google_client_id'")
    if "google_client_secret" in errors:
        print("  export GOOGLE_CLIENT_SECRET='your_google_client_secret'")
    if "google_redirect_uri" in errors:
        print("  export GOOGLE_REDIRECT_URI='your_redirect_uri'")


def setup_wizard() -> None:
    """
    Interactive setup wizard to guide users through configuration.
    """
    print("=== Simplified Google Bot Setup Wizard ===")
    print("This wizard will help you configure the bot.")

    # Check if .env file exists
    env_file = Path(settings.BASE_DIR.parent) / ".env"
    env_exists = env_file.exists()

    if not env_exists:
        create_env = input("No .env file found. Would you like to create one? (y/n): ")
        if create_env.lower() == 'y':
            with open(env_file, "w") as f:
                f.write("# Simplified Google Bot Configuration\n\n")
            print(f"Created .env file at {env_file}")

    # Telegram Bot Token
    if not settings.BOT_TOKEN:
        print("\n== Telegram Bot Setup ==")
        print("1. Go to https://t.me/BotFather on Telegram")
        print("2. Send /newbot and follow instructions to create a new bot")
        print("3. Copy the API token provided by BotFather")

        bot_token = input("Enter your Telegram Bot Token: ")
        if bot_token:
            append_to_env(env_file, "TELEGRAM_BOT_TOKEN", bot_token)

    # Google API Credentials
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        print("\n== Google API Setup ==")
        print("1. Go to https://console.developers.google.com/")
        print("2. Create a new project")
        print("3. Enable the Gmail, Calendar, and Drive APIs")
        print("4. Create OAuth 2.0 credentials")
        print("5. Set up the OAuth consent screen")

        client_id = input("Enter your Google Client ID: ")
        if client_id:
            append_to_env(env_file, "GOOGLE_CLIENT_ID", client_id)

        client_secret = input("Enter your Google Client Secret: ")
        if client_secret:
            append_to_env(env_file, "GOOGLE_CLIENT_SECRET", client_secret)

        redirect_uri = input("Enter your OAuth Redirect URI (default: http://localhost:8080): ")
        if not redirect_uri:
            redirect_uri = "http://localhost:8080"
        append_to_env(env_file, "GOOGLE_REDIRECT_URI", redirect_uri)

    print("\nSetup complete! Restart the application for changes to take effect.")


def append_to_env(env_file: Path, key: str, value: str) -> None:
    """
    Append a key-value pair to the .env file.

    Args:
        env_file (Path): Path to the .env file
        key (str): Environment variable key
        value (str): Environment variable value
    """
    with open(env_file, "a") as f:
        f.write(f"{key}='{value}'\n")
