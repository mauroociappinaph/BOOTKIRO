"""
Command handlers for the Simplified Google Bot.
"""

import logging
from simplified_google_bot.bot.commands.auth_commands import register_auth_handlers
from simplified_google_bot.bot.commands.calendar_commands import register_calendar_handlers

logger = logging.getLogger(__name__)

def register_commands():
    """Register all command handlers."""
    # Register authentication commands
    register_auth_handlers()

    # Register calendar commands
    register_calendar_handlers()

    logger.info("All command handlers registered")
