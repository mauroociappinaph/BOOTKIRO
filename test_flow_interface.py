"""
Test the flow interface implementation.

This script tests the basic functionality of the flow interface by directly
using the flow engine and trigger manager.
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


class MockService:
    """Mock service for testing."""

    def __init__(self):
        self.actions = []

    def perform_action(self, action_type, data=None):
        """Mock performing an action."""
        self.actions.append({"type": action_type, "data": data, "timestamp": datetime.now()})
        return {"status": "success", "id": f"action_{len(self.actions)}"}


def test_flow_interface():
    """Test the flow interface."""
    # Create temporary directory for flow storage
    temp_dir = tempfile.mkdtemp()

    try:
        # Create service registry
        mock_service = MockService()
        service_registry = {"mock": mock_service}

        # Create flow engine
        engine = FlowEngine(temp_dir, service_registry)

        # Create a flow
        trigger = FlowTrigger(
            type=TriggerType.COMMAND,
            parameters={"command_name": "test_interface"}
        )

        actions = [
            FlowAction(
                service="mock",
                method="perform_action",
                parameters={
                    "action_type": "interface_test",
                    "data": "Interface test"
                }
            )
        ]

        flow = engine.create_flow(
            name="Interface Test Flow",
            trigger=trigger,
            actions=actions,
            user_id="test_user"
        )

        print(f"Created flow: {flow.flow_id}")

        # List flows
        flows = engine.list_flows()
        print(f"Number of flows: {len(flows)}")

        # Get flow
        retrieved_flow = engine.get_flow(flow.flow_id)
        print(f"Retrieved flow: {retrieved_flow.name}")

        # Execute flow
        result = engine.execute_flow(flow.flow_id)
        print(f"Flow execution result: {result.success}")

        # Verify action was performed
        assert len(mock_service.actions) == 1
        assert mock_service.actions[0]["type"] == "interface_test"

        # Deactivate flow
        deactivated_flow = engine.deactivate_flow(flow.flow_id)
        print(f"Flow status after deactivation: {deactivated_flow.status}")

        # Try to execute deactivated flow
        result = engine.execute_flow(flow.flow_id)
        print(f"Deactivated flow execution result: {result.success}")
        print(f"Error message: {result.error_message}")

        # Activate flow
        activated_flow = engine.activate_flow(flow.flow_id)
        print(f"Flow status after activation: {activated_flow.status}")

        # Execute flow again
        result = engine.execute_flow(flow.flow_id)
        print(f"Flow execution result after activation: {result.success}")

        # Verify action was performed again
        assert len(mock_service.actions) == 2

        # Delete flow
        engine.delete_flow(flow.flow_id)
        print("Flow deleted")

        # Verify flow was deleted
        flows = engine.list_flows()
        print(f"Number of flows after deletion: {len(flows)}")

        print("All interface tests passed!")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_flow_interface()
