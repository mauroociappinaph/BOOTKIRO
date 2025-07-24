"""
Configuration settings for the Simplified Google Bot.
Handles environment variables, default values, and configuration validation.
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR.parent / "data"

# Create data directories if they don't exist
TOKENS_DIR = DATA_DIR / "tokens"
USERS_DIR = DATA_DIR / "users"
TOKENS_DIR.mkdir(parents=True, exist_ok=True)
USERS_DIR.mkdir(parents=True, exist_ok=True)

# Bot settings
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
BOT_NAME = os.environ.get("BOT_NAME", "SimplifiedGoogleBot")

# Google API settings
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "")

# Scopes for Google APIs
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive",
]

# Logging settings
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.environ.get("LOG_FILE", "bot.log")

# Default configuration
DEFAULT_CONFIG = {
    "bot_token": BOT_TOKEN,
    "bot_name": BOT_NAME,
    "google_client_id": GOOGLE_CLIENT_ID,
    "google_client_secret": GOOGLE_CLIENT_SECRET,
    "google_redirect_uri": GOOGLE_REDIRECT_URI,
    "google_scopes": GOOGLE_SCOPES,
    "log_level": LOG_LEVEL,
    "log_format": LOG_FORMAT,
    "log_file": LOG_FILE,
}


def get_config() -> Dict[str, Any]:
    """
    Get the current configuration.

    Returns:
        Dict[str, Any]: The current configuration dictionary.
    """
    return DEFAULT_CONFIG


def validate_config() -> Dict[str, Optional[str]]:
    """
    Validate the current configuration and return any errors.

    Returns:
        Dict[str, Optional[str]]: Dictionary of configuration errors, empty if valid.
    """
    errors = {}

    # Check required settings
    if not BOT_TOKEN:
        errors["bot_token"] = "Telegram bot token is required"

    if not GOOGLE_CLIENT_ID:
        errors["google_client_id"] = "Google Client ID is required"

    if not GOOGLE_CLIENT_SECRET:
        errors["google_client_secret"] = "Google Client Secret is required"

    if not GOOGLE_REDIRECT_URI:
        errors["google_redirect_uri"] = "Google Redirect URI is required"

    return errors


def setup_logging() -> None:
    """
    Configure the logging system based on current settings.
    """
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

    # Set specific loggers to different levels if needed
    logging.getLogger("telegram").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
