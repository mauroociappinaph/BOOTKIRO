#!/usr/bin/env python3
"""
Test script for Google Drive integration.
"""
import sys
import os
import asyncio
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from personal_automation_bot.services.documents import DocumentService, StorageBackend
from personal_automation_bot.utils.auth import google_auth_manager


async def test_drive_integration():
    """Test Google Drive integration."""
    print("🔧 Testing Google Drive Integration")
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
        test_title = f"Test Document {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_content = f"""This is a test document created by the Personal Automation Bot.

Created at: {datetime.now().isoformat()}

This document tests the Google Drive integration functionality.
It should be stored in the PersonalAutomationBot folder in Google Drive.

Features being tested:
- Document creation
- Content storage
- Metadata handling
- File organization
"""

        doc_metadata = doc_service.create_document(
            user_id=test_user_id,
            title=test_title,
            content=test_content,
            backend=StorageBackend.GOOGLE_DRIVE,
            tags=["test", "automation", "bot"]
        )

        if doc_metadata:
            print(f"✅ Document created successfully!")
            print(f"   Title: {doc_metadata.title}")
            print(f"   ID: {doc_metadata.id}")
            print(f"   External ID: {doc_metadata.external_id}")
            print(f"   Size: {doc_metadata.size} bytes")
            print(f"   Created: {doc_metadata.created_at}")
        else:
            print("❌ Failed to create document")
            return False

        # Test listing documents
        print("\n📂 Testing document listing...")
        documents = doc_service.list_documents(
            user_id=test_user_id,
            backend=StorageBackend.GOOGLE_DRIVE,
            max_results=10
        )

        print(f"✅ Found {len(documents)} documents:")
        for i, doc in enumerate(documents[:5], 1):  # Show first 5
            print(f"   {i}. {doc.title} ({doc.content_type.value}, {doc.size} bytes)")

        # Test retrieving the created document
        print(f"\n📖 Testing document retrieval...")
        retrieved_doc = doc_service.get_document(
            user_id=test_user_id,
            document_id=doc_metadata.external_id,
            backend=StorageBackend.GOOGLE_DRIVE
        )

        if retrieved_doc:
            print("✅ Document retrieved successfully!")
            print(f"   Title: {retrieved_doc.metadata.title}")
            print(f"   Content length: {len(retrieved_doc.text_content or '')} characters")
            print(f"   First 100 chars: {(retrieved_doc.text_content or '')[:100]}...")
        else:
            print("❌ Failed to retrieve document")

        # Test searching documents
        print(f"\n🔍 Testing document search...")
        search_results = doc_service.search_documents(
            user_id=test_user_id,
            query="test",
            backend=StorageBackend.GOOGLE_DRIVE,
            max_results=10
        )

        print(f"✅ Search completed in {search_results.search_time_ms}ms")
        print(f"   Found {search_results.total_count} documents matching 'test':")
        for i, doc in enumerate(search_results.documents[:3], 1):  # Show first 3
            print(f"   {i}. {doc.title} ({doc.content_type.value})")

        # Test updating the document
        print(f"\n✏️ Testing document update...")
        updated_content = test_content + f"\n\nUpdated at: {datetime.now().isoformat()}"
        update_success = doc_service.update_document(
            user_id=test_user_id,
            document_id=doc_metadata.external_id,
            backend=StorageBackend.GOOGLE_DRIVE,
            title=f"{test_title} (Updated)",
            content=updated_content
        )

        if update_success:
            print("✅ Document updated successfully!")
        else:
            print("❌ Failed to update document")

        # Test storage quota
        print(f"\n💾 Testing storage quota...")
        quota = doc_service.get_storage_quota(test_user_id, StorageBackend.GOOGLE_DRIVE)

        if quota:
            print("✅ Storage quota retrieved:")
            print(f"   Total: {quota.total_bytes:,} bytes")
            print(f"   Used: {quota.used_bytes:,} bytes ({quota.usage_percentage:.1f}%)")
            print(f"   Available: {quota.available_bytes:,} bytes")
        else:
            print("❌ Failed to get storage quota")

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

        print("\n🎉 Google Drive integration test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_drive_integration())
    sys.exit(0 if success else 1)
