"""
Authentication command handlers for the Simplified Google Bot.
"""

import logging
from typing import Dict, Any
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from simplified_google_bot.utils.auth import google_auth_manager
from simplified_google_bot.bot.core import register_command, register_conversation

# Set up logger
logger = logging.getLogger(__name__)

# Conversation states
AUTH_START, AUTH_CODE, AUTH_CONFIRM = range(3)

# Callback data patterns
AUTH_CALLBACK_PATTERN = r"auth_(.+)"


async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the /auth command to start the authentication process.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    user = update.effective_user
    user_id = user.id

    # Check if user is already authenticated
    if google_auth_manager.is_user_authenticated(user_id):
        # Show auth status and options
        auth_status = google_auth_manager.get_auth_status_summary(user_id)

        keyboard = [
            [InlineKeyboardButton("Refresh Authentication", callback_data="auth_refresh")],
            [InlineKeyboardButton("Revoke Access", callback_data="auth_revoke")],
            [InlineKeyboardButton("Cancel", callback_data="auth_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"You are already authenticated with Google.\n\n"
            f"Status: {auth_status['status']}\n"
            f"Expires: {auth_status.get('expires_at', 'Unknown')}\n\n"
            f"What would you like to do?",
            reply_markup=reply_markup
        )
        return AUTH_CONFIRM

    # Start new authentication flow
    try:
        auth_url, state = google_auth_manager.start_auth_flow(user_id)

        # Store state in user data
        context.user_data["auth_state"] = state

        keyboard = [
            [InlineKeyboardButton("Authenticate with Google", url=auth_url)],
            [InlineKeyboardButton("Cancel", callback_data="auth_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Please authenticate with Google to use this bot.\n\n"
            "1. Click the button below to open Google authentication\n"
            "2. Grant the requested permissions\n"
            "3. Copy the authorization code from the redirect page\n"
            "4. Paste the code here\n\n"
            "The code will look something like: 4/0AY0e-g6_DLJ8j5xhqT...",
            reply_markup=reply_markup
        )
        return AUTH_CODE

    except Exception as e:
        logger.error(f"Failed to start auth flow for user {user_id}: {e}")
        await update.message.reply_text(
            "Sorry, there was an error starting the authentication process. "
            "Please try again later or contact the administrator."
        )
        return ConversationHandler.END


async def auth_code_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the authorization code input.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    user = update.effective_user
    user_id = user.id
    auth_code = update.message.text.strip()

    # Get state from user data
    state = context.user_data.get("auth_state")
    if not state:
        await update.message.reply_text(
            "Authentication session expired. Please start again with /auth."
        )
        return ConversationHandler.END

    # Complete the auth flow
    await update.message.reply_text("Processing your authentication code...")

    success = google_auth_manager.complete_auth_flow(state, auth_code)

    if success:
        await update.message.reply_text(
            "✅ Authentication successful! You can now use Google services.\n\n"
            "Available commands:\n"
            "/calendar - Manage your Google Calendar\n"
            "/email - Manage your Gmail\n"
            "/drive - Manage your Google Drive"
        )
    else:
        await update.message.reply_text(
            "❌ Authentication failed. Please try again with /auth.\n\n"
            "Make sure you're copying the entire authorization code correctly."
        )

    # Clean up user data
    if "auth_state" in context.user_data:
        del context.user_data["auth_state"]

    return ConversationHandler.END


async def auth_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle authentication-related callback queries.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id

    # Extract action from callback data
    match = re.match(AUTH_CALLBACK_PATTERN, query.data)
    if not match:
        return ConversationHandler.END

    action = match.group(1)

    if action == "cancel":
        await query.edit_message_text("Authentication process cancelled.")
        return ConversationHandler.END

    elif action == "refresh":
        # Force token refresh
        credentials = google_auth_manager.get_user_credentials(user_id)
        if credentials and credentials.valid:
            await query.edit_message_text("Authentication refreshed successfully.")
        else:
            await query.edit_message_text(
                "Failed to refresh authentication. Please try authenticating again with /auth."
            )
        return ConversationHandler.END

    elif action == "revoke":
        # Show confirmation
        keyboard = [
            [InlineKeyboardButton("Yes, revoke access", callback_data="auth_confirm_revoke")],
            [InlineKeyboardButton("No, keep access", callback_data="auth_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "Are you sure you want to revoke Google access?\n\n"
            "You'll need to authenticate again to use Google services.",
            reply_markup=reply_markup
        )
        return AUTH_CONFIRM

    elif action == "confirm_revoke":
        # Revoke authentication
        success = google_auth_manager.revoke_user_authentication(user_id)

        if success:
            await query.edit_message_text(
                "✅ Google access has been revoked successfully.\n\n"
                "Use /auth to authenticate again when needed."
            )
        else:
            await query.edit_message_text(
                "❌ Failed to revoke Google access. Please try again later."
            )
        return ConversationHandler.END

    return AUTH_CONFIRM


async def auth_timeout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle conversation timeout.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    user_id = update.effective_user.id
    await update.message.reply_text(
        "Authentication process timed out. Please start again with /auth if needed."
    )

    # Clean up user data
    if "auth_state" in context.user_data:
        del context.user_data["auth_state"]

    return ConversationHandler.END


async def auth_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /auth_status command to check authentication status.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object
    """
    user = update.effective_user
    user_id = user.id

    auth_status = google_auth_manager.get_auth_status_summary(user_id)

    if auth_status["authenticated"]:
        scopes = auth_status.get("scopes", [])
        scope_text = "\n".join([f"- {scope}" for scope in scopes]) if scopes else "No scopes"

        await update.message.reply_text(
            f"✅ You are authenticated with Google.\n\n"
            f"Status: {auth_status['status']}\n"
            f"Expires: {auth_status.get('expires_at', 'Unknown')}\n"
            f"Created: {auth_status.get('created_at', 'Unknown')}\n"
            f"Updated: {auth_status.get('updated_at', 'Unknown')}\n\n"
            f"Authorized scopes:\n{scope_text}\n\n"
            f"Use /auth to manage your authentication."
        )
    else:
        await update.message.reply_text(
            "❌ You are not authenticated with Google.\n\n"
            "Use /auth to start the authentication process."
        )


async def auth_logout_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /logout command to revoke authentication.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object
    """
    user = update.effective_user
    user_id = user.id

    if not google_auth_manager.is_user_authenticated(user_id):
        await update.message.reply_text(
            "You are not currently authenticated with Google."
        )
        return

    keyboard = [
        [InlineKeyboardButton("Yes, log out", callback_data="auth_confirm_revoke")],
        [InlineKeyboardButton("No, stay logged in", callback_data="auth_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Are you sure you want to log out from Google?\n\n"
        "You'll need to authenticate again to use Google services.",
        reply_markup=reply_markup
    )


def register_auth_handlers():
    """Register authentication command handlers."""
    # Register simple commands
    register_command("auth_status", auth_status_command, "Check your Google authentication status")
    register_command("logout", auth_logout_command, "Log out from Google")

    # Register auth conversation handler
    auth_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("auth", auth_command)],
        states={
            AUTH_START: [
                CallbackQueryHandler(auth_callback_handler, pattern=AUTH_CALLBACK_PATTERN)
            ],
            AUTH_CODE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, auth_code_handler),
                CallbackQueryHandler(auth_callback_handler, pattern=AUTH_CALLBACK_PATTERN)
            ],
            AUTH_CONFIRM: [
                CallbackQueryHandler(auth_callback_handler, pattern=AUTH_CALLBACK_PATTERN)
            ],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        conversation_timeout=300,  # 5 minutes timeout
    )

    register_conversation("auth", auth_conv_handler)

    # Register standalone callback handler for auth callbacks outside conversation
    register_command("auth_callback", auth_callback_handler)

    logger.info("Registered authentication command handlers")
