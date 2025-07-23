"""
Document processors for extracting text from various file formats.
"""

from personal_automation_bot.services.rag.document_processors.base import DocumentProcessor
from personal_automation_bot.services.rag.document_processors.text import TextProcessor
from personal_automation_bot.services.rag.document_processors.pdf import PDFProcessor
from personal_automation_bot.services.rag.document_processors.docx import DocxProcessor
from personal_automation_bot.services.rag.document_processors.html import HTMLProcessor
from personal_automation_bot.services.rag.document_processors.factory import get_document_processor

__all__ = [
    'DocumentProcessor',
    'TextProcessor',
    'PDFProcessor',
    'DocxProcessor',
    'HTMLProcessor',
    'get_document_processor',
]
