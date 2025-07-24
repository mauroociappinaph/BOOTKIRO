"""
Calendar service package for the Simplified Google Bot.
"""

from simplified_google_bot.services.calendar.calendar_client import CalendarClient
from simplified_google_bot.services.calendar.calendar_service import CalendarService, calendar_service
from simplified_google_bot.services.calendar.models import CalendarEvent, Calendar, TimeSlot

__all__ = [
    'CalendarClient',
    'CalendarService',
    'calendar_service',
    'CalendarEvent',
    'Calendar',
    'TimeSlot'
]
