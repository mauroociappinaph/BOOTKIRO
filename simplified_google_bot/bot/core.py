"""
Core bot functionality for the Simplified Google Bot.
"""

import logging
from typing import Dict, List, Optional, Callable, Any

from telegram import Update, Bot, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from simplified_google_bot.config import settings
from simplified_google_bot.bot.commands import register_commands

# Set up logger
logger = logging.getLogger(__name__)

# Dictionary to store registered command handlers
_command_handlers: Dict[str, CommandHandler] = {}

# Dictionary to store registered conversation handlers
_conversation_handlers: Dict[str, ConversationHandler] = {}

# Dictionary to store callback query handlers
_callback_handlers: Dict[str, CallbackQueryHandler] = {}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object
    """
    user = update.effective_user
    await update.message.reply_text(
        f"Hello {user.first_name}! I'm your Simplified Google Bot. "
        f"I can help you manage your Google Calendar, Gmail, and Drive. "
        f"Type /help to see available commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object
    """
    help_text = (
        "Available commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/auth - Authenticate with Google\n"
        "/calendar - Manage your Google Calendar\n"
        "/email - Manage your Gmail\n"
        "/drive - Manage your Google Drive\n"
    )
    await update.message.reply_text(help_text)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle unknown commands.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object
    """
    await update.message.reply_text(
        "Sorry, I don't understand that command. Type /help to see available commands."
    )


def register_command(name: str, handler: Callable, help_text: str = "") -> None:
    """
    Register a command handler.

    Args:
        name (str): Command name without the leading slash
        handler (Callable): Command handler function
        help_text (str, optional): Help text for the command
    """
    _command_handlers[name] = CommandHandler(name, handler)
    logger.info(f"Registered command handler: /{name}")


def register_conversation(name: str, handler: ConversationHandler) -> None:
    """
    Register a conversation handler.

    Args:
        name (str): Conversation name
        handler (ConversationHandler): Conversation handler
    """
    _conversation_handlers[name] = handler
    logger.info(f"Registered conversation handler: {name}")


def register_callback(pattern: str, handler: Callable) -> None:
    """
    Register a callback query handler.

    Args:
        pattern (str): Regex pattern to match callback data
        handler (Callable): Callback handler function
    """
    _callback_handlers[pattern] = CallbackQueryHandler(handler, pattern=pattern)
    logger.info(f"Registered callback handler for pattern: {pattern}")


async def setup_commands(bot: Bot) -> None:
    """
    Set up bot commands for the command menu.

    Args:
        bot (Bot): The bot instance
    """
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help information"),
        BotCommand("auth", "Authenticate with Google"),
        BotCommand("calendar", "Manage your Google Calendar"),
        BotCommand("email", "Manage your Gmail"),
        BotCommand("drive", "Manage your Google Drive"),
    ]

    await bot.set_my_commands(commands)
    logger.info("Bot commands have been set up")


def setup_bot() -> Application:
    """
    Set up the Telegram bot application.

    Returns:
        Application: The configured bot application
    """
    # Validate bot token
    if not settings.BOT_TOKEN:
        raise ValueError("Telegram bot token is not set. Please set the TELEGRAM_BOT_TOKEN environment variable.")

    # Create the application
    application = Application.builder().token(settings.BOT_TOKEN).build()

    # Register built-in command handlers
    register_command("start", start_command, "Start the bot")
    register_command("help", help_command, "Show help information")

    # Register all command handlers from the commands module
    register_commands()

    # Add command handlers to the application
    for name, handler in _command_handlers.items():
        application.add_handler(handler)

    # Add conversation handlers to the application
    for name, handler in _conversation_handlers.items():
        application.add_handler(handler)

    # Add callback query handlers to the application
    for pattern, handler in _callback_handlers.items():
        application.add_handler(handler)

    # Add unknown command handler
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Set up error handler
    application.add_error_handler(error_handler)

    # Set up bot commands
    application.post_init = setup_commands

    logger.info("Bot application has been set up")
    return application


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors in the bot.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object
    """
    logger.error(f"Update {update} caused error: {context.error}")

    # Send error message to user if possible
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, an error occurred while processing your request. Please try again later."
        )


def run_bot(application: Application) -> None:
    """
    Run the Telegram bot.

    Args:
        application (Application): The configured bot application
    """
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
