"""
Google OAuth authentication utilities for the Simplified Google Bot.
"""
import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.exceptions import RefreshError

from simplified_google_bot.config import settings
from simplified_google_bot.utils.storage import TokenStorage

logger = logging.getLogger(__name__)

class GoogleAuthManager:
    """
    Manages Google OAuth authentication for users.
    """

    def __init__(self):
        """Initialize the Google Auth Manager."""
        self.token_storage = TokenStorage()
        self.pending_auth = {}  # Store pending authentication sessions

        # Validate required settings
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            logger.warning("Google OAuth credentials not configured")

    def _generate_state(self) -> str:
        """Generate a secure random state parameter for OAuth."""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

    def start_auth_flow(self, user_id: int) -> Tuple[str, str]:
        """
        Start the OAuth flow for a user.

        Args:
            user_id (int): The Telegram user ID.

        Returns:
            Tuple[str, str]: (authorization_url, state) for the OAuth flow.

        Raises:
            ValueError: If OAuth credentials are not configured.
        """
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError("Google OAuth credentials not configured")

        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
                }
            },
            scopes=settings.GOOGLE_SCOPES
        )

        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        # Generate state parameter
        state = self._generate_state()

        # Store the flow for later use
        self.pending_auth[state] = {
            'user_id': user_id,
            'flow': flow,
            'created_at': datetime.now()
        }

        # Generate authorization URL
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent to get refresh token
        )

        logger.info(f"Started OAuth flow for user {user_id}")
        return authorization_url, state

    def complete_auth_flow(self, state: str, authorization_code: str) -> bool:
        """
        Complete the OAuth flow with the authorization code.

        Args:
            state (str): The state parameter from the OAuth flow.
            authorization_code (str): The authorization code from Google.

        Returns:
            bool: True if authentication was successful, False otherwise.
        """
        if state not in self.pending_auth:
            logger.error(f"Invalid or expired state parameter: {state}")
            return False

        auth_data = self.pending_auth[state]
        user_id = auth_data['user_id']
        flow = auth_data['flow']

        try:
            # Exchange authorization code for tokens
            flow.fetch_token(code=authorization_code)

            # Get credentials
            credentials = flow.credentials

            # Store tokens securely
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes,
                'expiry': credentials.expiry.isoformat() if credentials.expiry else None,
                'created_at': datetime.now().isoformat()
            }

            success = self.token_storage.store_user_tokens(user_id, token_data)

            # Clean up pending auth
            del self.pending_auth[state]

            if success:
                logger.info(f"OAuth flow completed successfully for user {user_id}")
            else:
                logger.error(f"Failed to store tokens for user {user_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to complete OAuth flow for user {user_id}: {e}")
            # Clean up pending auth
            if state in self.pending_auth:
                del self.pending_auth[state]
            return False

    def get_user_credentials(self, user_id: int) -> Optional[Credentials]:
        """
        Get valid Google credentials for a user.

        Args:
            user_id (int): The Telegram user ID.

        Returns:
            Optional[Credentials]: Valid Google credentials, or None if not available.
        """
        token_data = self.token_storage.load_user_tokens(user_id)
        if not token_data:
            return None

        try:
            # Create credentials from stored data
            credentials = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )

            # Set expiry if available
            if token_data.get('expiry'):
                credentials.expiry = datetime.fromisoformat(token_data['expiry'])

            # Refresh token if needed
            if credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())

                    # Update stored tokens
                    token_data.update({
                        'token': credentials.token,
                        'expiry': credentials.expiry.isoformat() if credentials.expiry else None,
                        'updated_at': datetime.now().isoformat()
                    })

                    self.token_storage.store_user_tokens(user_id, token_data)
                    logger.info(f"Refreshed tokens for user {user_id}")

                except RefreshError as e:
                    logger.error(f"Failed to refresh tokens for user {user_id}: {e}")
                    # Delete invalid tokens
                    self.token_storage.delete_user_tokens(user_id)
                    return None

            return credentials

        except Exception as e:
            logger.error(f"Failed to get credentials for user {user_id}: {e}")
            return None

    def is_user_authenticated(self, user_id: int) -> bool:
        """
        Check if a user is authenticated with Google.

        Args:
            user_id (int): The Telegram user ID.

        Returns:
            bool: True if user is authenticated, False otherwise.
        """
        credentials = self.get_user_credentials(user_id)
        return credentials is not None and credentials.valid

    def revoke_user_authentication(self, user_id: int) -> bool:
        """
        Revoke authentication for a user.

        Args:
            user_id (int): The Telegram user ID.

        Returns:
            bool: True if revocation was successful, False otherwise.
        """
        try:
            credentials = self.get_user_credentials(user_id)
            if credentials:
                # Revoke the token with Google
                try:
                    credentials.revoke(Request())
                except Exception as e:
                    logger.warning(f"Failed to revoke token with Google for user {user_id}: {e}")

            # Delete stored tokens
            success = self.token_storage.delete_user_tokens(user_id)

            if success:
                logger.info(f"Revoked authentication for user {user_id}")

            return success

        except Exception as e:
            logger.error(f"Failed to revoke authentication for user {user_id}: {e}")
            return False

    def cleanup_expired_auth_sessions(self):
        """Clean up expired pending authentication sessions."""
        current_time = datetime.now()
        expired_states = []

        for state, auth_data in self.pending_auth.items():
            # Remove sessions older than 1 hour
            if current_time - auth_data['created_at'] > timedelta(hours=1):
                expired_states.append(state)

        for state in expired_states:
            del self.pending_auth[state]
            logger.info(f"Cleaned up expired auth session: {state}")

    def get_auth_status_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Get authentication status summary for a user.

        Args:
            user_id (int): The Telegram user ID.

        Returns:
            Dict[str, Any]: Authentication status information.
        """
        credentials = self.get_user_credentials(user_id)

        if not credentials:
            return {
                'authenticated': False,
                'status': 'Not authenticated'
            }

        token_data = self.token_storage.load_user_tokens(user_id)

        return {
            'authenticated': True,
            'status': 'Authenticated',
            'scopes': credentials.scopes,
            'expires_at': credentials.expiry.isoformat() if credentials.expiry else None,
            'created_at': token_data.get('created_at') if token_data else None,
            'updated_at': token_data.get('updated_at') if token_data else None
        }

# Global auth manager instance
google_auth_manager = GoogleAuthManager()
