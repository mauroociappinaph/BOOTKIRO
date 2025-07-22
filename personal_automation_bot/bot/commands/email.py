"""
Email command handlers for the Telegram bot.

This module handles all email-related commands and interactions.
"""

import logging
from typing import List, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from personal_automation_bot.services.email import EmailService

logger = logging.getLogger(__name__)

# Conversation states
EMAIL_MENU, EMAIL_AUTH, EMAIL_LIST, EMAIL_DETAILS, EMAIL_SEARCH = range(5)

# Initialize email service
email_service = EmailService()


async def email_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Main email command handler.
    Shows the email management menu.
    """
    user_id = str(update.effective_user.id)

    # Check if user is authenticated
    is_authenticated = email_service.is_user_authenticated(user_id)

    keyboard = []

    if is_authenticated:
        keyboard.extend([
            [InlineKeyboardButton("📧 Ver correos recientes", callback_data="email_list_recent")],
            [InlineKeyboardButton("🔍 Buscar correos", callback_data="email_search")],
            [InlineKeyboardButton("✉️ Enviar correo", callback_data="email_send")],
            [InlineKeyboardButton("👤 Ver perfil", callback_data="email_profile")],
            [InlineKeyboardButton("🔓 Cerrar sesión", callback_data="email_logout")]
        ])
    else:
        keyboard.append([InlineKeyboardButton("🔐 Autenticar con Gmail", callback_data="email_auth")])

    keyboard.append([InlineKeyboardButton("🔙 Volver al menú", callback_data="main_menu")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = "📧 **Gestión de Correo Electrónico**\n\n"

    if is_authenticated:
        message_text += "✅ Autenticado con Gmail\n\nSelecciona una opción:"
    else:
        message_text += "❌ No autenticado\n\nPrimero necesitas autenticarte con Gmail para usar las funciones de correo."

    if update.callback_query:
        await update.callback_query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    return EMAIL_MENU


async def handle_email_auth(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle email authentication."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)

    # Show authentication instructions
    auth_text = """🔐 **Autenticación con Gmail**

Para autenticarte con Gmail, necesitas seguir estos pasos:

1. **Configurar Google Cloud Console** (solo la primera vez)
2. **Autorizar la aplicación** en tu navegador
3. **Confirmar permisos** para Gmail

⚠️ **Nota**: La autenticación se realiza de forma segura usando OAuth 2.0 de Google.

