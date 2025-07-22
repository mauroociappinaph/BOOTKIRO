"""
Callback query handlers for inline keyboards.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from personal_automation_bot.bot.keyboards.main_menu import (
    get_main_menu_keyboard,
    get_email_menu_keyboard,
    get_calendar_menu_keyboard,
    get_content_menu_keyboard,
    get_back_keyboard
)
from personal_automation_bot.bot.conversations.base import conversation_data, ConversationState
from personal_automation_bot.bot.commands.auth import handle_auth_callback
from personal_automation_bot.bot.commands.email import get_email_callback_handler
from personal_automation_bot.services.email import EmailService

logger = logging.getLogger(__name__)

# Initialize email service
email_service = EmailService()

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle callback queries from inline keyboards.
    """
    query = update.callback_query
    user_id = update.effective_user.id

    # Answer the callback query to remove the loading state
    await query.answer()

    # Handle different callback data
    if query.data == "back_to_main":
        await show_main_menu(query)
        # Clear any ongoing conversation
        conversation_data.clear_user_data(user_id)

    elif query.data == "menu_email":
        # Use the new email command handler
        from personal_automation_bot.bot.commands.email import email_command
        await email_command(update, context)

    elif query.data == "menu_calendar":
        await show_calendar_menu(query)

    elif query.data == "menu_content":
        await show_content_menu(query)

    elif query.data == "menu_documents":
        await show_coming_soon(query, "📁 Documentos")

    elif query.data == "menu_social":
        await show_coming_soon(query, "📱 Redes Sociales")

    elif query.data == "menu_rag":
        await show_coming_soon(query, "🤖 RAG")

    elif query.data == "menu_flows":
        await show_coming_soon(query, "⚙️ Flujos")

    elif query.data == "menu_help":
        await show_help_menu(query)

    # Email callbacks
    elif query.data == "email_read":
        await show_coming_soon(query, "📥 Leer correos")

    elif query.data == "email_send":
        await start_email_conversation(query, user_id)

    # Calendar callbacks
    elif query.data == "calendar_view":
        await show_coming_soon(query, "📅 Ver eventos")

    elif query.data == "calendar_create":
        await start_calendar_conversation(query, user_id)

    elif query.data == "calendar_delete":
        await show_coming_soon(query, "🗑️ Eliminar evento")

    # Content callbacks
    elif query.data == "content_text":
        await start_text_generation_conversation(query, user_id)

    elif query.data == "content_image":
        await start_image_generation_conversation(query, user_id)

    # Authentication callbacks
    elif query.data.startswith("auth_"):
        await handle_auth_callback(update, context, query.data)

    # Email confirmation callbacks
    elif query.data == "email_confirm_send":
        await handle_email_confirm_send(query, user_id)

    elif query.data == "email_cancel_send":
        await handle_email_cancel_send(query, user_id)

    # Email callbacks - handle all email-related callbacks
    elif query.data.startswith("email_"):
        email_handler = get_email_callback_handler(query.data)
        if email_handler:
            await email_handler(update, context)
        else:
            logger.warning(f"Unknown email callback data: {query.data}")

    else:
        logger.warning(f"Unknown callback data: {query.data}")

async def show_main_menu(query):
    """Show the main menu."""
    text = (
        "🏠 **Menú Principal**\n\n"
        "Selecciona una opción del menú para comenzar:"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )

async def show_email_menu(query):
    """Show the email menu."""
    text = (
        "📧 **Gestión de Correo**\n\n"
        "¿Qué te gustaría hacer con tu correo?"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=get_email_menu_keyboard(),
        parse_mode='Markdown'
    )

async def show_calendar_menu(query):
    """Show the calendar menu."""
    text = (
        "📅 **Gestión de Calendario**\n\n"
        "¿Qué te gustaría hacer con tu calendario?"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=get_calendar_menu_keyboard(),
        parse_mode='Markdown'
    )

async def show_content_menu(query):
    """Show the content generation menu."""
    text = (
        "✨ **Generación de Contenido con IA**\n\n"
        "¿Qué tipo de contenido te gustaría generar?"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=get_content_menu_keyboard(),
        parse_mode='Markdown'
    )

