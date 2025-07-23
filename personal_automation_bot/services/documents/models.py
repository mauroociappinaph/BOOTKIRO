"""
Data models for document management.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class StorageBackend(Enum):
    """Supported storage backends."""
    GOOGLE_DRIVE = "google_drive"
    NOTION = "notion"
    LOCAL = "local"


class DocumentType(Enum):
    """Document types."""
    TEXT = "text"
    IMAGE = "image"
    PDF = "pdf"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    OTHER = "other"


@dataclass
class DocumentMetadata:
    """
    Metadata for a document.
    """
    id: str
    title: str
    content_type: DocumentType
    storage_backend: StorageBackend
    external_id: str  # ID in the external storage system
    size: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
    parent_folder_id: Optional[str] = None
    mime_type: Optional[str] = None
    url: Optional[str] = None
    is_shared: bool = False
    permissions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'title': self.title,
            'content_type': self.content_type.value,
            'storage_backend': self.storage_backend.value,
            'external_id': self.external_id,
            'size': self.size,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'tags': self.tags,
            'description': self.description,
            'parent_folder_id': self.parent_folder_id,
            'mime_type': self.mime_type,
            'url': self.url,
            'is_shared': self.is_shared,
            'permissions': self.permissions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DocumentMetadata':
        """Create from dictionary representation."""
        return cls(
            id=data['id'],
            title=data['title'],
            content_type=DocumentType(data['content_type']),
            storage_backend=StorageBackend(data['storage_backend']),
            external_id=data['external_id'],
            size=data.get('size'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            tags=data.get('tags', []),
            description=data.get('description'),
            parent_folder_id=data.get('parent_folder_id'),
            mime_type=data.get('mime_type'),
            url=data.get('url'),
            is_shared=data.get('is_shared', False),
            permissions=data.get('permissions', {})
        )


@dataclass
class Document:
    """
    Represents a document with its content and metadata.
    """
    metadata: DocumentMetadata
    content: Optional[bytes] = None
    text_content: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            'metadata': self.metadata.to_dict(),
            'text_content': self.text_content
        }
        # Don't include binary content in dict representation
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create from dictionary representation."""
        return cls(
            metadata=DocumentMetadata.from_dict(data['metadata']),
            text_content=data.get('text_content')
        )


@dataclass
class FolderMetadata:
    """
    Metadata for a folder.
    """
    id: str
    name: str
    storage_backend: StorageBackend
    external_id: str
    parent_folder_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    description: Optional[str] = None
    is_shared: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'storage_backend': self.storage_backend.value,
            'external_id': self.external_id,
            'parent_folder_id': self.parent_folder_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'description': self.description,
            'is_shared': self.is_shared
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FolderMetadata':
        """Create from dictionary representation."""
        return cls(
            id=data['id'],
            name=data['name'],
            storage_backend=StorageBackend(data['storage_backend']),
            external_id=data['external_id'],
            parent_folder_id=data.get('parent_folder_id'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            description=data.get('description'),
            is_shared=data.get('is_shared', False)
        )


@dataclass
class SearchResult:
    """
    Result from a document search operation.
    """
    documents: List[DocumentMetadata]
    total_count: int
    query: str
    search_time_ms: int
    has_more: bool = False
    next_page_token: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'documents': [doc.to_dict() for doc in self.documents],
            'total_count': self.total_count,
            'query': self.query,
            'search_time_ms': self.search_time_ms,
            'has_more': self.has_more,
            'next_page_token': self.next_page_token
        }


@dataclass
class StorageQuota:
    """
    Storage quota information.
    """
    total_bytes: int
    used_bytes: int
    available_bytes: int
    storage_backend: StorageBackend

    @property
    def usage_percentage(self) -> float:
        """Calculate usage percentage."""
        if self.total_bytes == 0:
            return 0.0
        return (self.used_bytes / self.total_bytes) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'total_bytes': self.total_bytes,
            'used_bytes': self.used_bytes,
            'available_bytes': self.available_bytes,
            'storage_backend': self.storage_backend.value,
            'usage_percentage': self.usage_percentage
        }


def get_document_type_from_mime(mime_type: str) -> DocumentType:
    """
    Determine document type from MIME type.

    Args:
        mime_type (str): MIME type string.

    Returns:
        DocumentType: Corresponding document type.
    """
    mime_type = mime_type.lower()

    if mime_type.startswith('text/'):
        return DocumentType.TEXT
    elif mime_type.startswith('image/'):
        return DocumentType.IMAGE
    elif mime_type == 'application/pdf':
        return DocumentType.PDF
    elif mime_type in [
        'application/vnd.google-apps.document',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/msword'
    ]:
        return DocumentType.DOCUMENT
    elif mime_type in [
        'application/vnd.google-apps.spreadsheet',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel'
    ]:
        return DocumentType.SPREADSHEET
    elif mime_type in [
        'application/vnd.google-apps.presentation',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.ms-powerpoint'
    ]:
        return DocumentType.PRESENTATION
    else:
        return DocumentType.OTHER


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes (int): Size in bytes.

    Returns:
        str: Formatted size string.
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"
