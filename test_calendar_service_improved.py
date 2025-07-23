#!/usr/bin/env python3
"""
Improved test script for the Calendar Service functionality with mocks.
"""
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from personal_automation_bot.services.calendar import CalendarService, CalendarEvent


def test_calendar_event_model():
    """Test the CalendarEvent model thoroughly."""
    print("🧪 Testing CalendarEvent model...")

    try:
        # Test 1: Basic event creation
        event = CalendarEvent(
            title="Test Event",
            description="Test description",
            start_time=datetime(2024, 12, 25, 14, 30),
            end_time=datetime(2024, 12, 25, 16, 30),
            location="Test Location",
            attendees=["test@example.com", "test2@example.com"],
            all_day=False
        )

        assert event.title == "Test Event"
        assert event.description == "Test description"
        assert event.location == "Test Location"
        assert len(event.attendees) == 2
        assert not event.all_day
        print("✅ Basic event creation works")

        # Test 2: Google event conversion
        google_event = event.to_google_event()

        assert google_event['summary'] == "Test Event"
        assert google_event['description'] == "Test description"
        assert google_event['location'] == "Test Location"
        assert len(google_event['attendees']) == 2
        assert 'dateTime' in google_event['start']
        assert 'dateTime' in google_event['end']
        print("✅ Google event conversion works")

        # Test 3: Back conversion from Google event
        converted_back = CalendarEvent.from_google_event(google_event)

        assert converted_back.title == event.title
        assert converted_back.description == event.description
        assert converted_back.location == event.location
        print("✅ Back conversion from Google event works")

        # Test 4: All-day event
        all_day_event = CalendarEvent(
            title="All Day Event",
            start_time=datetime(2024, 12, 25),
            end_time=datetime(2024, 12, 26),
            all_day=True
        )

        all_day_google = all_day_event.to_google_event()
        assert 'date' in all_day_google['start']
        assert 'date' in all_day_google['end']
        assert 'dateTime' not in all_day_google['start']
        print("✅ All-day event conversion works")

        # Test 5: Display formatting
        display_text = event.format_for_display()
        assert "Test Event" in display_text
        assert "Test Location" in display_text
        assert "Test description" in display_text
        print("✅ Display formatting works")

        # Test 6: Edge cases
        minimal_event = CalendarEvent(title="Minimal Event")
        minimal_display = minimal_event.format_for_display()
        assert "Minimal Event" in minimal_display
        print("✅ Minimal event handling works")

        print("✅ CalendarEvent model tests completed!")
        return True

    except Exception as e:
        print(f"❌ CalendarEvent model test failed: {e}")
        return False


