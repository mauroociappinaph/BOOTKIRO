"""
Tests for the Calendar service.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from simplified_google_bot.services.calendar.calendar_service import CalendarService
from simplified_google_bot.services.calendar.models import CalendarEvent, Calendar, TimeSlot


class TestCalendarService(unittest.TestCase):
    """Test cases for the Calendar service."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the auth manager
        self.auth_manager_patcher = patch('simplified_google_bot.services.calendar.calendar_service.google_auth_manager')
        self.mock_auth_manager = self.auth_manager_patcher.start()

        # Mock credentials
        self.mock_credentials = MagicMock()
        self.mock_auth_manager.get_user_credentials.return_value = self.mock_credentials

        # Mock the calendar client
        self.client_patcher = patch('simplified_google_bot.services.calendar.calendar_service.CalendarClient')
        self.mock_client_class = self.client_patcher.start()
        self.mock_client = MagicMock()
        self.mock_client_class.return_value = self.mock_client

        # Create the service
        self.service = CalendarService()

        # Test user ID
        self.user_id = 123456789

    def tearDown(self):
        """Tear down test fixtures."""
        self.auth_manager_patcher.stop()
        self.client_patcher.stop()

    def test_get_client(self):
        """Test getting a client for a user."""
        client = self.service._get_client(self.user_id)

        self.mock_auth_manager.get_user_credentials.assert_called_once_with(self.user_id)
        self.mock_client_class.assert_called_once_with(self.mock_credentials)
        self.assertEqual(client, self.mock_client)

    def test_get_client_not_authenticated(self):
        """Test getting a client for an unauthenticated user."""
        self.mock_auth_manager.get_user_credentials.return_value = None

        with self.assertRaises(ValueError):
            self.service._get_client(self.user_id)

    def test_get_calendars(self):
        """Test getting calendars."""
        # Mock the API response
        mock_calendars = [
            {'id': 'calendar1', 'summary': 'Calendar 1'},
            {'id': 'calendar2', 'summary': 'Calendar 2', 'primary': True}
        ]
        self.mock_client.list_calendars.return_value = mock_calendars

        # Call the method
        calendars = self.service.get_calendars(self.user_id)

        # Verify the result
        self.assertEqual(len(calendars), 2)
        self.assertIsInstance(calendars[0], Calendar)
        self.assertEqual(calendars[0].id, 'calendar1')
        self.assertEqual(calendars[0].summary, 'Calendar 1')
        self.assertFalse(calendars[0].primary)
        self.assertEqual(calendars[1].id, 'calendar2')
        self.assertEqual(calendars[1].summary, 'Calendar 2')
        self.assertTrue(calendars[1].primary)

    def test_get_upcoming_events(self):
        """Test getting upcoming events."""
        # Mock the API response
        mock_events = [
            {
                'id': 'event1',
                'summary': 'Event 1',
                'start': {'dateTime': '2023-01-01T10:00:00Z'},
                'end': {'dateTime': '2023-01-01T11:00:00Z'}
            },
            {
                'id': 'event2',
                'summary': 'Event 2',
                'start': {'dateTime': '2023-01-02T14:00:00Z'},
                'end': {'dateTime': '2023-01-02T15:00:00Z'}
            }
        ]
        self.mock_client.get_events.return_value = mock_events

        # Call the method
        events = self.service.get_upcoming_events(self.user_id)

        # Verify the result
        self.assertEqual(len(events), 2)
        self.assertIsInstance(events[0], CalendarEvent)
        self.assertEqual(events[0].id, 'event1')
        self.assertEqual(events[0].summary, 'Event 1')
        self.assertEqual(events[1].id, 'event2')
        self.assertEqual(events[1].summary, 'Event 2')

    def test_create_event(self):
        """Test creating an event."""
        # Mock the API response
        mock_created_event = {
            'id': 'new_event',
            'summary': 'New Event',
            'start': {'dateTime': '2023-01-01T10:00:00Z'},
            'end': {'dateTime': '2023-01-01T11:00:00Z'}
        }
        self.mock_client.create_event.return_value = mock_created_event

        # Event data to create
        event_data = {
            'summary': 'New Event',
            'start': {'dateTime': '2023-01-01T10:00:00Z'},
            'end': {'dateTime': '2023-01-01T11:00:00Z'}
        }

        # Call the method
        event = self.service.create_event(self.user_id, event_data)

        # Verify the result
        self.assertIsInstance(event, CalendarEvent)
        self.assertEqual(event.id, 'new_event')
        self.assertEqual(event.summary, 'New Event')
        self.mock_client.create_event.assert_called_once_with(
            event_data=event_data,
            calendar_id='primary',
            send_notifications=True
        )

    def test_update_event(self):
        """Test updating an event."""
        # Mock the API response
        mock_updated_event = {
            'id': 'event1',
            'summary': 'Updated Event',
            'start': {'dateTime': '2023-01-01T10:00:00Z'},
            'end': {'dateTime': '2023-01-01T11:00:00Z'}
        }
        self.mock_client.update_event.return_value = mock_updated_event

        # Event data to update
        event_data = {
            'summary': 'Updated Event',
            'start': {'dateTime': '2023-01-01T10:00:00Z'},
            'end': {'dateTime': '2023-01-01T11:00:00Z'}
        }

        # Call the method
        event = self.service.update_event(self.user_id, 'event1', event_data)

        # Verify the result
        self.assertIsInstance(event, CalendarEvent)
        self.assertEqual(event.id, 'event1')
        self.assertEqual(event.summary, 'Updated Event')
        self.mock_client.update_event.assert_called_once_with(
            event_id='event1',
            event_data={'id': 'event1', **event_data},
            calendar_id='primary',
            send_notifications=True
        )

    def test_delete_event(self):
        """Test deleting an event."""
        # Mock the API response
        self.mock_client.delete_event.return_value = True

        # Call the method
        result = self.service.delete_event(self.user_id, 'event1')

        # Verify the result
        self.assertTrue(result)
        self.mock_client.delete_event.assert_called_once_with(
            event_id='event1',
            calendar_id='primary',
            send_notifications=True
        )

    def test_quick_add_event(self):
        """Test quick adding an event."""
        # Mock the API response
        mock_event = {
            'id': 'quick_event',
            'summary': 'Meeting with John',
            'start': {'dateTime': '2023-01-01T15:00:00Z'},
            'end': {'dateTime': '2023-01-01T16:00:00Z'}
        }
        self.mock_client.quick_add_event.return_value = mock_event

        # Call the method
        event = self.service.quick_add_event(self.user_id, 'Meeting with John tomorrow at 3pm')

        # Verify the result
        self.assertIsInstance(event, CalendarEvent)
        self.assertEqual(event.id, 'quick_event')
        self.assertEqual(event.summary, 'Meeting with John')
        self.mock_client.quick_add_event.assert_called_once_with(
            'Meeting with John tomorrow at 3pm',
            'primary'
        )

    def test_format_event_list(self):
        """Test formatting an event list."""
        # Create test events
        event1 = CalendarEvent(
            id='event1',
            summary='Morning Meeting',
            start_time=datetime(2023, 1, 1, 9, 0),
            end_time=datetime(2023, 1, 1, 10, 0)
        )
        event2 = CalendarEvent(
            id='event2',
            summary='Lunch',
            start_time=datetime(2023, 1, 1, 12, 0),
            end_time=datetime(2023, 1, 1, 13, 0),
            location='Cafeteria'
        )
        event3 = CalendarEvent(
            id='event3',
            summary='Next Day Meeting',
            start_time=datetime(2023, 1, 2, 10, 0),
            end_time=datetime(2023, 1, 2, 11, 0)
        )

        # Call the method
        formatted = self.service.format_event_list([event1, event2, event3])

        # Verify the result contains expected elements
        self.assertIn('Morning Meeting', formatted)
        self.assertIn('Lunch', formatted)
        self.assertIn('Next Day Meeting', formatted)
        self.assertIn('Cafeteria', formatted)
        self.assertIn('January 01, 2023', formatted)
        self.assertIn('January 02, 2023', formatted)


if __name__ == '__main__':
    unittest.main()
