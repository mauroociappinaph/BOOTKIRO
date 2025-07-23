"""
Basic command handlers for the Telegram bot.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes
from personal_automation_bot.bot.keyboards.main_menu import get_main_menu_keyboard

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /start command.
    Sends a welcome message with the main menu when the command /start is issued.
    """
    user = update.effective_user
    welcome_text = (
        f"¡Hola {user.first_name}! 👋\n\n"
        f"Soy tu **Asistente de Automatización Personal**. "
        f"Estoy aquí para ayudarte con tus tareas de productividad y creación de contenido.\n\n"
        f"Puedes usar los botones del menú para navegar por las diferentes funcionalidades:"
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /help command.
    Sends a message with available commands and features.
    """
    help_text = (
        "🤖 **Asistente de Automatización Personal**\n\n"
        "**Comandos disponibles:**\n"
        "/start - Iniciar el bot y mostrar menú principal\n"
        "/help - Mostrar esta ayuda\n"
        "/menu - Mostrar menú principal\n"
        "/auth - Gestionar autenticación con Google\n"
        "/calendar - Gestionar eventos de calendario\n"
        "/email - Gestionar correos electrónicos\n"
        "/rag - Hacer preguntas sobre tus documentos (RAG)\n"
        "/raghelp - Mostrar ayuda sobre el sistema RAG\n\n"
        "**Funcionalidades:**\n"
        "📧 **Correo** - Leer y enviar emails\n"
        "📅 **Calendario** - Ver, crear, actualizar y eliminar eventos\n"
        "✨ **Contenido IA** - Generar texto e imágenes\n"
        "📁 **Documentos** - Gestionar archivos\n"
        "📱 **Redes Sociales** - Publicar contenido\n"
        "🤖 **RAG** - Hacer preguntas sobre tus documentos personales\n"
        "⚙️ **Flujos** - Automatizar tareas\n\n"
        "**Calendario - Funciones disponibles:**\n"
        "• Ver eventos próximos, de hoy o de la semana\n"
        "• Crear nuevos eventos con fechas flexibles\n"
        "• Actualizar eventos existentes\n"
        "• Eliminar eventos con confirmación\n"
        "• Buscar eventos por texto\n\n"
        "Usa los botones del menú para navegar fácilmente por todas las opciones."
    )

    await update.message.reply_text(
        help_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for the /menu command.
    Shows the main menu.
    """
    menu_text = (
        "🏠 **Menú Principal**\n\n"
        "Selecciona una opción del menú para comenzar:"
    )

    await update.message.reply_text(
        menu_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode='Markdown'
    )
