"""
Google Calendar service implementation.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from personal_automation_bot.utils.auth import google_auth_manager
from .models import CalendarEvent

logger = logging.getLogger(__name__)


class CalendarService:
    """Service for interacting with Google Calendar API."""

    def __init__(self):
        """Initialize the Calendar service."""
        self.auth_manager = google_auth_manager

    def _get_calendar_client(self, user_id: int):
        """Get authenticated Google Calendar client for user."""
        credentials = self.auth_manager.get_user_credentials(user_id)
        if not credentials:
            raise ValueError("User not authenticated with Google")

        return build('calendar', 'v3', credentials=credentials)

    def get_events(self, user_id: int, start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None, max_results: int = 10,
                   calendar_id: str = 'primary') -> List[CalendarEvent]:
        """
        Get calendar events for a user.

        Args:
            user_id (int): Telegram user ID
            start_date (Optional[datetime]): Start date for events (default: now)
            end_date (Optional[datetime]): End date for events (default: 7 days from now)
            max_results (int): Maximum number of events to return
            calendar_id (str): Calendar ID to query (default: primary)

        Returns:
            List[CalendarEvent]: List of calendar events

        Raises:
            ValueError: If user is not authenticated
            Exception: If API call fails
        """
        try:
            service = self._get_calendar_client(user_id)

            # Set default date range if not provided
            if start_date is None:
                start_date = datetime.now()
            if end_date is None:
                end_date = start_date + timedelta(days=7)

            # Format dates for API
            time_min = start_date.isoformat() + 'Z'
            time_max = end_date.isoformat() + 'Z'

            # Call the Calendar API
            events_result = service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Convert to CalendarEvent objects
            calendar_events = []
            for event in events:
                try:
                    calendar_event = CalendarEvent.from_google_event(event)
                    calendar_events.append(calendar_event)
                except Exception as e:
                    logger.warning(f"Failed to parse event {event.get('id', 'unknown')}: {e}")
                    continue

            logger.info(f"Retrieved {len(calendar_events)} events for user {user_id}")
            return calendar_events

        except HttpError as e:
            logger.error(f"Google Calendar API error for user {user_id}: {e}")
            raise Exception(f"Error al acceder al calendario: {e}")
        except Exception as e:
            logger.error(f"Failed to get events for user {user_id}: {e}")
            raise

    def create_event(self, user_id: int, event: CalendarEvent,
                     calendar_id: str = 'primary') -> CalendarEvent:
        """
        Create a new calendar event.

        Args:
            user_id (int): Telegram user ID
            event (CalendarEvent): Event to create
            calendar_id (str): Calendar ID to create event in

        Returns:
            CalendarEvent: Created event with ID

        Raises:
            ValueError: If user is not authenticated or event data is invalid
            Exception: If API call fails
        """
        try:
            service = self._get_calendar_client(user_id)

            # Validate event data
            if not event.title:
                raise ValueError("El título del evento es obligatorio")
            if not event.start_time or not event.end_time:
                raise ValueError("Las fechas de inicio y fin son obligatorias")
            if event.start_time >= event.end_time:
                raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")

            # Convert to Google Calendar format
            google_event = event.to_google_event()

            # Create the event
            created_event = service.events().insert(
                calendarId=calendar_id,
                body=google_event
            ).execute()

            # Convert back to CalendarEvent
            result_event = CalendarEvent.from_google_event(created_event)

            logger.info(f"Created event {result_event.id} for user {user_id}")
            return result_event

        except HttpError as e:
            logger.error(f"Google Calendar API error for user {user_id}: {e}")
            raise Exception(f"Error al crear el evento: {e}")
        except ValueError as e:
            logger.warning(f"Invalid event data for user {user_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create event for user {user_id}: {e}")
            raise

    def delete_event(self, user_id: int, event_id: str,
                     calendar_id: str = 'primary') -> bool:
        """
        Delete a calendar event.

        Args:
            user_id (int): Telegram user ID
            event_id (str): ID of the event to delete
            calendar_id (str): Calendar ID containing the event

        Returns:
            bool: True if event was deleted successfully

        Raises:
            ValueError: If user is not authenticated
            Exception: If API call fails
        """
        try:
            service = self._get_calendar_client(user_id)

            # Delete the event
            service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            logger.info(f"Deleted event {event_id} for user {user_id}")
            return True

        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Event {event_id} not found for user {user_id}")
                raise Exception("El evento no existe o ya fue eliminado")
            else:
                logger.error(f"Google Calendar API error for user {user_id}: {e}")
                raise Exception(f"Error al eliminar el evento: {e}")
        except Exception as e:
            logger.error(f"Failed to delete event {event_id} for user {user_id}: {e}")
            raise

    def get_event_by_id(self, user_id: int, event_id: str,
                        calendar_id: str = 'primary') -> Optional[CalendarEvent]:
        """
        Get a specific event by ID.

        Args:
            user_id (int): Telegram user ID
            event_id (str): ID of the event to retrieve
            calendar_id (str): Calendar ID containing the event

        Returns:
            Optional[CalendarEvent]: Event if found, None otherwise

        Raises:
            ValueError: If user is not authenticated
            Exception: If API call fails
        """
        try:
            service = self._get_calendar_client(user_id)

            # Get the event
            google_event = service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # Convert to CalendarEvent
            event = CalendarEvent.from_google_event(google_event)

            logger.info(f"Retrieved event {event_id} for user {user_id}")
            return event

        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Event {event_id} not found for user {user_id}")
                return None
            else:
                logger.error(f"Google Calendar API error for user {user_id}: {e}")
                raise Exception(f"Error al obtener el evento: {e}")
        except Exception as e:
            logger.error(f"Failed to get event {event_id} for user {user_id}: {e}")
            raise

    def list_calendars(self, user_id: int) -> List[Dict[str, Any]]:
        """
        List available calendars for the user.

        Args:
            user_id (int): Telegram user ID

        Returns:
            List[Dict[str, Any]]: List of calendar information

        Raises:
            ValueError: If user is not authenticated
            Exception: If API call fails
        """
        try:
            service = self._get_calendar_client(user_id)

            # Get calendar list
            calendar_list = service.calendarList().list().execute()

            calendars = []
            for calendar_item in calendar_list.get('items', []):
                calendars.append({
                    'id': calendar_item['id'],
                    'summary': calendar_item.get('summary', 'Sin nombre'),
                    'description': calendar_item.get('description', ''),
                    'primary': calendar_item.get('primary', False),
                    'access_role': calendar_item.get('accessRole', 'reader')
                })

            logger.info(f"Retrieved {len(calendars)} calendars for user {user_id}")
            return calendars

        except HttpError as e:
            logger.error(f"Google Calendar API error for user {user_id}: {e}")
            raise Exception(f"Error al obtener la lista de calendarios: {e}")
        except Exception as e:
            logger.error(f"Failed to list calendars for user {user_id}: {e}")
            raise

    def search_events(self, user_id: int, query: str, max_results: int = 10,
                      calendar_id: str = 'primary') -> List[CalendarEvent]:
        """
        Search for events by text query.

        Args:
            user_id (int): Telegram user ID
            query (str): Search query
            max_results (int): Maximum number of results
            calendar_id (str): Calendar ID to search in

        Returns:
            List[CalendarEvent]: List of matching events

        Raises:
            ValueError: If user is not authenticated
            Exception: If API call fails
        """
        try:
            service = self._get_calendar_client(user_id)

            # Search events
            events_result = service.events().list(
                calendarId=calendar_id,
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Convert to CalendarEvent objects
            calendar_events = []
            for event in events:
                try:
                    calendar_event = CalendarEvent.from_google_event(event)
                    calendar_events.append(calendar_event)
                except Exception as e:
                    logger.warning(f"Failed to parse event {event.get('id', 'unknown')}: {e}")
                    continue

            logger.info(f"Found {len(calendar_events)} events matching '{query}' for user {user_id}")
            return calendar_events

        except HttpError as e:
            logger.error(f"Google Calendar API error for user {user_id}: {e}")
            raise Exception(f"Error al buscar eventos: {e}")
        except Exception as e:
            logger.error(f"Failed to search events for user {user_id}: {e}")
            raise

    def update_event(self, user_id: int, event: CalendarEvent,
                     calendar_id: str = 'primary') -> CalendarEvent:
        """
        Update an existing calendar event.

        Args:
            user_id (int): Telegram user ID
            event (CalendarEvent): Event to update (must have ID)
            calendar_id (str): Calendar ID containing the event

        Returns:
            CalendarEvent: Updated event

        Raises:
            ValueError: If user is not authenticated or event data is invalid
            Exception: If API call fails
        """
        try:
            service = self._get_calendar_client(user_id)

            # Validate event data
            if not event.id:
                raise ValueError("El ID del evento es obligatorio para actualizar")
            if not event.title:
                raise ValueError("El título del evento es obligatorio")
            if not event.start_time or not event.end_time:
                raise ValueError("Las fechas de inicio y fin son obligatorias")
            if event.start_time >= event.end_time:
                raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")

            # Convert to Google Calendar format
            google_event = event.to_google_event()

            # Update the event
            updated_event = service.events().update(
                calendarId=calendar_id,
                eventId=event.id,
                body=google_event
            ).execute()

            # Convert back to CalendarEvent
            result_event = CalendarEvent.from_google_event(updated_event)

            logger.info(f"Updated event {result_event.id} for user {user_id}")
            return result_event

        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Event {event.id} not found for user {user_id}")
                raise Exception("El evento no existe o ya fue eliminado")
            else:
                logger.error(f"Google Calendar API error for user {user_id}: {e}")
                raise Exception(f"Error al actualizar el evento: {e}")
        except ValueError as e:
            logger.warning(f"Invalid event data for user {user_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to update event for user {user_id}: {e}")
            raise
