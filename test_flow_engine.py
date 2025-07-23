"""
Test the flow engine implementation.

This script tests the basic functionality of the flow engine, including
creating, executing, and managing flows.
"""

import json
import os
import shutil
import tempfile
import time
from datetime import datetime

from personal_automation_bot.services.flows.engine import FlowEngine
from personal_automation_bot.services.flows.models import (
    Flow, FlowAction, FlowStatus, FlowTrigger, TriggerType
)
from personal_automation_bot.services.flows.triggers import TriggerManager


class MockEmailService:
    """Mock email service for testing."""

    def __init__(self):
        self.sent_emails = []

    def send_email(self, to, subject, body):
        """Mock sending an email."""
        self.sent_emails.append({"to": to, "subject": subject, "body": body})
        return {"status": "sent", "id": f"email_{len(self.sent_emails)}"}


class MockCalendarService:
    """Mock calendar service for testing."""

    def __init__(self):
        self.events = []

    def create_event(self, title, start, end, description=None):
        """Mock creating a calendar event."""
        event = {
            "id": f"event_{len(self.events)}",
            "title": title,
            "start": start,
            "end": end,
            "description": description
        }
        self.events.append(event)
        return event


def test_flow_engine():
    """Test the flow engine."""
    # Create temporary directory for flow storage
    temp_dir = tempfile.mkdtemp()

    try:
        # Create service registry
        email_service = MockEmailService()
        calendar_service = MockCalendarService()

        service_registry = {
            "email": email_service,
            "calendar": calendar_service
        }

        # Create flow engine
        engine = FlowEngine(temp_dir, service_registry)

        # Create a flow
        trigger = FlowTrigger(
            type=TriggerType.COMMAND,
            parameters={"command_name": "meeting_summary"}
        )

        actions = [
            FlowAction(
                service="calendar",
                method="create_event",
                parameters={
                    "title": "Meeting Summary",
                    "start": "2025-07-23T10:00:00",
                    "end": "2025-07-23T11:00:00",
                    "description": "Review meeting notes"
                },
                next_on_success=1
            ),
            FlowAction(
                service="email",
                method="send_email",
                parameters={
                    "to": "team@example.com",
                    "subject": "Meeting Summary",
                    "body": "Please review the attached meeting notes."
                }
            )
        ]

        flow = engine.create_flow(
            name="Meeting Summary Workflow",
            trigger=trigger,
            actions=actions,
            user_id="test_user"
        )

        print(f"Created flow: {flow.flow_id}")

        # Execute the flow
        result = engine.execute_flow(flow.flow_id)

        print(f"Flow execution result: {result.success}")
        print(f"Actions executed: {result.actions_executed}")
        print(f"Action results: {result.action_results}")

        # Verify results
        assert result.success
        assert len(result.actions_executed) == 2
        assert len(email_service.sent_emails) == 1
        assert len(calendar_service.events) == 1

        # Test trigger manager
        trigger_manager = TriggerManager(engine)
        trigger_manager.register_flow(flow)

        # Trigger the flow by command
        triggered_flow_id = trigger_manager.trigger_command("meeting_summary")
        assert triggered_flow_id == flow.flow_id

        # Verify more emails and events were created
        assert len(email_service.sent_emails) == 2
        assert len(calendar_service.events) == 2

        print("All tests passed!")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_flow_engine()
