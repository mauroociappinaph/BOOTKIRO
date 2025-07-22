"""
Base conversation system for multi-step interactions.
"""
from enum import Enum
from typing import Dict, Any

class ConversationState(Enum):
    """
    Enumeration of conversation states.
    """
    # Email conversation states
    EMAIL_SEND_TO = "email_send_to"
    EMAIL_SEND_SUBJECT = "email_send_subject"
    EMAIL_SEND_BODY = "email_send_body"
    EMAIL_SEND_CONFIRM = "email_send_confirm"

    # Calendar conversation states
    CALENDAR_CREATE_TITLE = "calendar_create_title"
    CALENDAR_CREATE_DATE = "calendar_create_date"
    CALENDAR_CREATE_TIME = "calendar_create_time"
    CALENDAR_CREATE_DESCRIPTION = "calendar_create_description"
    CALENDAR_CREATE_CONFIRM = "calendar_create_confirm"

    # Content generation conversation states
    CONTENT_TEXT_PROMPT = "content_text_prompt"
    CONTENT_TEXT_STYLE = "content_text_style"
    CONTENT_IMAGE_PROMPT = "content_image_prompt"
    CONTENT_IMAGE_STYLE = "content_image_style"

    # General states
    WAITING_FOR_INPUT = "waiting_for_input"
    CONFIRMING_ACTION = "confirming_action"

class ConversationData:
    """
    Class to store conversation data for users.
    """
    def __init__(self):
        self.user_data: Dict[int, Dict[str, Any]] = {}

    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get conversation data for a specific user.

        Args:
            user_id (int): The user ID.

        Returns:
            Dict[str, Any]: The user's conversation data.
        """
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        return self.user_data[user_id]

    def set_user_state(self, user_id: int, state: ConversationState):
        """
        Set the conversation state for a user.

        Args:
            user_id (int): The user ID.
            state (ConversationState): The conversation state.
        """
        user_data = self.get_user_data(user_id)
        user_data['state'] = state

    def get_user_state(self, user_id: int) -> ConversationState:
        """
        Get the conversation state for a user.

        Args:
            user_id (int): The user ID.

        Returns:
            ConversationState: The user's conversation state, or None if not set.
        """
        user_data = self.get_user_data(user_id)
        return user_data.get('state')

    def clear_user_data(self, user_id: int):
        """
        Clear all conversation data for a user.

        Args:
            user_id (int): The user ID.
        """
        if user_id in self.user_data:
            del self.user_data[user_id]

    def set_user_field(self, user_id: int, field: str, value: Any):
        """
        Set a specific field in the user's conversation data.

        Args:
            user_id (int): The user ID.
            field (str): The field name.
            value (Any): The field value.
        """
        user_data = self.get_user_data(user_id)
        user_data[field] = value

    def get_user_field(self, user_id: int, field: str, default: Any = None) -> Any:
        """
        Get a specific field from the user's conversation data.

        Args:
            user_id (int): The user ID.
            field (str): The field name.
            default (Any): Default value if field doesn't exist.

        Returns:
            Any: The field value or default.
        """
        user_data = self.get_user_data(user_id)
        return user_data.get(field, default)

# Global conversation data instance
conversation_data = ConversationData()
