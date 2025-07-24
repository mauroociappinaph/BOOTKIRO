"""
Google Calendar API client for the Simplified Google Bot.
Handles direct interactions with the Google Calendar API.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

logger = logging.getLogger(__name__)

class CalendarClient:
    """
    Client for interacting with the Google Calendar API.
    """

    def __init__(self, credentials: Credentials):
        """
        Initialize the Calendar API client.

        Args:
            credentials (Credentials): Google OAuth2 credentials.
        """
        self.service = build('calendar', 'v3', credentials=credentials)
        self.primary_calendar_id = 'primary'  # Use the user's primary calendar by default

    def list_calendars(self) -> List[Dict[str, Any]]:
        """
        List available calendars for the authenticated user.

        Returns:
            List[Dict[str, Any]]: List of calendar objects.

        Raises:
            HttpError: If the API request fails.
        """
        try:
            calendars_result = self.service.calendarList().list().execute()
            return calendars_result.get('items', [])
        except HttpError as error:
            logger.error(f"Failed to list calendars: {error}")
            raise

    def get_events(self,
                  calendar_id: str = 'primary',
                  time_min: Optional[datetime] = None,
                  time_max: Optional[datetime] = None,
                  max_results: int = 10,
                  query: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get events from a calendar.

        Args:
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.
            time_min (datetime, optional): Start time for events. Defaults to now.
            time_max (datetime, optional): End time for events. Defaults to 7 days from now.
            max_results (int, optional): Maximum number of events to return. Defaults to 10.
            query (str, optional): Free text search term. Defaults to None.

        Returns:
            List[Dict[str, Any]]: List of event objects.

        Raises:
            HttpError: If the API request fails.
        """
        try:
            # Set default time range if not provided
            if time_min is None:
                time_min = datetime.utcnow()
            if time_max is None:
                time_max = time_min + timedelta(days=7)

            # Format times for API
            time_min_str = time_min.isoformat() + 'Z'  # 'Z' indicates UTC time
            time_max_str = time_max.isoformat() + 'Z'

            # Prepare request parameters
            params = {
                'calendarId': calendar_id,
                'timeMin': time_min_str,
                'timeMax': time_max_str,
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime'
            }

            # Add query if provided
            if query:
                params['q'] = query

            events_result = self.service.events().list(**params).execute()
            return events_result.get('items', [])

        except HttpError as error:
            logger.error(f"Failed to get events: {error}")
            raise

    def get_event(self, event_id: str, calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        Get a specific event by ID.

        Args:
            event_id (str): The event ID.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.

        Returns:
            Dict[str, Any]: Event object.

        Raises:
            HttpError: If the API request fails.
        """
        try:
            return self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
        except HttpError as error:
            logger.error(f"Failed to get event {event_id}: {error}")
            raise

    def create_event(self,
                    event_data: Dict[str, Any],
                    calendar_id: str = 'primary',
                    send_notifications: bool = True) -> Dict[str, Any]:
        """
        Create a new calendar event.

        Args:
            event_data (Dict[str, Any]): Event data.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.
            send_notifications (bool, optional): Whether to send notifications. Defaults to True.

        Returns:
            Dict[str, Any]: Created event object.

        Raises:
            HttpError: If the API request fails.
        """
        try:
            return self.service.events().insert(
                calendarId=calendar_id,
                body=event_data,
                sendUpdates='all' if send_notifications else 'none'
            ).execute()
        except HttpError as error:
            logger.error(f"Failed to create event: {error}")
            raise

    def update_event(self,
                    event_id: str,
                    event_data: Dict[str, Any],
                    calendar_id: str = 'primary',
                    send_notifications: bool = True) -> Dict[str, Any]:
        """
        Update an existing calendar event.

        Args:
            event_id (str): The event ID.
            event_data (Dict[str, Any]): Updated event data.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.
            send_notifications (bool, optional): Whether to send notifications. Defaults to True.

        Returns:
            Dict[str, Any]: Updated event object.

        Raises:
            HttpError: If the API request fails.
        """
        try:
            return self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event_data,
                sendUpdates='all' if send_notifications else 'none'
            ).execute()
        except HttpError as error:
            logger.error(f"Failed to update event {event_id}: {error}")
            raise

    def delete_event(self,
                    event_id: str,
                    calendar_id: str = 'primary',
                    send_notifications: bool = True) -> bool:
        """
        Delete a calendar event.

        Args:
            event_id (str): The event ID.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.
            send_notifications (bool, optional): Whether to send notifications. Defaults to True.

        Returns:
            bool: True if deletion was successful.

        Raises:
            HttpError: If the API request fails.
        """
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id,
                sendUpdates='all' if send_notifications else 'none'
            ).execute()
            return True
        except HttpError as error:
            logger.error(f"Failed to delete event {event_id}: {error}")
            raise

    def quick_add_event(self, text: str, calendar_id: str = 'primary') -> Dict[str, Any]:
        """
        Quickly add an event using natural language text.

        Args:
            text (str): Natural language description of the event.
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.

        Returns:
            Dict[str, Any]: Created event object.

        Raises:
            HttpError: If the API request fails.
        """
        try:
            return self.service.events().quickAdd(
                calendarId=calendar_id,
                text=text
            ).execute()
        except HttpError as error:
            logger.error(f"Failed to quick add event: {error}")
            raise

    def get_free_busy(self,
                     time_min: datetime,
                     time_max: datetime,
                     calendar_ids: List[str] = None) -> Dict[str, Any]:
        """
        Get free/busy information for calendars.

        Args:
            time_min (datetime): Start time.
            time_max (datetime): End time.
            calendar_ids (List[str], optional): List of calendar IDs. Defaults to ['primary'].

        Returns:
            Dict[str, Any]: Free/busy information.

        Raises:
            HttpError: If the API request fails.
        """
        if calendar_ids is None:
            calendar_ids = ['primary']

        try:
            body = {
                "timeMin": time_min.isoformat() + 'Z',
                "timeMax": time_max.isoformat() + 'Z',
                "items": [{"id": calendar_id} for calendar_id in calendar_ids]
            }

            return self.service.freebusy().query(body=body).execute()
        except HttpError as error:
            logger.error(f"Failed to get free/busy information: {error}")
            raise

    def find_available_slots(self,
                            duration_minutes: int = 30,
                            days_ahead: int = 7,
                            working_hours: Tuple[int, int] = (9, 17),
                            calendar_id: str = 'primary') -> List[Dict[str, datetime]]:
        """
        Find available time slots for a meeting.

        Args:
            duration_minutes (int, optional): Duration in minutes. Defaults to 30.
            days_ahead (int, optional): Number of days to look ahead. Defaults to 7.
            working_hours (Tuple[int, int], optional): Working hours (start, end). Defaults to (9, 17).
            calendar_id (str, optional): Calendar ID. Defaults to 'primary'.

        Returns:
            List[Dict[str, datetime]]: List of available slots with start and end times.

        Raises:
            HttpError: If the API request fails.
        """
        try:
            now = datetime.utcnow()
            end_date = now + timedelta(days=days_ahead)

            # Get busy periods
            busy_periods = []
            events = self.get_events(
                calendar_id=calendar_id,
                time_min=now,
                time_max=end_date,
                max_results=100
            )

            for event in events:
                # Skip events that are declined or tentative
                if 'attendees' in event:
                    for attendee in event['attendees']:
                        if attendee.get('self', False) and attendee.get('responseStatus') in ['declined', 'tentative']:
                            continue

                start = event['start'].get('dateTime')
                end = event['end'].get('dateTime')

                if start and end:  # Only consider events with specific times
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                    busy_periods.append((start_dt, end_dt))

            # Find available slots
            available_slots = []
            current_date = now.replace(hour=working_hours[0], minute=0, second=0, microsecond=0)

            # If current time is past working hours, move to next day
            if now.hour >= working_hours[1]:
                current_date += timedelta(days=1)

            while current_date.date() <= end_date.date():
                if current_date.weekday() < 5:  # Weekdays only (0-4 are Monday to Friday)
                    day_end = current_date.replace(hour=working_hours[1], minute=0, second=0, microsecond=0)

                    # Start from current time if it's today
                    if current_date.date() == now.date() and now.hour > working_hours[0]:
                        slot_start = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                    else:
                        slot_start = current_date

                    while slot_start < day_end:
                        slot_end = slot_start + timedelta(minutes=duration_minutes)

                        # Check if slot overlaps with any busy period
                        is_available = True
                        for busy_start, busy_end in busy_periods:
                            if (slot_start < busy_end and slot_end > busy_start):
                                is_available = False
                                break

                        if is_available and slot_end <= day_end:
                            available_slots.append({
                                'start': slot_start,
                                'end': slot_end
                            })

                        slot_start += timedelta(minutes=30)  # 30-minute increments

                # Move to next day
                current_date += timedelta(days=1)
                current_date = current_date.replace(hour=working_hours[0], minute=0, second=0, microsecond=0)

            return available_slots

        except HttpError as error:
            logger.error(f"Failed to find available slots: {error}")
            raise
