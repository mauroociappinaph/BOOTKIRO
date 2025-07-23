#!/usr/bin/env python3
"""
Test script for the unified storage system.
"""
import sys
import os
import asyncio
import tempfile
import shutil
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from personal_automation_bot.services.documents import (
    DocumentService, StorageManager, StorageBackend, Document, DocumentMetadata, DocumentType
)


async def test_storage_manager():
    """Test the storage manager."""
    print("🔧 Testing Storage Manager")
    print("=" * 50)

    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Using temporary directory: {temp_dir}")

    try:
        # Initialize storage manager with test directory
        storage_manager = StorageManager(cache_dir=temp_dir)
        print("✅ Storage manager initialized")

        # Create test document
        doc_id = "test-doc-123"
        backend = StorageBackend.GOOGLE_DRIVE

        metadata = DocumentMetadata(
            id="internal-id-123",
            title="Test Document",
            content_type=DocumentType.TEXT,
            storage_backend=backend,
            external_id=doc_id,
            size=100,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["test", "storage"]
        )

        content = "This is a test document for storage manager testing.".encode('utf-8')

        document = Document(
            metadata=metadata,
            content=content,
            text_content=content.decode('utf-8')
        )

        # Test caching document
        print("\n📝 Testing document caching...")
        storage_manager.cache_document(document)
        print("✅ Document cached")

        # Test cache validity
        print("\n🔍 Testing cache validity...")
        is_valid = storage_manager.is_cache_valid(doc_id, backend)
        print(f"✅ Cache validity: {is_valid}")

        # Test retrieving cached document
        print("\n📖 Testing document retrieval from cache...")
        cached_doc = storage_manager.get_cached_document(doc_id, backend)

        if cached_doc:
            print("✅ Document retrieved from cache")
            print(f"   Title: {cached_doc.metadata.title}")
            print(f"   Content: {cached_doc.text_content}")
        else:
            print("❌ Failed to retrieve document from cache")

        # Test cache stats
        print("\n📊 Testing cache statistics...")
        stats = storage_manager.get_cache_stats()
        print(f"✅ Cache stats: {stats}")

        # Test invalidating cache
        print("\n🗑️ Testing cache invalidation...")
        storage_manager.invalidate_cache(doc_id, backend)
        is_valid_after = storage_manager.is_cache_valid(doc_id, backend)
        print(f"✅ Cache validity after invalidation: {is_valid_after}")

        # Test clear cache
        print("\n🧹 Testing clear cache...")

        # Add another document first
        doc_id2 = "test-doc-456"
        metadata2 = DocumentMetadata(
            id="internal-id-456",
            title="Test Document 2",
            content_type=DocumentType.TEXT,
            storage_backend=backend,
            external_id=doc_id2,
            size=200,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["test", "storage", "second"]
        )

        content2 = "This is another test document.".encode('utf-8')

        document2 = Document(
            metadata=metadata2,
            content=content2,
            text_content=content2.decode('utf-8')
        )

        storage_manager.cache_document(document2)
        print("✅ Second document cached")

        # Clear cache for specific backend
        storage_manager.clear_cache(backend)
        stats_after = storage_manager.get_cache_stats()
        print(f"✅ Cache stats after clearing: {stats_after}")

        print("\n🎉 Storage manager test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        print(f"🧹 Cleaned up temporary directory")


async def test_document_service_with_cache():
    """Test document service with caching."""
    print("\n\n🔧 Testing Document Service with Cache")
    print("=" * 50)

    # Test user ID (you can change this)
    test_user_id = 123456789

    # Initialize document service
    doc_service = DocumentService()

    # Check authentication status
    print(f"📋 Checking authentication for user {test_user_id}...")
    is_authenticated = doc_service.is_user_authenticated(test_user_id, StorageBackend.GOOGLE_DRIVE)

    if not is_authenticated:
        print("❌ User is not authenticated with Google Drive")
        print("💡 Please run the bot and authenticate first using /auth command")
        return False

    print("✅ User is authenticated with Google Drive")

    try:
        # Test creating a document
        print("\n📝 Testing document creation...")
        test_title = f"Cache Test Document {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_content = f"""This is a test document for cache testing.

Created at: {datetime.now().isoformat()}

This document tests the caching functionality.
"""

        doc_metadata = doc_service.create_document(
            user_id=test_user_id,
            title=test_title,
            content=test_content,
            backend=StorageBackend.GOOGLE_DRIVE,
            tags=["test", "cache"]
        )

        if not doc_metadata:
            print("❌ Failed to create document")
            return False

        print(f"✅ Document created successfully!")
        print(f"   Title: {doc_metadata.title}")
        print(f"   ID: {doc_metadata.external_id}")

        # Test retrieving document (should cache it)
        print("\n📖 Testing first document retrieval (should cache)...")
        start_time = datetime.now()
        doc1 = doc_service.get_document(
            user_id=test_user_id,
            document_id=doc_metadata.external_id,
            backend=StorageBackend.GOOGLE_DRIVE
        )
        time1 = (datetime.now() - start_time).total_seconds()

        if not doc1:
            print("❌ Failed to retrieve document")
            return False

        print(f"✅ Document retrieved in {time1:.3f} seconds")

        # Test retrieving document again (should use cache)
        print("\n📖 Testing second document retrieval (should use cache)...")
        start_time = datetime.now()
        doc2 = doc_service.get_document(
            user_id=test_user_id,
            document_id=doc_metadata.external_id,
            backend=StorageBackend.GOOGLE_DRIVE
        )
        time2 = (datetime.now() - start_time).total_seconds()

        if not doc2:
            print("❌ Failed to retrieve document from cache")
            return False

        print(f"✅ Document retrieved in {time2:.3f} seconds")
        print(f"   Cache speedup: {time1/time2:.1f}x faster")

        # Test cache stats
        print("\n📊 Testing cache statistics...")
        stats = doc_service.get_cache_stats()
        print(f"✅ Cache stats: {stats}")

        # Test updating document (should invalidate cache)
        print("\n✏️ Testing document update (should invalidate cache)...")
        updated_content = test_content + f"\n\nUpdated at: {datetime.now().isoformat()}"
        update_success = doc_service.update_document(
            user_id=test_user_id,
            document_id=doc_metadata.external_id,
            backend=StorageBackend.GOOGLE_DRIVE,
            content=updated_content
        )

        if not update_success:
            print("❌ Failed to update document")
            return False

        print("✅ Document updated successfully")

        # Test retrieving updated document
        print("\n📖 Testing retrieval of updated document...")
        updated_doc = doc_service.get_document(
            user_id=test_user_id,
            document_id=doc_metadata.external_id,
            backend=StorageBackend.GOOGLE_DRIVE
        )

        if not updated_doc or "Updated at:" not in updated_doc.text_content:
            print("❌ Failed to retrieve updated document")
            return False

        print("✅ Updated document retrieved successfully")
        print(f"   Content contains update: {'Updated at:' in updated_doc.text_content}")

        # Test document sync
        print("\n🔄 Testing document synchronization...")
        total, added, updated = doc_service.sync_documents(
            user_id=test_user_id,
            backend=StorageBackend.GOOGLE_DRIVE
        )

        print(f"✅ Sync completed: {total} documents synced ({added} added, {updated} updated)")

        # Clean up - delete the test document
        print(f"\n🗑️ Cleaning up test document...")
        delete_success = doc_service.delete_document(
            user_id=test_user_id,
            document_id=doc_metadata.external_id,
            backend=StorageBackend.GOOGLE_DRIVE
        )

        if delete_success:
            print("✅ Test document deleted successfully!")
        else:
            print("❌ Failed to delete test document")

        # Clear cache
        print("\n🧹 Testing clear cache...")
        doc_service.clear_cache(StorageBackend.GOOGLE_DRIVE)
        stats_after = doc_service.get_cache_stats()
        print(f"✅ Cache stats after clearing: {stats_after}")

        print("\n🎉 Document service cache test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success1 = asyncio.run(test_storage_manager())
    success2 = asyncio.run(test_document_service_with_cache())
    sys.exit(0 if success1 and success2 else 1)
