"""
Calendar command handlers for the Simplified Google Bot.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from simplified_google_bot.utils.auth import google_auth_manager
from simplified_google_bot.services.calendar import calendar_service, CalendarEvent
from simplified_google_bot.bot.core import register_command, register_conversation

# Set up logger
logger = logging.getLogger(__name__)

# Conversation states
(
    CALENDAR_MENU,
    VIEW_EVENTS,
    VIEW_EVENT_DETAILS,
    CREATE_EVENT_NAME,
    CREATE_EVENT_DATE,
    CREATE_EVENT_TIME,
    CREATE_EVENT_DURATION,
    CREATE_EVENT_LOCATION,
    CREATE_EVENT_DESCRIPTION,
    CREATE_EVENT_CONFIRM,
    MODIFY_EVENT_SELECT,
    MODIFY_EVENT_FIELD,
    MODIFY_EVENT_VALUE,
    MODIFY_EVENT_CONFIRM,
    DELETE_EVENT_SELECT,
    DELETE_EVENT_CONFIRM,
) = range(16)

# Callback data patterns
CALENDAR_CALLBACK_PATTERN = r"calendar_(.+)"
EVENT_CALLBACK_PATTERN = r"event_(.+)"
DATE_CALLBACK_PATTERN = r"date_(.+)"
MODIFY_CALLBACK_PATTERN = r"modify_(.+)"
DELETE_CALLBACK_PATTERN = r"delete_(.+)"


async def calendar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle the /calendar command to access calendar features.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    user = update.effective_user
    user_id = user.id

    # Check if user is authenticated
    if not google_auth_manager.is_user_authenticated(user_id):
        await update.message.reply_text(
            "You need to authenticate with Google first. Use /auth to get started."
        )
        return ConversationHandler.END

    # Show calendar menu
    keyboard = [
        [InlineKeyboardButton("View Today's Events", callback_data="calendar_view_today")],
        [InlineKeyboardButton("View Upcoming Events", callback_data="calendar_view_upcoming")],
        [InlineKeyboardButton("Create New Event", callback_data="calendar_create")],
        [InlineKeyboardButton("Modify Event", callback_data="calendar_modify")],
        [InlineKeyboardButton("Delete Event", callback_data="calendar_delete")],
        [InlineKeyboardButton("Quick Add Event", callback_data="calendar_quick_add")],
        [InlineKeyboardButton("Cancel", callback_data="calendar_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📅 *Google Calendar*\n\n"
        "What would you like to do with your calendar?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return CALENDAR_MENU


async def calendar_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle calendar menu selections.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id

    # Extract action from callback data
    match = re.match(CALENDAR_CALLBACK_PATTERN, query.data)
    if not match:
        return ConversationHandler.END

    action = match.group(1)

    if action == "cancel":
        await query.edit_message_text("Calendar operation cancelled.")
        return ConversationHandler.END

    elif action == "view_today":
        # View today's events
        try:
            today = datetime.now()
            events = calendar_service.get_events_for_date(user_id, today)

            if not events:
                await query.edit_message_text(
                    f"📅 *Today's Events ({today.strftime('%A, %B %d')})*\n\n"
                    f"You have no events scheduled for today.",
                    parse_mode="Markdown"
                )
                return ConversationHandler.END

            formatted_events = calendar_service.format_event_list(events)

            # Create keyboard with event buttons
            keyboard = []
            for event in events:
                # Truncate summary if too long
                summary = event.summary
                if len(summary) > 30:
                    summary = summary[:27] + "..."
                keyboard.append([InlineKeyboardButton(summary, callback_data=f"event_{event.id}")])

            keyboard.append([InlineKeyboardButton("Back to Menu", callback_data="calendar_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"📅 *Today's Events ({today.strftime('%A, %B %d')})*\n\n"
                f"{formatted_events}\n\n"
                f"Select an event to view details:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return VIEW_EVENT_DETAILS

        except Exception as e:
            logger.error(f"Failed to get today's events for user {user_id}: {e}")
            await query.edit_message_text(
                "Sorry, there was an error retrieving your events. Please try again later."
            )
            return ConversationHandler.END

    elif action == "view_upcoming":
        # View upcoming events
        try:
            events = calendar_service.get_upcoming_events(user_id, days=7)

            if not events:
                await query.edit_message_text(
                    "📅 *Upcoming Events*\n\n"
                    "You have no upcoming events in the next 7 days.",
                    parse_mode="Markdown"
                )
                return ConversationHandler.END

            formatted_events = calendar_service.format_event_list(events)

            # Create keyboard with event buttons
            keyboard = []
            for event in events:
                # Truncate summary if too long
                summary = event.summary
                if len(summary) > 30:
                    summary = summary[:27] + "..."
                keyboard.append([InlineKeyboardButton(summary, callback_data=f"event_{event.id}")])

            keyboard.append([InlineKeyboardButton("Back to Menu", callback_data="calendar_menu")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "📅 *Upcoming Events*\n\n"
                f"{formatted_events}\n\n"
                f"Select an event to view details:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return VIEW_EVENT_DETAILS

        except Exception as e:
            logger.error(f"Failed to get upcoming events for user {user_id}: {e}")
            await query.edit_message_text(
                "Sorry, there was an error retrieving your events. Please try again later."
            )
            return ConversationHandler.END

    elif action == "create":
        # Start event creation flow
        await query.edit_message_text(
            "📝 *Create New Event*\n\n"
            "Let's create a new calendar event. First, what's the name or title of the event?",
            parse_mode="Markdown"
        )
        return CREATE_EVENT_NAME

    elif action == "modify":
        # Start event modification flow
        try:
            events = calendar_service.get_upcoming_events(user_id, days=7)

            if not events:
                await query.edit_message_text(
                    "You have no upcoming events to modify.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back to Menu", callback_data="calendar_menu")]])
                )
                return CALENDAR_MENU

            # Create keyboard with event buttons
            keyboard = []
            for event in events:
                # Format date/time with event title
                event_time = event.start_time.strftime("%m/%d %H:%M")
                # Truncate summary if too long
                summary = event.summary
                if len(summary) > 25:
                    summary = summary[:22] + "..."
                keyboard.append([InlineKeyboardButton(f"{event_time} - {summary}", callback_data=f"modify_{event.id}")])

            keyboard.append([InlineKeyboardButton("Cancel", callback_data="calendar_cancel")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "🔄 *Modify Event*\n\n"
                "Select an event to modify:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return MODIFY_EVENT_SELECT

        except Exception as e:
            logger.error(f"Failed to get events for modification for user {user_id}: {e}")
            await query.edit_message_text(
                "Sorry, there was an error retrieving your events. Please try again later."
            )
            return ConversationHandler.END

    elif action == "delete":
        # Start event deletion flow
        try:
            events = calendar_service.get_upcoming_events(user_id, days=7)

            if not events:
                await query.edit_message_text(
                    "You have no upcoming events to delete.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back to Menu", callback_data="calendar_menu")]])
                )
                return CALENDAR_MENU

            # Create keyboard with event buttons
            keyboard = []
            for event in events:
                # Format date/time with event title
                event_time = event.start_time.strftime("%m/%d %H:%M")
                # Truncate summary if too long
                summary = event.summary
                if len(summary) > 25:
                    summary = summary[:22] + "..."
                keyboard.append([InlineKeyboardButton(f"{event_time} - {summary}", callback_data=f"delete_{event.id}")])

            keyboard.append([InlineKeyboardButton("Cancel", callback_data="calendar_cancel")])
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "🗑️ *Delete Event*\n\n"
                "Select an event to delete:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return DELETE_EVENT_SELECT

        except Exception as e:
            logger.error(f"Failed to get events for deletion for user {user_id}: {e}")
            await query.edit_message_text(
                "Sorry, there was an error retrieving your events. Please try again later."
            )
            return ConversationHandler.END

    elif action == "quick_add":
        # Start quick add flow
        await query.edit_message_text(
            "⚡ *Quick Add Event*\n\n"
            "Enter your event in natural language. For example:\n"
            "\"Meeting with John tomorrow at 3pm\"\n"
            "\"Dentist appointment on Friday at 10am\"\n"
            "\"Lunch with Sarah at Cafe Milano on Monday 12:30pm\"",
            parse_mode="Markdown"
        )
        context.user_data["calendar_action"] = "quick_add"
        return CREATE_EVENT_NAME

    elif action == "menu":
        # Return to main calendar menu
        keyboard = [
            [InlineKeyboardButton("View Today's Events", callback_data="calendar_view_today")],
            [InlineKeyboardButton("View Upcoming Events", callback_data="calendar_view_upcoming")],
            [InlineKeyboardButton("Create New Event", callback_data="calendar_create")],
            [InlineKeyboardButton("Modify Event", callback_data="calendar_modify")],
            [InlineKeyboardButton("Delete Event", callback_data="calendar_delete")],
            [InlineKeyboardButton("Quick Add Event", callback_data="calendar_quick_add")],
            [InlineKeyboardButton("Cancel", callback_data="calendar_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "📅 *Google Calendar*\n\n"
            "What would you like to do with your calendar?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return CALENDAR_MENU

    return CALENDAR_MENU


async def event_details_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle event selection for viewing details.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id

    # Check if it's a return to menu action
    if query.data == "calendar_menu":
        return await calendar_menu_handler(update, context)

    # Extract event ID from callback data
    match = re.match(EVENT_CALLBACK_PATTERN, query.data)
    if not match:
        return ConversationHandler.END

    event_id = match.group(1)

    try:
        # Get event details
        event = calendar_service.get_event(user_id, event_id)

        # Format event details
        formatted_event = event.format_for_display()

        # Create keyboard with actions
        keyboard = [
            [InlineKeyboardButton("Modify Event", callback_data=f"modify_{event_id}")],
            [InlineKeyboardButton("Delete Event", callback_data=f"delete_{event_id}")],
            [InlineKeyboardButton("Back to Events", callback_data="calendar_view_upcoming")],
            [InlineKeyboardButton("Back to Menu", callback_data="calendar_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"*Event Details*\n\n{formatted_event}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return VIEW_EVENT_DETAILS

    except Exception as e:
        logger.error(f"Failed to get event details for user {user_id}, event {event_id}: {e}")
        await query.edit_message_text(
            "Sorry, there was an error retrieving the event details. Please try again later.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Back to Menu", callback_data="calendar_menu")]])
        )
        return CALENDAR_MENU


async def create_event_name_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle event name input for creation.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    user = update.effective_user
    user_id = user.id

    # Check if this is a quick add event
    if context.user_data.get("calendar_action") == "quick_add":
        event_text = update.message.text.strip()

        if not event_text:
            await update.message.reply_text(
                "Event description cannot be empty. Please try again or type /cancel to cancel."
            )
            return CREATE_EVENT_NAME

        try:
            # Use quick add to create the event
            event = calendar_service.quick_add_event(user_id, event_text)

            # Format event details
            formatted_event = event.format_for_display()

            await update.message.reply_text(
                f"✅ Event created successfully!\n\n{formatted_event}",
                parse_mode="Markdown"
            )

            # Clean up user data
            if "calendar_action" in context.user_data:
                del context.user_data["calendar_action"]

            return ConversationHandler.END

        except Exception as e:
            logger.error(f"Failed to quick add event for user {user_id}: {e}")
            await update.message.reply_text(
                "Sorry, there was an error creating your event. Please try again with a different format or use the regular create event option."
            )
            return ConversationHandler.END

    # Regular event creation flow
    event_name = update.message.text.strip()

    if not event_name:
        await update.message.reply_text(
            "Event name cannot be empty. Please enter a name for your event or type /cancel to cancel."
        )
        return CREATE_EVENT_NAME

    # Store event name in user data
    context.user_data["event_name"] = event_name

    # Ask for date
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)

    keyboard = [
        [InlineKeyboardButton("Today", callback_data=f"date_{today.strftime('%Y-%m-%d')}")],
        [InlineKeyboardButton("Tomorrow", callback_data=f"date_{tomorrow.strftime('%Y-%m-%d')}")],
        [InlineKeyboardButton("Next Week", callback_data=f"date_{next_week.strftime('%Y-%m-%d')}")],
        [InlineKeyboardButton("Cancel", callback_data="calendar_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📅 When is *{event_name}*?\n\n"
        f"Select a date or enter a date in YYYY-MM-DD format:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return CREATE_EVENT_DATE


async def create_event_date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle event date input for creation.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    # Check if this is a callback query (button press)
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        # Check for cancel action
        if query.data == "calendar_cancel":
            await query.edit_message_text("Event creation cancelled.")
            return ConversationHandler.END

        # Extract date from callback data
        match = re.match(DATE_CALLBACK_PATTERN, query.data)
        if match:
            date_str = match.group(1)
            try:
                event_date = datetime.strptime(date_str, "%Y-%m-%d")
                context.user_data["event_date"] = event_date

                # Ask for time
                keyboard = [
                    [
                        InlineKeyboardButton("9:00 AM", callback_data="time_09:00"),
                        InlineKeyboardButton("10:00 AM", callback_data="time_10:00"),
                        InlineKeyboardButton("11:00 AM", callback_data="time_11:00")
                    ],
                    [
                        InlineKeyboardButton("12:00 PM", callback_data="time_12:00"),
                        InlineKeyboardButton("1:00 PM", callback_data="time_13:00"),
                        InlineKeyboardButton("2:00 PM", callback_data="time_14:00")
                    ],
                    [
                        InlineKeyboardButton("3:00 PM", callback_data="time_15:00"),
                        InlineKeyboardButton("4:00 PM", callback_data="time_16:00"),
                        InlineKeyboardButton("5:00 PM", callback_data="time_17:00")
                    ],
                    [
                        InlineKeyboardButton("All Day", callback_data="time_all_day")
                    ],
                    [
                        InlineKeyboardButton("Cancel", callback_data="calendar_cancel")
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)

                await query.edit_message_text(
                    f"🕒 What time is *{context.user_data['event_name']}* on {event_date.strftime('%A, %B %d')}?\n\n"
                    f"Select a time or enter a time in HH:MM format:",
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
                return CREATE_EVENT_TIME

            except ValueError:
                await query.edit_message_text(
                    "Invalid date format. Please enter a date in YYYY-MM-DD format or select from the options."
                )
                return CREATE_EVENT_DATE

    # Handle text input
    else:
        date_str = update.message.text.strip()

        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d")
            context.user_data["event_date"] = event_date

            # Ask for time
            keyboard = [
                [
                    InlineKeyboardButton("9:00 AM", callback_data="time_09:00"),
                    InlineKeyboardButton("10:00 AM", callback_data="time_10:00"),
                    InlineKeyboardButton("11:00 AM", callback_data="time_11:00")
                ],
                [
                    InlineKeyboardButton("12:00 PM", callback_data="time_12:00"),
                    InlineKeyboardButton("1:00 PM", callback_data="time_13:00"),
                    InlineKeyboardButton("2:00 PM", callback_data="time_14:00")
                ],
                [
                    InlineKeyboardButton("3:00 PM", callback_data="time_15:00"),
                    InlineKeyboardButton("4:00 PM", callback_data="time_16:00"),
                    InlineKeyboardButton("5:00 PM", callback_data="time_17:00")
                ],
                [
                    InlineKeyboardButton("All Day", callback_data="time_all_day")
                ],
                [
                    InlineKeyboardButton("Cancel", callback_data="calendar_cancel")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"🕒 What time is *{context.user_data['event_name']}* on {event_date.strftime('%A, %B %d')}?\n\n"
                f"Select a time or enter a time in HH:MM format:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return CREATE_EVENT_TIME

        except ValueError:
            await update.message.reply_text(
                "Invalid date format. Please enter a date in YYYY-MM-DD format or type /cancel to cancel."
            )
            return CREATE_EVENT_DATE


async def create_event_time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle event time input for creation.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    # Check if this is a callback query (button press)
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        # Check for cancel action
        if query.data == "calendar_cancel":
            await query.edit_message_text("Event creation cancelled.")
            return ConversationHandler.END

        # Check for all-day event
        if query.data == "time_all_day":
            context.user_data["event_all_day"] = True

            # Skip time and duration, go to location
            await query.edit_message_text(
                f"📍 Where is *{context.user_data['event_name']}* taking place?\n\n"
                f"Enter a location or type 'skip' to skip:",
                parse_mode="Markdown"
            )
            return CREATE_EVENT_LOCATION

        # Extract time from callback data
        time_match = re.match(r"time_(\d{2}):(\d{2})", query.data)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))

            event_date = context.user_data["event_date"]
            event_time = event_date.replace(hour=hour, minute=minute)
            context.user_data["event_time"] = event_time

            # Ask for duration
            keyboard = [
                [
                    InlineKeyboardButton("30 minutes", callback_data="duration_30"),
                    InlineKeyboardButton("1 hour", callback_data="duration_60")
                ],
                [
                    InlineKeyboardButton("1.5 hours", callback_data="duration_90"),
                    InlineKeyboardButton("2 hours", callback_data="duration_120")
                ],
                [
                    InlineKeyboardButton("Cancel", callback_data="calendar_cancel")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"⏱️ How long is *{context.user_data['event_name']}*?\n\n"
                f"Select a duration or enter minutes:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return CREATE_EVENT_DURATION

    # Handle text input
    else:
        time_str = update.message.text.strip()

        try:
            # Try to parse time in HH:MM format
            time_parts = time_str.split(":")
            if len(time_parts) != 2:
                raise ValueError("Invalid time format")

            hour = int(time_parts[0])
            minute = int(time_parts[1])

            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                raise ValueError("Invalid time values")

            event_date = context.user_data["event_date"]
            event_time = event_date.replace(hour=hour, minute=minute)
            context.user_data["event_time"] = event_time

            # Ask for duration
            keyboard = [
                [
                    InlineKeyboardButton("30 minutes", callback_data="duration_30"),
                    InlineKeyboardButton("1 hour", callback_data="duration_60")
                ],
                [
                    InlineKeyboardButton("1.5 hours", callback_data="duration_90"),
                    InlineKeyboardButton("2 hours", callback_data="duration_120")
                ],
                [
                    InlineKeyboardButton("Cancel", callback_data="calendar_cancel")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"⏱️ How long is *{context.user_data['event_name']}*?\n\n"
                f"Select a duration or enter minutes:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            return CREATE_EVENT_DURATION

        except ValueError:
            await update.message.reply_text(
                "Invalid time format. Please enter a time in HH:MM format (e.g., 14:30) or type /cancel to cancel."
            )
            return CREATE_EVENT_TIME


async def create_event_duration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle event duration input for creation.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    # Check if this is a callback query (button press)
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        # Check for cancel action
        if query.data == "calendar_cancel":
            await query.edit_message_text("Event creation cancelled.")
            return ConversationHandler.END

        # Extract duration from callback data
        duration_match = re.match(r"duration_(\d+)", query.data)
        if duration_match:
            duration_minutes = int(duration_match.group(1))
            context.user_data["event_duration"] = duration_minutes

            # Calculate end time
            event_time = context.user_data["event_time"]
            end_time = event_time + timedelta(minutes=duration_minutes)
            context.user_data["event_end_time"] = end_time

            # Ask for location
            await query.edit_message_text(
                f"📍 Where is *{context.user_data['event_name']}* taking place?\n\n"
                f"Enter a location or type 'skip' to skip:",
                parse_mode="Markdown"
            )
            return CREATE_EVENT_LOCATION

    # Handle text input
    else:
        duration_str = update.message.text.strip()

        try:
            duration_minutes = int(duration_str)

            if duration_minutes <= 0:
                raise ValueError("Duration must be positive")

            context.user_data["event_duration"] = duration_minutes

            # Calculate end time
            event_time = context.user_data["event_time"]
            end_time = event_time + timedelta(minutes=duration_minutes)
            context.user_data["event_end_time"] = end_time

            # Ask for location
            await update.message.reply_text(
                f"📍 Where is *{context.user_data['event_name']}* taking place?\n\n"
                f"Enter a location or type 'skip' to skip:",
                parse_mode="Markdown"
            )
            return CREATE_EVENT_LOCATION

        except ValueError:
            await update.message.reply_text(
                "Invalid duration. Please enter a positive number of minutes or type /cancel to cancel."
            )
            return CREATE_EVENT_DURATION


async def create_event_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle event location input for creation.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    location = update.message.text.strip()

    if location.lower() == "skip":
        context.user_data["event_location"] = None
    else:
        context.user_data["event_location"] = location

    # Ask for description
    await update.message.reply_text(
        f"📝 Add a description for *{context.user_data['event_name']}*?\n\n"
        f"Enter a description or type 'skip' to skip:",
        parse_mode="Markdown"
    )
    return CREATE_EVENT_DESCRIPTION


async def create_event_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle event description input for creation.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    description = update.message.text.strip()

    if description.lower() == "skip":
        context.user_data["event_description"] = None
    else:
        context.user_data["event_description"] = description

    # Prepare event summary for confirmation
    event_name = context.user_data["event_name"]

    if context.user_data.get("event_all_day"):
        event_date = context.user_data["event_date"]
        time_str = "All day"
        date_str = event_date.strftime("%A, %B %d, %Y")
    else:
        event_time = context.user_data["event_time"]
        end_time = context.user_data["event_end_time"]
        time_str = f"{event_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
        date_str = event_time.strftime("%A, %B %d, %Y")

    location = context.user_data.get("event_location") or "Not specified"
    description = context.user_data.get("event_description") or "Not specified"

    confirmation_text = (
        f"📅 *Event Summary*\n\n"
        f"*{event_name}*\n"
        f"📆 {date_str}\n"
        f"🕒 {time_str}\n"
        f"📍 {location}\n"
        f"📝 {description}\n\n"
        f"Would you like to create this event?"
    )

    keyboard = [
        [InlineKeyboardButton("Create Event", callback_data="confirm_create")],
        [InlineKeyboardButton("Cancel", callback_data="calendar_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        confirmation_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return CREATE_EVENT_CONFIRM


async def create_event_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle event creation confirmation.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id

    # Check for cancel action
    if query.data == "calendar_cancel":
        await query.edit_message_text("Event creation cancelled.")
        return ConversationHandler.END

    # Create the event
    if query.data == "confirm_create":
        try:
            # Prepare event data
            event_data = {
                "summary": context.user_data["event_name"],
                "start": {},
                "end": {}
            }

            if context.user_data.get("event_all_day"):
                # All-day event
                event_date = context.user_data["event_date"]
                event_data["start"]["date"] = event_date.strftime("%Y-%m-%d")

                # End date for all-day events should be the next day in Google Calendar
                next_day = event_date + timedelta(days=1)
                event_data["end"]["date"] = next_day.strftime("%Y-%m-%d")
            else:
                # Timed event
                event_time = context.user_data["event_time"]
                end_time = context.user_data["event_end_time"]

                event_data["start"]["dateTime"] = event_time.isoformat()
                event_data["end"]["dateTime"] = end_time.isoformat()

            # Add location if specified
            if context.user_data.get("event_location"):
                event_data["location"] = context.user_data["event_location"]

            # Add description if specified
            if context.user_data.get("event_description"):
                event_data["description"] = context.user_data["event_description"]

            # Create the event
            event = calendar_service.create_event(user_id, event_data)

            # Format event details
            formatted_event = event.format_for_display()

            await query.edit_message_text(
                f"✅ Event created successfully!\n\n{formatted_event}",
                parse_mode="Markdown"
            )

            # Clean up user data
            for key in list(context.user_data.keys()):
                if key.startswith("event_"):
                    del context.user_data[key]

            return ConversationHandler.END

        except Exception as e:
            logger.error(f"Failed to create event for user {user_id}: {e}")
            await query.edit_message_text(
                "Sorry, there was an error creating your event. Please try again later."
            )
            return ConversationHandler.END

    return CREATE_EVENT_CONFIRM


async def modify_event_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle event selection for modification.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id

    # Check for cancel action
    if query.data == "calendar_cancel":
        await query.edit_message_text("Event modification cancelled.")
        return ConversationHandler.END

    # Extract event ID from callback data
    match = re.match(MODIFY_CALLBACK_PATTERN, query.data)
    if not match:
        return ConversationHandler.END

    event_id = match.group(1)
    context.user_data["modify_event_id"] = event_id

    try:
        # Get event details
        event = calendar_service.get_event(user_id, event_id)
        context.user_data["modify_event"] = event

        # Show event details and modification options
        keyboard = [
            [InlineKeyboardButton("Change Title", callback_data="modify_field_summary")],
            [InlineKeyboardButton("Change Date/Time", callback_data="modify_field_datetime")],
            [InlineKeyboardButton("Change Location", callback_data="modify_field_location")],
            [InlineKeyboardButton("Change Description", callback_data="modify_field_description")],
            [InlineKeyboardButton("Cancel", callback_data="calendar_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🔄 *Modify Event*\n\n"
            f"Current details:\n{event.format_for_display()}\n\n"
            f"What would you like to change?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return MODIFY_EVENT_FIELD

    except Exception as e:
        logger.error(f"Failed to get event for modification for user {user_id}, event {event_id}: {e}")
        await query.edit_message_text(
            "Sorry, there was an error retrieving the event. Please try again later."
        )
        return ConversationHandler.END


async def modify_event_field_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle field selection for event modification.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    query = update.callback_query
    await query.answer()

    # Check for cancel action
    if query.data == "calendar_cancel":
        await query.edit_message_text("Event modification cancelled.")
        return ConversationHandler.END

    # Extract field from callback data
    field_match = re.match(r"modify_field_(.+)", query.data)
    if not field_match:
        return ConversationHandler.END

    field = field_match.group(1)
    context.user_data["modify_field"] = field

    event = context.user_data["modify_event"]

    if field == "summary":
        await query.edit_message_text(
            f"Enter a new title for the event (current: *{event.summary}*):",
            parse_mode="Markdown"
        )
        return MODIFY_EVENT_VALUE

    elif field == "datetime":
        # For date/time modifications, we'll use a multi-step approach
        # First, ask for the date
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)

        keyboard = [
            [InlineKeyboardButton("Today", callback_data=f"date_{today.strftime('%Y-%m-%d')}")],
            [InlineKeyboardButton("Tomorrow", callback_data=f"date_{tomorrow.strftime('%Y-%m-%d')}")],
            [InlineKeyboardButton("Next Week", callback_data=f"date_{next_week.strftime('%Y-%m-%d')}")],
            [InlineKeyboardButton("Cancel", callback_data="calendar_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        current_date = event.start_time.strftime("%Y-%m-%d")

        await query.edit_message_text(
            f"Select a new date for the event (current: *{current_date}*):\n\n"
            f"Select a date or enter a date in YYYY-MM-DD format:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return CREATE_EVENT_DATE  # Reuse the date selection state

    elif field == "location":
        current_location = event.location or "Not set"
        await query.edit_message_text(
            f"Enter a new location for the event (current: *{current_location}*):\n\n"
            f"Enter a location or type 'clear' to remove the location:",
            parse_mode="Markdown"
        )
        return MODIFY_EVENT_VALUE

    elif field == "description":
        current_description = event.description or "Not set"
        # Truncate if too long
        if len(current_description) > 100:
            current_description = current_description[:97] + "..."

        await query.edit_message_text(
            f"Enter a new description for the event (current: *{current_description}*):\n\n"
            f"Enter a description or type 'clear' to remove the description:",
            parse_mode="Markdown"
        )
        return MODIFY_EVENT_VALUE

    return MODIFY_EVENT_FIELD


async def modify_event_value_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle new value input for event modification.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    user = update.effective_user
    user_id = user.id
    new_value = update.message.text.strip()

    field = context.user_data["modify_field"]
    event_id = context.user_data["modify_event_id"]
    event = context.user_data["modify_event"]

    # Prepare event data for update
    event_data = event.to_api_event()

    if field == "summary":
        if not new_value:
            await update.message.reply_text(
                "Event title cannot be empty. Please enter a valid title or type /cancel to cancel."
            )
            return MODIFY_EVENT_VALUE

        event_data["summary"] = new_value

    elif field == "location":
        if new_value.lower() == "clear":
            if "location" in event_data:
                del event_data["location"]
        else:
            event_data["location"] = new_value

    elif field == "description":
        if new_value.lower() == "clear":
            if "description" in event_data:
                del event_data["description"]
        else:
            event_data["description"] = new_value

    # Show confirmation
    keyboard = [
        [InlineKeyboardButton("Save Changes", callback_data="confirm_modify")],
        [InlineKeyboardButton("Cancel", callback_data="calendar_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Store updated event data for confirmation
    context.user_data["modified_event_data"] = event_data

    # Format field name for display
    field_display = {
        "summary": "title",
        "location": "location",
        "description": "description"
    }.get(field, field)

    await update.message.reply_text(
        f"You're about to change the {field_display} of the event *{event.summary}*.\n\n"
        f"New {field_display}: {new_value}\n\n"
        f"Would you like to save these changes?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return MODIFY_EVENT_CONFIRM


async def modify_event_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle confirmation for event modification.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id

    # Check for cancel action
    if query.data == "calendar_cancel":
        await query.edit_message_text("Event modification cancelled.")
        return ConversationHandler.END

    # Update the event
    if query.data == "confirm_modify":
        try:
            event_id = context.user_data["modify_event_id"]
            event_data = context.user_data["modified_event_data"]

            # Update the event
            updated_event = calendar_service.update_event(user_id, event_id, event_data)

            # Format event details
            formatted_event = updated_event.format_for_display()

            await query.edit_message_text(
                f"✅ Event updated successfully!\n\n{formatted_event}",
                parse_mode="Markdown"
            )

            # Clean up user data
            for key in list(context.user_data.keys()):
                if key.startswith("modify_") or key == "modified_event_data":
                    del context.user_data[key]

            return ConversationHandler.END

        except Exception as e:
            logger.error(f"Failed to update event for user {user_id}, event {event_id}: {e}")
            await query.edit_message_text(
                "Sorry, there was an error updating your event. Please try again later."
            )
            return ConversationHandler.END

    return MODIFY_EVENT_CONFIRM


async def delete_event_select_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle event selection for deletion.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id

    # Check for cancel action
    if query.data == "calendar_cancel":
        await query.edit_message_text("Event deletion cancelled.")
        return ConversationHandler.END

    # Extract event ID from callback data
    match = re.match(DELETE_CALLBACK_PATTERN, query.data)
    if not match:
        return ConversationHandler.END

    event_id = match.group(1)
    context.user_data["delete_event_id"] = event_id

    try:
        # Get event details
        event = calendar_service.get_event(user_id, event_id)
        context.user_data["delete_event"] = event

        # Show confirmation
        keyboard = [
            [InlineKeyboardButton("Yes, delete this event", callback_data="confirm_delete")],
            [InlineKeyboardButton("No, keep this event", callback_data="calendar_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🗑️ *Delete Event*\n\n"
            f"Are you sure you want to delete this event?\n\n"
            f"{event.format_for_display()}\n\n"
            f"This action cannot be undone.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        return DELETE_EVENT_CONFIRM

    except Exception as e:
        logger.error(f"Failed to get event for deletion for user {user_id}, event {event_id}: {e}")
        await query.edit_message_text(
            "Sorry, there was an error retrieving the event. Please try again later."
        )
        return ConversationHandler.END


async def delete_event_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle confirmation for event deletion.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id

    # Check for cancel action
    if query.data == "calendar_cancel":
        await query.edit_message_text("Event deletion cancelled.")
        return ConversationHandler.END

    # Delete the event
    if query.data == "confirm_delete":
        try:
            event_id = context.user_data["delete_event_id"]
            event = context.user_data["delete_event"]

            # Delete the event
            success = calendar_service.delete_event(user_id, event_id)

            if success:
                await query.edit_message_text(
                    f"✅ Event *{event.summary}* has been deleted successfully.",
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(
                    f"❌ Failed to delete event *{event.summary}*. Please try again later.",
                    parse_mode="Markdown"
                )

            # Clean up user data
            for key in list(context.user_data.keys()):
                if key.startswith("delete_"):
                    del context.user_data[key]

            return ConversationHandler.END

        except Exception as e:
            logger.error(f"Failed to delete event for user {user_id}, event {event_id}: {e}")
            await query.edit_message_text(
                "Sorry, there was an error deleting your event. Please try again later."
            )
            return ConversationHandler.END

    return DELETE_EVENT_CONFIRM


async def calendar_conversation_timeout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle conversation timeout.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object

    Returns:
        int: The next conversation state
    """
    await update.message.reply_text(
        "The calendar operation timed out. Please start again if needed."
    )
    return ConversationHandler.END