async def show_help_menu(query):
    """Show the help information."""
    help_text = (
        "❓ **Ayuda**\n\n"
        "**Funcionalidades disponibles:**\n\n"
        "📧 **Correo** - Leer y enviar emails a través de Gmail\n"
        "📅 **Calendario** - Gestionar eventos en Google Calendar\n"
        "✨ **Contenido IA** - Generar texto e imágenes con IA\n"
        "📁 **Documentos** - Gestionar archivos en Drive/Notion\n"
        "📱 **Redes Sociales** - Publicar en redes sociales\n"
        "🤖 **RAG** - Generar contenido basado en tus documentos\n"
        "⚙️ **Flujos** - Automatizar tareas repetitivas\n\n"
        "**Comandos útiles:**\n"
        "/start - Mostrar menú principal\n"
        "/help - Mostrar ayuda\n"
        "/menu - Volver al menú principal\n\n"
        "💡 **Tip:** Usa los botones para navegar fácilmente."
    )

    await query.edit_message_text(
        text=help_text,
        reply_markup=get_back_keyboard(),
        parse_mode='Markdown'
    )

async def show_coming_soon(query, feature_name):
    """Show a coming soon message for features not yet implemented."""
    text = (
        f"🚧 **{feature_name}**\n\n"
        f"Esta funcionalidad estará disponible próximamente.\n\n"
        f"¡Gracias por tu paciencia! 🙏"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=get_back_keyboard(),
        parse_mode='Markdown'
    )

async def start_email_conversation(query, user_id):
    """Start the email sending conversation."""
    conversation_data.set_user_state(user_id, ConversationState.EMAIL_SEND_TO)

    text = (
        "📤 **Enviar Correo**\n\n"
        "Por favor, escribe la dirección de correo del destinatario:"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=get_back_keyboard(),
        parse_mode='Markdown'
    )

async def start_calendar_conversation(query, user_id):
    """Start the calendar event creation conversation."""
    conversation_data.set_user_state(user_id, ConversationState.CALENDAR_CREATE_TITLE)

    text = (
        "➕ **Crear Evento**\n\n"
        "Por favor, escribe el título del evento:"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=get_back_keyboard(),
        parse_mode='Markdown'
    )

async def start_text_generation_conversation(query, user_id):
    """Start the text generation conversation."""
    conversation_data.set_user_state(user_id, ConversationState.CONTENT_TEXT_PROMPT)

    text = (
        "📝 **Generar Texto**\n\n"
        "Por favor, describe qué tipo de texto quieres generar:"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=get_back_keyboard(),
        parse_mode='Markdown'
    )

async def start_image_generation_conversation(query, user_id):
    """Start the image generation conversation."""
    conversation_data.set_user_state(user_id, ConversationState.CONTENT_IMAGE_PROMPT)

    text = (
        "🎨 **Generar Imagen**\n\n"
        "Por favor, describe la imagen que quieres generar:"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=get_back_keyboard(),
        parse_mode='Markdown'
    )

async def handle_email_confirm_send(query, user_id):
    """Handle email send confirmation."""
    # Get email data from conversation
    email_to = conversation_data.get_user_field(user_id, "email_to")
    email_subject = conversation_data.get_user_field(user_id, "email_subject")
    email_body = conversation_data.get_user_field(user_id, "email_body")

    if not all([email_to, email_subject, email_body]):
        await query.edit_message_text(
            "❌ **Error**\n\nFaltan datos del correo. Por favor, inicia el proceso nuevamente.",
            reply_markup=get_main_menu_keyboard(),
            parse_mode='Markdown'
        )
        conversation_data.clear_user_data(user_id)
        return

    # Show sending message
    await query.edit_message_text(
        "📤 **Enviando correo...**\n\nPor favor, espera un momento.",
        parse_mode='Markdown'
    )

    try:
        # Send the email
        success, message = email_service.send_email(str(user_id), email_to, email_subject, email_body)

        if success:
            result_text = (
                "✅ **¡Correo enviado exitosamente!**\n\n"
                f"**Para:** {email_to}\n"
                f"**Asunto:** {email_subject}\n\n"
                f"{message}"
            )
        else:
            result_text = (
                "❌ **Error al enviar correo**\n\n"
                f"{message}\n\n"
                "Por favor, verifica tu autenticación y conexión a internet."
            )

        await query.edit_message_text(
            result_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Error sending email for user {user_id}: {e}")
        await query.edit_message_text(
            f"❌ **Error técnico**\n\nOcurrió un error al enviar el correo: {str(e)}",
            reply_markup=get_main_menu_keyboard(),
            parse_mode='Markdown'
        )

    # Clear conversation data
    conversation_data.clear_user_data(user_id)

async def handle_email_cancel_send(query, user_id):
    """Handle email send cancellation."""
    await query.edit_message_text(
        "❌ **Envío cancelado**\n\nEl correo no fue enviado.",
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )

    # Clear conversation data
    conversation_data.clear_user_data(user_id)
