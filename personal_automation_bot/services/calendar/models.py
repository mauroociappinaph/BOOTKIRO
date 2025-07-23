"""
Data models for calendar events.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class CalendarEvent:
    """Represents a calendar event."""

    id: Optional[str] = None
    title: str = ""
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    attendees: Optional[List[str]] = None
    all_day: bool = False
    calendar_id: str = "primary"

    def to_google_event(self) -> Dict[str, Any]:
        """Convert to Google Calendar API event format."""
        event = {
            'summary': self.title,
            'description': self.description or '',
            'location': self.location or '',
        }

        if self.all_day:
            # All-day event
            event['start'] = {
                'date': self.start_time.strftime('%Y-%m-%d'),
                'timeZone': 'UTC',
            }
            event['end'] = {
                'date': self.end_time.strftime('%Y-%m-%d'),
                'timeZone': 'UTC',
            }
        else:
            # Timed event
            event['start'] = {
                'dateTime': self.start_time.isoformat(),
                'timeZone': 'UTC',
            }
            event['end'] = {
                'dateTime': self.end_time.isoformat(),
                'timeZone': 'UTC',
            }

        if self.attendees:
            event['attendees'] = [{'email': email} for email in self.attendees]

        return event

    @classmethod
    def from_google_event(cls, google_event: Dict[str, Any]) -> 'CalendarEvent':
        """Create CalendarEvent from Google Calendar API event."""
        event = cls()

        event.id = google_event.get('id')
        event.title = google_event.get('summary', 'Sin título')
        event.description = google_event.get('description')
        event.location = google_event.get('location')

        # Parse start and end times
        start = google_event.get('start', {})
        end = google_event.get('end', {})

        if 'date' in start:
            # All-day event
            event.all_day = True
            event.start_time = datetime.fromisoformat(start['date'])
            event.end_time = datetime.fromisoformat(end['date'])
        else:
            # Timed event
            event.all_day = False
            start_dt = start.get('dateTime')
            end_dt = end.get('dateTime')

            if start_dt:
                # Remove timezone info for simplicity
                if start_dt.endswith('Z'):
                    start_dt = start_dt[:-1] + '+00:00'
                event.start_time = datetime.fromisoformat(start_dt.replace('Z', '+00:00'))

            if end_dt:
                # Remove timezone info for simplicity
                if end_dt.endswith('Z'):
                    end_dt = end_dt[:-1] + '+00:00'
                event.end_time = datetime.fromisoformat(end_dt.replace('Z', '+00:00'))

        # Parse attendees
        attendees = google_event.get('attendees', [])
        if attendees:
            event.attendees = [attendee.get('email') for attendee in attendees if attendee.get('email')]

        return event

    def format_for_display(self) -> str:
        """Format event for display in Telegram."""
        lines = [f"📅 **{self.title}**"]

        if self.start_time and self.end_time:
            if self.all_day:
                lines.append(f"🕐 Todo el día - {self.start_time.strftime('%d/%m/%Y')}")
            else:
                start_str = self.start_time.strftime('%d/%m/%Y %H:%M')
                end_str = self.end_time.strftime('%H:%M')
                lines.append(f"🕐 {start_str} - {end_str}")

        if self.location:
            lines.append(f"📍 {self.location}")

        if self.description:
            # Truncate long descriptions
            desc = self.description[:100] + "..." if len(self.description) > 100 else self.description
            lines.append(f"📝 {desc}")

        if self.attendees:
            attendees_str = ", ".join(self.attendees[:3])
            if len(self.attendees) > 3:
                attendees_str += f" y {len(self.attendees) - 3} más"
            lines.append(f"👥 {attendees_str}")

        return "\n".join(lines)
