"""
Secure token storage utilities for the Simplified Google Bot.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from cryptography.fernet import Fernet

from simplified_google_bot.config import settings

logger = logging.getLogger(__name__)

class TokenStorage:
    """
    Secure storage for OAuth tokens and other sensitive data.
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize the token storage.

        Args:
            storage_dir (Path, optional): Directory to store encrypted tokens.
                                       Defaults to TOKENS_DIR.
        """
        self.storage_dir = storage_dir or settings.TOKENS_DIR
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Initialize encryption key
        self._init_encryption_key()

    def _init_encryption_key(self):
        """Initialize or load the encryption key."""
        key_file = self.storage_dir / ".key"

        if key_file.exists():
            # Load existing key
            with open(key_file, "rb") as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)

        self.cipher = Fernet(key)

    def store_user_tokens(self, user_id: int, tokens: Dict[str, Any]) -> bool:
        """
        Store encrypted tokens for a user.

        Args:
            user_id (int): The user ID.
            tokens (Dict[str, Any]): The tokens to store.

        Returns:
            bool: True if tokens were stored successfully, False otherwise.
        """
        try:
            # Serialize tokens to JSON
            tokens_json = json.dumps(tokens)

            # Encrypt the tokens
            encrypted_tokens = self.cipher.encrypt(tokens_json.encode())

            # Store to file
            token_file = self.storage_dir / f"user_{user_id}.token"
            with open(token_file, "wb") as f:
                f.write(encrypted_tokens)

            # Set restrictive permissions
            os.chmod(token_file, 0o600)

            logger.info(f"Tokens stored for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store tokens for user {user_id}: {e}")
            return False

    def load_user_tokens(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Load and decrypt tokens for a user.

        Args:
            user_id (int): The user ID.

        Returns:
            Optional[Dict[str, Any]]: The decrypted tokens, or None if not found.
        """
        try:
            token_file = self.storage_dir / f"user_{user_id}.token"

            if not token_file.exists():
                return None

            # Read encrypted tokens
            with open(token_file, "rb") as f:
                encrypted_tokens = f.read()

            # Decrypt the tokens
            decrypted_tokens = self.cipher.decrypt(encrypted_tokens)

            # Parse JSON
            tokens = json.loads(decrypted_tokens.decode())

            logger.info(f"Tokens loaded for user {user_id}")
            return tokens

        except Exception as e:
            logger.error(f"Failed to load tokens for user {user_id}: {e}")
            return None

    def delete_user_tokens(self, user_id: int) -> bool:
        """
        Delete stored tokens for a user.

        Args:
            user_id (int): The user ID.

        Returns:
            bool: True if tokens were deleted, False if not found.
        """
        try:
            token_file = self.storage_dir / f"user_{user_id}.token"

            if token_file.exists():
                token_file.unlink()
                logger.info(f"Tokens deleted for user {user_id}")
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"Failed to delete tokens for user {user_id}: {e}")
            return False

    def user_has_tokens(self, user_id: int) -> bool:
        """
        Check if a user has stored tokens.

        Args:
            user_id (int): The user ID.

        Returns:
            bool: True if user has tokens, False otherwise.
        """
        token_file = self.storage_dir / f"user_{user_id}.token"
        return token_file.exists()

    def list_users_with_tokens(self) -> list:
        """
        Get a list of user IDs that have stored tokens.

        Returns:
            list: List of user IDs.
        """
        users = []
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.startswith("user_") and filename.endswith(".token"):
                    user_id_str = filename[5:-6]  # Remove "user_" prefix and ".token" suffix
                    try:
                        user_id = int(user_id_str)
                        users.append(user_id)
                    except ValueError:
                        continue
        except Exception as e:
            logger.error(f"Failed to list users with tokens: {e}")

        return users

    def validate_token(self, user_id: int) -> bool:
        """
        Validate if a user's token exists and is properly formatted.

        Args:
            user_id (int): The user ID.

        Returns:
            bool: True if token is valid, False otherwise.
        """
        tokens = self.load_user_tokens(user_id)
        if not tokens:
            return False

        # Check for required token fields
        required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret']
        return all(field in tokens for field in required_fields)


def get_user_data_path(user_id: str) -> Path:
    """
    Get the data directory path for a specific user.

    Args:
        user_id: Unique identifier for the user

    Returns:
        Path: Path to user's data directory
    """
    user_data_dir = settings.USERS_DIR / str(user_id)
    user_data_dir.mkdir(parents=True, exist_ok=True)
    return user_data_dir
