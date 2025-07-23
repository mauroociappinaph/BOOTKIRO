"""
Base class for document processors.
"""
import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, BinaryIO, Union

logger = logging.getLogger(__name__)

class DocumentProcessor(ABC):
    """Base class for document processors."""

    def __init__(self):
        """Initialize the document processor."""
        pass

    @abstractmethod
    def can_process(self, file_path: str) -> bool:
        """
        Check if this processor can handle the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if this processor can handle the file, False otherwise
        """
        pass

    @abstractmethod
    def extract_text(self, file_path: str, **kwargs) -> str:
        """
        Extract text from a file.

        Args:
            file_path: Path to the file
            **kwargs: Additional arguments for the processor

        Returns:
            Extracted text
        """
        pass

    @abstractmethod
    def extract_metadata(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Extract metadata from a file.

        Args:
            file_path: Path to the file
            **kwargs: Additional arguments for the processor

        Returns:
            Dictionary of metadata
        """
        pass

    def process_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Process a file and extract text and metadata.

        Args:
            file_path: Path to the file
            **kwargs: Additional arguments for the processor

        Returns:
            Dictionary with text and metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.can_process(file_path):
            raise ValueError(f"This processor cannot handle file: {file_path}")

        try:
            text = self.extract_text(file_path, **kwargs)
            metadata = self.extract_metadata(file_path, **kwargs)

            return {
                "text": text,
                "metadata": metadata,
                "source": file_path,
                "processor": self.__class__.__name__
            }
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise

    def process_binary(self, file_content: bytes, file_name: str, **kwargs) -> Dict[str, Any]:
        """
        Process binary file content.

        Args:
            file_content: Binary content of the file
            file_name: Name of the file (for determining type)
            **kwargs: Additional arguments for the processor

        Returns:
            Dictionary with text and metadata
        """
        # Default implementation saves to a temporary file and processes it
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_path = temp_file.name

        try:
            result = self.process_file(temp_path, **kwargs)
            # Update source to original file name instead of temp path
            result["source"] = file_name
            return result
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
