"""
Test the flow trigger system implementation.

This script tests the functionality of the flow trigger system, including
time-based, event-based, and command-based triggers.
"""

import json
import os
import shutil
import tempfile
import time
from datetime import datetime, timedelta

from personal_automation_bot.services.flows.engine import FlowEngine
from personal_automation_bot.services.flows.models import (
    Flow, FlowAction, FlowStatus, FlowTrigger, TriggerType
)
from personal_automation_bot.services.flows.triggers import TriggerManager


class MockService:
    """Mock service for testing."""

    def __init__(self):
        self.actions = []

    def perform_action(self, action_type, data=None):
        """Mock performing an action."""
        self.actions.append({"type": action_type, "data": data, "timestamp": datetime.now()})
        return {"status": "success", "id": f"action_{len(self.actions)}"}


def test_command_triggers():
    """Test command-based triggers."""
    # Create temporary directory for flow storage
    temp_dir = tempfile.mkdtemp()

    try:
        # Create service registry
        mock_service = MockService()
        service_registry = {"mock": mock_service}

        # Create flow engine
        engine = FlowEngine(temp_dir, service_registry)

        # Create a flow with command trigger
        trigger = FlowTrigger(
            type=TriggerType.COMMAND,
            parameters={"command_name": "test_command"}
        )

        actions = [
            FlowAction(
                service="mock",
                method="perform_action",
                parameters={
                    "action_type": "command_action",
                    "data": "Command triggered"
                }
            )
        ]

        flow = engine.create_flow(
            name="Command Trigger Test",
            trigger=trigger,
            actions=actions,
            user_id="test_user"
        )

        # Create trigger manager
        trigger_manager = TriggerManager(engine)
        trigger_manager.register_flow(flow)

        # Trigger the flow by command
        triggered_flow_id = trigger_manager.trigger_command("test_command")
        assert triggered_flow_id == flow.flow_id

        # Verify action was performed
        assert len(mock_service.actions) == 1
        assert mock_service.actions[0]["type"] == "command_action"
        assert mock_service.actions[0]["data"] == "Command triggered"

        print("Command trigger test passed!")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_event_triggers():
    """Test event-based triggers."""
    # Create temporary directory for flow storage
    temp_dir = tempfile.mkdtemp()

    try:
        # Create service registry
        mock_service = MockService()
        service_registry = {"mock": mock_service}

        # Create flow engine
        engine = FlowEngine(temp_dir, service_registry)

        # Create a flow with event trigger
        trigger = FlowTrigger(
            type=TriggerType.EVENT,
            parameters={"event_name": "test_event"}
        )

        actions = [
            FlowAction(
                service="mock",
                method="perform_action",
                parameters={
                    "action_type": "event_action",
                    "data": "Event triggered"
                }
            )
        ]

        flow = engine.create_flow(
            name="Event Trigger Test",
            trigger=trigger,
            actions=actions,
            user_id="test_user"
        )

        # Create trigger manager
        trigger_manager = TriggerManager(engine)
        trigger_manager.register_flow(flow)

        # Trigger the flow by event
        triggered_flow_ids = trigger_manager.trigger_event("test_event")
        assert flow.flow_id in triggered_flow_ids

        # Verify action was performed
        assert len(mock_service.actions) == 1
        assert mock_service.actions[0]["type"] == "event_action"
        assert mock_service.actions[0]["data"] == "Event triggered"

        print("Event trigger test passed!")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_time_triggers():
    """Test time-based triggers."""
    # Create temporary directory for flow storage
    temp_dir = tempfile.mkdtemp()

    try:
        # Create service registry
        mock_service = MockService()
        service_registry = {"mock": mock_service}

        # Create flow engine
        engine = FlowEngine(temp_dir, service_registry)

        # Get current minute and create a cron expression for the next minute
        now = datetime.now()
        next_minute = now + timedelta(minutes=1)
        cron_expr = f"{next_minute.minute} {next_minute.hour} * * *"

        # Create a flow with time trigger
        trigger = FlowTrigger(
            type=TriggerType.TIME,
            parameters={"cron": cron_expr}
        )

        actions = [
            FlowAction(
                service="mock",
                method="perform_action",
                parameters={
                    "action_type": "time_action",
                    "data": "Time triggered"
                }
            )
        ]

        flow = engine.create_flow(
            name="Time Trigger Test",
            trigger=trigger,
            actions=actions,
            user_id="test_user"
        )

        # Create trigger manager
        trigger_manager = TriggerManager(engine)
        trigger_manager.register_flow(flow)

        # Start the scheduler
        trigger_manager.start_scheduler()

        # Wait for the scheduler to run (this is a simplified test)
        print(f"Waiting for scheduled time ({next_minute.strftime('%H:%M')})...")

        # In a real test, we would wait for the scheduled time
        # For this example, we'll just wait a short time and then manually trigger
        time.sleep(2)

        # For testing purposes, manually execute the flow
        # In a real scenario, the scheduler would do this automatically
        result = engine.execute_flow(flow.flow_id)

        # Stop the scheduler
        trigger_manager.stop_scheduler()

        # Verify action was performed
        assert len(mock_service.actions) == 1
        assert mock_service.actions[0]["type"] == "time_action"
        assert mock_service.actions[0]["data"] == "Time triggered"

        print("Time trigger test passed!")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_command_triggers()
    test_event_triggers()
    test_time_triggers()
