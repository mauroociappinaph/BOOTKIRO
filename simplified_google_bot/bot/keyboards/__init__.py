"""
Keyboard utilities for the Simplified Google Bot.
"""

import logging
from typing import List, Dict, Any, Union, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Set up logger
logger = logging.getLogger(__name__)


def create_inline_keyboard(
    buttons: List[List[Dict[str, str]]],
) -> InlineKeyboardMarkup:
    """
    Create an inline keyboard from a list of button definitions.

    Args:
        buttons (List[List[Dict[str, str]]]): List of button rows, where each button is a dict
            with 'text' and one of 'callback_data', 'url', 'switch_inline_query', etc.

    Returns:
        InlineKeyboardMarkup: The configured inline keyboard
    """
    keyboard = []

    for row in buttons:
        keyboard_row = []

        for button in row:
            # Extract button properties
            text = button.get("text", "")

            # Create the appropriate button type based on the provided properties
            if "callback_data" in button:
                keyboard_row.append(InlineKeyboardButton(text, callback_data=button["callback_data"]))
            elif "url" in button:
                keyboard_row.append(InlineKeyboardButton(text, url=button["url"]))
            elif "switch_inline_query" in button:
                keyboard_row.append(InlineKeyboardButton(text, switch_inline_query=button["switch_inline_query"]))
            elif "switch_inline_query_current_chat" in button:
                keyboard_row.append(InlineKeyboardButton(
                    text, switch_inline_query_current_chat=button["switch_inline_query_current_chat"]
                ))
            else:
                logger.warning(f"Invalid button configuration: {button}")
                continue

        keyboard.append(keyboard_row)

    return InlineKeyboardMarkup(keyboard)


def create_pagination_keyboard(
    current_page: int,
    total_pages: int,
    prefix: str = "page",
) -> InlineKeyboardMarkup:
    """
    Create a pagination keyboard.

    Args:
        current_page (int): Current page number (1-based)
        total_pages (int): Total number of pages
        prefix (str, optional): Prefix for callback data. Defaults to "page".

    Returns:
        InlineKeyboardMarkup: The configured pagination keyboard
    """
    buttons = []

    # Add navigation buttons
    nav_buttons = []

    # Previous page button
    if current_page > 1:
        nav_buttons.append({
            "text": "◀️ Previous",
            "callback_data": f"{prefix}:{current_page - 1}"
        })

    # Page indicator
    nav_buttons.append({
        "text": f"{current_page}/{total_pages}",
        "callback_data": f"{prefix}:current"
    })

    # Next page button
    if current_page < total_pages:
        nav_buttons.append({
            "text": "Next ▶️",
            "callback_data": f"{prefix}:{current_page + 1}"
        })

    buttons.append(nav_buttons)

    return create_inline_keyboard(buttons)
