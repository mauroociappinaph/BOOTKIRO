"""
Secure token storage utilities.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
from personal_automation_bot.config import settings

logger = logging.getLogger(__name__)

class TokenStorage:
    """
    Secure storage for OAuth tokens and other sensitive data.
    """

    def __init__(self, storage_dir: str = None):
        """
        Initialize the token storage.

        Args:
            storage_dir (str, optional): Directory to store encrypted tokens.
                                       Defaults to DATA_DIR/tokens.
        """
        if storage_dir is None:
            storage_dir = os.path.join(settings.DATA_DIR, "tokens")

        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

        # Initialize encryption key
        self._init_encryption_key()

    def _init_encryption_key(self):
        """Initialize or load the encryption key."""
        key_file = os.path.join(self.storage_dir, ".key")

        if os.path.exists(key_file):
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

    def store_user_tokens(self, user_id: int, tokens: Dict[str, Any]):
        """
        Store encrypted tokens for a user.

        Args:
            user_id (int): The user ID.
            tokens (Dict[str, Any]): The tokens to store.
        """
        try:
            # Serialize tokens to JSON
            tokens_json = json.dumps(tokens)

            # Encrypt the tokens
            encrypted_tokens = self.cipher.encrypt(tokens_json.encode())

            # Store to file
            token_file = os.path.join(self.storage_dir, f"user_{user_id}.token")
            with open(token_file, "wb") as f:
                f.write(encrypted_tokens)

            # Set restrictive permissions
            os.chmod(token_file, 0o600)

            logger.info(f"Tokens stored for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to store tokens for user {user_id}: {e}")
            raise

    def load_user_tokens(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Load and decrypt tokens for a user.

        Args:
            user_id (int): The user ID.

        Returns:
            Dict[str, Any]: The decrypted tokens, or None if not found.
        """
        try:
            token_file = os.path.join(self.storage_dir, f"user_{user_id}.token")

            if not os.path.exists(token_file):
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
            token_file = os.path.join(self.storage_dir, f"user_{user_id}.token")

            if os.path.exists(token_file):
                os.remove(token_file)
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
        token_file = os.path.join(self.storage_dir, f"user_{user_id}.token")
        return os.path.exists(token_file)

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


def get_user_data_path(user_id: str) -> str:
    """
    Get the data directory path for a specific user.

    Args:
        user_id: Unique identifier for the user

    Returns:
        str: Path to user's data directory
    """
    user_data_dir = os.path.join(settings.DATA_DIR, "users", str(user_id))
    os.makedirs(user_data_dir, exist_ok=True)
    return user_data_dir
