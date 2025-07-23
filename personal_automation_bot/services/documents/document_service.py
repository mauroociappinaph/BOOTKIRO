"""
Document service for managing documents across different storage backends.
"""
import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from personal_automation_bot.services.documents.drive_client import GoogleDriveClient
from personal_automation_bot.services.documents.notion_client import NotionClient
from personal_automation_bot.services.documents.storage_manager import StorageManager
from personal_automation_bot.services.documents.models import (
    Document, DocumentMetadata, FolderMetadata, SearchResult, StorageQuota,
    StorageBackend, DocumentType, get_document_type_from_mime, format_file_size
)
from personal_automation_bot.utils.auth import google_auth_manager
from personal_automation_bot.config import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Service for managing documents across different storage backends.
    """

    def __init__(self):
        """Initialize the document service."""
        self.auth_manager = google_auth_manager
        self._notion_clients = {}  # Cache for Notion clients per user
        self.storage_manager = StorageManager()  # Unified storage manager

    def _get_drive_client(self, user_id: int) -> Optional[GoogleDriveClient]:
        """
        Get Google Drive client for a user.

        Args:
            user_id (int): Telegram user ID.

        Returns:
            Optional[GoogleDriveClient]: Drive client or None if not authenticated.
        """
        credentials = self.auth_manager.get_user_credentials(user_id)
        if not credentials:
            return None

        return GoogleDriveClient(credentials)

    def _get_notion_client(self, user_id: int) -> Optional[NotionClient]:
        """
        Get Notion client for a user.

        Args:
            user_id (int): Telegram user ID.

        Returns:
            Optional[NotionClient]: Notion client or None if not configured.
        """
        # For now, use global Notion API key from settings
        # TODO: Implement per-user Notion authentication
        if not settings.NOTION_API_KEY:
            return None

        if user_id not in self._notion_clients:
            self._notion_clients[user_id] = NotionClient(settings.NOTION_API_KEY)

        return self._notion_clients[user_id]

    def is_user_authenticated(self, user_id: int, backend: StorageBackend) -> bool:
        """
        Check if user is authenticated for a storage backend.

        Args:
            user_id (int): Telegram user ID.
            backend (StorageBackend): Storage backend to check.

        Returns:
            bool: True if authenticated, False otherwise.
        """
        if backend == StorageBackend.GOOGLE_DRIVE:
            return self.auth_manager.is_user_authenticated(user_id)
        elif backend == StorageBackend.NOTION:
            return self._get_notion_client(user_id) is not None
        else:
            return True  # Local storage doesn't require authentication

    def create_document(self, user_id: int, title: str, content: str,
                       backend: StorageBackend = StorageBackend.GOOGLE_DRIVE,
                       tags: Optional[List[str]] = None,
                       folder_id: Optional[str] = None) -> Optional[DocumentMetadata]:
        """
        Create a new document.

        Args:
            user_id (int): Telegram user ID.
            title (str): Document title.
            content (str): Document content.
            backend (StorageBackend): Storage backend to use.
            tags (Optional[List[str]]): Document tags.
            folder_id (Optional[str]): Parent folder ID.

        Returns:
            Optional[DocumentMetadata]: Created document metadata or None if failed.
        """
        try:
            if backend == StorageBackend.GOOGLE_DRIVE:
                return self._create_drive_document(user_id, title, content, tags, folder_id)
            elif backend == StorageBackend.NOTION:
                return self._create_notion_document(user_id, title, content, tags, folder_id)
            else:
                # TODO: Implement local storage
                logger.warning("Local backend not yet implemented")
                return None

        except Exception as e:
            logger.error(f"Failed to create document '{title}': {e}")
            return None

    def _create_drive_document(self, user_id: int, title: str, content: str,
                              tags: Optional[List[str]] = None,
                              folder_id: Optional[str] = None) -> Optional[DocumentMetadata]:
        """Create a document in Google Drive."""
        drive_client = self._get_drive_client(user_id)
        if not drive_client:
            logger.error(f"User {user_id} not authenticated with Google Drive")
            return None

        # Ensure we have an app folder
        if not folder_id:
            folder_id = drive_client.create_app_folder()
            if not folder_id:
                logger.error("Failed to create/get app folder")
                return None

        # Upload document as text file
        filename = f"{title}.txt"
        file_content = content.encode('utf-8')

        external_id = drive_client.upload_file(
            file_content=file_content,
            filename=filename,
            parent_id=folder_id,
            mime_type='text/plain'
        )

        if not external_id:
            return None

        # Get file metadata from Drive
        file_metadata = drive_client.get_file_metadata(external_id)
        if not file_metadata:
            return None

        # Create document metadata
        doc_id = str(uuid.uuid4())
        created_time = datetime.fromisoformat(file_metadata['createdTime'].replace('Z', '+00:00'))
        modified_time = datetime.fromisoformat(file_metadata['modifiedTime'].replace('Z', '+00:00'))

        metadata = DocumentMetadata(
            id=doc_id,
            title=title,
            content_type=DocumentType.TEXT,
            storage_backend=StorageBackend.GOOGLE_DRIVE,
            external_id=external_id,
            size=int(file_metadata.get('size', 0)),
            created_at=created_time,
            updated_at=modified_time,
            tags=tags or [],
            parent_folder_id=folder_id,
            mime_type=file_metadata.get('mimeType')
        )

        logger.info(f"Created document '{title}' in Google Drive")
        return metadata

    def _create_notion_document(self, user_id: int, title: str, content: str,
                               tags: Optional[List[str]] = None,
                               database_id: Optional[str] = None) -> Optional[DocumentMetadata]:
        """Create a document in Notion."""
        notion_client = self._get_notion_client(user_id)
        if not notion_client:
            logger.error(f"User {user_id} not configured for Notion")
            return None

        # Use default database if none specified
        if not database_id:
            # TODO: Get or create default database for user
            # For now, we need a database ID to be provided
            logger.error("No Notion database ID provided")
            return None

        # Create page in Notion
        external_id = notion_client.create_page(
            database_id=database_id,
            title=title,
            content=content,
            tags=tags
        )

        if not external_id:
            return None

        # Get page metadata from Notion
        page_data = notion_client.get_page(external_id)
        if not page_data:
            return None

        # Create document metadata
        doc_id = str(uuid.uuid4())
        created_time = datetime.fromisoformat(page_data['created_time'].replace('Z', '+00:00'))
        modified_time = datetime.fromisoformat(page_data['last_edited_time'].replace('Z', '+00:00'))

        metadata = DocumentMetadata(
            id=doc_id,
            title=title,
            content_type=DocumentType.TEXT,
            storage_backend=StorageBackend.NOTION,
            external_id=external_id,
            created_at=created_time,
            updated_at=modified_time,
            tags=tags or [],
            parent_folder_id=database_id,
            url=page_data.get('url')
        )

        logger.info(f"Created document '{title}' in Notion")
        return metadata

    def get_document(self, user_id: int, document_id: str,
                    backend: StorageBackend, use_cache: bool = True) -> Optional[Document]:
        """
        Get a document by ID.

        Args:
            user_id (int): Telegram user ID.
            document_id (str): Document ID.
            backend (StorageBackend): Storage backend.
            use_cache (bool): Whether to use cached document if available.

        Returns:
            Optional[Document]: Document with content or None if not found.
        """
        try:
            # Check cache first if enabled
            if use_cache and self.storage_manager.is_cache_valid(document_id, backend):
                cached_doc = self.storage_manager.get_cached_document(document_id, backend)
                if cached_doc:
                    logger.info(f"Retrieved document '{document_id}' from cache")
                    return cached_doc

            # Get from backend
            document = None
            if backend == StorageBackend.GOOGLE_DRIVE:
                document = self._get_drive_document(user_id, document_id)
            elif backend == StorageBackend.NOTION:
                document = self._get_notion_document(user_id, document_id)
            else:
                # TODO: Implement local storage
                logger.warning("Local backend not yet implemented")
                return None

            # Cache document if retrieved successfully
            if document:
                self.storage_manager.cache_document(document)

            return document

        except Exception as e:
            logger.error(f"Failed to get document '{document_id}': {e}")
            return None

    def _get_drive_document(self, user_id: int, external_id: str) -> Optional[Document]:
        """Get a document from Google Drive."""
        drive_client = self._get_drive_client(user_id)
        if not drive_client:
            return None

        # Get file metadata
        file_metadata = drive_client.get_file_metadata(external_id)
        if not file_metadata:
            return None

        # Download file content
        file_content = drive_client.download_file(external_id)
        if file_content is None:
            return None

        # Create document metadata
        doc_id = str(uuid.uuid4())
        created_time = datetime.fromisoformat(file_metadata['createdTime'].replace('Z', '+00:00'))
        modified_time = datetime.fromisoformat(file_metadata['modifiedTime'].replace('Z', '+00:00'))

        metadata = DocumentMetadata(
            id=doc_id,
            title=file_metadata['name'],
            content_type=get_document_type_from_mime(file_metadata.get('mimeType', '')),
            storage_backend=StorageBackend.GOOGLE_DRIVE,
            external_id=external_id,
            size=int(file_metadata.get('size', 0)),
            created_at=created_time,
            updated_at=modified_time,
            parent_folder_id=file_metadata.get('parents', [None])[0],
            mime_type=file_metadata.get('mimeType')
        )

        # Decode text content if it's a text file
        text_content = None
        if metadata.content_type == DocumentType.TEXT:
            try:
                text_content = file_content.decode('utf-8')
            except UnicodeDecodeError:
                logger.warning(f"Failed to decode text content for file {external_id}")

        return Document(
            metadata=metadata,
            content=file_content,
            text_content=text_content
        )

    def _get_notion_document(self, user_id: int, external_id: str) -> Optional[Document]:
        """Get a document from Notion."""
        notion_client = self._get_notion_client(user_id)
        if not notion_client:
            return None

        # Get page metadata
        page_data = notion_client.get_page(external_id)
        if not page_data:
            return None

        # Get page content
        text_content = notion_client.get_page_content(external_id)
        if text_content is None:
            text_content = ""

        # Extract title from properties
        title_property = page_data.get('properties', {}).get('Title', {})
        title = ""
        if title_property.get('type') == 'title':
            title_array = title_property.get('title', [])
            if title_array:
                title = title_array[0].get('text', {}).get('content', '')

        # Extract tags from properties
        tags = []
        tags_property = page_data.get('properties', {}).get('Tags', {})
        if tags_property.get('type') == 'multi_select':
            tags = [tag['name'] for tag in tags_property.get('multi_select', [])]

        # Create document metadata
        doc_id = str(uuid.uuid4())
        created_time = datetime.fromisoformat(page_data['created_time'].replace('Z', '+00:00'))
        modified_time = datetime.fromisoformat(page_data['last_edited_time'].replace('Z', '+00:00'))

        metadata = DocumentMetadata(
            id=doc_id,
            title=title,
            content_type=DocumentType.TEXT,
            storage_backend=StorageBackend.NOTION,
            external_id=external_id,
            created_at=created_time,
            updated_at=modified_time,
            tags=tags,
            url=page_data.get('url')
        )

        return Document(
            metadata=metadata,
            content=text_content.encode('utf-8') if text_content else b'',
            text_content=text_content
        )

    def update_document(self, user_id: int, document_id: str, backend: StorageBackend,
                       title: Optional[str] = None, content: Optional[str] = None,
                       tags: Optional[List[str]] = None) -> bool:
        """
        Update a document.

        Args:
            user_id (int): Telegram user ID.
            document_id (str): Document ID (external_id for Drive).
            backend (StorageBackend): Storage backend.
            title (Optional[str]): New title.
            content (Optional[str]): New content.
            tags (Optional[List[str]]): New tags.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            success = False

            if backend == StorageBackend.GOOGLE_DRIVE:
                success = self._update_drive_document(user_id, document_id, title, content)
            elif backend == StorageBackend.NOTION:
                success = self._update_notion_document(user_id, document_id, title, content, tags)
            else:
                # TODO: Implement local storage
                logger.warning("Local backend not yet implemented")
                return False

            # Invalidate cache if update was successful
            if success:
                self.storage_manager.invalidate_cache(document_id, backend)

                # Re-cache the updated document
                updated_doc = self.get_document(user_id, document_id, backend, use_cache=False)
                if updated_doc:
                    self.storage_manager.cache_document(updated_doc)

            return success

        except Exception as e:
            logger.error(f"Failed to update document '{document_id}': {e}")
            return False

    def _update_drive_document(self, user_id: int, external_id: str,
                              title: Optional[str] = None,
                              content: Optional[str] = None) -> bool:
        """Update a document in Google Drive."""
        drive_client = self._get_drive_client(user_id)
        if not drive_client:
            return False

        metadata_update = {}
        file_content = None

        if title:
            metadata_update['name'] = f"{title}.txt"

        if content:
            file_content = content.encode('utf-8')

        return drive_client.update_file(
            file_id=external_id,
            file_content=file_content,
            metadata=metadata_update if metadata_update else None
        )

    def _update_notion_document(self, user_id: int, external_id: str,
                               title: Optional[str] = None,
                               content: Optional[str] = None,
                               tags: Optional[List[str]] = None) -> bool:
        """Update a document in Notion."""
        notion_client = self._get_notion_client(user_id)
        if not notion_client:
            return False

        return notion_client.update_page(
            page_id=external_id,
            title=title,
            content=content,
            tags=tags
        )

    def delete_document(self, user_id: int, document_id: str,
                       backend: StorageBackend) -> bool:
        """
        Delete a document.

        Args:
            user_id (int): Telegram user ID.
            document_id (str): Document ID (external_id for Drive).
            backend (StorageBackend): Storage backend.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            success = False

            if backend == StorageBackend.GOOGLE_DRIVE:
                success = self._delete_drive_document(user_id, document_id)
            elif backend == StorageBackend.NOTION:
                success = self._delete_notion_document(user_id, document_id)
            else:
                # TODO: Implement local storage
                logger.warning("Local backend not yet implemented")
                return False

            # Invalidate cache if deletion was successful
            if success:
                self.storage_manager.invalidate_cache(document_id, backend)

            return success

        except Exception as e:
            logger.error(f"Failed to delete document '{document_id}': {e}")
            return False

    def _delete_drive_document(self, user_id: int, external_id: str) -> bool:
        """Delete a document from Google Drive."""
        drive_client = self._get_drive_client(user_id)
        if not drive_client:
            return False

        return drive_client.delete_file(external_id)

    def _delete_notion_document(self, user_id: int, external_id: str) -> bool:
        """Delete a document from Notion."""
        notion_client = self._get_notion_client(user_id)
        if not notion_client:
            return False

        return notion_client.delete_page(external_id)

    def list_documents(self, user_id: int, backend: StorageBackend,
                      folder_id: Optional[str] = None,
                      max_results: int = 50) -> List[DocumentMetadata]:
        """
        List documents in a folder or root.

        Args:
            user_id (int): Telegram user ID.
            backend (StorageBackend): Storage backend.
            folder_id (Optional[str]): Folder ID to list from.
            max_results (int): Maximum number of results.

        Returns:
            List[DocumentMetadata]: List of document metadata.
        """
        try:
            if backend == StorageBackend.GOOGLE_DRIVE:
                return self._list_drive_documents(user_id, folder_id, max_results)
            elif backend == StorageBackend.NOTION:
                return self._list_notion_documents(user_id, folder_id, max_results)
            else:
                # TODO: Implement local storage
                logger.warning("Local backend not yet implemented")
                return []

        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []

    def _list_drive_documents(self, user_id: int, folder_id: Optional[str] = None,
                             max_results: int = 50) -> List[DocumentMetadata]:
        """List documents from Google Drive."""
        drive_client = self._get_drive_client(user_id)
        if not drive_client:
            return []

        # If no folder specified, use app folder
        if not folder_id:
            folder_id = drive_client.create_app_folder()
            if not folder_id:
                return []

        files = drive_client.list_files(parent_id=folder_id, max_results=max_results)
        documents = []

        for file_data in files:
            # Skip folders
            if file_data.get('mimeType') == 'application/vnd.google-apps.folder':
                continue

            doc_id = str(uuid.uuid4())
            created_time = datetime.fromisoformat(file_data['createdTime'].replace('Z', '+00:00'))
            modified_time = datetime.fromisoformat(file_data['modifiedTime'].replace('Z', '+00:00'))

            metadata = DocumentMetadata(
                id=doc_id,
                title=file_data['name'],
                content_type=get_document_type_from_mime(file_data.get('mimeType', '')),
                storage_backend=StorageBackend.GOOGLE_DRIVE,
                external_id=file_data['id'],
                size=int(file_data.get('size', 0)),
                created_at=created_time,
                updated_at=modified_time,
                parent_folder_id=file_data.get('parents', [None])[0],
                mime_type=file_data.get('mimeType')
            )

            documents.append(metadata)

        return documents

    def search_documents(self, user_id: int, query: str,
                        backend: StorageBackend,
                        max_results: int = 50) -> SearchResult:
        """
        Search for documents.

        Args:
            user_id (int): Telegram user ID.
            query (str): Search query.
            backend (StorageBackend): Storage backend.
            max_results (int): Maximum number of results.

        Returns:
            SearchResult: Search results.
        """
        start_time = datetime.now()

        try:
            if backend == StorageBackend.GOOGLE_DRIVE:
                documents = self._search_drive_documents(user_id, query, max_results)
            elif backend == StorageBackend.NOTION:
                documents = self._search_notion_documents(user_id, query, max_results)
            else:
                # TODO: Implement local storage
                logger.warning("Local backend not yet implemented")
                documents = []

            search_time = int((datetime.now() - start_time).total_seconds() * 1000)

            return SearchResult(
                documents=documents,
                total_count=len(documents),
                query=query,
                search_time_ms=search_time,
                has_more=len(documents) >= max_results
            )

        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            search_time = int((datetime.now() - start_time).total_seconds() * 1000)
            return SearchResult(
                documents=[],
                total_count=0,
                query=query,
                search_time_ms=search_time
            )

    def _search_drive_documents(self, user_id: int, query: str,
                               max_results: int = 50) -> List[DocumentMetadata]:
        """Search documents in Google Drive."""
        drive_client = self._get_drive_client(user_id)
        if not drive_client:
            return []

        files = drive_client.search_files(query, max_results)
        documents = []

        for file_data in files:
            # Skip folders
            if file_data.get('mimeType') == 'application/vnd.google-apps.folder':
                continue

            doc_id = str(uuid.uuid4())
            created_time = datetime.fromisoformat(file_data['createdTime'].replace('Z', '+00:00'))
            modified_time = datetime.fromisoformat(file_data['modifiedTime'].replace('Z', '+00:00'))

            metadata = DocumentMetadata(
                id=doc_id,
                title=file_data['name'],
                content_type=get_document_type_from_mime(file_data.get('mimeType', '')),
                storage_backend=StorageBackend.GOOGLE_DRIVE,
                external_id=file_data['id'],
                size=int(file_data.get('size', 0)),
                created_at=created_time,
                updated_at=modified_time,
                parent_folder_id=file_data.get('parents', [None])[0],
                mime_type=file_data.get('mimeType')
            )

            documents.append(metadata)

        return documents

    def get_storage_quota(self, user_id: int, backend: StorageBackend) -> Optional[StorageQuota]:
        """
        Get storage quota information.

        Args:
            user_id (int): Telegram user ID.
            backend (StorageBackend): Storage backend.

        Returns:
            Optional[StorageQuota]: Storage quota information or None if unavailable.
        """
        try:
            if backend == StorageBackend.GOOGLE_DRIVE:
                return self._get_drive_quota(user_id)
            elif backend == StorageBackend.NOTION:
                # TODO: Implement Notion quota check
                logger.warning("Notion backend not yet implemented")
                return None
            else:
                # TODO: Implement local storage quota
                logger.warning("Local backend not yet implemented")
                return None

        except Exception as e:
            logger.error(f"Failed to get storage quota: {e}")
            return None

    def _get_drive_quota(self, user_id: int) -> Optional[StorageQuota]:
        """Get Google Drive storage quota."""
        drive_client = self._get_drive_client(user_id)
        if not drive_client:
            return None

        try:
            about = drive_client.service.about().get(fields='storageQuota').execute()
            quota = about.get('storageQuota', {})

            total_bytes = int(quota.get('limit', 0))
            used_bytes = int(quota.get('usage', 0))
            available_bytes = total_bytes - used_bytes

            return StorageQuota(
                total_bytes=total_bytes,
                used_bytes=used_bytes,
                available_bytes=available_bytes,
                storage_backend=StorageBackend.GOOGLE_DRIVE
            )

        except Exception as e:
            logger.error(f"Failed to get Drive quota: {e}")
            return None
    def _list_notion_documents(self, user_id: int, database_id: Optional[str] = None,
                              max_results: int = 50) -> List[DocumentMetadata]:
        """List documents from Notion."""
        notion_client = self._get_notion_client(user_id)
        if not notion_client:
            return []

        if not database_id:
            # TODO: Get default database for user
            logger.error("No Notion database ID provided")
            return []

        pages = notion_client.query_database(database_id, max_results=max_results)
        documents = []

        for page_data in pages:
            # Extract title from properties
            title_property = page_data.get('properties', {}).get('Title', {})
            title = ""
            if title_property.get('type') == 'title':
                title_array = title_property.get('title', [])
                if title_array:
                    title = title_array[0].get('text', {}).get('content', '')

            # Extract tags from properties
            tags = []
            tags_property = page_data.get('properties', {}).get('Tags', {})
            if tags_property.get('type') == 'multi_select':
                tags = [tag['name'] for tag in tags_property.get('multi_select', [])]

            doc_id = str(uuid.uuid4())
            created_time = datetime.fromisoformat(page_data['created_time'].replace('Z', '+00:00'))
            modified_time = datetime.fromisoformat(page_data['last_edited_time'].replace('Z', '+00:00'))

            metadata = DocumentMetadata(
                id=doc_id,
                title=title,
                content_type=DocumentType.TEXT,
                storage_backend=StorageBackend.NOTION,
                external_id=page_data['id'],
                created_at=created_time,
                updated_at=modified_time,
                tags=tags,
                parent_folder_id=database_id,
                url=page_data.get('url')
            )

            documents.append(metadata)

        return documents

    def _search_notion_documents(self, user_id: int, query: str,
                                max_results: int = 50) -> List[DocumentMetadata]:
        """Search documents in Notion."""
        notion_client = self._get_notion_client(user_id)
        if not notion_client:
            return []

        pages = notion_client.search_pages(query, max_results)
        documents = []

        for page_data in pages:
            # Skip databases, only include pages
            if page_data.get('object') != 'page':
                continue

            # Extract title from properties
            title_property = page_data.get('properties', {}).get('Title', {})
            title = ""
            if title_property.get('type') == 'title':
                title_array = title_property.get('title', [])
                if title_array:
                    title = title_array[0].get('text', {}).get('content', '')

            # Extract tags from properties
            tags = []
            tags_property = page_data.get('properties', {}).get('Tags', {})
            if tags_property.get('type') == 'multi_select':
                tags = [tag['name'] for tag in tags_property.get('multi_select', [])]

            doc_id = str(uuid.uuid4())
            created_time = datetime.fromisoformat(page_data['created_time'].replace('Z', '+00:00'))
            modified_time = datetime.fromisoformat(page_data['last_edited_time'].replace('Z', '+00:00'))

            metadata = DocumentMetadata(
                id=doc_id,
                title=title,
                content_type=DocumentType.TEXT,
                storage_backend=StorageBackend.NOTION,
                external_id=page_data['id'],
                created_at=created_time,
                updated_at=modified_time,
                tags=tags,
                url=page_data.get('url')
            )

            documents.append(metadata)

        return documents
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict[str, Any]: Cache statistics.
        """
        return self.storage_manager.get_cache_stats()

    def clear_cache(self, backend: Optional[StorageBackend] = None):
        """
        Clear document cache.

        Args:
            backend (Optional[StorageBackend]): Storage backend to clear cache for.
                If None, clears cache for all backends.
        """
        self.storage_manager.clear_cache(backend)

    def sync_documents(self, user_id: int, backend: StorageBackend) -> Tuple[int, int, int]:
        """
        Synchronize documents between local cache and remote backend.

        Args:
            user_id (int): Telegram user ID.
            backend (StorageBackend): Storage backend.

        Returns:
            Tuple[int, int, int]: (total_synced, added, updated)
        """
        try:
            # Get cached documents
            cached_docs = self.storage_manager.get_cached_documents_by_backend(backend)

            # Get remote documents
            remote_docs = []
            if backend == StorageBackend.GOOGLE_DRIVE:
                # For Drive, we need to get app folder first
                drive_client = self._get_drive_client(user_id)
                if drive_client:
                    folder_id = drive_client.create_app_folder()
                    if folder_id:
                        remote_docs = self.list_documents(user_id, backend, folder_id)
            elif backend == StorageBackend.NOTION:
                # For Notion, we need a database ID
                # This is a limitation - we can't sync all Notion documents without a database ID
                logger.warning("Notion sync requires a database ID")
                return (0, 0, 0)

            # Track sync statistics
            total_synced = 0
            added = 0
            updated = 0

            # Process remote documents
            for remote_doc_meta in remote_docs:
                # Check if document exists in cache
                cached = False
                for cached_doc_meta in cached_docs:
                    if cached_doc_meta.external_id == remote_doc_meta.external_id:
                        cached = True
                        # Check if document needs update
                        if (cached_doc_meta.updated_at is None or
                            remote_doc_meta.updated_at is None or
                            remote_doc_meta.updated_at > cached_doc_meta.updated_at):
                            # Get remote document
                            remote_doc = self.get_document(
                                user_id, remote_doc_meta.external_id, backend, use_cache=False
                            )
                            if remote_doc:
                                # Cache document
                                self.storage_manager.cache_document(remote_doc)
                                updated += 1
                                total_synced += 1
                        break

                # If document doesn't exist in cache, add it
                if not cached:
                    remote_doc = self.get_document(
                        user_id, remote_doc_meta.external_id, backend, use_cache=False
                    )
                    if remote_doc:
                        # Cache document
                        self.storage_manager.cache_document(remote_doc)
                        added += 1
                        total_synced += 1

            logger.info(f"Synced {total_synced} documents ({added} added, {updated} updated)")
            return (total_synced, added, updated)

        except Exception as e:
            logger.error(f"Failed to sync documents: {e}")
            return (0, 0, 0)
