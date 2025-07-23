"""
RAG (Retrieval-Augmented Generation) conversation for the Telegram bot.
"""
import logging
import os
from typing import Dict, Any, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler, CallbackQueryHandler, MessageHandler, filters,
    ConversationHandler, CallbackContext
)

from personal_automation_bot.bot.commands.rag import get_rag_generator
from personal_automation_bot.services.rag import DocumentIndexingService, get_vector_store, DocumentIndexer

logger = logging.getLogger(__name__)

# Conversation states
RAG_STATES = {
    "MAIN_MENU": 0,
    "WAITING_FOR_QUESTION": 1,
    "PROCESSING_QUESTION": 2,
    "SHOWING_DOCUMENTS": 3,
    "DOCUMENT_DETAILS": 4,
    "WAITING_FOR_FILE": 5,
    "PROCESSING_FILE": 6
}

# Global document indexing service
_indexing_service = None

def get_indexing_service() -> DocumentIndexingService:
    """
    Get or create document indexing service.

    Returns:
        DocumentIndexingService instance
    """
    global _indexing_service

    if _indexing_service is None:
        try:
            # Create vector store
            vector_store = get_vector_store("faiss")

            # Create indexer
            indexer = DocumentIndexer(vector_store=vector_store)

            # Create indexing service
            _indexing_service = DocumentIndexingService(indexer=indexer)

            logger.info("Document indexing service initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing document indexing service: {e}")
            raise

    return _indexing_service

