"""
Processor for HTML files.
"""
import os
import logging
import re
from typing import Dict, Any, List, Optional

from personal_automation_bot.services.rag.document_processors.base import DocumentProcessor

logger = logging.getLogger(__name__)

class HTMLProcessor(DocumentProcessor):
    """Processor for HTML files."""

    def __init__(self):
        """Initialize the HTML processor."""
        super().__init__()
        self.extensions = ['.html', '.htm', '.xhtml']

        # Check if required libraries are available
        self.has_bs4 = self._check_bs4()

        if not self.has_bs4:
            logger.warning("BeautifulSoup is not available. HTML processing will be limited.")

    def _check_bs4(self) -> bool:
        """Check if BeautifulSoup is available."""
        try:
            from bs4 import BeautifulSoup
            return True
        except ImportError:
            return False

    def can_process(self, file_path: str) -> bool:
        """Check if this processor can handle the given file."""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.extensions

    def extract_text(self, file_path: str, **kwargs) -> str:
        """Extract text from an HTML file."""
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            html_content = f.read()

        if self.has_bs4:
            return self._extract_with_bs4(html_content)
        else:
            return self._extract_with_regex(html_content)

    def _extract_with_bs4(self, html_content: str) -> str:
        """Extract text using BeautifulSoup."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script_or_style in soup(['script', 'style', 'meta', 'noscript', 'header', 'footer', 'nav']):
            script_or_style.decompose()

        # Get text
        text = soup.get_text(separator='\\n')

        # Clean text
        text = self._clean_text(text)

        return text

    def _extract_with_regex(self, html_content: str) -> str:
        """Extract text using regex (fallback method)."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html_content)

        # Decode HTML entities
        text = self._decode_html_entities(text)

        # Clean text
        text = self._clean_text(text)

        return text

    def _decode_html_entities(self, text: str) -> str:
        """Decode common HTML entities."""
        entities = {
            '&nbsp;': ' ',
            '&lt;': '<',
            '&gt;': '>',
            '&amp;': '&',
            '&quot;': '"',
            '&apos;': "'",
            '&#39;': "'",
            '&ndash;': '-',
            '&mdash;': '—',
            '&lsquo;': ''',
            '&rsquo;': ''',
            '&ldquo;': '"',
            '&rdquo;': '"',
        }

        for entity, replacement in entities.items():
            text = text.replace(entity, replacement)

        return text

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Replace multiple whitespace with a single space
        text = re.sub(r'\\s+', ' ', text)

        # Replace multiple newlines with a single one
        text = re.sub(r'\\n{3,}', '\\n\\n', text)

        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\\n')]
        text = '\\n'.join(lines)

        return text.strip()

    def extract_metadata(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Extract metadata from an HTML file."""
        metadata = {
            "filename": os.path.basename(file_path),
            "extension": os.path.splitext(file_path.lower())[1],
            "file_type": "html",
            "mime_type": "text/html"
        }

        # Add file stats
        stat = os.stat(file_path)
        metadata.update({
            "size_bytes": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime
        })

        # Try to extract HTML-specific metadata
        if self.has_bs4:
            try:
                from bs4 import BeautifulSoup

                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    html_content = f.read()

                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract title
                title_tag = soup.find('title')
                if title_tag:
                    metadata["title"] = title_tag.string

                # Extract meta tags
                for meta in soup.find_all('meta'):
                    name = meta.get('name', meta.get('property', ''))
                    content = meta.get('content', '')

                    if name and content:
                        # Convert name to lowercase and replace colons with underscores
                        name = name.lower().replace(':', '_')
                        metadata[f"meta_{name}"] = content
            except Exception as e:
                logger.warning(f"Error extracting HTML metadata: {e}")

        return metadata
