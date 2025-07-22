"""
Message handlers for conversation flows.
"""
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from personal_automation_bot.bot.conversations.base import conversation_data, ConversationState
from personal_automation_bot.bot.keyboards.main_menu import get_back_keyboard, get_main_menu_keyboard
from personal_automation_bot.bot.commands.auth import handle_auth_code_message
from personal_automation_bot.services.email import EmailService

logger = logging.getLogger(__name__)

# Initialize email service
email_service = EmailService()


def _is_valid_email(email: str) -> bool:
    """
    Validate email address with enhanced checks.

    Args:
        email: Email address to validate

    Returns:
        bool: True if valid, False otherwise
    """
    # Basic format check
    if not email or '@' not in email or '.' not in email:
        return False

    # Check for consecutive dots
    if '..' in email:
        return False

    # Check for dots at start or end of local part
    local_part = email.split('@')[0]
    if local_part.startswith('.') or local_part.endswith('.'):
        return False

    # Enhanced regex pattern
    email_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._+%-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$'

    return bool(re.match(email_pattern, email))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle text messages based on conversation state.
    """
    user_id = update.effective_user.id
    message_text = update.message.text
    current_state = conversation_data.get_user_state(user_id)

    if current_state is None:
        # Check if this might be an authorization code
        if await handle_auth_code_message(update, context, message_text):
            return

        # No active conversation, show help
        await update.message.reply_text(
            "👋 ¡Hola! Usa /start para ver el menú principal o /help para obtener ayuda.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    # Handle different conversation states
    if current_state == ConversationState.EMAIL_SEND_TO:
        await handle_email_to(update, user_id, message_text)

    elif current_state == ConversationState.EMAIL_SEND_SUBJECT:
        await handle_email_subject(update, user_id, message_text)

    elif current_state == ConversationState.EMAIL_SEND_BODY:
        await handle_email_body(update, user_id, message_text)

    elif current_state == ConversationState.CALENDAR_CREATE_TITLE:
        await handle_calendar_title(update, user_id, message_text)

    elif current_state == ConversationState.CALENDAR_CREATE_DATE:
        await handle_calendar_date(update, user_id, message_text)

    elif current_state == ConversationState.CALENDAR_CREATE_TIME:
        await handle_calendar_time(update, user_id, message_text)

    elif current_state == ConversationState.CONTENT_TEXT_PROMPT:
        await handle_text_generation(update, user_id, message_text)

    elif current_state == ConversationState.CONTENT_IMAGE_PROMPT:
        await handle_image_generation(update, user_id, message_text)

    else:
        logger.warning(f"Unknown conversation state: {current_state}")
        await update.message.reply_text(
            "Lo siento, algo salió mal. Usa /start para volver al menú principal.",
            reply_markup=get_main_menu_keyboard()
        )

async def handle_email_to(update: Update, user_id: int, message_text: str):
    """Handle email recipient input."""
    email = message_text.strip()

    if not _is_valid_email(email):
        await update.message.reply_text(
            "❌ Por favor, introduce una dirección de correo válida.\n\n"
            "Ejemplo: usuario@ejemplo.com",
            reply_markup=get_back_keyboard()
        )
        return

    # Check if user is authenticated before proceeding
    if not email_service.is_user_authenticated(str(user_id)):
        await update.message.reply_text(
            "❌ No estás autenticado con Gmail.\n\n"
            "Por favor, usa /email y autentica tu cuenta primero.",
            reply_markup=get_main_menu_keyboard()
        )
        conversation_data.clear_user_data(user_id)
        return

    conversation_data.set_user_field(user_id, "email_to", email)
    conversation_data.set_user_state(user_id, ConversationState.EMAIL_SEND_SUBJECT)

    await update.message.reply_text(
        f"✅ Destinatario: {email}\n\n"
        f"📝 Ahora escribe el asunto del correo:",
        reply_markup=get_back_keyboard()
    )

async def handle_email_subject(update: Update, user_id: int, message_text: str):
    """Handle email subject input."""
    subject = message_text.strip()

    if not subject:
        await update.message.reply_text(
            "❌ El asunto no puede estar vacío.\n\n"
            "Por favor, escribe un asunto para el correo:",
            reply_markup=get_back_keyboard()
        )
        return

    conversation_data.set_user_field(user_id, "email_subject", subject)
    conversation_data.set_user_state(user_id, ConversationState.EMAIL_SEND_BODY)

    await update.message.reply_text(
        f"✅ Asunto: {subject}\n\n"
        f"📝 Ahora escribe el contenido del correo:",
        reply_markup=get_back_keyboard()
    )

async def handle_email_body(update: Update, user_id: int, message_text: str):
    """Handle email body input and show confirmation."""
    body = message_text.strip()

    if not body:
        await update.message.reply_text(
            "❌ El contenido del correo no puede estar vacío.\n\n"
            "Por favor, escribe el contenido del correo:",
            reply_markup=get_back_keyboard()
        )
        return

    conversation_data.set_user_field(user_id, "email_body", body)
    conversation_data.set_user_state(user_id, ConversationState.EMAIL_SEND_CONFIRM)

    # Get all email data
    email_to = conversation_data.get_user_field(user_id, "email_to")
    email_subject = conversation_data.get_user_field(user_id, "email_subject")

    # Truncate long content for preview
    body_preview = body
    if len(body_preview) > 200:
        body_preview = body_preview[:197] + "..."

    confirmation_text = (
        "📧 **Confirmar envío de correo:**\n\n"
        f"**Para:** {email_to}\n"
        f"**Asunto:** {email_subject}\n"
        f"**Mensaje:** {body_preview}\n\n"
        f"¿Deseas enviar este correo?"
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Enviar", callback_data="email_confirm_send"),
            InlineKeyboardButton("❌ Cancelar", callback_data="email_cancel_send")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        confirmation_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_calendar_title(update: Update, user_id: int, message_text: str):
    """Handle calendar event title input."""
    conversation_data.set_user_field(user_id, "calendar_title", message_text)
    conversation_data.set_user_state(user_id, ConversationState.CALENDAR_CREATE_DATE)

    await update.message.reply_text(
        f"✅ Título: {message_text}\n\n"
        f"Ahora escribe la fecha del evento (formato: DD/MM/YYYY):",
        reply_markup=get_back_keyboard()
    )

async def handle_calendar_date(update: Update, user_id: int, message_text: str):
    """Handle calendar event date input."""
    # Basic date validation
    if len(message_text.split("/")) != 3:
        await update.message.reply_text(
            "❌ Por favor, usa el formato DD/MM/YYYY (ejemplo: 25/12/2024):",
            reply_markup=get_back_keyboard()
        )
        return

    conversation_data.set_user_field(user_id, "calendar_date", message_text)
    conversation_data.set_user_state(user_id, ConversationState.CALENDAR_CREATE_TIME)

    await update.message.reply_text(
        f"✅ Fecha: {message_text}\n\n"
        f"Ahora escribe la hora del evento (formato: HH:MM):",
        reply_markup=get_back_keyboard()
    )

async def handle_calendar_time(update: Update, user_id: int, message_text: str):
    """Handle calendar event time input and show confirmation."""
    # Basic time validation
    if ":" not in message_text or len(message_text.split(":")) != 2:
        await update.message.reply_text(
            "❌ Por favor, usa el formato HH:MM (ejemplo: 14:30):",
            reply_markup=get_back_keyboard()
        )
        return

    conversation_data.set_user_field(user_id, "calendar_time", message_text)

    # Get all calendar data
    calendar_title = conversation_data.get_user_field(user_id, "calendar_title")
    calendar_date = conversation_data.get_user_field(user_id, "calendar_date")

    confirmation_text = (
        "📅 **Resumen del evento:**\n\n"
        f"**Título:** {calendar_title}\n"
        f"**Fecha:** {calendar_date}\n"
        f"**Hora:** {message_text}\n\n"
        f"🚧 **Nota:** La funcionalidad de calendario estará disponible próximamente.\n\n"
        f"¡Gracias por probar el sistema! 🙏"
    )

    await update.message.reply_text(
        confirmation_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )

    # Clear conversation data
    conversation_data.clear_user_data(user_id)

async def handle_text_generation(update: Update, user_id: int, message_text: str):
    """Handle text generation request."""
    confirmation_text = (
        "📝 **Solicitud de generación de texto:**\n\n"
        f"**Prompt:** {message_text}\n\n"
        f"🚧 **Nota:** La funcionalidad de generación de contenido estará disponible próximamente.\n\n"
        f"¡Gracias por probar el sistema! 🙏"
    )

    await update.message.reply_text(
        confirmation_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )

    # Clear conversation data
    conversation_data.clear_user_data(user_id)

async def handle_image_generation(update: Update, user_id: int, message_text: str):
    """Handle image generation request."""
    confirmation_text = (
        "🎨 **Solicitud de generación de imagen:**\n\n"
        f"**Descripción:** {message_text}\n\n"
        f"🚧 **Nota:** La funcionalidad de generación de imágenes estará disponible próximamente.\n\n"
        f"¡Gracias por probar el sistema! 🙏"
    )

    await update.message.reply_text(
        confirmation_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )

    # Clear conversation data
    conversation_data.clear_user_data(user_id)
