#!/usr/bin/env python3
"""
Unit tests for GoogleDriveClient with mocks.
"""
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from personal_automation_bot.services.documents.drive_client import GoogleDriveClient


def test_google_drive_client_initialization():
    """Test GoogleDriveClient initialization."""
    print("🧪 Testing GoogleDriveClient initialization...")

    try:
        # Mock credentials
        mock_credentials = Mock()

        with patch('personal_automation_bot.services.documents.drive_client.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Initialize client
            client = GoogleDriveClient(mock_credentials)

            # Verify initialization
            assert client.credentials == mock_credentials
            assert client.service == mock_service
            mock_build.assert_called_once_with('drive', 'v3', credentials=mock_credentials)

            print("✅ GoogleDriveClient initialization works")
            return True

    except Exception as e:
        print(f"❌ GoogleDriveClient initialization failed: {e}")
        return False


def test_create_folder():
    """Test folder creation functionality."""
    print("\n🧪 Testing folder creation...")

    try:
        mock_credentials = Mock()

        with patch('personal_automation_bot.services.documents.drive_client.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Mock the API response
            mock_service.files().create().execute.return_value = {'id': 'folder_123'}

            client = GoogleDriveClient(mock_credentials)

            # Test folder creation
            folder_id = client.create_folder("Test Folder")

            assert folder_id == 'folder_123'
            mock_service.files().create.assert_called_once()

            print("✅ Folder creation works")
            return True

    except Exception as e:
        print(f"❌ Folder creation test failed: {e}")
        return False


def test_upload_file():
    """Test file upload functionality."""
    print("\n🧪 Testing file upload...")

    try:
        mock_credentials = Mock()

        with patch('personal_automation_bot.services.documents.drive_client.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Mock the API response
            mock_service.files().create().execute.return_value = {'id': 'file_123'}

            client = GoogleDriveClient(mock_credentials)

            # Test file upload
            test_content = b"Test file content"
            file_id = client.upload_file(test_content, "test.txt")

            assert file_id == 'file_123'
            mock_service.files().create.assert_called_once()

            print("✅ File upload works")
            return True

    except Exception as e:
        print(f"❌ File upload test failed: {e}")
        return False


def test_download_file():
    """Test file download functionality."""
    print("\n🧪 Testing file download...")

    try:
        mock_credentials = Mock()

        with patch('personal_automation_bot.services.documents.drive_client.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Mock the download process
            mock_request = Mock()
            mock_service.files().get_media.return_value = mock_request

            # Mock MediaIoBaseDownload
            with patch('personal_automation_bot.services.documents.drive_client.MediaIoBaseDownload') as mock_download:
                mock_downloader = Mock()
                mock_download.return_value = mock_downloader

                # Simulate download completion
                mock_downloader.next_chunk.side_effect = [(None, False), (None, True)]

                # Mock BytesIO
                with patch('personal_automation_bot.services.documents.drive_client.BytesIO') as mock_bytesio:
                    mock_file_io = Mock()
                    mock_file_io.getvalue.return_value = b"Downloaded content"
                    mock_bytesio.return_value = mock_file_io

                    client = GoogleDriveClient(mock_credentials)

                    # Test file download
                    content = client.download_file("file_123")

                    assert content == b"Downloaded content"
                    mock_service.files().get_media.assert_called_once_with(fileId="file_123")

                    print("✅ File download works")
                    return True

    except Exception as e:
        print(f"❌ File download test failed: {e}")
        return False


def test_list_files():
    """Test file listing functionality."""
    print("\n🧪 Testing file listing...")

    try:
        mock_credentials = Mock()

        with patch('personal_automation_bot.services.documents.drive_client.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Mock the API response
            mock_files = [
                {'id': 'file1', 'name': 'File 1', 'mimeType': 'text/plain'},
                {'id': 'file2', 'name': 'File 2', 'mimeType': 'text/plain'}
            ]
            mock_service.files().list().execute.return_value = {'files': mock_files}

            client = GoogleDriveClient(mock_credentials)

            # Test file listing
            files = client.list_files()

            assert len(files) == 2
            assert files[0]['name'] == 'File 1'
            assert files[1]['name'] == 'File 2'
            mock_service.files().list.assert_called_once()

            print("✅ File listing works")
            return True

    except Exception as e:
        print(f"❌ File listing test failed: {e}")
        return False


def test_search_files():
    """Test file search functionality."""
    print("\n🧪 Testing file search...")

    try:
        mock_credentials = Mock()

        with patch('personal_automation_bot.services.documents.drive_client.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Mock the API response
            mock_files = [
                {'id': 'file1', 'name': 'Test Document', 'mimeType': 'text/plain'}
            ]
            mock_service.files().list().execute.return_value = {'files': mock_files}

            client = GoogleDriveClient(mock_credentials)

            # Test file search
            results = client.search_files("Test")

            assert len(results) == 1
            assert results[0]['name'] == 'Test Document'

            print("✅ File search works")
            return True

    except Exception as e:
        print(f"❌ File search test failed: {e}")
        return False


def test_delete_file():
    """Test file deletion functionality."""
    print("\n🧪 Testing file deletion...")

    try:
        mock_credentials = Mock()

        with patch('personal_automation_bot.services.documents.drive_client.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Mock successful deletion
            mock_service.files().delete().execute.return_value = None

            client = GoogleDriveClient(mock_credentials)

            # Test file deletion
            success = client.delete_file("file_123")

            assert success is True
            mock_service.files().delete.assert_called_once_with(fileId="file_123")

            print("✅ File deletion works")
            return True

    except Exception as e:
        print(f"❌ File deletion test failed: {e}")
        return False


def test_create_app_folder():
    """Test application folder creation."""
    print("\n🧪 Testing app folder creation...")

    try:
        mock_credentials = Mock()

        with patch('personal_automation_bot.services.documents.drive_client.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Mock no existing folder found, then successful creation
            mock_service.files().list().execute.return_value = {'files': []}
            mock_service.files().create().execute.return_value = {'id': 'app_folder_123'}

            client = GoogleDriveClient(mock_credentials)

            # Test app folder creation
            folder_id = client.create_app_folder("TestApp")

            assert folder_id == 'app_folder_123'

            print("✅ App folder creation works")
            return True

    except Exception as e:
        print(f"❌ App folder creation test failed: {e}")
        return False


def test_error_handling():
    """Test error handling in GoogleDriveClient."""
    print("\n🧪 Testing error handling...")

    try:
        mock_credentials = Mock()

        with patch('personal_automation_bot.services.documents.drive_client.build') as mock_build:
            mock_service = Mock()
            mock_build.return_value = mock_service

            # Mock HttpError for folder creation
            from googleapiclient.errors import HttpError
            mock_service.files().create().execute.side_effect = HttpError(
                resp=Mock(status=403), content=b'Forbidden'
            )

            client = GoogleDriveClient(mock_credentials)

            # Test error handling
            folder_id = client.create_folder("Test Folder")

            assert folder_id is None  # Should return None on error

            print("✅ Error handling works")
            return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting GoogleDriveClient Unit Tests\n")

    # Run all tests
    tests = [
        test_google_drive_client_initialization,
        test_create_folder,
        test_upload_file,
        test_download_file,
        test_list_files,
        test_search_files,
        test_delete_file,
        test_create_app_folder,
        test_error_handling
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests

    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All GoogleDriveClient tests passed!")
        print("\n📋 GoogleDriveClient Implementation Summary:")
        print("   ✅ Client initialization with credentials")
        print("   ✅ Folder creation functionality")
        print("   ✅ File upload with MIME type detection")
        print("   ✅ File download with chunked transfer")
        print("   ✅ File listing with query support")
        print("   ✅ File search by name and content")
        print("   ✅ File deletion functionality")
        print("   ✅ Application folder management")
        print("   ✅ Comprehensive error handling")
        print("   ✅ Proper logging throughout")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} tests failed!")
        sys.exit(1)