¿Quieres continuar con la autenticación?"""

    keyboard = [
        [InlineKeyboardButton("✅ Sí, autenticar", callback_data="email_auth_start")],
        [InlineKeyboardButton("❌ Cancelar", callback_data="email_menu")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        auth_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    return EMAIL_AUTH


async def handle_email_auth_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the email authentication process."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)

    # Show loading message
    await query.edit_message_text("🔄 Iniciando autenticación con Gmail...")

    try:
        # Attempt authentication
        success, message = email_service.authenticate_user(user_id)

        if success:
            # Authentication successful
            keyboard = [[InlineKeyboardButton("📧 Ir a correos", callback_data="email_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"🎉 **¡Autenticación exitosa!**\n\n{message}\n\nYa puedes usar todas las funciones de correo.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            # Authentication failed
            keyboard = [
                [InlineKeyboardButton("🔄 Reintentar", callback_data="email_auth_start")],
                [InlineKeyboardButton("🔙 Volver", callback_data="email_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"❌ **Error de autenticación**\n\n{message}\n\n**Posibles soluciones:**\n• Verifica tu configuración de Google Cloud Console\n• Asegúrate de que el archivo credentials.json esté presente\n• Revisa que las URIs de redirección estén configuradas correctamente",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    except Exception as e:
        logger.error(f"Error during authentication for user {user_id}: {e}")

        keyboard = [
            [InlineKeyboardButton("🔄 Reintentar", callback_data="email_auth_start")],
            [InlineKeyboardButton("🔙 Volver", callback_data="email_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"❌ **Error técnico**\n\nOcurrió un error durante la autenticación: {str(e)}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    return EMAIL_MENU


async def handle_email_list_recent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle listing recent emails."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)

    # Show loading message
    await query.edit_message_text("🔄 Obteniendo correos recientes...")

    try:
        # Get recent emails
        success, emails, message = email_service.get_recent_emails(user_id, count=10)

        if not success:
            keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="email_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"❌ **Error**\n\n{message}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return EMAIL_MENU

        if not emails:
            keyboard = [
                [InlineKeyboardButton("🔄 Actualizar", callback_data="email_list_recent")],
                [InlineKeyboardButton("🔙 Volver", callback_data="email_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "📭 **No hay correos recientes**\n\nNo se encontraron correos en tu bandeja de entrada.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return EMAIL_MENU

        # Store emails in context for pagination
        context.user_data['emails'] = emails
        context.user_data['current_page'] = 0

        # Show first page
        await show_email_page(query, context, 0)

        return EMAIL_LIST

    except Exception as e:
        logger.error(f"Error getting recent emails for user {user_id}: {e}")

        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="email_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"❌ **Error técnico**\n\nOcurrió un error al obtener los correos: {str(e)}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return EMAIL_MENU


async def show_email_page(query, context: ContextTypes.DEFAULT_TYPE, page: int):
    """Show a page of emails with pagination."""
    emails = context.user_data.get('emails', [])
    emails_per_page = 5
    total_pages = (len(emails) + emails_per_page - 1) // emails_per_page

    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1

    start_idx = page * emails_per_page
    end_idx = min(start_idx + emails_per_page, len(emails))
    page_emails = emails[start_idx:end_idx]

    # Build message text
    message_text = f"📧 **Correos Recientes** (Página {page + 1}/{total_pages})\n\n"

    keyboard = []

    # Add email buttons
    for i, email in enumerate(page_emails):
        email_idx = start_idx + i
        subject = email.get('subject', 'Sin asunto')
        if len(subject) > 40:
            subject = subject[:37] + "..."

        sender = email.get('sender', 'Desconocido')
        if len(sender) > 30:
            sender = sender[:27] + "..."

        button_text = f"📧 {subject}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"email_details_{email_idx}")])

        # Add summary to message
        formatted_email = email_service.format_email_summary(email)
        message_text += f"**{i + 1}.** {formatted_email}\n\n"

    # Add pagination buttons
    pagination_row = []
    if page > 0:
        pagination_row.append(InlineKeyboardButton("⬅️ Anterior", callback_data=f"email_page_{page - 1}"))
    if page < total_pages - 1:
        pagination_row.append(InlineKeyboardButton("➡️ Siguiente", callback_data=f"email_page_{page + 1}"))

    if pagination_row:
        keyboard.append(pagination_row)

    # Add action buttons
    keyboard.extend([
        [InlineKeyboardButton("🔄 Actualizar", callback_data="email_list_recent")],
        [InlineKeyboardButton("🔙 Volver", callback_data="email_menu")]
    ])

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data['current_page'] = page

    await query.edit_message_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def handle_email_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle email pagination."""
    query = update.callback_query
    await query.answer()

    # Extract page number from callback data
    page = int(query.data.split('_')[-1])

    await show_email_page(query, context, page)
    return EMAIL_LIST


