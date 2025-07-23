"""
Data models for the flow service.

This module defines the data structures used by the flow service to represent
workflows, actions, and triggers.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class TriggerType(str, Enum):
    """Types of triggers that can initiate a flow."""
    TIME = "time"      # Scheduled time-based trigger (cron)
    EVENT = "event"    # Event-based trigger
    COMMAND = "command"  # Manual command trigger


class FlowStatus(str, Enum):
    """Status of a flow."""
    ACTIVE = "active"      # Flow is active and can be triggered
    INACTIVE = "inactive"  # Flow is inactive and won't be triggered
    ERROR = "error"        # Flow has encountered an error


@dataclass
class FlowTrigger:
    """Represents a trigger that initiates a flow."""
    type: TriggerType
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the trigger to a dictionary."""
        return {
            "type": self.type.value,
            "parameters": self.parameters
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlowTrigger':
        """Create a trigger from a dictionary."""
        return cls(
            type=TriggerType(data["type"]),
            parameters=data.get("parameters", {})
        )


@dataclass
class FlowAction:
    """Represents an action to be executed as part of a flow."""
    service: str  # Service name (e.g., "email", "calendar")
    method: str   # Method name within the service
    parameters: Dict[str, Any] = field(default_factory=dict)
    next_on_success: Optional[int] = None  # Index of next action on success
    next_on_failure: Optional[int] = None  # Index of next action on failure

    def to_dict(self) -> Dict[str, Any]:
        """Convert the action to a dictionary."""
        return {
            "service": self.service,
            "method": self.method,
            "parameters": self.parameters,
            "next_on_success": self.next_on_success,
            "next_on_failure": self.next_on_failure
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FlowAction':
        """Create an action from a dictionary."""
        return cls(
            service=data["service"],
            method=data["method"],
            parameters=data.get("parameters", {}),
            next_on_success=data.get("next_on_success"),
            next_on_failure=data.get("next_on_failure")
        )


@dataclass
class Flow:
    """Represents a complete workflow with trigger and actions."""
    flow_id: str
    name: str
    trigger: FlowTrigger
    actions: List[FlowAction]
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    status: FlowStatus = FlowStatus.ACTIVE
    user_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the flow to a dictionary."""
        return {
            "flow_id": self.flow_id,
            "name": self.name,
            "trigger": self.trigger.to_dict(),
            "actions": [action.to_dict() for action in self.actions],
            "created_at": self.created_at.isoformat(),
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "status": self.status.value,
            "user_id": self.user_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Flow':
        """Create a flow from a dictionary."""
        return cls(
            flow_id=data["flow_id"],
            name=data["name"],
            trigger=FlowTrigger.from_dict(data["trigger"]),
            actions=[FlowAction.from_dict(action) for action in data["actions"]],
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            last_run=datetime.fromisoformat(data["last_run"]) if data.get("last_run") else None,
            status=FlowStatus(data.get("status", "active")),
            user_id=data.get("user_id")
        )


@dataclass
class FlowExecutionResult:
    """Result of a flow execution."""
    flow_id: str
    success: bool
    start_time: datetime
    end_time: Optional[datetime] = None
    actions_executed: List[int] = field(default_factory=list)
    error_message: Optional[str] = None
    action_results: Dict[int, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the execution result to a dictionary."""
        return {
            "flow_id": self.flow_id,
            "success": self.success,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "actions_executed": self.actions_executed,
            "error_message": self.error_message,
            "action_results": {str(k): v for k, v in self.action_results.items()}
        }
