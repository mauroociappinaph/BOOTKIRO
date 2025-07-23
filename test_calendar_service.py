#!/usr/bin/env python3
"""
Test script for the Calendar Service functionality.
"""
import os
import sys
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from personal_automation_bot.services.calendar import CalendarService, CalendarEvent
from personal_automation_bot.utils.auth import google_auth_manager


def test_calendar_service():
    """Test the calendar service functionality."""
    print("🧪 Testing Calendar Service...")

    # Test user ID (you should replace this with a real authenticated user ID)
    test_user_id = "test_user_123"

    try:
        # Initialize service
        calendar_service = CalendarService()
        print("✅ Calendar service initialized")

        # Check if user is authenticated
        if not google_auth_manager.is_user_authenticated(test_user_id):
            print("❌ Test user is not authenticated with Google")
            print("   Please run the authentication flow first")
            return False

        print("✅ User is authenticated")

        # Test 1: Get upcoming events
        print("\n📅 Testing event retrieval...")
        try:
            events = calendar_service.get_events(test_user_id, max_results=5)
            print(f"✅ Retrieved {len(events)} events")

            for i, event in enumerate(events[:3], 1):  # Show first 3 events
                print(f"   {i}. {event.title} - {event.start_time}")

        except Exception as e:
            print(f"❌ Error retrieving events: {e}")

        # Test 2: Create a test event
        print("\n➕ Testing event creation...")
        try:
            test_event = CalendarEvent(
                title="Test Event - Calendar Service",
                description="This is a test event created by the calendar service test",
                start_time=datetime.now() + timedelta(hours=1),
                end_time=datetime.now() + timedelta(hours=2),
                all_day=False
            )

            created_event = calendar_service.create_event(test_user_id, test_event)
            print(f"✅ Created test event: {created_event.id}")
            print(f"   Title: {created_event.title}")
            print(f"   Start: {created_event.start_time}")

            # Test 3: Get the created event by ID
            print("\n🔍 Testing event retrieval by ID...")
            retrieved_event = calendar_service.get_event_by_id(test_user_id, created_event.id)
            if retrieved_event:
                print(f"✅ Retrieved event by ID: {retrieved_event.title}")
            else:
                print("❌ Could not retrieve event by ID")

            # Test 4: Delete the test event
            print("\n🗑️ Testing event deletion...")
            success = calendar_service.delete_event(test_user_id, created_event.id)
            if success:
                print("✅ Test event deleted successfully")
            else:
                print("❌ Failed to delete test event")

        except Exception as e:
            print(f"❌ Error in event creation/deletion test: {e}")

        # Test 5: List calendars
        print("\n📋 Testing calendar list...")
        try:
            calendars = calendar_service.list_calendars(test_user_id)
            print(f"✅ Found {len(calendars)} calendars")

            for calendar in calendars[:3]:  # Show first 3 calendars
                primary = " (Primary)" if calendar.get('primary') else ""
                print(f"   - {calendar['summary']}{primary}")

        except Exception as e:
            print(f"❌ Error listing calendars: {e}")

        print("\n✅ Calendar service tests completed!")
        return True

    except Exception as e:
        print(f"❌ Calendar service test failed: {e}")
        return False


def test_calendar_event_model():
    """Test the CalendarEvent model."""
    print("\n🧪 Testing CalendarEvent model...")

    try:
        # Test event creation
        event = CalendarEvent(
            title="Test Event",
            description="Test description",
            start_time=datetime(2024, 12, 25, 14, 30),
            end_time=datetime(2024, 12, 25, 16, 30),
            location="Test Location",
            attendees=["test@example.com"],
            all_day=False
        )

        print("✅ CalendarEvent created successfully")

        # Test Google event conversion
        google_event = event.to_google_event()
        print("✅ Converted to Google event format")

        # Test back conversion
        converted_back = CalendarEvent.from_google_event(google_event)
        print("✅ Converted back from Google event format")

        # Test display formatting
        display_text = event.format_for_display()
        print("✅ Formatted for display")
        print(f"   Display text: {display_text[:100]}...")

        # Test all-day event
        all_day_event = CalendarEvent(
            title="All Day Event",
            start_time=datetime(2024, 12, 25),
            end_time=datetime(2024, 12, 26),
            all_day=True
        )

        all_day_google = all_day_event.to_google_event()
        print("✅ All-day event conversion works")

        print("✅ CalendarEvent model tests completed!")
        return True

    except Exception as e:
        print(f"❌ CalendarEvent model test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Calendar Service Tests\n")

    # Test the model first
    model_success = test_calendar_event_model()

    # Test the service
    service_success = test_calendar_service()

    if model_success and service_success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
