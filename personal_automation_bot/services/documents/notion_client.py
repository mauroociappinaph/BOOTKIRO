"""
Notion API client for document storage and management.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from notion_client import Client
from notion_client.errors import APIResponseError

logger = logging.getLogger(__name__)


class NotionClient:
    """
    Client for interacting with Notion API.
    """

    def __init__(self, api_key: str):
        """
        Initialize the Notion client.

        Args:
            api_key (str): Notion API key.
        """
        self.api_key = api_key
        self.client = Client(auth=api_key)

    def create_database(self, parent_page_id: str, title: str,
                       properties: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Create a database in Notion.

        Args:
            parent_page_id (str): ID of the parent page.
            title (str): Title of the database.
            properties (Optional[Dict[str, Any]]): Database properties schema.

        Returns:
            Optional[str]: ID of the created database, or None if creation failed.
        """
        try:
            if properties is None:
                properties = {
                    "Title": {
                        "title": {}
                    },
                    "Content": {
                        "rich_text": {}
                    },
                    "Tags": {
                        "multi_select": {
                            "options": []
                        }
                    },
                    "Created": {
                        "created_time": {}
                    },
                    "Modified": {
                        "last_edited_time": {}
                    }
                }

            database = self.client.databases.create(
                parent={
                    "type": "page_id",
                    "page_id": parent_page_id
                },
                title=[
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }
                ],
                properties=properties
            )

            database_id = database['id']
            logger.info(f"Created database '{title}' with ID: {database_id}")
            return database_id

        except APIResponseError as e:
            logger.error(f"Failed to create database '{title}': {e}")
            return None

    def create_page(self, database_id: str, title: str, content: str,
                   tags: Optional[List[str]] = None) -> Optional[str]:
        """
        Create a page in a Notion database.

        Args:
            database_id (str): ID of the database.
            title (str): Title of the page.
            content (str): Content of the page.
            tags (Optional[List[str]]): Tags for the page.

        Returns:
            Optional[str]: ID of the created page, or None if creation failed.
        """
        try:
            properties = {
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                },
                "Content": {
                    "rich_text": [
                        {
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }
            }

            if tags:
                properties["Tags"] = {
                    "multi_select": [
                        {"name": tag} for tag in tags
                    ]
                }

            page = self.client.pages.create(
                parent={
                    "database_id": database_id
                },
                properties=properties
            )

            page_id = page['id']
            logger.info(f"Created page '{title}' with ID: {page_id}")
            return page_id

        except APIResponseError as e:
            logger.error(f"Failed to create page '{title}': {e}")
            return None

    def get_page(self, page_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a page from Notion.

        Args:
            page_id (str): ID of the page.

        Returns:
            Optional[Dict[str, Any]]: Page data, or None if not found.
        """
        try:
            page = self.client.pages.retrieve(page_id=page_id)
            logger.info(f"Retrieved page with ID: {page_id}")
            return page

        except APIResponseError as e:
            logger.error(f"Failed to get page with ID '{page_id}': {e}")
            return None

    def update_page(self, page_id: str, title: Optional[str] = None,
                   content: Optional[str] = None,
                   tags: Optional[List[str]] = None) -> bool:
        """
        Update a page in Notion.

        Args:
            page_id (str): ID of the page to update.
            title (Optional[str]): New title.
            content (Optional[str]): New content.
            tags (Optional[List[str]]): New tags.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            properties = {}

            if title:
                properties["Title"] = {
                    "title": [
                        {
                            "text": {
                                "content": title
                            }
                        }
                    ]
                }

            if content:
                properties["Content"] = {
                    "rich_text": [
                        {
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }

            if tags:
                properties["Tags"] = {
                    "multi_select": [
                        {"name": tag} for tag in tags
                    ]
                }

            if properties:
                self.client.pages.update(
                    page_id=page_id,
                    properties=properties
                )

            logger.info(f"Updated page with ID: {page_id}")
            return True

        except APIResponseError as e:
            logger.error(f"Failed to update page with ID '{page_id}': {e}")
            return False

    def delete_page(self, page_id: str) -> bool:
        """
        Delete (archive) a page in Notion.

        Args:
            page_id (str): ID of the page to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            self.client.pages.update(
                page_id=page_id,
                archived=True
            )

            logger.info(f"Deleted page with ID: {page_id}")
            return True

        except APIResponseError as e:
            logger.error(f"Failed to delete page with ID '{page_id}': {e}")
            return False

    def query_database(self, database_id: str, filter_conditions: Optional[Dict[str, Any]] = None,
                      sorts: Optional[List[Dict[str, Any]]] = None,
                      max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Query a database in Notion.

        Args:
            database_id (str): ID of the database.
            filter_conditions (Optional[Dict[str, Any]]): Filter conditions.
            sorts (Optional[List[Dict[str, Any]]]): Sort conditions.
            max_results (int): Maximum number of results.

        Returns:
            List[Dict[str, Any]]: List of pages matching the query.
        """
        try:
            query_params = {
                "database_id": database_id,
                "page_size": min(max_results, 100)
            }

            if filter_conditions:
                query_params["filter"] = filter_conditions

            if sorts:
                query_params["sorts"] = sorts

            response = self.client.databases.query(**query_params)
            pages = response.get('results', [])

            logger.info(f"Queried database {database_id}, found {len(pages)} pages")
            return pages

        except APIResponseError as e:
            logger.error(f"Failed to query database '{database_id}': {e}")
            return []

    def search_pages(self, query: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Search for pages by title or content.

        Args:
            query (str): Search query.
            max_results (int): Maximum number of results.

        Returns:
            List[Dict[str, Any]]: List of matching pages.
        """
        try:
            response = self.client.search(
                query=query,
                page_size=min(max_results, 100),
                filter={
                    "value": "page",
                    "property": "object"
                }
            )

            pages = response.get('results', [])
            logger.info(f"Search for '{query}' found {len(pages)} pages")
            return pages

        except APIResponseError as e:
            logger.error(f"Failed to search for '{query}': {e}")
            return []

    def get_page_content(self, page_id: str) -> Optional[str]:
        """
        Get the text content of a page.

        Args:
            page_id (str): ID of the page.

        Returns:
            Optional[str]: Text content of the page, or None if failed.
        """
        try:
            # Get page blocks
            blocks = self.client.blocks.children.list(block_id=page_id)
            content_parts = []

            for block in blocks.get('results', []):
                block_type = block.get('type')

                if block_type == 'paragraph':
                    text_content = self._extract_text_from_rich_text(
                        block.get('paragraph', {}).get('rich_text', [])
                    )
                    if text_content:
                        content_parts.append(text_content)

                elif block_type == 'heading_1':
                    text_content = self._extract_text_from_rich_text(
                        block.get('heading_1', {}).get('rich_text', [])
                    )
                    if text_content:
                        content_parts.append(f"# {text_content}")

                elif block_type == 'heading_2':
                    text_content = self._extract_text_from_rich_text(
                        block.get('heading_2', {}).get('rich_text', [])
                    )
                    if text_content:
                        content_parts.append(f"## {text_content}")

                elif block_type == 'heading_3':
                    text_content = self._extract_text_from_rich_text(
                        block.get('heading_3', {}).get('rich_text', [])
                    )
                    if text_content:
                        content_parts.append(f"### {text_content}")

            content = '\n\n'.join(content_parts)
            logger.info(f"Extracted content from page {page_id}: {len(content)} characters")
            return content

        except APIResponseError as e:
            logger.error(f"Failed to get content for page '{page_id}': {e}")
            return None

    def _extract_text_from_rich_text(self, rich_text: List[Dict[str, Any]]) -> str:
        """
        Extract plain text from Notion rich text format.

        Args:
            rich_text (List[Dict[str, Any]]): Rich text array.

        Returns:
            str: Plain text content.
        """
        text_parts = []
        for text_obj in rich_text:
            if text_obj.get('type') == 'text':
                text_parts.append(text_obj.get('text', {}).get('content', ''))

        return ''.join(text_parts)

    def get_database_info(self, database_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a database.

        Args:
            database_id (str): ID of the database.

        Returns:
            Optional[Dict[str, Any]]: Database information, or None if not found.
        """
        try:
            database = self.client.databases.retrieve(database_id=database_id)
            logger.info(f"Retrieved database info for ID: {database_id}")
            return database

        except APIResponseError as e:
            logger.error(f"Failed to get database info for ID '{database_id}': {e}")
            return None

    def create_app_database(self, parent_page_id: str,
                           app_name: str = "PersonalAutomationBot") -> Optional[str]:
        """
        Create or get the application database in Notion.

        Args:
            parent_page_id (str): ID of the parent page.
            app_name (str): Name of the application database.

        Returns:
            Optional[str]: ID of the application database.
        """
        try:
            # Search for existing app database
            search_results = self.search_pages(app_name)

            for result in search_results:
                if (result.get('object') == 'database' and
                    result.get('title', [{}])[0].get('text', {}).get('content') == app_name):
                    database_id = result['id']
                    logger.info(f"Found existing app database with ID: {database_id}")
                    return database_id

            # Create new app database
            database_id = self.create_database(parent_page_id, app_name)
            if database_id:
                logger.info(f"Created new app database with ID: {database_id}")

            return database_id

        except Exception as e:
            logger.error(f"Failed to create/get app database: {e}")
            return None
