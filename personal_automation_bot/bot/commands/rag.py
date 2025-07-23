"""
RAG (Retrieval-Augmented Generation) commands for the Telegram bot.
"""
import logging
from typing import Dict, Any, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from personal_automation_bot.services.content import RAGGenerator
from personal_automation_bot.services.rag import DocumentRetriever, get_vector_store
from personal_automation_bot.bot.conversations.rag_conversation import RAG_CONVERSATION, RAG_STATES

logger = logging.getLogger(__name__)

# Global RAG generator instance
_rag_generator = None

def get_rag_generator() -> RAGGenerator:
    """
    Get or create RAG generator instance.

    Returns:
        RAGGenerator instance
    """
    global _rag_generator

    if _rag_generator is None:
        try:
            # Create vector store
            vector_store = get_vector_store("faiss")

            # Create retriever
            retriever = DocumentRetriever(vector_store=vector_store)

            # Create RAG generator
            _rag_generator = RAGGenerator(retriever=retriever)

            logger.info("RAG generator initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing RAG generator: {e}")
            raise

    return _rag_generator

async def rag_command(update: Update, context: CallbackContext) -> int:
    """
    Handle /rag command to start RAG conversation.

    Args:
        update: Telegram update
        context: Callback context

    Returns:
        Next conversation state
    """
    user = update.effective_user
    logger.info(f"User {user.id} started RAG conversation")

    # Create keyboard with options
    keyboard = [
        [InlineKeyboardButton("Hacer una pregunta", callback_data="rag_ask")],
        [InlineKeyboardButton("Ver documentos indexados", callback_data="rag_docs")],
        [InlineKeyboardButton("Cancelar", callback_data="rag_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🤖 *Sistema RAG (Retrieval-Augmented Generation)*\\n\\n"
        "Este sistema te permite hacer preguntas sobre tus documentos personales. "
        "El bot buscará información relevante en tus documentos y generará una respuesta "
        "basada en esa información.\\n\\n"
        "¿Qué te gustaría hacer?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

    return RAG_STATES["MAIN_MENU"]

async def rag_help(update: Update, context: CallbackContext) -> None:
    """
    Show help for RAG commands.

    Args:
        update: Telegram update
        context: Callback context
    """
    help_text = (
        "🔍 *Comandos RAG*\\n\\n"
        "/rag - Iniciar conversación RAG para hacer preguntas sobre tus documentos\\n"
        "/raghelp - Mostrar esta ayuda\\n\\n"
        "*¿Qué es RAG?*\\n"
        "RAG (Retrieval-Augmented Generation) es una técnica que combina la recuperación "
        "de información relevante de tus documentos con la generación de texto para "
        "proporcionar respuestas precisas y con referencias a las fuentes."
    )

    await update.message.reply_text(help_text, parse_mode="Markdown")

def get_rag_conversation_handler() -> ConversationHandler:
    """
    Get RAG conversation handler.

    Returns:
        ConversationHandler for RAG conversation
    """
    return RAG_CONVERSATION
