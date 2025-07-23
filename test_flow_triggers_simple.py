"""
Test the flow trigger system implementation.
"""

import os
import shutil
import tempfile
from datetime import datetime

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
    print("\nTesting command triggers...")

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

        print(f"Created flow: {flow.flow_id}")

        # Create trigger manager
        trigger_manager = TriggerManager(engine)
        trigger_manager.register_flow(flow)

        # Trigger the flow by command
        print("Triggering flow by command...")
        triggered_flow_id = trigger_manager.trigger_command("test_command")
        print(f"Triggered flow ID: {triggered_flow_id}")

        assert triggered_flow_id == flow.flow_id

        # Verify action was performed
        print(f"Mock service actions: {mock_service.actions}")
        assert len(mock_service.actions) == 1
        assert mock_service.actions[0]["type"] == "command_action"
        assert mock_service.actions[0]["data"] == "Command triggered"

        print("Command trigger test passed!")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_event_triggers():
    """Test event-based triggers."""
    print("\nTesting event triggers...")

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

        print(f"Created flow: {flow.flow_id}")

        # Create trigger manager
        trigger_manager = TriggerManager(engine)
        trigger_manager.register_flow(flow)

        # Trigger the flow by event
        print("Triggering flow by event...")
        triggered_flow_ids = trigger_manager.trigger_event("test_event")
        print(f"Triggered flow IDs: {triggered_flow_ids}")

        assert flow.flow_id in triggered_flow_ids

        # Verify action was performed
        print(f"Mock service actions: {mock_service.actions}")
        assert len(mock_service.actions) == 1
        assert mock_service.actions[0]["type"] == "event_action"
        assert mock_service.actions[0]["data"] == "Event triggered"

        print("Event trigger test passed!")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_command_triggers()
    test_event_triggers()
    print("\nAll trigger tests passed!")
