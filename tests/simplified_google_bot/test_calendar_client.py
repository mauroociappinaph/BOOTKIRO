"""
Tests for the Calendar API client.
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from simplified_google_bot.services.calendar.calendar_client import CalendarClient


class TestCalendarClient(unittest.TestCase):
    """Test cases for the Calendar API client."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_credentials = MagicMock()
        self.mock_service = MagicMock()

        # Create a patch for the build function
        self.build_patcher = patch('simplified_google_bot.services.calendar.calendar_client.build')
        self.mock_build = self.build_patcher.start()
        self.mock_build.return_value = self.mock_service

        # Create the client with mock credentials
        self.client = CalendarClient(self.mock_credentials)

    def tearDown(self):
        """Tear down test fixtures."""
        self.build_patcher.stop()

    def test_init(self):
        """Test client initialization."""
        self.mock_build.assert_called_once_with('calendar', 'v3', credentials=self.mock_credentials)
        self.assertEqual(self.client.primary_calendar_id, 'primary')

    def test_list_calendars(self):
        """Test listing calendars."""
        # Mock the API response
        mock_response = {
            'items': [
                {'id': 'calendar1', 'summary': 'Calendar 1'},
                {'id': 'calendar2', 'summary': 'Calendar 2'}
            ]
        }
        self.mock_service.calendarList().list().execute.return_value = mock_response

        # Call the method
        result = self.client.list_calendars()

        # Verify the result
        self.assertEqual(result, mock_response['items'])
        self.mock_service.calendarList().list.assert_called_once()

    def test_get_events(self):
        """Test getting events."""
        # Mock the API response
        mock_response = {
            'items': [
                {'id': 'event1', 'summary': 'Event 1'},
                {'id': 'event2', 'summary': 'Event 2'}
            ]
        }
        self.mock_service.events().list().execute.return_value = mock_response

        # Call the method with default parameters
        result = self.client.get_events()

        # Verify the result
        self.assertEqual(result, mock_response['items'])
        self.mock_service.events().list.assert_called_once()

    def test_get_event(self):
        """Test getting a specific event."""
        # Mock the API response
        mock_event = {'id': 'event1', 'summary': 'Event 1'}
        self.mock_service.events().get().execute.return_value = mock_event

        # Call the method
        result = self.client.get_event('event1')

        # Verify the result
        self.assertEqual(result, mock_event)
        self.mock_service.events().get.assert_called_once_with(
            calendarId='primary',
            eventId='event1'
        )

    def test_create_event(self):
        """Test creating an event."""
        # Mock the API response
        mock_event = {'id': 'new_event', 'summary': 'New Event'}
        self.mock_service.events().insert().execute.return_value = mock_event

        # Event data to create
        event_data = {
            'summary': 'New Event',
            'start': {'dateTime': '2023-01-01T10:00:00Z'},
            'end': {'dateTime': '2023-01-01T11:00:00Z'}
        }

        # Call the method
        result = self.client.create_event(event_data)

        # Verify the result
        self.assertEqual(result, mock_event)
        self.mock_service.events().insert.assert_called_once_with(
            calendarId='primary',
            body=event_data,
            sendUpdates='all'
        )

    def test_update_event(self):
        """Test updating an event."""
        # Mock the API response
        mock_event = {'id': 'event1', 'summary': 'Updated Event'}
        self.mock_service.events().update().execute.return_value = mock_event

        # Event data to update
        event_data = {
            'summary': 'Updated Event',
            'start': {'dateTime': '2023-01-01T10:00:00Z'},
            'end': {'dateTime': '2023-01-01T11:00:00Z'}
        }

        # Call the method
        result = self.client.update_event('event1', event_data)

        # Verify the result
        self.assertEqual(result, mock_event)
        self.mock_service.events().update.assert_called_once_with(
            calendarId='primary',
            eventId='event1',
            body=event_data,
            sendUpdates='all'
        )

    def test_delete_event(self):
        """Test deleting an event."""
        # Mock the API response
        self.mock_service.events().delete().execute.return_value = None

        # Call the method
        result = self.client.delete_event('event1')

        # Verify the result
        self.assertTrue(result)
        self.mock_service.events().delete.assert_called_once_with(
            calendarId='primary',
            eventId='event1',
            sendUpdates='all'
        )

    def test_quick_add_event(self):
        """Test quick adding an event."""
        # Mock the API response
        mock_event = {'id': 'quick_event', 'summary': 'Meeting with John'}
        self.mock_service.events().quickAdd().execute.return_value = mock_event

        # Call the method
        result = self.client.quick_add_event('Meeting with John tomorrow at 3pm')

        # Verify the result
        self.assertEqual(result, mock_event)
        self.mock_service.events().quickAdd.assert_called_once_with(
            calendarId='primary',
            text='Meeting with John tomorrow at 3pm'
        )


if __name__ == '__main__':
    unittest.main()
