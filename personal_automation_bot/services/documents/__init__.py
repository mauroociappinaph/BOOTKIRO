"""
Document management service for Personal Automation Bot.

This module provides document storage and management capabilities
across different backends including Google Drive and Notion.
"""

from .document_service import DocumentService
from .drive_client import GoogleDriveClient
from .notion_client import NotionClient
from .storage_manager import StorageManager
from .models import (
    Document,
    DocumentMetadata,
    FolderMetadata,
    SearchResult,
    StorageQuota,
    StorageBackend,
    DocumentType,
    get_document_type_from_mime,
    format_file_size
)

__all__ = [
    'DocumentService',
    'GoogleDriveClient',
    'NotionClient',
    'StorageManager',
    'Document',
    'DocumentMetadata',
    'FolderMetadata',
    'SearchResult',
    'StorageQuota',
    'StorageBackend',
    'DocumentType',
    'get_document_type_from_mime',
    'format_file_size'
]
