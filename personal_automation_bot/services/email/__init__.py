"""
Email service module for Personal Automation Bot.

This module provides email functionality through Gmail API integration.
"""

from .gmail_client import GmailClient
from .email_service import EmailService

__all__ = ['GmailClient', 'EmailService']
