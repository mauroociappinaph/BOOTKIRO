"""
Authentication command handlers for the Telegram bot.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from personal_automation_bot.utils.auth import google_auth_manager
from personal_automation_bot.bot.keyboards.main_menu import get_back_keyboard

logger = logging.getLogger(__name__)

async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /auth command.
    Shows authentication status and options.
    """
    user_id = update.effective_user.id

    # Get authentication status
    auth_status = google_auth_manager.get_auth_status_summary(user_id)

    if auth_status['authenticated']:
        # User is authenticated
        status_text = (
            "🔐 **Estado de Autenticación**\n\n"
            f"✅ **Estado:** {auth_status['status']}\n"
            f"📅 **Autenticado desde:** {auth_status.get('created_at', 'N/A')[:10] if auth_status.get('created_at') else 'N/A'}\n"
            f"⏰ **Expira:** {auth_status.get('expires_at', 'N/A')[:10] if auth_status.get('expires_at') else 'N/A'}\n\n"
            f"🔧 **Servicios disponibles:**\n"
            f"• 📧 Gmail\n"
            f"• 📅 Google Calendar\n"
            f"• 📁 Google Drive\n\n"
            f"Puedes revocar la autenticación usando el botón de abajo."
        )

        keyboard = [
            [InlineKeyboardButton("🚫 Revocar Autenticación", callback_data="auth_revoke")],
            [InlineKeyboardButton("🔙 Volver al menú", callback_data="back_to_main")]
        ]

    else:
        # User is not authenticated
        status_text = (
            "🔐 **Estado de Autenticación**\n\n"
            f"❌ **Estado:** No autenticado\n\n"
            f"Para usar las funcionalidades de Gmail, Calendar y Drive, "
            f"necesitas autenticarte con Google.\n\n"
            f"🔒 **Seguridad:**\n"
            f"• Tus tokens se almacenan de forma encriptada\n"
            f"• Solo solicito permisos mínimos necesarios\n"
            f"• Puedes revocar el acceso en cualquier momento\n\n"
            f"Haz clic en 'Autenticar' para comenzar."
        )

        keyboard = [
            [InlineKeyboardButton("🔑 Autenticar con Google", callback_data="auth_start")],
            [InlineKeyboardButton("🔙 Volver al menú", callback_data="back_to_main")]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        status_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_auth_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> None:
    """
    Handle authentication-related callback queries.

    Args:
        update: The update object.
        context: The context object.
        callback_data: The callback data string.
    """
    query = update.callback_query
    user_id = update.effective_user.id

    await query.answer()

    if callback_data == "auth_start":
        await start_authentication(query, user_id)
    elif callback_data == "auth_revoke":
        await revoke_authentication(query, user_id)
    elif callback_data == "auth_confirm_revoke":
        await confirm_revoke_authentication(query, user_id)

async def start_authentication(query, user_id: int):
    """Start the Google OAuth authentication process."""
    try:
        # Start OAuth flow
        auth_url, state = google_auth_manager.start_auth_flow(user_id)

        text = (
            "🔑 **Autenticación con Google**\n\n"
            f"Para autenticarte, sigue estos pasos:\n\n"
            f"1️⃣ Haz clic en el enlace de abajo\n"
            f"2️⃣ Inicia sesión con tu cuenta de Google\n"
            f"3️⃣ Autoriza los permisos solicitados\n"
            f"4️⃣ Copia el código de autorización\n"
            f"5️⃣ Envíamelo como mensaje\n\n"
            f"🔗 **Enlace de autenticación:**\n"
            f"[Hacer clic aquí para autenticar]({auth_url})\n\n"
            f"⚠️ **Importante:** Este enlace expira en 1 hora."
        )

        keyboard = [
            [InlineKeyboardButton("🔙 Cancelar", callback_data="back_to_main")]
        ]

        await query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    except ValueError as e:
        error_text = (
            "❌ **Error de Configuración**\n\n"
            f"No se pudo iniciar la autenticación: {str(e)}\n\n"
            f"Por favor, contacta al administrador del bot."
        )

        await query.edit_message_text(
            text=error_text,
            reply_markup=get_back_keyboard(),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Failed to start authentication for user {user_id}: {e}")

        error_text = (
            "❌ **Error**\n\n"
            f"Ocurrió un error al iniciar la autenticación.\n"
            f"Por favor, intenta de nuevo más tarde."
        )

        await query.edit_message_text(
            text=error_text,
            reply_markup=get_back_keyboard(),
            parse_mode='Markdown'
        )

async def revoke_authentication(query, user_id: int):
    """Show confirmation for revoking authentication."""
    text = (
        "🚫 **Revocar Autenticación**\n\n"
        f"¿Estás seguro de que quieres revocar la autenticación?\n\n"
        f"Esto significa que:\n"
        f"• Ya no podrás usar Gmail, Calendar ni Drive\n"
        f"• Tus tokens almacenados serán eliminados\n"
        f"• Tendrás que autenticarte de nuevo para usar estos servicios\n\n"
        f"Esta acción no se puede deshacer."
    )

    keyboard = [
        [
            InlineKeyboardButton("✅ Sí, revocar", callback_data="auth_confirm_revoke"),
            InlineKeyboardButton("❌ Cancelar", callback_data="back_to_main")
        ]
    ]

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def confirm_revoke_authentication(query, user_id: int):
    """Confirm and execute authentication revocation."""
    try:
        success = google_auth_manager.revoke_user_authentication(user_id)

        if success:
            text = (
                "✅ **Autenticación Revocada**\n\n"
                f"Tu autenticación con Google ha sido revocada exitosamente.\n\n"
                f"• Tokens eliminados de forma segura\n"
                f"• Acceso revocado en Google\n"
                f"• Ya no puedes usar Gmail, Calendar ni Drive\n\n"
                f"Puedes autenticarte de nuevo cuando lo necesites."
            )
        else:
            text = (
                "❌ **Error al Revocar**\n\n"
                f"Hubo un problema al revocar la autenticación.\n"
                f"Por favor, intenta de nuevo más tarde."
            )

        await query.edit_message_text(
            text=text,
            reply_markup=get_back_keyboard(),
            parse_mode='Markdown'
        )

    except Exception as e:
        logger.error(f"Failed to revoke authentication for user {user_id}: {e}")

        error_text = (
            "❌ **Error**\n\n"
            f"Ocurrió un error al revocar la autenticación.\n"
            f"Por favor, intenta de nuevo más tarde."
        )

        await query.edit_message_text(
            text=error_text,
            reply_markup=get_back_keyboard(),
            parse_mode='Markdown'
        )

async def handle_auth_code_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str) -> bool:
    """
    Handle potential authorization code messages.

    Args:
        update: The update object.
        context: The context object.
        message_text: The message text that might be an auth code.

    Returns:
        bool: True if message was handled as auth code, False otherwise.
    """
    user_id = update.effective_user.id

    # Check if this looks like an authorization code
    # Google auth codes are typically long alphanumeric strings
    if len(message_text) > 20 and message_text.replace('-', '').replace('_', '').isalnum():
        # Check if user has pending auth
        for state, auth_data in google_auth_manager.pending_auth.items():
            if auth_data['user_id'] == user_id:
                # Try to complete auth flow
                success = google_auth_manager.complete_auth_flow(state, message_text)

                if success:
                    success_text = (
                        "🎉 **¡Autenticación Exitosa!**\n\n"
                        f"Te has autenticado correctamente con Google.\n\n"
                        f"✅ **Servicios disponibles:**\n"
                        f"• 📧 Gmail - Leer y enviar correos\n"
                        f"• 📅 Google Calendar - Gestionar eventos\n"
                        f"• 📁 Google Drive - Gestionar archivos\n\n"
                        f"¡Ya puedes usar todas las funcionalidades!"
                    )

                    await update.message.reply_text(
                        success_text,
                        parse_mode='Markdown'
                    )
                    return True
                else:
                    error_text = (
                        "❌ **Error de Autenticación**\n\n"
                        f"El código de autorización no es válido o ha expirado.\n"
                        f"Por favor, intenta el proceso de autenticación de nuevo."
                    )

                    await update.message.reply_text(
                        error_text,
                        parse_mode='Markdown'
                    )
                    return True

    return False
