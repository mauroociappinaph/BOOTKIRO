"""
Factory for document processors.
"""
import os
import logging
from typing import Optional, List, Type

from personal_automation_bot.services.rag.document_processors.base import DocumentProcessor
from personal_automation_bot.services.rag.document_processors.text import TextProcessor
from personal_automation_bot.services.rag.document_processors.pdf import PDFProcessor
from personal_automation_bot.services.rag.document_processors.docx import DocxProcessor
from personal_automation_bot.services.rag.document_processors.html import HTMLProcessor

logger = logging.getLogger(__name__)

# Registry of document processors
PROCESSORS = [
    TextProcessor,
    PDFProcessor,
    DocxProcessor,
    HTMLProcessor,
]

def get_document_processor(file_path: str) -> Optional[DocumentProcessor]:
    """
    Get an appropriate document processor for the given file.

    Args:
        file_path: Path to the file

    Returns:
        Document processor instance or None if no suitable processor is found
    """
    _, ext = os.path.splitext(file_path.lower())

    # Try each processor
    for processor_class in PROCESSORS:
        processor = processor_class()
        if processor.can_process(file_path):
            logger.debug(f"Using {processor.__class__.__name__} for {file_path}")
            return processor

    logger.warning(f"No suitable processor found for {file_path}")
    return None

def register_processor(processor_class: Type[DocumentProcessor]) -> None:
    """
    Register a new document processor.

    Args:
        processor_class: Document processor class to register
    """
    if processor_class not in PROCESSORS:
        PROCESSORS.append(processor_class)
        logger.debug(f"Registered document processor: {processor_class.__name__}")

def get_supported_extensions() -> List[str]:
    """
    Get a list of all supported file extensions.

    Returns:
        List of supported file extensions
    """
    extensions = []
    for processor_class in PROCESSORS:
        processor = processor_class()
        if hasattr(processor, 'extensions'):
            extensions.extend(processor.extensions)

    return sorted(list(set(extensions)))
