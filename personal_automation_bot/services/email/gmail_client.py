"""
Gmail API client for the Personal Automation Bot.

This module provides a client for interacting with Gmail API using OAuth 2.0 authentication.
It supports reading emails, sending emails, and searching through the mailbox.
"""

import os
import pickle
import base64
from typing import List, Dict, Optional, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from personal_automation_bot.utils.storage import get_user_data_path


class GmailClient:
    """Gmail API client with OAuth 2.0 authentication."""

    # Gmail API scopes - modify as needed
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]

    def __init__(self, user_id: str):
        """
        Initialize Gmail client for a specific user.

        Args:
            user_id: Unique identifier for the user
        """
        self.user_id = user_id
        self.service = None
        self.credentials = None
        self._load_credentials()

    def _get_credentials_path(self) -> str:
        """Get the path to store user credentials."""
        user_data_path = get_user_data_path(self.user_id)
        return os.path.join(user_data_path, 'gmail_credentials.pickle')

    def _get_client_secrets_path(self) -> str:
        """Get the path to client secrets file."""
        # This should be configured in your environment
        return os.getenv('GOOGLE_CLIENT_SECRETS_PATH', 'credentials.json')

    def _load_credentials(self):
        """Load existing credentials from storage."""
        creds_path = self._get_credentials_path()
        if os.path.exists(creds_path):
            with open(creds_path, 'rb') as token:
                self.credentials = pickle.load(token)

    def _save_credentials(self):
        """Save credentials to storage."""
        creds_path = self._get_credentials_path()
        os.makedirs(os.path.dirname(creds_path), exist_ok=True)
        with open(creds_path, 'wb') as token:
            pickle.dump(self.credentials, token)

    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth 2.0.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Check if credentials exist and are valid
            if self.credentials and self.credentials.valid:
                self.service = build('gmail', 'v1', credentials=self.credentials)
                return True

            # Refresh credentials if they exist but are expired
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
                self._save_credentials()
                self.service = build('gmail', 'v1', credentials=self.credentials)
                return True

            # Start OAuth flow for new credentials
            client_secrets_path = self._get_client_secrets_path()
            if not os.path.exists(client_secrets_path):
                raise FileNotFoundError(
                    f"Client secrets file not found at {client_secrets_path}. "
                    "Please download it from Google Cloud Console."
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_path, self.SCOPES
            )
            self.credentials = flow.run_local_server(port=0)
            self._save_credentials()
            self.service = build('gmail', 'v1', credentials=self.credentials)
            return True

        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def is_authenticated(self) -> bool:
        """Check if the client is authenticated and ready to use."""
        return self.service is not None

    def get_recent_emails(self, max_results: int = 10, query: str = '') -> List[Dict[str, Any]]:
        """
        Get recent emails from the inbox.

        Args:
            max_results: Maximum number of emails to retrieve
            query: Gmail search query (optional)

        Returns:
            List of email dictionaries with basic information
        """
        if not self.is_authenticated():
            raise RuntimeError("Client not authenticated. Call authenticate() first.")

        try:
            # Get list of messages
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)

            return emails

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific email.

        Args:
            message_id: Gmail message ID

        Returns:
            Dictionary with email details or None if error
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            headers = message['payload'].get('headers', [])

            # Extract common headers
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')

            # Extract body
            body = self._extract_body(message['payload'])

            return {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body,
                'snippet': message.get('snippet', ''),
                'thread_id': message.get('threadId', ''),
                'label_ids': message.get('labelIds', [])
            }

        except HttpError as error:
            print(f"Error getting email details: {error}")
            return None

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract email body from message payload.

        Args:
            payload: Message payload from Gmail API

        Returns:
            Email body as string
        """
        body = ""

        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            # Single part message
            if payload['mimeType'] == 'text/plain' and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        return body

    def send_email(self, to: str, subject: str, body: str, html_body: str = None) -> bool:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: HTML body (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.is_authenticated():
            raise RuntimeError("Client not authenticated. Call authenticate() first.")

        try:
            # Create message
            if html_body:
                message = MIMEMultipart('alternative')
                text_part = MIMEText(body, 'plain')
                html_part = MIMEText(html_body, 'html')
                message.attach(text_part)
                message.attach(html_part)
            else:
                message = MIMEText(body)

            message['to'] = to
            message['subject'] = subject

            # Send message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_message = {'raw': raw_message}

            result = self.service.users().messages().send(
                userId='me',
                body=send_message
            ).execute()

            print(f"Email sent successfully. Message ID: {result['id']}")
            return True

        except HttpError as error:
            print(f"Error sending email: {error}")
            return False

    def search_emails(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search emails using Gmail search syntax.

        Args:
            query: Gmail search query (e.g., "from:example@gmail.com", "subject:important")
            max_results: Maximum number of results to return

        Returns:
            List of matching emails
        """
        return self.get_recent_emails(max_results=max_results, query=query)

    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark an email as read.

        Args:
            message_id: Gmail message ID

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_authenticated():
            raise RuntimeError("Client not authenticated. Call authenticate() first.")

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True

        except HttpError as error:
            print(f"Error marking email as read: {error}")
            return False

    def get_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get user's Gmail profile information.

        Returns:
            Dictionary with profile information or None if error
        """
        if not self.is_authenticated():
            raise RuntimeError("Client not authenticated. Call authenticate() first.")

        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return {
                'email': profile.get('emailAddress'),
                'messages_total': profile.get('messagesTotal'),
                'threads_total': profile.get('threadsTotal'),
                'history_id': profile.get('historyId')
            }

        except HttpError as error:
            print(f"Error getting profile: {error}")
            return None
