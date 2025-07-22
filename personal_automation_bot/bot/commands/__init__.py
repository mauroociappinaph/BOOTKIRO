"""
Command handlers for the Telegram bot.
This module contains all command handler functions.
"""
from personal_automation_bot.bot.commands.basic import (
    start_command,
    help_command,
    menu_command
)
from personal_automation_bot.bot.commands.callbacks import handle_callback_query
from personal_automation_bot.bot.commands.email import (
    email_command,
    get_email_callback_handler,
    EMAIL_CALLBACK_HANDLERS
)

__all__ = [
    'start_command',
    'help_command',
    'menu_command',
    'handle_callback_query',
    'email_command',
    'get_email_callback_handler',
    'EMAIL_CALLBACK_HANDLERS'
]
