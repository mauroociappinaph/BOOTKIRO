"""
Core functionality for the Telegram bot.
"""
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from personal_automation_bot.config import settings
from personal_automation_bot.bot.commands.basic import (
    start_command,
    help_command,
    menu_command
)
from personal_automation_bot.bot.commands.auth import auth_command
from personal_automation_bot.bot.commands.email import email_command
from personal_automation_bot.bot.commands.callbacks import handle_callback_query
from personal_automation_bot.bot.commands.messages import handle_message
from personal_automation_bot.bot.conversations.calendar_conversation import get_calendar_conversation_handler
from personal_automation_bot.bot.commands.rag import rag_command, rag_help, get_rag_conversation_handler

logger = logging.getLogger(__name__)

def setup_bot(token=None):
    """
    Set up and configure the Telegram bot.

    Args:
        token (str, optional): The Telegram bot token. If not provided,
                              it will be read from the settings.

    Returns:
        telegram.ext.Application: The configured bot application.
    """
    # Get the token from settings if not provided
    if token is None:
        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            raise ValueError(
                "Telegram bot token not provided. Set the TELEGRAM_BOT_TOKEN "
                "environment variable or pass the token as an argument."
            )

    # Create the Application and pass it the bot's token
    application = Application.builder().token(token).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("auth", auth_command))
    application.add_handler(CommandHandler("email", email_command))
    application.add_handler(CommandHandler("raghelp", rag_help))

    # Register conversation handlers
    application.add_handler(get_calendar_conversation_handler())
    application.add_handler(get_rag_conversation_handler())

    # Register callback query handler for inline keyboards
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # Register message handler for conversations
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Register message handler for unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Register error handler
    application.add_error_handler(error_handler)

    logger.info("Bot setup completed")
    return application

async def unknown_command(update, context):
    """
    Handler for unknown commands.
    Responds to unknown commands with a helpful message.
    """
    await update.message.reply_text(
        "Lo siento, no reconozco ese comando. "
        "Usa /help para ver los comandos disponibles o /menu para ver el menú principal."
    )

async def error_handler(update, context):
    """
    Handler for bot errors.
    Logs errors caused by updates.
    """
    logger.error(f"Update {update} caused error {context.error}")
    # Notify user of error if possible
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Lo siento, ha ocurrido un error al procesar tu solicitud. "
            "Por favor, intenta de nuevo más tarde."
        )
