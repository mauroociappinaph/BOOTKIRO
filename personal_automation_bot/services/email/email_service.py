"""
Email service for Personal Automation Bot.

This module provides high-level email functionality that integrates with the Telegram bot.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .gmail_client import GmailClient

logger = logging.getLogger(__name__)


class EmailService:
    """High-level email service that manages Gmail operations for users."""

    def __init__(self):
        """Initialize the email service."""
        self._clients = {}  # Cache for Gmail clients

    def _get_client(self, user_id: str) -> GmailClient:
        """
        Get or create a Gmail client for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            GmailClient instance for the user
        """
        if user_id not in self._clients:
            self._clients[user_id] = GmailClient(user_id)
        return self._clients[user_id]

    def authenticate_user(self, user_id: str) -> Tuple[bool, str]:
        """
        Authenticate a user with Gmail.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Tuple of (success, message)
        """
        try:
            client = self._get_client(user_id)
            success = client.authenticate()

            if success:
                profile = client.get_profile()
                if profile:
                    return True, f"✅ Autenticado exitosamente con Gmail: {profile['email']}"
                else:
                    return True, "✅ Autenticado exitosamente con Gmail"
            else:
                return False, "❌ Error en la autenticación. Verifica tu configuración de Google Cloud Console."

        except Exception as e:
            logger.error(f"Authentication error for user {user_id}: {e}")
            return False, f"❌ Error de autenticación: {str(e)}"

    def is_user_authenticated(self, user_id: str) -> bool:
        """
        Check if a user is authenticated with Gmail.

        Args:
            user_id: Unique identifier for the user

        Returns:
            bool: True if authenticated, False otherwise
        """
        try:
            client = self._get_client(user_id)
            return client.is_authenticated()
        except Exception as e:
            logger.error(f"Error checking authentication for user {user_id}: {e}")
            return False

    def get_recent_emails(self, user_id: str, count: int = 10) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Get recent emails for a user.

        Args:
            user_id: Unique identifier for the user
            count: Number of emails to retrieve

        Returns:
            Tuple of (success, emails_list, message)
        """
        try:
            client = self._get_client(user_id)

            if not client.is_authenticated():
                return False, [], "❌ No estás autenticado. Usa /email auth primero."

            emails = client.get_recent_emails(max_results=count)

            if not emails:
                return True, [], "📭 No se encontraron correos recientes."

            return True, emails, f"📧 Se encontraron {len(emails)} correos recientes."

        except Exception as e:
            logger.error(f"Error getting emails for user {user_id}: {e}")
            return False, [], f"❌ Error al obtener correos: {str(e)}"

    def get_email_details(self, user_id: str, email_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Get detailed information about a specific email.

        Args:
            user_id: Unique identifier for the user
            email_id: Gmail message ID

        Returns:
            Tuple of (success, email_details, message)
        """
        try:
            client = self._get_client(user_id)

            if not client.is_authenticated():
                return False, None, "❌ No estás autenticado. Usa /email auth primero."

            email_details = client._get_email_details(email_id)

            if not email_details:
                return False, None, "❌ No se pudo obtener los detalles del correo."

            return True, email_details, "✅ Detalles del correo obtenidos."

        except Exception as e:
            logger.error(f"Error getting email details for user {user_id}: {e}")
            return False, None, f"❌ Error al obtener detalles: {str(e)}"

    def send_email(self, user_id: str, to: str, subject: str, body: str) -> Tuple[bool, str]:
        """
        Send an email for a user.

        Args:
            user_id: Unique identifier for the user
            to: Recipient email address
            subject: Email subject
            body: Email body

        Returns:
            Tuple of (success, message)
        """
        try:
            client = self._get_client(user_id)

            if not client.is_authenticated():
                return False, "❌ No estás autenticado. Usa /email auth primero."

            # Basic email validation
            if not to or '@' not in to:
                return False, "❌ Dirección de correo del destinatario inválida."

            if not subject.strip():
                return False, "❌ El asunto no puede estar vacío."

            if not body.strip():
                return False, "❌ El cuerpo del correo no puede estar vacío."

            success = client.send_email(to, subject, body)

            if success:
                return True, f"✅ Correo enviado exitosamente a {to}"
            else:
                return False, "❌ Error al enviar el correo. Intenta nuevamente."

        except Exception as e:
            logger.error(f"Error sending email for user {user_id}: {e}")
            return False, f"❌ Error al enviar correo: {str(e)}"

    def search_emails(self, user_id: str, query: str, max_results: int = 20) -> Tuple[bool, List[Dict[str, Any]], str]:
        """
        Search emails for a user.

        Args:
            user_id: Unique identifier for the user
            query: Gmail search query
            max_results: Maximum number of results

        Returns:
            Tuple of (success, emails_list, message)
        """
        try:
            client = self._get_client(user_id)

            if not client.is_authenticated():
                return False, [], "❌ No estás autenticado. Usa /email auth primero."

            if not query.strip():
                return False, [], "❌ La consulta de búsqueda no puede estar vacía."

            emails = client.search_emails(query, max_results)

            if not emails:
                return True, [], f"🔍 No se encontraron correos para la búsqueda: '{query}'"

            return True, emails, f"🔍 Se encontraron {len(emails)} correos para: '{query}'"

        except Exception as e:
            logger.error(f"Error searching emails for user {user_id}: {e}")
            return False, [], f"❌ Error en la búsqueda: {str(e)}"

    def mark_email_as_read(self, user_id: str, email_id: str) -> Tuple[bool, str]:
        """
        Mark an email as read.

        Args:
            user_id: Unique identifier for the user
            email_id: Gmail message ID

        Returns:
            Tuple of (success, message)
        """
        try:
            client = self._get_client(user_id)

            if not client.is_authenticated():
                return False, "❌ No estás autenticado. Usa /email auth primero."

            success = client.mark_as_read(email_id)

            if success:
                return True, "✅ Correo marcado como leído."
            else:
                return False, "❌ Error al marcar el correo como leído."

        except Exception as e:
            logger.error(f"Error marking email as read for user {user_id}: {e}")
            return False, f"❌ Error: {str(e)}"

    def get_user_profile(self, user_id: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Get Gmail profile information for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Tuple of (success, profile_info, message)
        """
        try:
            client = self._get_client(user_id)

            if not client.is_authenticated():
                return False, None, "❌ No estás autenticado. Usa /email auth primero."

            profile = client.get_profile()

            if profile:
                return True, profile, "✅ Información de perfil obtenida."
            else:
                return False, None, "❌ No se pudo obtener la información del perfil."

        except Exception as e:
            logger.error(f"Error getting profile for user {user_id}: {e}")
            return False, None, f"❌ Error: {str(e)}"

    def format_email_summary(self, email: Dict[str, Any]) -> str:
        """
        Format an email for display in Telegram.

        Args:
            email: Email dictionary from Gmail API

        Returns:
            Formatted string for Telegram display
        """
        # Truncate long subjects and senders
        subject = email.get('subject', 'Sin asunto')
        if len(subject) > 50:
            subject = subject[:47] + "..."

        sender = email.get('sender', 'Remitente desconocido')
        if len(sender) > 40:
            sender = sender[:37] + "..."

        snippet = email.get('snippet', '')
        if len(snippet) > 100:
            snippet = snippet[:97] + "..."

        # Format date (basic formatting)
        date = email.get('date', 'Fecha desconocida')

        return f"📧 **{subject}**\n👤 De: {sender}\n📅 {date}\n💬 {snippet}\n🆔 ID: `{email['id']}`"

    def format_email_details(self, email: Dict[str, Any]) -> str:
        """
        Format detailed email information for display.

        Args:
            email: Email dictionary with full details

        Returns:
            Formatted string for Telegram display
        """
        subject = email.get('subject', 'Sin asunto')
        sender = email.get('sender', 'Remitente desconocido')
        date = email.get('date', 'Fecha desconocida')
        body = email.get('body', 'Sin contenido')

        # Truncate very long bodies
        if len(body) > 1000:
            body = body[:997] + "..."

        return f"""📧 **Detalles del Correo**

**Asunto:** {subject}
**De:** {sender}
**Fecha:** {date}

**Contenido:**
{body}

🆔 **ID:** `{email['id']}`"""
