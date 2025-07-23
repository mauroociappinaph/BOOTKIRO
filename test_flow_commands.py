"""
Test the flow commands implementation.

This script tests the basic functionality of the flow commands, including
creating, executing, and managing flows through the Telegram bot interface.
"""

import asyncio
import os
import shutil
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

from telegram import InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from personal_automation_bot.bot.commands.flow_commands import FlowCommands
from personal_automation_bot.services.flows.engine import FlowEngine
from personal_automation_bot.services.flows.models import Flow, FlowStatus


class MockService:
    """Mock service for testing."""

    def __init__(self):
        self.actions = []

    def perform_action(self, action_type, data=None):
        """Mock performing an action."""
        self.actions.append({"type": action_type, "data": data})
        return {"status": "success", "id": f"action_{len(self.actions)}"}


async def test_flow_command():
    """Test the flow command."""
    # Create temporary directory for flow storage
    temp_dir = tempfile.mkdtemp()

    try:
        # Create service registry
        mock_service = MockService()
        service_registry = {"mock": mock_service}

        # Create flow engine
        engine = FlowEngine(temp_dir, service_registry)

        # Create flow commands
        flow_commands = FlowCommands(engine, service_registry)

        # Mock update and context
        update = MagicMock(spec=Update)
        context = MagicMock(spec=CallbackContext)

        # Mock message
        message = AsyncMock()
        update.message = message
        update.effective_user.id = 123456

        # Test flow command
        await flow_commands.flow_command(update, context)

        # Verify message was sent
        message.reply_text.assert_called_once()
        args, kwargs = message.reply_text.call_args
        assert "Flow Management" in kwargs.get("text", "")
        assert isinstance(kwargs.get("reply_markup"), InlineKeyboardMarkup)

        print("Flow command test passed!")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


async def test_flow_list():
    """Test the flow list command."""
    # Create temporary directory for flow storage
    temp_dir = tempfile.mkdtemp()

    try:
        # Create service registry
        mock_service = MockService()
        service_registry = {"mock": mock_service}

        # Create flow engine
        engine = FlowEngine(temp_dir, service_registry)

        # Create flow commands
        flow_commands = FlowCommands(engine, service_registry)

        # Mock update and context
        update = MagicMock(spec=Update)
        context = MagicMock(spec=CallbackContext)

        # Mock callback query
        query = AsyncMock()
        update.callback_query = query
        update.effective_user.id = 123456

        # Test flow list with no flows
        await flow_commands.flow_list(update, context)

        # Verify message was sent
        query.edit_message_text.assert_called_once()
        args, kwargs = query.edit_message_text.call_args
        assert "Flow List" in kwargs.get("text", "")
        assert "don't have any flows" in kwargs.get("text", "")

        print("Flow list test passed!")

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


async def main():
    """Run all tests."""
    await test_flow_command()
    await test_flow_list()
    print("All tests passed!")


if __name__ == "__main__":
    asyncio.run(main())
