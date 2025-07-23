"""
Google Drive API client for document storage and management.
"""
import logging
import mimetypes
from typing import List, Dict, Any, Optional, BinaryIO
from io import BytesIO

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)


class GoogleDriveClient:
    """
    Client for interacting with Google Drive API.
    """

    def __init__(self, credentials: Credentials):
        """
        Initialize the Google Drive client.

        Args:
            credentials (Credentials): Google OAuth2 credentials.
        """
        self.credentials = credentials
        self.service = build('drive', 'v3', credentials=credentials)

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """
        Create a folder in Google Drive.

        Args:
            name (str): Name of the folder.
            parent_id (Optional[str]): ID of the parent folder. If None, creates in root.

        Returns:
            Optional[str]: ID of the created folder, or None if creation failed.
        """
        try:
            folder_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }

            if parent_id:
                folder_metadata['parents'] = [parent_id]

            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()

            folder_id = folder.get('id')
            logger.info(f"Created folder '{name}' with ID: {folder_id}")
            return folder_id

        except HttpError as e:
            logger.error(f"Failed to create folder '{name}': {e}")
            return None

    def upload_file(self, file_content: bytes, filename: str,
                   parent_id: Optional[str] = None,
                   mime_type: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to Google Drive.

        Args:
            file_content (bytes): Content of the file to upload.
            filename (str): Name of the file.
            parent_id (Optional[str]): ID of the parent folder.
            mime_type (Optional[str]): MIME type of the file. Auto-detected if None.

        Returns:
            Optional[str]: ID of the uploaded file, or None if upload failed.
        """
        try:
            if mime_type is None:
                mime_type, _ = mimetypes.guess_type(filename)
                if mime_type is None:
                    mime_type = 'application/octet-stream'

            file_metadata = {'name': filename}
            if parent_id:
                file_metadata['parents'] = [parent_id]

            media = MediaIoBaseUpload(
                BytesIO(file_content),
                mimetype=mime_type,
                resumable=True
            )

            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            file_id = file.get('id')
            logger.info(f"Uploaded file '{filename}' with ID: {file_id}")
            return file_id

        except HttpError as e:
            logger.error(f"Failed to upload file '{filename}': {e}")
            return None

    def download_file(self, file_id: str) -> Optional[bytes]:
        """
        Download a file from Google Drive.

        Args:
            file_id (str): ID of the file to download.

        Returns:
            Optional[bytes]: File content, or None if download failed.
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_io = BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)

            done = False
            while done is False:
                status, done = downloader.next_chunk()

            file_content = file_io.getvalue()
            logger.info(f"Downloaded file with ID: {file_id}")
            return file_content

        except HttpError as e:
            logger.error(f"Failed to download file with ID '{file_id}': {e}")
            return None

    def list_files(self, parent_id: Optional[str] = None,
                   query: Optional[str] = None,
                   max_results: int = 100) -> List[Dict[str, Any]]:
        """
        List files in Google Drive.

        Args:
            parent_id (Optional[str]): ID of the parent folder. If None, lists from root.
            query (Optional[str]): Search query to filter files.
            max_results (int): Maximum number of results to return.

        Returns:
            List[Dict[str, Any]]: List of file metadata.
        """
        try:
            # Build query
            query_parts = []

            if parent_id:
                query_parts.append(f"'{parent_id}' in parents")

            if query:
                query_parts.append(query)

            # Exclude trashed files
            query_parts.append("trashed=false")

            full_query = " and ".join(query_parts)

            results = self.service.files().list(
                q=full_query,
                pageSize=max_results,
                fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime, parents)"
            ).execute()

            files = results.get('files', [])
            logger.info(f"Listed {len(files)} files")
            return files

        except HttpError as e:
            logger.error(f"Failed to list files: {e}")
            return []

    def search_files(self, search_term: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for files by name or content.

        Args:
            search_term (str): Term to search for.
            max_results (int): Maximum number of results to return.

        Returns:
            List[Dict[str, Any]]: List of matching file metadata.
        """
        try:
            query = f"name contains '{search_term}' or fullText contains '{search_term}'"
            return self.list_files(query=query, max_results=max_results)

        except Exception as e:
            logger.error(f"Failed to search files for term '{search_term}': {e}")
            return []

    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific file.

        Args:
            file_id (str): ID of the file.

        Returns:
            Optional[Dict[str, Any]]: File metadata, or None if not found.
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, createdTime, modifiedTime, parents, description"
            ).execute()

            logger.info(f"Retrieved metadata for file: {file.get('name')}")
            return file

        except HttpError as e:
            logger.error(f"Failed to get metadata for file ID '{file_id}': {e}")
            return None

    def update_file(self, file_id: str, file_content: Optional[bytes] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a file in Google Drive.

        Args:
            file_id (str): ID of the file to update.
            file_content (Optional[bytes]): New content for the file.
            metadata (Optional[Dict[str, Any]]): New metadata for the file.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            update_kwargs = {'fileId': file_id}

            if metadata:
                update_kwargs['body'] = metadata

            if file_content:
                media = MediaIoBaseUpload(
                    BytesIO(file_content),
                    mimetype='application/octet-stream',
                    resumable=True
                )
                update_kwargs['media_body'] = media

            self.service.files().update(**update_kwargs).execute()
            logger.info(f"Updated file with ID: {file_id}")
            return True

        except HttpError as e:
            logger.error(f"Failed to update file with ID '{file_id}': {e}")
            return False

    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive.

        Args:
            file_id (str): ID of the file to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            logger.info(f"Deleted file with ID: {file_id}")
            return True

        except HttpError as e:
            logger.error(f"Failed to delete file with ID '{file_id}': {e}")
            return False

    def create_app_folder(self, app_name: str = "PersonalAutomationBot") -> Optional[str]:
        """
        Create or get the application folder in Google Drive.

        Args:
            app_name (str): Name of the application folder.

        Returns:
            Optional[str]: ID of the application folder.
        """
        try:
            # Search for existing app folder
            existing_folders = self.list_files(
                query=f"name='{app_name}' and mimeType='application/vnd.google-apps.folder'"
            )

            if existing_folders:
                folder_id = existing_folders[0]['id']
                logger.info(f"Found existing app folder with ID: {folder_id}")
                return folder_id

            # Create new app folder
            folder_id = self.create_folder(app_name)
            if folder_id:
                logger.info(f"Created new app folder with ID: {folder_id}")

            return folder_id

        except Exception as e:
            logger.error(f"Failed to create/get app folder: {e}")
            return None