async def handle_email_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle showing email details."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)

    # Extract email index from callback data
    email_idx = int(query.data.split('_')[-1])
    emails = context.user_data.get('emails', [])

    if email_idx >= len(emails):
        await query.edit_message_text("❌ Correo no encontrado.")
        return EMAIL_LIST

    email = emails[email_idx]

    # Show loading message
    await query.edit_message_text("🔄 Cargando detalles del correo...")

    try:
        # Get detailed email information
        success, email_details, message = email_service.get_email_details(user_id, email['id'])

        if not success or not email_details:
            keyboard = [[InlineKeyboardButton("🔙 Volver a la lista", callback_data=f"email_page_{context.user_data.get('current_page', 0)}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"❌ **Error**\n\n{message}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return EMAIL_LIST

        # Format email details
        formatted_details = email_service.format_email_details(email_details)

        # Create action buttons
        keyboard = [
            [InlineKeyboardButton("✅ Marcar como leído", callback_data=f"email_mark_read_{email['id']}")],
            [InlineKeyboardButton("↩️ Responder", callback_data=f"email_reply_{email['id']}")],
            [InlineKeyboardButton("🔙 Volver a la lista", callback_data=f"email_page_{context.user_data.get('current_page', 0)}")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            formatted_details,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

        return EMAIL_DETAILS

    except Exception as e:
        logger.error(f"Error getting email details for user {user_id}: {e}")

        keyboard = [[InlineKeyboardButton("🔙 Volver a la lista", callback_data=f"email_page_{context.user_data.get('current_page', 0)}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"❌ **Error técnico**\n\nOcurrió un error al obtener los detalles: {str(e)}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return EMAIL_LIST


async def handle_email_mark_read(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle marking email as read."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)

    # Extract email ID from callback data
    email_id = query.data.split('_')[-1]

    try:
        # Mark email as read
        success, message = email_service.mark_email_as_read(user_id, email_id)

        if success:
            await query.answer("✅ Correo marcado como leído", show_alert=True)
        else:
            await query.answer(f"❌ Error: {message}", show_alert=True)

    except Exception as e:
        logger.error(f"Error marking email as read for user {user_id}: {e}")
        await query.answer(f"❌ Error técnico: {str(e)}", show_alert=True)

    return EMAIL_DETAILS


async def handle_email_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle showing email profile information."""
    query = update.callback_query
    await query.answer()

    user_id = str(update.effective_user.id)

    # Show loading message
    await query.edit_message_text("🔄 Obteniendo información del perfil...")

    try:
        # Get profile information
        success, profile, message = email_service.get_user_profile(user_id)

        if not success or not profile:
            keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="email_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"❌ **Error**\n\n{message}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return EMAIL_MENU

        # Format profile information
        profile_text = f"""👤 **Perfil de Gmail**

📧 **Email:** {profile['email']}
📊 **Total de mensajes:** {profile['messages_total']:,}
🧵 **Total de conversaciones:** {profile['threads_total']:,}
🆔 **ID de historial:** {profile['history_id']}

✅ **Estado:** Conectado y funcionando"""

        keyboard = [
            [InlineKeyboardButton("🔄 Actualizar", callback_data="email_profile")],
            [InlineKeyboardButton("🔙 Volver", callback_data="email_menu")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            profile_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

        return EMAIL_MENU

    except Exception as e:
        logger.error(f"Error getting profile for user {user_id}: {e}")

        keyboard = [[InlineKeyboardButton("🔙 Volver", callback_data="email_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"❌ **Error técnico**\n\nOcurrió un error al obtener el perfil: {str(e)}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return EMAIL_MENU


# Callback handlers mapping
EMAIL_CALLBACK_HANDLERS = {
    'email_menu': email_command,
    'email_auth': handle_email_auth,
    'email_auth_start': handle_email_auth_start,
    'email_list_recent': handle_email_list_recent,
    'email_profile': handle_email_profile,
}


def get_email_callback_handler(callback_data: str):
    """Get the appropriate callback handler for email-related callbacks."""

    # Handle pagination callbacks
    if callback_data.startswith('email_page_'):
        return handle_email_page

    # Handle email details callbacks
    if callback_data.startswith('email_details_'):
        return handle_email_details

    # Handle mark as read callbacks
    if callback_data.startswith('email_mark_read_'):
        return handle_email_mark_read

    # Handle direct callbacks
    return EMAIL_CALLBACK_HANDLERS.get(callback_data)
