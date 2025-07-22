"""
Main menu keyboard for the Telegram bot.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_main_menu_keyboard():
    """
    Create the main menu inline keyboard.

    Returns:
        InlineKeyboardMarkup: The main menu keyboard.
    """
    keyboard = [
        [
            InlineKeyboardButton("📧 Correo", callback_data="menu_email"),
            InlineKeyboardButton("📅 Calendario", callback_data="menu_calendar")
        ],
        [
            InlineKeyboardButton("✨ Contenido IA", callback_data="menu_content"),
            InlineKeyboardButton("📁 Documentos", callback_data="menu_documents")
        ],
        [
            InlineKeyboardButton("📱 Redes Sociales", callback_data="menu_social"),
            InlineKeyboardButton("🤖 RAG", callback_data="menu_rag")
        ],
        [
            InlineKeyboardButton("⚙️ Flujos", callback_data="menu_flows"),
            InlineKeyboardButton("❓ Ayuda", callback_data="menu_help")
        ],
        [
            InlineKeyboardButton("🔐 Autenticación", callback_data="auth_start")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

def get_email_menu_keyboard():
    """
    Create the email menu inline keyboard.

    Returns:
        InlineKeyboardMarkup: The email menu keyboard.
    """
    keyboard = [
        [
            InlineKeyboardButton("📥 Leer correos", callback_data="email_read"),
            InlineKeyboardButton("📤 Enviar correo", callback_data="email_send")
        ],
        [
            InlineKeyboardButton("🔙 Volver al menú", callback_data="back_to_main")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

def get_calendar_menu_keyboard():
    """
    Create the calendar menu inline keyboard.

    Returns:
        InlineKeyboardMarkup: The calendar menu keyboard.
    """
    keyboard = [
        [
            InlineKeyboardButton("📅 Ver eventos", callback_data="calendar_view"),
            InlineKeyboardButton("➕ Crear evento", callback_data="calendar_create")
        ],
        [
            InlineKeyboardButton("🗑️ Eliminar evento", callback_data="calendar_delete"),
            InlineKeyboardButton("🔙 Volver al menú", callback_data="back_to_main")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

def get_content_menu_keyboard():
    """
    Create the content generation menu inline keyboard.

    Returns:
        InlineKeyboardMarkup: The content menu keyboard.
    """
    keyboard = [
        [
            InlineKeyboardButton("📝 Generar texto", callback_data="content_text"),
            InlineKeyboardButton("🎨 Generar imagen", callback_data="content_image")
        ],
        [
            InlineKeyboardButton("🔙 Volver al menú", callback_data="back_to_main")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """
    Create a simple back button keyboard.

    Returns:
        InlineKeyboardMarkup: The back button keyboard.
    """
    keyboard = [
        [InlineKeyboardButton("🔙 Volver al menú", callback_data="back_to_main")]
    ]

    return InlineKeyboardMarkup(keyboard)
