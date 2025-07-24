"""
Conversation handlers for the Simplified Google Bot.
"""

import logging
from typing import Dict, Any, List, Callable, Optional

from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Set up logger
logger = logging.getLogger(__name__)


class BaseConversation:
    """
    Base class for conversation handlers.
    """

    # Define conversation states
    STATES = {}

    # Entry points for the conversation
    ENTRY_POINTS = []

    # Fallback handlers
    FALLBACKS = []

    def __init__(self, name: str):
        """
        Initialize the conversation.

        Args:
            name (str): Conversation name
        """
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

    def get_handler(self) -> ConversationHandler:
        """
        Get the conversation handler.

        Returns:
            ConversationHandler: The configured conversation handler
        """
        return ConversationHandler(
            entry_points=self.ENTRY_POINTS,
            states=self.STATES,
            fallbacks=self.FALLBACKS,
            name=self.name,
        )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """
        Cancel the conversation.

        Args:
            update (Update): The update object
            context (ContextTypes.DEFAULT_TYPE): The context object

        Returns:
            int: ConversationHandler.END
        """
        user = update.effective_user
        self.logger.info(f"User {user.id} canceled the conversation")

        await update.message.reply_text(
            "Conversation canceled. What would you like to do next?"
        )

        return ConversationHandler.END


def register_conversation(conversation: BaseConversation) -> None:
    """
    Register a conversation handler with the bot application.

    Args:
        conversation (BaseConversation): The conversation instance
    """
    from simplified_google_bot.bot.core import register_conversation

    handler = conversation.get_handler()
    register_conversation(conversation.name, handler)
    logger.info(f"Registered conversation: {conversation.name}")
