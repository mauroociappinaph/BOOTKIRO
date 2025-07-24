"""
Calendar service for the Simplified Google Bot.
Provides business logic for calendar operations.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union

from googleapiclient.errors import HttpError

from simplified_google_bot.utils.auth import google_auth_manager
from simplified_google_bot.services.calendar.calendar_client import CalendarClient
from simplified_google_bot.services.calendar.models import CalendarEvent, Calendar, TimeSlot

logger = logging.getLogger(__name__)

class CalendarService:
    """
    Service for managing calendar operations.
    """

    def __init__(self):
        """Initialize the calendar service."""
        self.auth_manager = google_auth_manager

    def _get_client(self, user_id: int) -> CalendarClient:
        """
        Get a Calendar API client for a user.

        Args:
            user_id (int): The Telegram user ID.

        Returns:
            CalendarClient: A Calendar API client.

        Raises:
            ValueError: If the user is not authenticated.
        """
        credentials = self.auth_manager.get_user_credentials(user_id)
        if not credentials:
            raise ValueError("User is not authenticated with Google")
        return CalendarClient(credentials)

    def get_calendars(self, user_id: int) -> List[Calendar]:
        """
        Get available calendars for a user.

        Args:
            user_id (int): The Telegram user ID.

        Returns:
            List[Calendar]: List of available calendars.

        Raises:
            ValueError: If the user is not authenticated.
            RuntimeError: If the API request fails.
        """
        try:
            client = self._get_client(user_id)
            calendars_data = client.list_calendars()
            return [Calendar.from_api_calendar(cal) for cal in calendars_data]
        except HttpError as error:
            logger.error(f"Failed to get calendars for user {user_id}: {error}")
            raise RuntimeError(f"Failed to get calendars: {error.reason}")
        except Exception as error:
            logger.error(f"Error getting calendars for user {user_id}: {error}")
            raise

    def get_upcoming_events(self,
                           user_id: int,
                           days: int = 7,
                           max_results: int = 10,
                           calendar_id: str = 'primary') -> List[CalendarEvent]:
        """
        Get upcoming events for a user.

        Args:
            user_id (int): The Telegram user ID.
            days (int, optional): Number of days to look ahead. Defaults to 7.
            max_results (int, optional): Maximum number of events to return. Defaults to 10.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.

        Returns:
            List[CalendarEvent]: List of upcoming events.

        Raises:
            ValueError: If the user is not authenticated.
            RuntimeError: If the API request fails.
        """
        try:
            client = self._get_client(user_id)
            now = datetime.utcnow()
            end_date = now + timedelta(days=days)

            events_data = client.get_events(
                calendar_id=calendar_id,
                time_min=now,
                time_max=end_date,
                max_results=max_results
            )

            return [CalendarEvent.from_api_event(event) for event in events_data]
        except HttpError as error:
            logger.error(f"Failed to get events for user {user_id}: {error}")
            raise RuntimeError(f"Failed to get events: {error.reason}")
        except Exception as error:
            logger.error(f"Error getting events for user {user_id}: {error}")
            raise

    def get_events_for_date(self,
                           user_id: int,
                           date: datetime,
                           calendar_id: str = 'primary') -> List[CalendarEvent]:
        """
        Get events for a specific date.

        Args:
            user_id (int): The Telegram user ID.
            date (datetime): The date to get events for.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.

        Returns:
            List[CalendarEvent]: List of events on the specified date.

        Raises:
            ValueError: If the user is not authenticated.
            RuntimeError: If the API request fails.
        """
        try:
            client = self._get_client(user_id)

            # Set time range for the entire day
            start_time = datetime(date.year, date.month, date.day, 0, 0, 0)
            end_time = datetime(date.year, date.month, date.day, 23, 59, 59)

            events_data = client.get_events(
                calendar_id=calendar_id,
                time_min=start_time,
                time_max=end_time
            )

            return [CalendarEvent.from_api_event(event) for event in events_data]
        except HttpError as error:
            logger.error(f"Failed to get events for date {date} for user {user_id}: {error}")
            raise RuntimeError(f"Failed to get events: {error.reason}")
        except Exception as error:
            logger.error(f"Error getting events for date {date} for user {user_id}: {error}")
            raise

    def get_event(self,
                 user_id: int,
                 event_id: str,
                 calendar_id: str = 'primary') -> CalendarEvent:
        """
        Get a specific event.

        Args:
            user_id (int): The Telegram user ID.
            event_id (str): The event ID.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.

        Returns:
            CalendarEvent: The requested event.

        Raises:
            ValueError: If the user is not authenticated.
            RuntimeError: If the API request fails.
            KeyError: If the event is not found.
        """
        try:
            client = self._get_client(user_id)
            event_data = client.get_event(event_id, calendar_id)
            return CalendarEvent.from_api_event(event_data)
        except HttpError as error:
            if error.resp.status == 404:
                raise KeyError(f"Event {event_id} not found")
            logger.error(f"Failed to get event {event_id} for user {user_id}: {error}")
            raise RuntimeError(f"Failed to get event: {error.reason}")
        except Exception as error:
            logger.error(f"Error getting event {event_id} for user {user_id}: {error}")
            raise

    def create_event(self,
                    user_id: int,
                    event: Union[CalendarEvent, Dict[str, Any]],
                    calendar_id: str = 'primary',
                    send_notifications: bool = True) -> CalendarEvent:
        """
        Create a new calendar event.

        Args:
            user_id (int): The Telegram user ID.
            event (Union[CalendarEvent, Dict[str, Any]]): Event data or CalendarEvent object.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.
            send_notifications (bool, optional): Whether to send notifications. Defaults to True.

        Returns:
            CalendarEvent: The created event.

        Raises:
            ValueError: If the user is not authenticated or event data is invalid.
            RuntimeError: If the API request fails.
        """
        try:
            client = self._get_client(user_id)

            # Convert to API format if needed
            if isinstance(event, CalendarEvent):
                event_data = event.to_api_event()
            else:
                event_data = event

            # Validate required fields
            if 'summary' not in event_data:
                raise ValueError("Event summary is required")
            if 'start' not in event_data or 'end' not in event_data:
                raise ValueError("Event start and end times are required")

            created_event = client.create_event(
                event_data=event_data,
                calendar_id=calendar_id,
                send_notifications=send_notifications
            )

            return CalendarEvent.from_api_event(created_event)
        except HttpError as error:
            logger.error(f"Failed to create event for user {user_id}: {error}")
            raise RuntimeError(f"Failed to create event: {error.reason}")
        except Exception as error:
            logger.error(f"Error creating event for user {user_id}: {error}")
            raise

    def update_event(self,
                    user_id: int,
                    event_id: str,
                    event: Union[CalendarEvent, Dict[str, Any]],
                    calendar_id: str = 'primary',
                    send_notifications: bool = True) -> CalendarEvent:
        """
        Update an existing calendar event.

        Args:
            user_id (int): The Telegram user ID.
            event_id (str): The event ID.
            event (Union[CalendarEvent, Dict[str, Any]]): Updated event data or CalendarEvent object.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.
            send_notifications (bool, optional): Whether to send notifications. Defaults to True.

        Returns:
            CalendarEvent: The updated event.

        Raises:
            ValueError: If the user is not authenticated or event data is invalid.
            RuntimeError: If the API request fails.
            KeyError: If the event is not found.
        """
        try:
            client = self._get_client(user_id)

            # Convert to API format if needed
            if isinstance(event, CalendarEvent):
                event_data = event.to_api_event()
            else:
                event_data = event

            # Ensure event ID is set
            event_data['id'] = event_id

            updated_event = client.update_event(
                event_id=event_id,
                event_data=event_data,
                calendar_id=calendar_id,
                send_notifications=send_notifications
            )

            return CalendarEvent.from_api_event(updated_event)
        except HttpError as error:
            if error.resp.status == 404:
                raise KeyError(f"Event {event_id} not found")
            logger.error(f"Failed to update event {event_id} for user {user_id}: {error}")
            raise RuntimeError(f"Failed to update event: {error.reason}")
        except Exception as error:
            logger.error(f"Error updating event {event_id} for user {user_id}: {error}")
            raise

    def delete_event(self,
                    user_id: int,
                    event_id: str,
                    calendar_id: str = 'primary',
                    send_notifications: bool = True) -> bool:
        """
        Delete a calendar event.

        Args:
            user_id (int): The Telegram user ID.
            event_id (str): The event ID.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.
            send_notifications (bool, optional): Whether to send notifications. Defaults to True.

        Returns:
            bool: True if deletion was successful.

        Raises:
            ValueError: If the user is not authenticated.
            RuntimeError: If the API request fails.
            KeyError: If the event is not found.
        """
        try:
            client = self._get_client(user_id)
            return client.delete_event(
                event_id=event_id,
                calendar_id=calendar_id,
                send_notifications=send_notifications
            )
        except HttpError as error:
            if error.resp.status == 404:
                raise KeyError(f"Event {event_id} not found")
            logger.error(f"Failed to delete event {event_id} for user {user_id}: {error}")
            raise RuntimeError(f"Failed to delete event: {error.reason}")
        except Exception as error:
            logger.error(f"Error deleting event {event_id} for user {user_id}: {error}")
            raise

    def quick_add_event(self,
                       user_id: int,
                       text: str,
                       calendar_id: str = 'primary') -> CalendarEvent:
        """
        Quickly add an event using natural language text.

        Args:
            user_id (int): The Telegram user ID.
            text (str): Natural language description of the event.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.

        Returns:
            CalendarEvent: The created event.

        Raises:
            ValueError: If the user is not authenticated or text is empty.
            RuntimeError: If the API request fails.
        """
        if not text.strip():
            raise ValueError("Event description cannot be empty")

        try:
            client = self._get_client(user_id)
            event_data = client.quick_add_event(text, calendar_id)
            return CalendarEvent.from_api_event(event_data)
        except HttpError as error:
            logger.error(f"Failed to quick add event for user {user_id}: {error}")
            raise RuntimeError(f"Failed to create event: {error.reason}")
        except Exception as error:
            logger.error(f"Error quick adding event for user {user_id}: {error}")
            raise

    def find_available_slots(self,
                            user_id: int,
                            duration_minutes: int = 30,
                            days_ahead: int = 7,
                            working_hours: Tuple[int, int] = (9, 17),
                            calendar_id: str = 'primary') -> List[TimeSlot]:
        """
        Find available time slots for a meeting.

        Args:
            user_id (int): The Telegram user ID.
            duration_minutes (int, optional): Duration in minutes. Defaults to 30.
            days_ahead (int, optional): Number of days to look ahead. Defaults to 7.
            working_hours (Tuple[int, int], optional): Working hours (start, end). Defaults to (9, 17).
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.

        Returns:
            List[TimeSlot]: List of available time slots.

        Raises:
            ValueError: If the user is not authenticated or parameters are invalid.
            RuntimeError: If the API request fails.
        """
        if duration_minutes <= 0:
            raise ValueError("Duration must be positive")

        if working_hours[0] < 0 or working_hours[0] > 23 or working_hours[1] < 0 or working_hours[1] > 23:
            raise ValueError("Working hours must be between 0 and 23")

        if working_hours[0] >= working_hours[1]:
            raise ValueError("Start working hour must be before end working hour")

        try:
            client = self._get_client(user_id)
            slots_data = client.find_available_slots(
                duration_minutes=duration_minutes,
                days_ahead=days_ahead,
                working_hours=working_hours,
                calendar_id=calendar_id
            )

            return [TimeSlot(start=slot['start'], end=slot['end']) for slot in slots_data]
        except HttpError as error:
            logger.error(f"Failed to find available slots for user {user_id}: {error}")
            raise RuntimeError(f"Failed to find available slots: {error.reason}")
        except Exception as error:
            logger.error(f"Error finding available slots for user {user_id}: {error}")
            raise

    def search_events(self,
                     user_id: int,
                     query: str,
                     max_results: int = 10,
                     calendar_id: str = 'primary') -> List[CalendarEvent]:
        """
        Search for events matching a query.

        Args:
            user_id (int): The Telegram user ID.
            query (str): Search query.
            max_results (int, optional): Maximum number of results. Defaults to 10.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.

        Returns:
            List[CalendarEvent]: List of matching events.

        Raises:
            ValueError: If the user is not authenticated or query is empty.
            RuntimeError: If the API request fails.
        """
        if not query.strip():
            raise ValueError("Search query cannot be empty")

        try:
            client = self._get_client(user_id)
            events_data = client.get_events(
                calendar_id=calendar_id,
                max_results=max_results,
                query=query
            )

            return [CalendarEvent.from_api_event(event) for event in events_data]
        except HttpError as error:
            logger.error(f"Failed to search events for user {user_id}: {error}")
            raise RuntimeError(f"Failed to search events: {error.reason}")
        except Exception as error:
            logger.error(f"Error searching events for user {user_id}: {error}")
            raise

    def parse_event_input(self, text: str) -> Dict[str, Any]:
        """
        Parse user input text into event data.

        Args:
            text (str): User input text describing an event.

        Returns:
            Dict[str, Any]: Parsed event data.

        Raises:
            ValueError: If the text cannot be parsed into a valid event.
        """
        # This is a simple implementation that could be enhanced with NLP
        lines = text.strip().split('\n')

        if not lines:
            raise ValueError("Event text cannot be empty")

        # First line is the summary
        summary = lines[0].strip()
        if not summary:
            raise ValueError("Event summary cannot be empty")

        event_data = {
            'summary': summary,
            'start': {},
            'end': {}
        }

        # Look for date/time, location, and description
        description_lines = []
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue

            # Try to identify date/time patterns
            # This is a very basic implementation
            if any(time_word in line.lower() for time_word in ['today', 'tomorrow', 'am', 'pm', ':']) and 'start' not in event_data:
                # For now, we'll just use quick_add for parsing dates
                # In a real implementation, you'd use a proper date parser
                return None  # Signal to use quick_add instead

            # Look for location
            elif line.lower().startswith('at ') or line.lower().startswith('location:'):
                event_data['location'] = line.split(':', 1)[-1].strip()

            # Everything else goes into description
            else:
                description_lines.append(line)

        if description_lines:
            event_data['description'] = '\n'.join(description_lines)

        return event_data

    def format_event_list(self, events: List[CalendarEvent]) -> str:
        """
        Format a list of events for display in Telegram.

        Args:
            events (List[CalendarEvent]): List of events to format.

        Returns:
            str: Formatted event list text.
        """
        if not events:
            return "No events found."

        result = []
        current_date = None

        for event in events:
            event_date = event.start_time.date()

            # Add date header if this is a new date
            if current_date != event_date:
                current_date = event_date
                date_header = f"\n📅 *{event_date.strftime('%A, %B %d, %Y')}*"
                result.append(date_header)

            # Format time
            if event.start_time.hour == 0 and event.start_time.minute == 0 and \
               event.end_time.hour == 23 and event.end_time.minute == 59:
                time_str = "All day"
            else:
                time_str = f"{event.start_time.strftime('%I:%M %p')} - {event.end_time.strftime('%I:%M %p')}"

            # Add event entry
            event_entry = f"• {time_str}: *{event.summary}*"
            if event.location:
                event_entry += f" 📍 {event.location}"

            result.append(event_entry)

        return "\n".join(result)

# Global calendar service instance
calendar_service = CalendarService()
