"""
Flow execution engine for Personal Automation Bot.

This module provides the core functionality for executing workflows defined
as sequences of actions triggered by specific events or schedules.
"""

import json
import logging
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from personal_automation_bot.services.flows.models import (
    Flow, FlowAction, FlowExecutionResult, FlowStatus, FlowTrigger
)

logger = logging.getLogger(__name__)


class FlowEngine:
    """Engine for executing and managing flows."""

    def __init__(self, storage_path: str, service_registry: Dict[str, Any]):
        """
        Initialize the flow engine.

        Args:
            storage_path: Path to store flow definitions
            service_registry: Dictionary mapping service names to service instances
        """
        self.storage_path = Path(storage_path)
        self.service_registry = service_registry
        self.flows: Dict[str, Flow] = {}

        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_path, exist_ok=True)

        # Load existing flows
        self._load_flows()

    def _load_flows(self) -> None:
        """Load all flow definitions from storage."""
        try:
            flow_files = list(self.storage_path.glob("*.json"))
            for flow_file in flow_files:
                try:
                    with open(flow_file, "r") as f:
                        flow_data = json.load(f)
                        flow = Flow.from_dict(flow_data)
                        self.flows[flow.flow_id] = flow
                except Exception as e:
                    logger.error(f"Error loading flow from {flow_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading flows: {e}")

    def _save_flow(self, flow: Flow) -> None:
        """
        Save a flow definition to storage.

        Args:
            flow: The flow to save
        """
        try:
            flow_path = self.storage_path / f"{flow.flow_id}.json"
            with open(flow_path, "w") as f:
                json.dump(flow.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving flow {flow.flow_id}: {e}")

    def create_flow(
        self,
        name: str,
        trigger: FlowTrigger,
        actions: List[FlowAction],
        user_id: Optional[str] = None
    ) -> Flow:
        """
        Create a new flow.

        Args:
            name: Name of the flow
            trigger: Trigger that initiates the flow
            actions: List of actions to execute
            user_id: ID of the user who owns the flow

        Returns:
            The created flow
        """
        flow_id = str(uuid.uuid4())
        flow = Flow(
            flow_id=flow_id,
            name=name,
            trigger=trigger,
            actions=actions,
            created_at=datetime.now(),
            status=FlowStatus.ACTIVE,
            user_id=user_id
        )

        self.flows[flow_id] = flow
        self._save_flow(flow)

        return flow

    def update_flow(self, flow: Flow) -> Flow:
        """
        Update an existing flow.

        Args:
            flow: The updated flow

        Returns:
            The updated flow

        Raises:
            ValueError: If the flow doesn't exist
        """
        if flow.flow_id not in self.flows:
            raise ValueError(f"Flow {flow.flow_id} not found")

        self.flows[flow.flow_id] = flow
        self._save_flow(flow)

        return flow

    def delete_flow(self, flow_id: str) -> None:
        """
        Delete a flow.

        Args:
            flow_id: ID of the flow to delete

        Raises:
            ValueError: If the flow doesn't exist
        """
        if flow_id not in self.flows:
            raise ValueError(f"Flow {flow_id} not found")

        flow_path = self.storage_path / f"{flow_id}.json"
        if flow_path.exists():
            os.remove(flow_path)

        del self.flows[flow_id]

    def get_flow(self, flow_id: str) -> Flow:
        """
        Get a flow by ID.

        Args:
            flow_id: ID of the flow to get

        Returns:
            The flow

        Raises:
            ValueError: If the flow doesn't exist
        """
        if flow_id not in self.flows:
            raise ValueError(f"Flow {flow_id} not found")

        return self.flows[flow_id]

    def list_flows(self, user_id: Optional[str] = None) -> List[Flow]:
        """
        List all flows, optionally filtered by user ID.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of flows
        """
        if user_id:
            return [flow for flow in self.flows.values() if flow.user_id == user_id]
        return list(self.flows.values())

    def activate_flow(self, flow_id: str) -> Flow:
        """
        Activate a flow.

        Args:
            flow_id: ID of the flow to activate

        Returns:
            The activated flow

        Raises:
            ValueError: If the flow doesn't exist
        """
        flow = self.get_flow(flow_id)
        flow.status = FlowStatus.ACTIVE
        self._save_flow(flow)
        return flow

    def deactivate_flow(self, flow_id: str) -> Flow:
        """
        Deactivate a flow.

        Args:
            flow_id: ID of the flow to deactivate

        Returns:
            The deactivated flow

        Raises:
            ValueError: If the flow doesn't exist
        """
        flow = self.get_flow(flow_id)
        flow.status = FlowStatus.INACTIVE
        self._save_flow(flow)
        return flow

    def execute_flow(
        self,
        flow_id: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> FlowExecutionResult:
        """
        Execute a flow.

        Args:
            flow_id: ID of the flow to execute
            parameters: Optional parameters to pass to the flow

        Returns:
            Result of the flow execution

        Raises:
            ValueError: If the flow doesn't exist
        """
        flow = self.get_flow(flow_id)

        if flow.status != FlowStatus.ACTIVE:
            return FlowExecutionResult(
                flow_id=flow_id,
                success=False,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_message=f"Flow is not active (status: {flow.status.value})"
            )

        result = FlowExecutionResult(
            flow_id=flow_id,
            success=True,
            start_time=datetime.now(),
            actions_executed=[]
        )

        try:
            # Execute actions
            current_action_idx = 0
            while current_action_idx is not None and current_action_idx < len(flow.actions):
                action = flow.actions[current_action_idx]
                result.actions_executed.append(current_action_idx)

                try:
                    # Get service and method
                    service = self.service_registry.get(action.service)
                    if not service:
                        raise ValueError(f"Service '{action.service}' not found")

                    method = getattr(service, action.method, None)
                    if not method or not callable(method):
                        raise ValueError(f"Method '{action.method}' not found in service '{action.service}'")

                    # Execute method with parameters
                    action_params = action.parameters.copy()
                    if parameters:
                        # Allow flow parameters to override action parameters
                        action_params.update(parameters)

                    action_result = method(**action_params)
                    result.action_results[current_action_idx] = action_result

                    # Determine next action
                    current_action_idx = action.next_on_success
                except Exception as e:
                    logger.error(f"Error executing action {current_action_idx} in flow {flow_id}: {e}")
                    result.action_results[current_action_idx] = str(e)

                    if action.next_on_failure is not None:
                        current_action_idx = action.next_on_failure
                    else:
                        # If no failure handler, stop execution
                        result.success = False
                        result.error_message = f"Action {current_action_idx} failed: {str(e)}"
                        break

            # Update flow's last run time
            flow.last_run = datetime.now()
            self._save_flow(flow)

        except Exception as e:
            logger.error(f"Error executing flow {flow_id}: {e}")
            result.success = False
            result.error_message = str(e)

        result.end_time = datetime.now()
        return result