async def rag_button(update: Update, context: CallbackContext) -> int:
    """
    Handle button presses in RAG conversation.

    Args:
        update: Telegram update
        context: Callback context

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "rag_ask":
        await query.edit_message_text(
            "📝 Por favor, escribe tu pregunta sobre tus documentos:",
            parse_mode="Markdown"
        )
        return RAG_STATES["WAITING_FOR_QUESTION"]

    elif data == "rag_docs":
        # Show indexed documents
        try:
            # Get vector store info
            vector_store = get_vector_store("faiss")
            num_docs = len(vector_store.doc_ids) if hasattr(vector_store, 'doc_ids') else 0

            if num_docs == 0:
                keyboard = [
                    [InlineKeyboardButton("Indexar un documento", callback_data="rag_index")],
                    [InlineKeyboardButton("Volver al menú", callback_data="rag_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    "📚 *Documentos indexados*\\n\\n"
                    "No hay documentos indexados. Puedes indexar un documento enviándolo al bot.",
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            else:
                keyboard = [
                    [InlineKeyboardButton("Indexar un documento", callback_data="rag_index")],
                    [InlineKeyboardButton("Volver al menú", callback_data="rag_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    f"📚 *Documentos indexados*\\n\\n"
                    f"Hay {num_docs} documentos indexados en el sistema.\\n\\n"
                    f"Puedes hacer preguntas sobre estos documentos usando el comando /rag.",
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )

            return RAG_STATES["SHOWING_DOCUMENTS"]
        except Exception as e:
            logger.error(f"Error showing documents: {e}")
            await query.edit_message_text(
                "❌ Error al mostrar los documentos indexados. Por favor, intenta de nuevo más tarde.",
                parse_mode="Markdown"
            )
            return ConversationHandler.END

    elif data == "rag_index":
        await query.edit_message_text(
            "📄 Por favor, envía un archivo de texto, PDF o Word para indexar:",
            parse_mode="Markdown"
        )
        return RAG_STATES["WAITING_FOR_FILE"]

    elif data == "rag_menu":
        # Return to main menu
        keyboard = [
            [InlineKeyboardButton("Hacer una pregunta", callback_data="rag_ask")],
            [InlineKeyboardButton("Ver documentos indexados", callback_data="rag_docs")],
            [InlineKeyboardButton("Cancelar", callback_data="rag_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "🤖 *Sistema RAG (Retrieval-Augmented Generation)*\\n\\n"
            "Este sistema te permite hacer preguntas sobre tus documentos personales. "
            "El bot buscará información relevante en tus documentos y generará una respuesta "
            "basada en esa información.\\n\\n"
            "¿Qué te gustaría hacer?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return RAG_STATES["MAIN_MENU"]

    elif data == "rag_cancel":
        await query.edit_message_text(
            "❌ Operación cancelada.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    return RAG_STATES["MAIN_MENU"]

async def process_question(update: Update, context: CallbackContext) -> int:
    """
    Process user question and generate response.

    Args:
        update: Telegram update
        context: Callback context

    Returns:
        Next conversation state
    """
    question = update.message.text
    user_id = update.effective_user.id

    # Store question in context
    context.user_data["rag_question"] = question

    # Send typing action
    await update.message.reply_text(
        "🔍 Buscando información relevante en tus documentos...",
        parse_mode="Markdown"
    )

    try:
        # Get RAG generator
        rag_generator = get_rag_generator()

        # Generate response
        response = rag_generator.generate(
            query=question,
            top_k=3,
            max_tokens=500
        )

        # Format response with citations
        formatted_text = response.get_formatted_text_with_citations()

        # Send response
        await update.message.reply_text(
            f"*Respuesta:*\\n\\n{formatted_text}",
            parse_mode="Markdown"
        )

        # Return to main menu
        keyboard = [
            [InlineKeyboardButton("Hacer otra pregunta", callback_data="rag_ask")],
            [InlineKeyboardButton("Ver documentos indexados", callback_data="rag_docs")],
            [InlineKeyboardButton("Salir", callback_data="rag_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "¿Qué más te gustaría hacer?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return RAG_STATES["MAIN_MENU"]

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        await update.message.reply_text(
            "❌ Error al procesar tu pregunta. Por favor, intenta de nuevo más tarde.",
            parse_mode="Markdown"
        )
        return ConversationHandler.END

async def process_file(update: Update, context: CallbackContext) -> int:
    """
    Process uploaded file for indexing.

    Args:
        update: Telegram update
        context: Callback context

    Returns:
        Next conversation state
    """
    # Check if message contains document
    if not update.message.document:
        await update.message.reply_text(
            "❌ Por favor, envía un archivo válido (texto, PDF, Word).",
            parse_mode="Markdown"
        )
        return RAG_STATES["WAITING_FOR_FILE"]

    document = update.message.document
    file_name = document.file_name

    # Check file extension
    _, ext = os.path.splitext(file_name.lower())
    supported_extensions = [".txt", ".pdf", ".docx", ".doc", ".md", ".html"]

    if ext not in supported_extensions:
        await update.message.reply_text(
            f"❌ Tipo de archivo no soportado. Por favor, envía un archivo de texto, PDF o Word.",
            parse_mode="Markdown"
        )
        return RAG_STATES["WAITING_FOR_FILE"]

    # Send processing message
    await update.message.reply_text(
        f"⏳ Procesando archivo {file_name}...",
        parse_mode="Markdown"
    )

    try:
        # Get file from Telegram
        file = await context.bot.get_file(document.file_id)

        # Create temporary file
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "temp")
        os.makedirs(temp_dir, exist_ok=True)

        temp_file_path = os.path.join(temp_dir, file_name)

        # Download file
        await file.download_to_drive(temp_file_path)

        # Get indexing service
        indexing_service = get_indexing_service()

        # Index file
        chunk_ids = indexing_service.index_document(temp_file_path, force=True)

        # Send success message
        await update.message.reply_text(
            f"✅ Archivo {file_name} indexado correctamente.\\n\\n"
            f"Se crearon {len(chunk_ids)} fragmentos para búsqueda.",
            parse_mode="Markdown"
        )

        # Return to main menu
        keyboard = [
            [InlineKeyboardButton("Hacer una pregunta", callback_data="rag_ask")],
            [InlineKeyboardButton("Ver documentos indexados", callback_data="rag_docs")],
            [InlineKeyboardButton("Salir", callback_data="rag_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "¿Qué te gustaría hacer ahora?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return RAG_STATES["MAIN_MENU"]

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        await update.message.reply_text(
            f"❌ Error al procesar el archivo: {str(e)}",
            parse_mode="Markdown"
        )
        return RAG_STATES["WAITING_FOR_FILE"]

async def cancel(update: Update, context: CallbackContext) -> int:
    """
    Cancel conversation.

    Args:
        update: Telegram update
        context: Callback context

    Returns:
        ConversationHandler.END
    """
    await update.message.reply_text(
        "❌ Operación cancelada.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# Create conversation handler
RAG_CONVERSATION = ConversationHandler(
    entry_points=[CommandHandler("rag", rag_button)],
    states={
        RAG_STATES["MAIN_MENU"]: [
            CallbackQueryHandler(rag_button, pattern="^rag_")
        ],
        RAG_STATES["WAITING_FOR_QUESTION"]: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, process_question)
        ],
        RAG_STATES["SHOWING_DOCUMENTS"]: [
            CallbackQueryHandler(rag_button, pattern="^rag_")
        ],
        RAG_STATES["WAITING_FOR_FILE"]: [
            MessageHandler(filters.Document.ALL, process_file)
        ]
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
