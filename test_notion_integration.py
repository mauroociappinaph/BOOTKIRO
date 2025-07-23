#!/usr/bin/env python3
"""
Test script for Notion integration.
"""
import sys
import os
import asyncio
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from personal_automation_bot.services.documents import DocumentService, StorageBackend
from personal_automation_bot.config import settings


async def test_notion_integration():
    """Test Notion integration."""
    print("🔧 Testing Notion Integration")
    print("=" * 50)

    # Test user ID (you can change this)
    test_user_id = 123456789

    # Check if Notion API key is configured
    if not settings.NOTION_API_KEY:
        print("❌ Notion API key not configured")
        print("💡 Please set NOTION_API_KEY in your .env file")
        return False

    # Initialize document service
    doc_service = DocumentService()

    # Check authentication status
    print(f"📋 Checking authentication for user {test_user_id}...")
    is_authenticated = doc_service.is_user_authenticated(test_user_id, StorageBackend.NOTION)

    if not is_authenticated:
        print("❌ Notion API key not configured or invalid")
        return False

    print("✅ Notion API key is configured")

    # For Notion tests, we need a database ID
    database_id = input("Please enter a Notion database ID to test with: ")
    if not database_id:
        print("❌ No database ID provided")
        return False

    try:
        # Test creating a document
        print("\n📝 Testing document creation...")
        test_title = f"Test Document {datetime.now().strftime('%Y%m%d_%H%M%S')}"
        test_content = f"""This is a test document created by the Personal Automation Bot.

Created at: {datetime.now().isoformat()}

This document tests the Notion integration functionality.
It should be stored in the specified Notion database.

Features being tested:
- Document creation
- Content storage
- Metadata handling
- Tagging
"""

        doc_metadata = doc_service.create_document(
            user_id=test_user_id,
            title=test_title,
            content=test_content,
            backend=StorageBackend.NOTION,
            tags=["test", "automation", "bot"],
            folder_id=database_id  # In Notion, folder_id is the database_id
        )

        if doc_metadata:
            print(f"✅ Document created successfully!")
            print(f"   Title: {doc_metadata.title}")
            print(f"   ID: {doc_metadata.id}")
            print(f"   External ID: {doc_metadata.external_id}")
            print(f"   Created: {doc_metadata.created_at}")
            print(f"   URL: {doc_metadata.url}")
        else:
            print("❌ Failed to create document")
            return False

        # Test listing documents
        print("\n📂 Testing document listing...")
        documents = doc_service.list_documents(
            user_id=test_user_id,
            backend=StorageBackend.NOTION,
            folder_id=database_id,  # In Notion, folder_id is the database_id
            max_results=10
        )

        print(f"✅ Found {len(documents)} documents:")
        for i, doc in enumerate(documents[:5], 1):  # Show first 5
            print(f"   {i}. {doc.title} ({doc.content_type.value})")

        # Test retrieving the created document
        print(f"\n📖 Testing document retrieval...")
        retrieved_doc = doc_service.get_document(
            user_id=test_user_id,
            document_id=doc_metadata.external_id,
            backend=StorageBackend.NOTION
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
            backend=StorageBackend.NOTION,
            max_results=10
        )

        print(f"✅ Search completed")
        print(f"   Found {search_results.total_count} documents matching 'test':")
        for i, doc in enumerate(search_results.documents[:3], 1):  # Show first 3
            print(f"   {i}. {doc.title} ({doc.content_type.value})")

        # Test updating the document
        print(f"\n✏️ Testing document update...")
        updated_content = test_content + f"\n\nUpdated at: {datetime.now().isoformat()}"
        update_success = doc_service.update_document(
            user_id=test_user_id,
            document_id=doc_metadata.external_id,
            backend=StorageBackend.NOTION,
            title=f"{test_title} (Updated)",
            content=updated_content,
            tags=["test", "automation", "bot", "updated"]
        )

        if update_success:
            print("✅ Document updated successfully!")
        else:
            print("❌ Failed to update document")

        # Clean up - delete the test document
        print(f"\n🗑️ Cleaning up test document...")
        delete_success = doc_service.delete_document(
            user_id=test_user_id,
            document_id=doc_metadata.external_id,
            backend=StorageBackend.NOTION
        )

        if delete_success:
            print("✅ Test document deleted successfully!")
        else:
            print("❌ Failed to delete test document")

        print("\n🎉 Notion integration test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_notion_integration())
    sys.exit(0 if success else 1)