async def calendar_today_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /calendar_today command to show today's events.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object
    """
    user = update.effective_user
    user_id = user.id

    # Check if user is authenticated
    if not google_auth_manager.is_user_authenticated(user_id):
        await update.message.reply_text(
            "You need to authenticate with Google first. Use /auth to get started."
        )
        return

    try:
        today = datetime.now()
        events = calendar_service.get_events_for_date(user_id, today)

        if not events:
            await update.message.reply_text(
                f"📅 *Today's Events ({today.strftime('%A, %B %d')})*\n\n"
                f"You have no events scheduled for today.",
                parse_mode="Markdown"
            )
            return

        formatted_events = calendar_service.format_event_list(events)

        await update.message.reply_text(
            f"📅 *Today's Events ({today.strftime('%A, %B %d')})*\n\n"
            f"{formatted_events}",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Failed to get today's events for user {user_id}: {e}")
        await update.message.reply_text(
            "Sorry, there was an error retrieving your events. Please try again later."
        )


async def calendar_upcoming_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /calendar_upcoming command to show upcoming events.

    Args:
        update (Update): The update object
        context (ContextTypes.DEFAULT_TYPE): The context object
    """
    user = update.effective_user
    user_id = user.id

    # Check if user is authenticated
    if not google_auth_manager.is_user_authenticated(user_id):
        await update.message.reply_text(
            "You need to authenticate with Google first. Use /auth to get started."
        )
        return

    try:
        events = calendar_service.get_upcoming_events(user_id, days=7)

        if not events:
            await update.message.reply_text(
                "📅 *Upcoming Events*\n\n"
                "You have no upcoming events in the next 7 days.",
                parse_mode="Markdown"
            )
            return

        formatted_events = calendar_service.format_event_list(events)

        await update.message.reply_text(
            "📅 *Upcoming Events*\n\n"
            f"{formatted_events}",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Failed to get upcoming events for user {user_id}: {e}")
        await update.message.reply_text(
            "Sorry, there was an error retrieving your events. Please try again later."
        )


def register_calendar_handlers():
    """Register calendar command handlers."""
    # Register simple commands
    register_command("calendar_today", calendar_today_command, "View today's calendar events")
    register_command("calendar_upcoming", calendar_upcoming_command, "View upcoming calendar events")

    # Register calendar conversation handler
    calendar_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("calendar", calendar_command)],
        states={
            CALENDAR_MENU: [
                CallbackQueryHandler(calendar_menu_handler, pattern=CALENDAR_CALLBACK_PATTERN)
            ],
            VIEW_EVENTS: [
                CallbackQueryHandler(calendar_menu_handler, pattern=CALENDAR_CALLBACK_PATTERN)
            ],
            VIEW_EVENT_DETAILS: [
                CallbackQueryHandler(event_details_handler, pattern=EVENT_CALLBACK_PATTERN),
                CallbackQueryHandler(calendar_menu_handler, pattern=CALENDAR_CALLBACK_PATTERN),
                CallbackQueryHandler(modify_event_select_handler, pattern=MODIFY_CALLBACK_PATTERN),
                CallbackQueryHandler(delete_event_select_handler, pattern=DELETE_CALLBACK_PATTERN)
            ],
            CREATE_EVENT_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_event_name_handler)
            ],
            CREATE_EVENT_DATE: [
                CallbackQueryHandler(create_event_date_handler, pattern=DATE_CALLBACK_PATTERN),
                CallbackQueryHandler(calendar_menu_handler, pattern=CALENDAR_CALLBACK_PATTERN),
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_event_date_handler)
            ],
            CREATE_EVENT_TIME: [
                CallbackQueryHandler(create_event_time_handler, pattern=r"time_.+"),
                CallbackQueryHandler(calendar_menu_handler, pattern=CALENDAR_CALLBACK_PATTERN),
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_event_time_handler)
            ],
            CREATE_EVENT_DURATION: [
                CallbackQueryHandler(create_event_duration_handler, pattern=r"duration_.+"),
                CallbackQueryHandler(calendar_menu_handler, pattern=CALENDAR_CALLBACK_PATTERN),
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_event_duration_handler)
            ],
            CREATE_EVENT_LOCATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_event_location_handler)
            ],
            CREATE_EVENT_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_event_description_handler)
            ],
            CREATE_EVENT_CONFIRM: [
                CallbackQueryHandler(create_event_confirm_handler, pattern=r"confirm_create"),
                CallbackQueryHandler(calendar_menu_handler, pattern=CALENDAR_CALLBACK_PATTERN)
            ],
            MODIFY_EVENT_SELECT: [
                CallbackQueryHandler(modify_event_select_handler, pattern=MODIFY_CALLBACK_PATTERN),
                CallbackQueryHandler(calendar_menu_handler, pattern=CALENDAR_CALLBACK_PATTERN)
            ],
            MODIFY_EVENT_FIELD: [
                CallbackQueryHandler(modify_event_field_handler, pattern=r"modify_field_.+"),
                CallbackQueryHandler(calendar_menu_handler, pattern=CALENDAR_CALLBACK_PATTERN)
            ],
            MODIFY_EVENT_VALUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, modify_event_value_handler)
            ],
            MODIFY_EVENT_CONFIRM: [
                CallbackQueryHandler(modify_event_confirm_handler, pattern=r"confirm_modify"),
                CallbackQueryHandler(calendar_menu_handler, pattern=CALENDAR_CALLBACK_PATTERN)
            ],
            DELETE_EVENT_SELECT: [
                CallbackQueryHandler(delete_event_select_handler, pattern=DELETE_CALLBACK_PATTERN),
                CallbackQueryHandler(calendar_menu_handler, pattern=CALENDAR_CALLBACK_PATTERN)
            ],
            DELETE_EVENT_CONFIRM: [
                CallbackQueryHandler(delete_event_confirm_handler, pattern=r"confirm_delete"),
                CallbackQueryHandler(calendar_menu_handler, pattern=CALENDAR_CALLBACK_PATTERN)
            ],
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        conversation_timeout=300,  # 5 minutes timeout
    )

    register_conversation("calendar", calendar_conv_handler)

    logger.info("Registered calendar command handlers")
