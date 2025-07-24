"""
Data models for the Calendar service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class CalendarEvent:
    """
    Represents a calendar event.
    """
    id: str
    summary: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: List[Dict[str, str]] = field(default_factory=list)
    html_link: Optional[str] = None
    creator: Optional[Dict[str, str]] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    status: str = "confirmed"

    @classmethod
    def from_api_event(cls, event: Dict[str, Any]) -> 'CalendarEvent':
        """
        Create a CalendarEvent from a Google Calendar API event.

        Args:
            event (Dict[str, Any]): Event data from the Google Calendar API.

        Returns:
            CalendarEvent: A CalendarEvent instance.
        """
        # Extract start and end times
        start = event.get('start', {})
        end = event.get('end', {})

        # Parse datetime strings
        start_time = None
        if 'dateTime' in start:
            start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
        elif 'date' in start:
            start_time = datetime.fromisoformat(f"{start['date']}T00:00:00")

        end_time = None
        if 'dateTime' in end:
            end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
        elif 'date' in end:
            end_time = datetime.fromisoformat(f"{end['date']}T23:59:59")

        # Parse created and updated times if available
        created = None
        if 'created' in event:
            created = datetime.fromisoformat(event['created'].replace('Z', '+00:00'))

        updated = None
        if 'updated' in event:
            updated = datetime.fromisoformat(event['updated'].replace('Z', '+00:00'))

        return cls(
            id=event.get('id', ''),
            summary=event.get('summary', 'Untitled Event'),
            start_time=start_time,
            end_time=end_time,
            description=event.get('description'),
            location=event.get('location'),
            attendees=event.get('attendees', []),
            html_link=event.get('htmlLink'),
            creator=event.get('creator'),
            created=created,
            updated=updated,
            status=event.get('status', 'confirmed')
        )

    def to_api_event(self) -> Dict[str, Any]:
        """
        Convert to a Google Calendar API event format.

        Returns:
            Dict[str, Any]: Event data for the Google Calendar API.
        """
        event = {
            'summary': self.summary,
            'start': {},
            'end': {},
        }

        # Add ID if it exists
        if self.id:
            event['id'] = self.id

        # Format start and end times
        if self.start_time:
            if self.start_time.hour == 0 and self.start_time.minute == 0 and self.start_time.second == 0:
                # All-day event
                event['start']['date'] = self.start_time.date().isoformat()
            else:
                # Timed event
                event['start']['dateTime'] = self.start_time.isoformat()

        if self.end_time:
            if self.end_time.hour == 23 and self.end_time.minute == 59 and self.end_time.second == 59:
                # All-day event
                event['end']['date'] = self.end_time.date().isoformat()
            else:
                # Timed event
                event['end']['dateTime'] = self.end_time.isoformat()

        # Add optional fields if they exist
        if self.description:
            event['description'] = self.description

        if self.location:
            event['location'] = self.location

        if self.attendees:
            event['attendees'] = self.attendees

        if self.status and self.status != 'confirmed':
            event['status'] = self.status

        return event

    def format_for_display(self) -> str:
        """
        Format the event for display in Telegram.

        Returns:
            str: Formatted event text.
        """
        # Format date and time
        if self.start_time.date() == self.end_time.date():
            # Same day event
            date_str = self.start_time.strftime("%A, %B %d, %Y")

            if self.start_time.hour == 0 and self.start_time.minute == 0 and \
               self.end_time.hour == 23 and self.end_time.minute == 59:
                # All-day event
                time_str = "All day"
            else:
                # Timed event
                time_str = f"{self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')}"
        else:
            # Multi-day event
            date_str = f"{self.start_time.strftime('%b %d')} - {self.end_time.strftime('%b %d, %Y')}"
            time_str = ""

        # Build the formatted string
        result = [f"📅 *{self.summary}*"]
        result.append(f"📆 {date_str}")

        if time_str:
            result.append(f"🕒 {time_str}")

        if self.location:
            result.append(f"📍 {self.location}")

        if self.description:
            # Truncate description if too long
            desc = self.description
            if len(desc) > 100:
                desc = desc[:97] + "..."
            result.append(f"\n{desc}")

        if self.attendees:
            attendee_count = len(self.attendees)
            result.append(f"\n👥 {attendee_count} attendee{'s' if attendee_count != 1 else ''}")

        if self.html_link:
            result.append(f"\n[View in Google Calendar]({self.html_link})")

        return "\n".join(result)


@dataclass
class TimeSlot:
    """
    Represents an available time slot.
    """
    start: datetime
    end: datetime

    def format_for_display(self) -> str:
        """
        Format the time slot for display.

        Returns:
            str: Formatted time slot text.
        """
        date_str = self.start.strftime("%A, %B %d, %Y")
        time_str = f"{self.start.strftime('%I:%M %p')} - {self.end.strftime('%I:%M %p')}"

        return f"{date_str}\n{time_str}"


@dataclass
class Calendar:
    """
    Represents a Google Calendar.
    """
    id: str
    summary: str
    description: Optional[str] = None
    primary: bool = False

    @classmethod
    def from_api_calendar(cls, calendar: Dict[str, Any]) -> 'Calendar':
        """
        Create a Calendar from a Google Calendar API calendar.

        Args:
            calendar (Dict[str, Any]): Calendar data from the Google Calendar API.

        Returns:
            Calendar: A Calendar instance.
        """
        return cls(
            id=calendar.get('id', ''),
            summary=calendar.get('summary', 'Untitled Calendar'),
            description=calendar.get('description'),
            primary=calendar.get('primary', False)
        )
