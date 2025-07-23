"""
Processor for PDF files.
"""
import os
import logging
from typing import Dict, Any, List, Optional
import re

from personal_automation_bot.services.rag.document_processors.base import DocumentProcessor

logger = logging.getLogger(__name__)

class PDFProcessor(DocumentProcessor):
    """Processor for PDF files."""

    def __init__(self):
        """Initialize the PDF processor."""
        super().__init__()
        self.extensions = ['.pdf']

        # Check if required libraries are available
        self.has_pypdf = self._check_pypdf()
        self.has_pdfminer = self._check_pdfminer()

        if not self.has_pypdf and not self.has_pdfminer:
            logger.warning("Neither PyPDF nor PDFMiner are available. PDF processing will be limited.")

    def _check_pypdf(self) -> bool:
        """Check if PyPDF is available."""
        try:
            import pypdf
            return True
        except ImportError:
            return False

    def _check_pdfminer(self) -> bool:
        """Check if PDFMiner is available."""
        try:
            from pdfminer.high_level import extract_text
            return True
        except ImportError:
            return False

    def can_process(self, file_path: str) -> bool:
        """Check if this processor can handle the given file."""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.extensions and (self.has_pypdf or self.has_pdfminer)

    def extract_text(self, file_path: str, **kwargs) -> str:
        """Extract text from a PDF file."""
        if self.has_pypdf:
            return self._extract_with_pypdf(file_path, **kwargs)
        elif self.has_pdfminer:
            return self._extract_with_pdfminer(file_path, **kwargs)
        else:
            raise ImportError("No PDF processing library available. Install either pypdf or pdfminer.six")

    def _extract_with_pypdf(self, file_path: str, **kwargs) -> str:
        """Extract text using PyPDF."""
        import pypdf

        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            text = ""

            # Extract text from each page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\\n\\n"

            # Clean up text
            text = self._clean_text(text)

            return text

    def _extract_with_pdfminer(self, file_path: str, **kwargs) -> str:
        """Extract text using PDFMiner."""
        from pdfminer.high_level import extract_text

        text = extract_text(file_path)
        text = self._clean_text(text)

        return text

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Replace multiple newlines with a single one
        text = re.sub(r'\\n{3,}', '\\n\\n', text)

        # Remove excessive whitespace
        text = re.sub(r' {2,}', ' ', text)

        # Remove non-printable characters
        text = re.sub(r'[\\x00-\\x08\\x0B\\x0C\\x0E-\\x1F\\x7F-\\x9F]', '', text)

        return text.strip()

    def extract_metadata(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """Extract metadata from a PDF file."""
        metadata = {
            "filename": os.path.basename(file_path),
            "extension": ".pdf",
            "file_type": "pdf",
            "mime_type": "application/pdf"
        }

        # Add file stats
        stat = os.stat(file_path)
        metadata.update({
            "size_bytes": stat.st_size,
            "created_at": stat.st_ctime,
            "modified_at": stat.st_mtime
        })

        # Try to extract PDF-specific metadata
        if self.has_pypdf:
            try:
                import pypdf
                with open(file_path, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    if pdf_reader.metadata:
                        pdf_info = pdf_reader.metadata

                        # Extract common metadata fields
                        for key in pdf_info:
                            clean_key = key[1:] if key.startswith('/') else key
                            metadata[clean_key.lower()] = str(pdf_info[key])

                    # Add page count
                    metadata["page_count"] = len(pdf_reader.pages)
            except Exception as e:
                logger.warning(f"Error extracting PDF metadata: {e}")

        return metadata
