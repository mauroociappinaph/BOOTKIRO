"""
Unified storage manager for document management across different backends.
"""
import logging
import json
import os
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from personal_automation_bot.services.documents.models import (
    Document, DocumentMetadata, StorageBackend, DocumentType
)
from personal_automation_bot.config import settings

logger = logging.getLogger(__name__)


class StorageManager:
    """
    Unified storage manager for document management across different backends.
    Provides caching and synchronization capabilities.
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the storage manager.

        Args:
            cache_dir (Optional[str]): Directory for local cache. If None, uses default.
        """
        if cache_dir is None:
            # Use default cache directory
            self.cache_dir = os.path.join(
                os.path.expanduser("~"),
                ".personal_automation_bot",
                "cache",
                "documents"
            )
        else:
            self.cache_dir = cache_dir

        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)

        # Cache expiration time (in seconds)
        self.cache_expiry = 3600  # 1 hour

        # Metadata index
        self.metadata_index_path = os.path.join(self.cache_dir, "metadata_index.json")
        self.metadata_index = self._load_metadata_index()

    def _load_metadata_index(self) -> Dict[str, Any]:
        """
        Load metadata index from disk.

        Returns:
            Dict[str, Any]: Metadata index.
        """
        if os.path.exists(self.metadata_index_path):
            try:
                with open(self.metadata_index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metadata index: {e}")
                return {"documents": {}, "last_updated": {}}
        else:
            return {"documents": {}, "last_updated": {}}

    def _save_metadata_index(self):
        """Save metadata index to disk."""
        try:
            with open(self.metadata_index_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata_index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata index: {e}")

    def _get_cache_path(self, document_id: str, backend: StorageBackend) -> str:
        """
        Get cache file path for a document.

        Args:
            document_id (str): Document ID.
            backend (StorageBackend): Storage backend.

        Returns:
            str: Cache file path.
        """
        backend_dir = os.path.join(self.cache_dir, backend.value)
        os.makedirs(backend_dir, exist_ok=True)
        return os.path.join(backend_dir, f"{document_id}.cache")

    def cache_document(self, document: Document):
        """
        Cache a document locally.

        Args:
            document (Document): Document to cache.
        """
        try:
            # Cache document content
            cache_path = self._get_cache_path(
                document.metadata.external_id,
                document.metadata.storage_backend
            )

            # Save document content
            with open(cache_path, 'wb') as f:
                f.write(document.content or b'')

            # Update metadata index
            doc_id = document.metadata.external_id
            backend = document.metadata.storage_backend.value

            if backend not in self.metadata_index["documents"]:
                self.metadata_index["documents"][backend] = {}

            self.metadata_index["documents"][backend][doc_id] = document.metadata.to_dict()

            if backend not in self.metadata_index["last_updated"]:
                self.metadata_index["last_updated"][backend] = {}

            self.metadata_index["last_updated"][backend][doc_id] = datetime.now().isoformat()

            # Save metadata index
            self._save_metadata_index()

            logger.info(f"Cached document {document.metadata.title} ({doc_id})")

        except Exception as e:
            logger.error(f"Failed to cache document {document.metadata.title}: {e}")

    def get_cached_document(self, document_id: str,
                           backend: StorageBackend) -> Optional[Document]:
        """
        Get a document from cache.

        Args:
            document_id (str): Document ID.
            backend (StorageBackend): Storage backend.

        Returns:
            Optional[Document]: Cached document or None if not found or expired.
        """
        try:
            backend_str = backend.value

            # Check if document exists in metadata index
            if (backend_str not in self.metadata_index["documents"] or
                document_id not in self.metadata_index["documents"][backend_str]):
                return None

            # Check if cache is expired
            if backend_str in self.metadata_index["last_updated"]:
                last_updated_str = self.metadata_index["last_updated"][backend_str].get(document_id)
                if last_updated_str:
                    last_updated = datetime.fromisoformat(last_updated_str)
                    if datetime.now() - last_updated > timedelta(seconds=self.cache_expiry):
                        logger.info(f"Cache expired for document {document_id}")
                        return None

            # Get document metadata
            metadata_dict = self.metadata_index["documents"][backend_str][document_id]
            metadata = DocumentMetadata.from_dict(metadata_dict)

            # Get document content
            cache_path = self._get_cache_path(document_id, backend)
            if not os.path.exists(cache_path):
                return None

            with open(cache_path, 'rb') as f:
                content = f.read()

            # Create document
            text_content = None
            if metadata.content_type == DocumentType.TEXT:
                try:
                    text_content = content.decode('utf-8')
                except UnicodeDecodeError:
                    logger.warning(f"Failed to decode text content for document {document_id}")

            document = Document(
                metadata=metadata,
                content=content,
                text_content=text_content
            )

            logger.info(f"Retrieved document {metadata.title} ({document_id}) from cache")
            return document

        except Exception as e:
            logger.error(f"Failed to get cached document {document_id}: {e}")
            return None

    def invalidate_cache(self, document_id: str, backend: StorageBackend):
        """
        Invalidate cache for a document.

        Args:
            document_id (str): Document ID.
            backend (StorageBackend): Storage backend.
        """
        try:
            backend_str = backend.value

            # Remove from metadata index
            if (backend_str in self.metadata_index["documents"] and
                document_id in self.metadata_index["documents"][backend_str]):
                del self.metadata_index["documents"][backend_str][document_id]

            if (backend_str in self.metadata_index["last_updated"] and
                document_id in self.metadata_index["last_updated"][backend_str]):
                del self.metadata_index["last_updated"][backend_str][document_id]

            # Remove cache file
            cache_path = self._get_cache_path(document_id, backend)
            if os.path.exists(cache_path):
                os.remove(cache_path)

            # Save metadata index
            self._save_metadata_index()

            logger.info(f"Invalidated cache for document {document_id}")

        except Exception as e:
            logger.error(f"Failed to invalidate cache for document {document_id}: {e}")

    def is_cache_valid(self, document_id: str, backend: StorageBackend) -> bool:
        """
        Check if cache is valid for a document.

        Args:
            document_id (str): Document ID.
            backend (StorageBackend): Storage backend.

        Returns:
            bool: True if cache is valid, False otherwise.
        """
        try:
            backend_str = backend.value

            # Check if document exists in metadata index
            if (backend_str not in self.metadata_index["documents"] or
                document_id not in self.metadata_index["documents"][backend_str]):
                return False

            # Check if cache file exists
            cache_path = self._get_cache_path(document_id, backend)
            if not os.path.exists(cache_path):
                return False

            # Check if cache is expired
            if backend_str in self.metadata_index["last_updated"]:
                last_updated_str = self.metadata_index["last_updated"][backend_str].get(document_id)
                if last_updated_str:
                    last_updated = datetime.fromisoformat(last_updated_str)
                    if datetime.now() - last_updated > timedelta(seconds=self.cache_expiry):
                        return False

            return True

        except Exception as e:
            logger.error(f"Failed to check cache validity for document {document_id}: {e}")
            return False

    def get_cached_documents_by_backend(self, backend: StorageBackend) -> List[DocumentMetadata]:
        """
        Get all cached documents for a backend.

        Args:
            backend (StorageBackend): Storage backend.

        Returns:
            List[DocumentMetadata]: List of document metadata.
        """
        try:
            backend_str = backend.value

            if backend_str not in self.metadata_index["documents"]:
                return []

            documents = []
            for doc_id, metadata_dict in self.metadata_index["documents"][backend_str].items():
                try:
                    metadata = DocumentMetadata.from_dict(metadata_dict)
                    documents.append(metadata)
                except Exception as e:
                    logger.error(f"Failed to parse metadata for document {doc_id}: {e}")

            return documents

        except Exception as e:
            logger.error(f"Failed to get cached documents for backend {backend}: {e}")
            return []

    def clear_cache(self, backend: Optional[StorageBackend] = None):
        """
        Clear cache for a backend or all backends.

        Args:
            backend (Optional[StorageBackend]): Storage backend to clear cache for.
                If None, clears cache for all backends.
        """
        try:
            if backend:
                backend_str = backend.value

                # Remove from metadata index
                if backend_str in self.metadata_index["documents"]:
                    del self.metadata_index["documents"][backend_str]

                if backend_str in self.metadata_index["last_updated"]:
                    del self.metadata_index["last_updated"][backend_str]

                # Remove cache files
                backend_dir = os.path.join(self.cache_dir, backend_str)
                if os.path.exists(backend_dir):
                    for file in os.listdir(backend_dir):
                        os.remove(os.path.join(backend_dir, file))

                logger.info(f"Cleared cache for backend {backend}")
            else:
                # Clear all cache
                self.metadata_index = {"documents": {}, "last_updated": {}}

                # Remove all cache files
                for item in os.listdir(self.cache_dir):
                    item_path = os.path.join(self.cache_dir, item)
                    if os.path.isdir(item_path):
                        for file in os.listdir(item_path):
                            os.remove(os.path.join(item_path, file))

                logger.info("Cleared all cache")

            # Save metadata index
            self._save_metadata_index()

        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict[str, Any]: Cache statistics.
        """
        try:
            stats = {
                "total_documents": 0,
                "backends": {},
                "cache_size_bytes": 0
            }

            # Count documents by backend
            for backend, docs in self.metadata_index["documents"].items():
                doc_count = len(docs)
                stats["backends"][backend] = {
                    "document_count": doc_count
                }
                stats["total_documents"] += doc_count

            # Calculate cache size
            for root, _, files in os.walk(self.cache_dir):
                for file in files:
                    if file.endswith('.cache'):
                        file_path = os.path.join(root, file)
                        stats["cache_size_bytes"] += os.path.getsize(file_path)

            return stats

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}

    def sync_document(self, document_id: str, backend: StorageBackend,
                     local_document: Document, remote_document: Document) -> Document:
        """
        Sync a document between local and remote versions.

        Args:
            document_id (str): Document ID.
            backend (StorageBackend): Storage backend.
            local_document (Document): Local document.
            remote_document (Document): Remote document.

        Returns:
            Document: Synced document.
        """
        # For now, remote version always wins
        # TODO: Implement more sophisticated conflict resolution
        self.cache_document(remote_document)
        return remote_document
