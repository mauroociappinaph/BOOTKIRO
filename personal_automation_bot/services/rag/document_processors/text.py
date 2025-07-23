"""
Processor for plain text files.
"""
import os
import logging
from typing import Dict, Any

from personal_automation_bot.services.rag.document_processors.base import DocumentProcessor

logger = logging.getLogger(__name__)

class TextProcessor(DocumentProcessor):
    """Processor for plain text files."""

    def __init__(self):
        """Initialize the text processor."""
        super().__init__()
        self.extensions = ['.txt', '.md', '.csv', '.json', '.log', '.py', '.js', '.html', '.css', '.xml']

    def can_process(self, file_path: str) -> bool:
        """Check if this processor can handle the given file."""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.extensions

    def extract_text(self, file_path: str, encoding: str = 'utf-8', **kwargs) -> str:
        """Extract text from a text file."""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with a different encoding if utf-8 fails
            logger.warning(f"Failed to decode {file_path} with {encoding}, trying with latin-1")
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()

    def extract_metadata(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Extract metadata from a text file."""
        stat = os.stat(file_path)
        _, ext = os.path.splitext(file_path.lower())

        return {
            "filename": os.path.basename(file_path),
            "extension": ext,
            "size_bytes": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime,
            "file_type": "text",
            "mime_type": self._get_mime_type(ext)
        }

    def _get_mime_type(self, ext: str) -> str:
        """Get MIME type for a file extension."""
        mime_types = {
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.log': 'text/plain',
            '.py': 'text/x-python',
            '.js': 'text/javascript',
            '.html': 'text/html',
            '.css': 'text/css',
            '.xml': 'application/xml'
        }
        return mime_types.get(ext, 'text/plain')