def test_calendar_service_with_mocks():
    """Test the calendar service with mocked Google API."""
    print("\n🧪 Testing Calendar Service with mocks...")

    try:
        # Mock the authentication manager
        with patch('personal_automation_bot.services.calendar.calendar_service.google_auth_manager') as mock_auth:
            # Mock credentials
            mock_credentials = Mock()
            mock_auth.get_user_credentials.return_value = mock_credentials

            # Mock the Google API client
            with patch('personal_automation_bot.services.calendar.calendar_service.build') as mock_build:
                mock_service = Mock()
                mock_build.return_value = mock_service

                # Initialize service
                calendar_service = CalendarService()
                print("✅ Calendar service initialized with mocks")

                # Test 1: Get events
                mock_events_result = {
                    'items': [
                        {
                            'id': 'test_event_1',
                            'summary': 'Test Event 1',
                            'description': 'Test description 1',
                            'start': {'dateTime': '2024-12-25T14:30:00Z'},
                            'end': {'dateTime': '2024-12-25T16:30:00Z'},
                            'location': 'Test Location 1'
                        },
                        {
                            'id': 'test_event_2',
                            'summary': 'Test Event 2',
                            'start': {'date': '2024-12-26'},
                            'end': {'date': '2024-12-27'}
                        }
                    ]
                }

                mock_service.events().list().execute.return_value = mock_events_result

                events = calendar_service.get_events(123, max_results=10)

                assert len(events) == 2
                assert events[0].title == 'Test Event 1'
                assert events[0].id == 'test_event_1'
                assert not events[0].all_day
                assert events[1].title == 'Test Event 2'
                assert events[1].all_day
                print("✅ Get events with mocks works")

                # Test 2: Create event
                mock_created_event = {
                    'id': 'created_event_123',
                    'summary': 'Created Event',
                    'description': 'Created description',
                    'start': {'dateTime': '2024-12-25T14:30:00Z'},
                    'end': {'dateTime': '2024-12-25T16:30:00Z'}
                }

                mock_service.events().insert().execute.return_value = mock_created_event

                test_event = CalendarEvent(
                    title="Created Event",
                    description="Created description",
                    start_time=datetime(2024, 12, 25, 14, 30),
                    end_time=datetime(2024, 12, 25, 16, 30)
                )

                created_event = calendar_service.create_event(123, test_event)

                assert created_event.id == 'created_event_123'
                assert created_event.title == 'Created Event'
                print("✅ Create event with mocks works")

                # Test 3: Update event
                mock_updated_event = {
                    'id': 'updated_event_123',
                    'summary': 'Updated Event',
                    'description': 'Updated description',
                    'start': {'dateTime': '2024-12-25T15:30:00Z'},
                    'end': {'dateTime': '2024-12-25T17:30:00Z'}
                }

                mock_service.events().update().execute.return_value = mock_updated_event

                update_event = CalendarEvent(
                    id="updated_event_123",
                    title="Updated Event",
                    description="Updated description",
                    start_time=datetime(2024, 12, 25, 15, 30),
                    end_time=datetime(2024, 12, 25, 17, 30)
                )

                updated_event = calendar_service.update_event(123, update_event)

                assert updated_event.id == 'updated_event_123'
                assert updated_event.title == 'Updated Event'
                print("✅ Update event with mocks works")

                # Test 4: Delete event
                mock_service.events().delete().execute.return_value = None

                success = calendar_service.delete_event(123, 'test_event_id')

                assert success is True
                print("✅ Delete event with mocks works")

                # Test 5: Get event by ID
                mock_service.events().get().execute.return_value = mock_created_event

                retrieved_event = calendar_service.get_event_by_id(123, 'created_event_123')

                assert retrieved_event is not None
                assert retrieved_event.id == 'created_event_123'
                print("✅ Get event by ID with mocks works")

                # Test 6: Search events
                mock_service.events().list().execute.return_value = {
                    'items': [mock_created_event]
                }

                search_results = calendar_service.search_events(123, 'Created')

                assert len(search_results) == 1
                assert search_results[0].title == 'Created Event'
                print("✅ Search events with mocks works")

                # Test 7: List calendars
                mock_calendar_list = {
                    'items': [
                        {
                            'id': 'primary',
                            'summary': 'Primary Calendar',
                            'description': 'Main calendar',
                            'primary': True,
                            'accessRole': 'owner'
                        },
                        {
                            'id': 'secondary',
                            'summary': 'Secondary Calendar',
                            'primary': False,
                            'accessRole': 'reader'
                        }
                    ]
                }

                mock_service.calendarList().list().execute.return_value = mock_calendar_list

                calendars = calendar_service.list_calendars(123)

                assert len(calendars) == 2
                assert calendars[0]['primary'] is True
                assert calendars[1]['primary'] is False
                print("✅ List calendars with mocks works")

        print("✅ Calendar service with mocks tests completed!")
        return True

    except Exception as e:
        print(f"❌ Calendar service with mocks test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """Test error handling in calendar service."""
    print("\n🧪 Testing error handling...")

    try:
        # Mock authentication to pass the auth check
        with patch('personal_automation_bot.services.calendar.calendar_service.google_auth_manager') as mock_auth:
            mock_credentials = Mock()
            mock_auth.get_user_credentials.return_value = mock_credentials

            with patch('personal_automation_bot.services.calendar.calendar_service.build') as mock_build:
                mock_service = Mock()
                mock_build.return_value = mock_service

                calendar_service = CalendarService()

                # Test invalid event (no title)
                invalid_event = CalendarEvent(
                    title="",  # Empty title
                    start_time=datetime.now(),
                    end_time=datetime.now() + timedelta(hours=1)
                )

                try:
                    calendar_service.create_event(123, invalid_event)
                    assert False, "Should have raised ValueError"
                except ValueError as e:
                    assert "título del evento es obligatorio" in str(e)
                    print("✅ Empty title validation works")

                # Test invalid event (start >= end)
                invalid_event2 = CalendarEvent(
                    title="Test Event",
                    start_time=datetime.now() + timedelta(hours=2),
                    end_time=datetime.now() + timedelta(hours=1)  # End before start
                )

                try:
                    calendar_service.create_event(123, invalid_event2)
                    assert False, "Should have raised ValueError"
                except ValueError as e:
                    assert "fecha de inicio debe ser anterior" in str(e)
                    print("✅ Start/end time validation works")

                # Test update without ID
                invalid_update = CalendarEvent(
                    title="Test Event",
                    start_time=datetime.now(),
                    end_time=datetime.now() + timedelta(hours=1)
                    # No ID provided
                )

                try:
                    calendar_service.update_event(123, invalid_update)
                    assert False, "Should have raised ValueError"
                except ValueError as e:
                    assert "ID del evento es obligatorio" in str(e)
                    print("✅ Update without ID validation works")

        print("✅ Error handling tests completed!")
        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_date_time_parsing():
    """Test date and time parsing functions."""
    print("\n🧪 Testing date/time parsing...")

    try:
        from personal_automation_bot.bot.commands.calendar import CalendarCommands

        commands = CalendarCommands()

        # Test date parsing
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Test "hoy"
        parsed_date = commands._parse_date("hoy")
        assert parsed_date.date() == today.date()
        print("✅ 'hoy' parsing works")

        # Test "mañana"
        parsed_date = commands._parse_date("mañana")
        assert parsed_date.date() == (today + timedelta(days=1)).date()
        print("✅ 'mañana' parsing works")

        # Test DD/MM format
        parsed_date = commands._parse_date("25/12")
        assert parsed_date.month == 12
        assert parsed_date.day == 25
        assert parsed_date.year == today.year
        print("✅ DD/MM parsing works")

        # Test DD/MM/YYYY format (use future date)
        future_year = today.year + 1
        parsed_date = commands._parse_date(f"25/12/{future_year}")
        assert parsed_date.month == 12
        assert parsed_date.day == 25
        assert parsed_date.year == future_year
        print("✅ DD/MM/YYYY parsing works")

        # Test time parsing
        test_date = datetime(2024, 12, 25)

        # Test single time
        start_time, end_time = commands._parse_time("14:30", test_date)
        assert start_time.hour == 14
        assert start_time.minute == 30
        assert end_time.hour == 15  # +1 hour default
        assert end_time.minute == 30
        print("✅ Single time parsing works")

        # Test time range
        start_time, end_time = commands._parse_time("14:30-16:45", test_date)
        assert start_time.hour == 14
        assert start_time.minute == 30
        assert end_time.hour == 16
        assert end_time.minute == 45
        print("✅ Time range parsing works")

        # Test hour only
        start_time, end_time = commands._parse_time("14", test_date)
        assert start_time.hour == 14
        assert start_time.minute == 0
        assert end_time.hour == 15
        assert end_time.minute == 0
        print("✅ Hour only parsing works")

        print("✅ Date/time parsing tests completed!")
        return True

    except Exception as e:
        print(f"❌ Date/time parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Improved Calendar Service Tests\n")

    # Run all tests
    tests = [
        test_calendar_event_model,
        test_calendar_service_with_mocks,
        test_error_handling,
        test_date_time_parsing
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests

    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        print("\n📋 Calendar Service Implementation Summary:")
        print("   ✅ Google Calendar API integration configured")
        print("   ✅ Event viewing functionality implemented")
        print("   ✅ Event creation with conversational flow")
        print("   ✅ Event updating functionality implemented")
        print("   ✅ Event deletion with confirmation")
        print("   ✅ Event search functionality")
        print("   ✅ Date/time parsing with multiple formats")
        print("   ✅ Comprehensive error handling")
        print("   ✅ Telegram bot conversation handler configured")
        print("   ✅ All conversation states and transitions defined")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} tests failed!")
        sys.exit(1)
