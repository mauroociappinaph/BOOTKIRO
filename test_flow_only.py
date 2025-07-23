"""
Test the flow functionality directly without importing the full bot.
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


def test_flow_functionality():
    """Test the flow functionality."""
    print("Testing flow functionality...")

    # Create temporary directory for flow storage
    temp_dir = tempfile.mkdtemp()

    try:
        # Create service registry
        mock_service = MockService()
        service_registry = {"mock": mock_service}

        # Create flow engine
        engine = FlowEngine(temp_dir, service_registry)

        # Test 1: Create a flow
        print("\nTest 1: Creating a flow")
        trigger = FlowTrigger(
            type=TriggerType.COMMAND,
            parameters={"command_name": "test_command"}
        )

        actions = [
            FlowAction(
                service="mock",
                method="perform_action",
                parameters={
                    "action_type": "test_action",
                    "data": "Test data"
                }
            )
        ]

        flow = engine.create_flow(
            name="Test Flow",
            trigger=trigger,
            actions=actions,
            user_id="test_user"
        )

        print(f"Created flow: {flow.flow_id}")
        print(f"Flow name: {flow.name}")
        print(f"Flow status: {flow.status}")

        # Test 2: List flows
        print("\nTest 2: Listing flows")
        flows = engine.list_flows()
        print(f"Number of flows: {len(flows)}")
        for f in flows:
            print(f"- {f.name} ({f.flow_id})")

        # Test 3: Execute flow
        print("\nTest 3: Executing flow")
        result = engine.execute_flow(flow.flow_id)
        print(f"Flow execution result: {result.success}")
        print(f"Actions executed: {result.actions_executed}")
        print(f"Action results: {result.action_results}")

        # Verify action was performed
        print(f"Mock service actions: {mock_service.actions}")
        assert len(mock_service.actions) == 1
        assert mock_service.actions[0]["type"] == "test_action"
        assert mock_service.actions[0]["data"] == "Test data"

        # Test 4: Deactivate flow
        print("\nTest 4: Deactivating flow")
        deactivated_flow = engine.deactivate_flow(flow.flow_id)
        print(f"Flow status after deactivation: {deactivated_flow.status}")

        # Test 5: Try to execute deactivated flow
        print("\nTest 5: Executing deactivated flow")
        result = engine.execute_flow(flow.flow_id)
        print(f"Deactivated flow execution result: {result.success}")
        print(f"Error message: {result.error_message}")

        # Test 6: Activate flow
        print("\nTest 6: Activating flow")
        activated_flow = engine.activate_flow(flow.flow_id)
        print(f"Flow status after activation: {activated_flow.status}")

        # Test 7: Execute flow again
        print("\nTest 7: Executing flow again")
        result = engine.execute_flow(flow.flow_id)
        print(f"Flow execution result after activation: {result.success}")

        # Verify action was performed again
        assert len(mock_service.actions) == 2

        # Test 8: Delete flow
        print("\nTest 8: Deleting flow")
        engine.delete_flow(flow.flow_id)
        print("Flow deleted")

        # Verify flow was deleted
        flows = engine.list_flows()
        print(f"Number of flows after deletion: {len(flows)}")
        assert len(flows) == 0

        print("\nAll flow functionality tests passed!")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_flow_functionality()
