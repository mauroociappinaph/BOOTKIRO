"""
Trigger management for the flow service.

This module provides functionality for registering, scheduling, and handling
triggers that initiate flows.
"""

import asyncio
import logging
import threading
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

import croniter

from personal_automation_bot.services.flows.models import Flow, FlowTrigger, TriggerType

logger = logging.getLogger(__name__)


class TriggerManager:
    """Manager for flow triggers."""

    def __init__(self, flow_engine):
        """
        Initialize the trigger manager.

        Args:
            flow_engine: The flow engine to use for executing flows
        """
        self.flow_engine = flow_engine
        self.event_handlers: Dict[str, Set[str]] = {}  # Event name -> set of flow IDs
        self.command_handlers: Dict[str, str] = {}  # Command name -> flow ID
        self.scheduled_flows: Dict[str, Tuple[str, datetime]] = {}  # Flow ID -> (cron expression, next run time)
        self.running = False
        self.scheduler_thread = None

    def register_flow(self, flow: Flow) -> None:
        """
        Register a flow's trigger.

        Args:
            flow: The flow to register
        """
        if flow.trigger.type == TriggerType.EVENT:
            event_name = flow.trigger.parameters.get("event_name")
            if event_name:
                if event_name not in self.event_handlers:
                    self.event_handlers[event_name] = set()
                self.event_handlers[event_name].add(flow.flow_id)

        elif flow.trigger.type == TriggerType.COMMAND:
            command_name = flow.trigger.parameters.get("command_name")
            if command_name:
                self.command_handlers[command_name] = flow.flow_id

        elif flow.trigger.type == TriggerType.TIME:
            cron_expression = flow.trigger.parameters.get("cron")
            if cron_expression:
                try:
                    cron = croniter.croniter(cron_expression, datetime.now())
                    next_run = cron.get_next(datetime)
                    self.scheduled_flows[flow.flow_id] = (cron_expression, next_run)
                except Exception as e:
                    logger.error(f"Invalid cron expression for flow {flow.flow_id}: {e}")

    def unregister_flow(self, flow_id: str) -> None:
        """
        Unregister a flow's trigger.

        Args:
            flow_id: ID of the flow to unregister
        """
        # Remove from event handlers
        for event_flows in self.event_handlers.values():
            if flow_id in event_flows:
                event_flows.remove(flow_id)

        # Remove from command handlers
        commands_to_remove = [
            cmd for cmd, fid in self.command_handlers.items() if fid == flow_id
        ]
        for cmd in commands_to_remove:
            del self.command_handlers[cmd]

        # Remove from scheduled flows
        if flow_id in self.scheduled_flows:
            del self.scheduled_flows[flow_id]

    def trigger_event(self, event_name: str, parameters: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Trigger flows associated with an event.

        Args:
            event_name: Name of the event
            parameters: Optional parameters to pass to the flows

        Returns:
            List of triggered flow IDs
        """
        triggered_flows = []
        if event_name in self.event_handlers:
            for flow_id in self.event_handlers[event_name]:
                try:
                    self.flow_engine.execute_flow(flow_id, parameters)
                    triggered_flows.append(flow_id)
                except Exception as e:
                    logger.error(f"Error triggering flow {flow_id} for event {event_name}: {e}")

        return triggered_flows

    def trigger_command(self, command_name: str, parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Trigger a flow associated with a command.

        Args:
            command_name: Name of the command
            parameters: Optional parameters to pass to the flow

        Returns:
            ID of the triggered flow, or None if no flow was triggered
        """
        if command_name in self.command_handlers:
            flow_id = self.command_handlers[command_name]
            try:
                self.flow_engine.execute_flow(flow_id, parameters)
                return flow_id
            except Exception as e:
                logger.error(f"Error triggering flow {flow_id} for command {command_name}: {e}")

        return None

    def _scheduler_loop(self) -> None:
        """Background loop for time-based triggers."""
        while self.running:
            now = datetime.now()
            flows_to_run = []

            # Find flows that need to be executed
            for flow_id, (cron_expr, next_run) in self.scheduled_flows.items():
                if now >= next_run:
                    flows_to_run.append(flow_id)

            # Execute flows and update next run times
            for flow_id in flows_to_run:
                try:
                    self.flow_engine.execute_flow(flow_id)

                    # Update next run time
                    cron_expr = self.scheduled_flows[flow_id][0]
                    cron = croniter.croniter(cron_expr, now)
                    next_run = cron.get_next(datetime)
                    self.scheduled_flows[flow_id] = (cron_expr, next_run)
                except Exception as e:
                    logger.error(f"Error executing scheduled flow {flow_id}: {e}")

            # Sleep for a short time before checking again
            time.sleep(10)  # Check every 10 seconds

    def start_scheduler(self) -> None:
        """Start the scheduler for time-based triggers."""
        if self.scheduler_thread is None or not self.scheduler_thread.is_alive():
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self.scheduler_thread.start()

    def stop_scheduler(self) -> None:
        """Stop the scheduler for time-based triggers."""
        self.running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=1.0)

    def reload_flows(self) -> None:
        """Reload all flows from the flow engine."""
        # Clear existing registrations
        self.event_handlers.clear()
        self.command_handlers.clear()
        self.scheduled_flows.clear()

        # Register all active flows
        for flow in self.flow_engine.list_flows():
            if flow.status == "active":
                self.register_flow(flow)
