"""
Document indexing service for the RAG system.
"""
import os
import logging
import hashlib
import json
from typing import Dict, Any, List, Optional, Union, Tuple
import time

from personal_automation_bot.services.rag.indexer import DocumentIndexer
from personal_automation_bot.services.rag.document_processors.factory import get_document_processor, get_supported_extensions

logger = logging.getLogger(__name__)

class DocumentIndexingService:
    """Service for indexing documents from various sources."""

    def __init__(
        self,
        indexer: Optional[DocumentIndexer] = None,
        cache_dir: Optional[str] = None,
        supported_extensions: Optional[List[str]] = None
    ):
        """
        Initialize the document indexing service.

        Args:
            indexer: Document indexer instance
            cache_dir: Directory for caching processed documents
            supported_extensions: List of supported file extensions (if None, get from processors)
        """
        self.indexer = indexer

        # Set up cache directory
        if cache_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            cache_dir = os.path.join(base_dir, "..", "data", "document_cache")

        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        # Set up supported extensions
        self.supported_extensions = supported_extensions or get_supported_extensions()

        # Load document cache
        self.document_cache_path = os.path.join(cache_dir, "document_cache.json")
        self.document_cache = self._load_document_cache()

    def _load_document_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load document cache from disk."""
        if os.path.exists(self.document_cache_path):
            try:
                with open(self.document_cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load document cache: {e}")

        return {}

    def _save_document_cache(self) -> None:
        """Save document cache to disk."""
        try:
            with open(self.document_cache_path, 'w') as f:
                json.dump(self.document_cache, f)
        except Exception as e:
            logger.warning(f"Failed to save document cache: {e}")

    def _compute_document_hash(self, file_path: str) -> str:
        """Compute a hash for a document to detect changes."""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5()
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(4096), b""):
                    file_hash.update(chunk)
                return file_hash.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to compute hash for {file_path}: {e}")
            # Use modification time as fallback
            return str(os.path.getmtime(file_path))

    def is_supported_file(self, file_path: str) -> bool:
        """
        Check if a file is supported for indexing.

        Args:
            file_path: Path to the file

        Returns:
            True if the file is supported, False otherwise
        """
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_extensions

    def process_document(self, file_path: str, force: bool = False) -> Dict[str, Any]:
        """
        Process a document and extract text and metadata.

        Args:
            file_path: Path to the document
            force: Force processing even if the document hasn't changed

        Returns:
            Processed document with text and metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.is_supported_file(file_path):
            raise ValueError(f"Unsupported file type: {file_path}")

        # Check cache
        doc_id = os.path.abspath(file_path)
        doc_hash = self._compute_document_hash(file_path)

        if not force and doc_id in self.document_cache and self.document_cache[doc_id].get("hash") == doc_hash:
            logger.info(f"Document {file_path} hasn't changed, using cached version")
            return self.document_cache[doc_id]["document"]

        # Get appropriate processor
        processor = get_document_processor(file_path)
        if not processor:
            raise ValueError(f"No processor available for {file_path}")

        # Process document
        start_time = time.time()
        document = processor.process_file(file_path)
        processing_time = time.time() - start_time

        # Add additional metadata
        document["id"] = doc_id
        document["hash"] = doc_hash
        document["processing_time"] = processing_time
        document["indexed_at"] = time.time()

        # Update cache
        self.document_cache[doc_id] = {
            "hash": doc_hash,
            "document": document,
            "last_indexed": time.time()
        }
        self._save_document_cache()

        logger.info(f"Processed document {file_path} in {processing_time:.2f}s")
        return document

    def index_document(self, file_path: str, force: bool = False) -> List[str]:
        """
        Index a document.

        Args:
            file_path: Path to the document
            force: Force indexing even if the document hasn't changed

        Returns:
            List of chunk IDs
        """
        if not self.indexer:
            raise ValueError("No indexer provided")

        # Process document
        document = self.process_document(file_path, force=force)

        # Index document
        chunk_ids = self.indexer.index_document(document)

        logger.info(f"Indexed document {file_path} into {len(chunk_ids)} chunks")
        return chunk_ids

    def index_directory(
        self,
        directory: str,
        recursive: bool = True,
        force: bool = False,
        exclude_patterns: Optional[List[str]] = None
    ) -> Dict[str, List[str]]:
        """
        Index all supported documents in a directory.

        Args:
            directory: Directory to index
            recursive: Whether to recursively index subdirectories
            force: Force indexing even if documents haven't changed
            exclude_patterns: List of glob patterns to exclude

        Returns:
            Dictionary mapping file paths to lists of chunk IDs
        """
        if not os.path.isdir(directory):
            raise ValueError(f"Not a directory: {directory}")

        if not self.indexer:
            raise ValueError("No indexer provided")

        import fnmatch

        exclude_patterns = exclude_patterns or []
        results = {}

        # Walk directory
        for root, dirs, files in os.walk(directory):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_patterns)]

            # Process files
            for file in files:
                # Skip excluded files
                if any(fnmatch.fnmatch(file, pattern) for pattern in exclude_patterns):
                    continue

                file_path = os.path.join(root, file)

                # Skip unsupported files
                if not self.is_supported_file(file_path):
                    continue

                try:
                    chunk_ids = self.index_document(file_path, force=force)
                    results[file_path] = chunk_ids
                except Exception as e:
                    logger.error(f"Error indexing {file_path}: {e}")

            # Stop if not recursive
            if not recursive:
                break

        return results
