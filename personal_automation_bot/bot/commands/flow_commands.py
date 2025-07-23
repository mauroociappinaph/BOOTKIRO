"""
Flow management commands for the Telegram bot.

This module provides commands for creating, editing, and managing flows
through the Telegram bot interface.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any, Callable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext, CommandHandler, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters
)

from personal_automation_bot.services.flows.models import (
    Flow, FlowAction, FlowStatus, FlowTrigger, TriggerType
)

logger = logging.getLogger(__name__)

# Conversation states
(
    FLOW_MENU,
    FLOW_LIST,
    FLOW_CREATE,
    FLOW_EDIT,
    FLOW_DELETE,
    FLOW_ACTIVATE,
    FLOW_DEACTIVATE,
    FLOW_EXECUTE,
    FLOW_DETAILS,
    FLOW_NAME,
    FLOW_TRIGGER_TYPE,
    FLOW_TRIGGER_PARAMS,
    FLOW_ACTION_SERVICE,
    FLOW_ACTION_METHOD,
    FLOW_ACTION_PARAMS,
    FLOW_ACTION_NEXT,
    FLOW_CONFIRM,
) = range(17)


class FlowCommands:
    """Flow management commands for the Telegram bot."""

    def __init__(self, flow_engine, service_registry):
        """
        Initialize flow commands.

        Args:
            flow_engine: The flow engine to use
            service_registry: Dictionary mapping service names to service instances
        """
        self.flow_engine = flow_engine
        self.service_registry = service_registry
        self.temp_flows: Dict[str, Dict[str, Any]] = {}  # User ID -> temporary flow data

    def get_handlers(self):
        """Get handlers for flow commands."""
        flow_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("flow", self.flow_command)],
            states={
                FLOW_MENU: [
                    CallbackQueryHandler(self.flow_list, pattern="^flow_list$"),
                    CallbackQueryHandler(self.flow_create_start, pattern="^flow_create$"),
                    CallbackQueryHandler(self.flow_execute_select, pattern="^flow_execute$"),
                    CallbackQueryHandler(self.flow_details_select, pattern="^flow_details$"),
                ],
                FLOW_LIST: [
                    CallbackQueryHandler(self.flow_activate, pattern="^flow_activate_"),
                    CallbackQueryHandler(self.flow_deactivate, pattern="^flow_deactivate_"),
                    CallbackQueryHandler(self.flow_edit_select, pattern="^flow_edit_"),
                    CallbackQueryHandler(self.flow_delete_confirm, pattern="^flow_delete_"),
                    CallbackQueryHandler(self.flow_menu, pattern="^back$"),
                ],
                FLOW_CREATE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.flow_name),
                    CallbackQueryHandler(self.flow_menu, pattern="^cancel$"),
                ],
                FLOW_NAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.flow_trigger_type),
                    CallbackQueryHandler(self.flow_menu, pattern="^cancel$"),
                ],
                FLOW_TRIGGER_TYPE: [
                    CallbackQueryHandler(self.flow_trigger_params, pattern="^trigger_"),
                    CallbackQueryHandler(self.flow_menu, pattern="^cancel$"),
                ],
                FLOW_TRIGGER_PARAMS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.flow_action_service),
                    CallbackQueryHandler(self.flow_menu, pattern="^cancel$"),
                ],
                FLOW_ACTION_SERVICE: [
                    CallbackQueryHandler(self.flow_action_method, pattern="^service_"),
                    CallbackQueryHandler(self.flow_confirm, pattern="^done$"),
                    CallbackQueryHandler(self.flow_menu, pattern="^cancel$"),
                ],
                FLOW_ACTION_METHOD: [
                    CallbackQueryHandler(self.flow_action_params, pattern="^method_"),
                    CallbackQueryHandler(self.flow_menu, pattern="^cancel$"),
                ],
                FLOW_ACTION_PARAMS: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.flow_action_next),
                    CallbackQueryHandler(self.flow_action_service, pattern="^skip$"),
                    CallbackQueryHandler(self.flow_menu, pattern="^cancel$"),
                ],
                FLOW_ACTION_NEXT: [
                    CallbackQueryHandler(self.flow_action_service, pattern="^next_"),
                    CallbackQueryHandler(self.flow_confirm, pattern="^done$"),
                    CallbackQueryHandler(self.flow_menu, pattern="^cancel$"),
                ],
                FLOW_CONFIRM: [
                    CallbackQueryHandler(self.flow_save, pattern="^confirm$"),
                    CallbackQueryHandler(self.flow_menu, pattern="^cancel$"),
                ],
                FLOW_EXECUTE: [
                    CallbackQueryHandler(self.flow_execute, pattern="^execute_"),
                    CallbackQueryHandler(self.flow_menu, pattern="^back$"),
                ],
                FLOW_DETAILS: [
                    CallbackQueryHandler(self.flow_edit_select, pattern="^flow_edit_"),
                    CallbackQueryHandler(self.flow_delete_confirm, pattern="^flow_delete_"),
                    CallbackQueryHandler(self.flow_list, pattern="^back$"),
                ],
                FLOW_DELETE: [
                    CallbackQueryHandler(self.flow_delete, pattern="^confirm$"),
                    CallbackQueryHandler(self.flow_list, pattern="^cancel$"),
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

        return [flow_conv_handler]

    async def flow_command(self, update: Update, context: CallbackContext) -> int:
        """Handle the /flow command."""
        keyboard = [
            [InlineKeyboardButton("📋 List Flows", callback_data="flow_list")],
            [InlineKeyboardButton("➕ Create Flow", callback_data="flow_create")],
            [InlineKeyboardButton("▶️ Execute Flow", callback_data="flow_execute")],
            [InlineKeyboardButton("ℹ️ Flow Details", callback_data="flow_details")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🔄 *Flow Management*\n\n"
            "What would you like to do with flows?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_MENU

    async def flow_menu(self, update: Update, context: CallbackContext) -> int:
        """Show the flow menu."""
        query = update.callback_query
        await query.answer()

        keyboard = [
            [InlineKeyboardButton("📋 List Flows", callback_data="flow_list")],
            [InlineKeyboardButton("➕ Create Flow", callback_data="flow_create")],
            [InlineKeyboardButton("▶️ Execute Flow", callback_data="flow_execute")],
            [InlineKeyboardButton("ℹ️ Flow Details", callback_data="flow_details")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "🔄 *Flow Management*\n\n"
            "What would you like to do with flows?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_MENU

    async def flow_list(self, update: Update, context: CallbackContext) -> int:
        """List all flows."""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)
        flows = self.flow_engine.list_flows(user_id)

        if not flows:
            keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "📋 *Flow List*\n\n"
                "You don't have any flows yet. Create one with the 'Create Flow' option.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

            return FLOW_LIST

        text = "📋 *Flow List*\n\n"
        keyboard = []

        for flow in flows:
            status_emoji = "✅" if flow.status == FlowStatus.ACTIVE else "❌"
            text += f"{status_emoji} *{flow.name}*\n"

            if flow.status == FlowStatus.ACTIVE:
                keyboard.append([
                    InlineKeyboardButton(
                        f"❌ Deactivate {flow.name}",
                        callback_data=f"flow_deactivate_{flow.flow_id}"
                    )
                ])
            else:
                keyboard.append([
                    InlineKeyboardButton(
                        f"✅ Activate {flow.name}",
                        callback_data=f"flow_activate_{flow.flow_id}"
                    )
                ])

            keyboard.append([
                InlineKeyboardButton(
                    f"✏️ Edit {flow.name}",
                    callback_data=f"flow_edit_{flow.flow_id}"
                ),
                InlineKeyboardButton(
                    f"🗑️ Delete {flow.name}",
                    callback_data=f"flow_delete_{flow.flow_id}"
                )
            ])

        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_LIST

    async def flow_create_start(self, update: Update, context: CallbackContext) -> int:
        """Start the flow creation process."""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)
        self.temp_flows[user_id] = {
            "actions": []
        }

        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "➕ *Create Flow*\n\n"
            "Please enter a name for your flow:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_CREATE

    async def flow_name(self, update: Update, context: CallbackContext) -> int:
        """Handle flow name input."""
        user_id = str(update.effective_user.id)
        name = update.message.text.strip()

        if not name:
            await update.message.reply_text(
                "❌ Flow name cannot be empty. Please enter a valid name:"
            )
            return FLOW_CREATE

        self.temp_flows[user_id]["name"] = name

        keyboard = [
            [InlineKeyboardButton("⏱️ Time (Cron)", callback_data="trigger_time")],
            [InlineKeyboardButton("📣 Event", callback_data="trigger_event")],
            [InlineKeyboardButton("🔤 Command", callback_data="trigger_command")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🔄 *Trigger Type*\n\n"
            "Select the type of trigger for your flow:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_TRIGGER_TYPE

    async def flow_trigger_type(self, update: Update, context: CallbackContext) -> int:
        """Handle trigger type selection."""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)
        trigger_type = query.data.split("_")[1]

        self.temp_flows[user_id]["trigger_type"] = trigger_type

        instructions = ""
        if trigger_type == "time":
            instructions = (
                "Enter a cron expression for when this flow should run.\n\n"
                "Format: minute hour day month weekday\n"
                "Example: '0 9 * * 1-5' (every weekday at 9:00 AM)"
            )
        elif trigger_type == "event":
            instructions = (
                "Enter the name of the event that should trigger this flow.\n\n"
                "Example: 'new_email' or 'document_updated'"
            )
        elif trigger_type == "command":
            instructions = (
                "Enter the command name that should trigger this flow.\n\n"
                "Example: 'daily_summary' or 'backup_documents'"
            )

        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🔄 *Trigger Parameters*\n\n{instructions}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_TRIGGER_PARAMS

    async def flow_trigger_params(self, update: Update, context: CallbackContext) -> int:
        """Handle trigger parameters input."""
        user_id = str(update.effective_user.id)
        params = update.message.text.strip()

        if not params:
            await update.message.reply_text(
                "❌ Trigger parameters cannot be empty. Please enter valid parameters:"
            )
            return FLOW_TRIGGER_PARAMS

        trigger_type = self.temp_flows[user_id]["trigger_type"]

        if trigger_type == "time":
            self.temp_flows[user_id]["trigger_params"] = {"cron": params}
        elif trigger_type == "event":
            self.temp_flows[user_id]["trigger_params"] = {"event_name": params}
        elif trigger_type == "command":
            self.temp_flows[user_id]["trigger_params"] = {"command_name": params}

        # Now let's add actions
        keyboard = []
        for service_name in self.service_registry.keys():
            keyboard.append([
                InlineKeyboardButton(
                    f"{service_name.capitalize()}",
                    callback_data=f"service_{service_name}"
                )
            ])

        if self.temp_flows[user_id].get("actions"):
            keyboard.append([InlineKeyboardButton("✅ Done", callback_data="done")])

        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🔄 *Add Action*\n\n"
            "Select a service for your action:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_ACTION_SERVICE

    async def flow_action_service(self, update: Update, context: CallbackContext) -> int:
        """Handle action service selection."""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)

        if query.data == "done":
            if not self.temp_flows[user_id].get("actions"):
                await query.edit_message_text(
                    "❌ You must add at least one action to your flow."
                )
                return FLOW_ACTION_SERVICE

            return await self.flow_confirm(update, context)

        service_name = query.data.split("_")[1]
        self.temp_flows[user_id]["current_action"] = {"service": service_name}

        service = self.service_registry.get(service_name)
        if not service:
            await query.edit_message_text(
                f"❌ Service '{service_name}' not found."
            )
            return FLOW_ACTION_SERVICE

        # Get methods from service
        methods = [
            name for name, func in service.__class__.__dict__.items()
            if callable(func) and not name.startswith("_")
        ]

        keyboard = []
        for method in methods:
            keyboard.append([
                InlineKeyboardButton(
                    f"{method}",
                    callback_data=f"method_{method}"
                )
            ])

        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"🔄 *Select Method*\n\n"
            f"Select a method from the {service_name} service:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_ACTION_METHOD

    async def flow_action_method(self, update: Update, context: CallbackContext) -> int:
        """Handle action method selection."""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)
        method_name = query.data.split("_")[1]

        self.temp_flows[user_id]["current_action"]["method"] = method_name

        keyboard = [
            [InlineKeyboardButton("⏭️ Skip Parameters", callback_data="skip")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "🔄 *Action Parameters*\n\n"
            "Enter the parameters for this action as a JSON object:\n"
            "Example: {\"param1\": \"value1\", \"param2\": 42}\n\n"
            "Or click 'Skip Parameters' if no parameters are needed.",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_ACTION_PARAMS

    async def flow_action_params(self, update: Update, context: CallbackContext) -> int:
        """Handle action parameters input."""
        user_id = str(update.effective_user.id)
        params_text = update.message.text.strip()

        try:
            params = json.loads(params_text) if params_text else {}
            self.temp_flows[user_id]["current_action"]["parameters"] = params
        except json.JSONDecodeError:
            await update.message.reply_text(
                "❌ Invalid JSON format. Please enter a valid JSON object or skip parameters."
            )
            return FLOW_ACTION_PARAMS

        keyboard = [
            [InlineKeyboardButton("➡️ Add Another Action", callback_data="next_action")],
            [InlineKeyboardButton("✅ Done", callback_data="done")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Add the current action to the list
        current_action = self.temp_flows[user_id]["current_action"]
        self.temp_flows[user_id].setdefault("actions", []).append(current_action)

        await update.message.reply_text(
            "🔄 *Action Added*\n\n"
            f"Service: {current_action['service']}\n"
            f"Method: {current_action['method']}\n"
            f"Parameters: {json.dumps(current_action.get('parameters', {}), indent=2)}\n\n"
            "What would you like to do next?",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_ACTION_NEXT

    async def flow_action_next(self, update: Update, context: CallbackContext) -> int:
        """Handle next action selection."""
        query = update.callback_query
        await query.answer()

        if query.data == "done":
            return await self.flow_confirm(update, context)

        # Reset current action
        user_id = str(update.effective_user.id)
        self.temp_flows[user_id].pop("current_action", None)

        # Show service selection again
        keyboard = []
        for service_name in self.service_registry.keys():
            keyboard.append([
                InlineKeyboardButton(
                    f"{service_name.capitalize()}",
                    callback_data=f"service_{service_name}"
                )
            ])

        keyboard.append([InlineKeyboardButton("✅ Done", callback_data="done")])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "🔄 *Add Another Action*\n\n"
            "Select a service for your next action:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_ACTION_SERVICE

    async def flow_confirm(self, update: Update, context: CallbackContext) -> int:
        """Confirm flow creation."""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)
        flow_data = self.temp_flows[user_id]

        # Build summary
        text = "🔄 *Flow Summary*\n\n"
        text += f"Name: {flow_data['name']}\n\n"

        text += "Trigger:\n"
        text += f"Type: {flow_data['trigger_type'].capitalize()}\n"
        text += f"Parameters: {json.dumps(flow_data['trigger_params'], indent=2)}\n\n"

        text += "Actions:\n"
        for i, action in enumerate(flow_data['actions'], 1):
            text += f"{i}. Service: {action['service']}\n"
            text += f"   Method: {action['method']}\n"
            text += f"   Parameters: {json.dumps(action.get('parameters', {}), indent=2)}\n\n"

        text += "Is this correct?"

        keyboard = [
            [InlineKeyboardButton("✅ Confirm", callback_data="confirm")],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_CONFIRM

    async def flow_save(self, update: Update, context: CallbackContext) -> int:
        """Save the flow."""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)
        flow_data = self.temp_flows[user_id]

        try:
            # Create trigger
            trigger = FlowTrigger(
                type=TriggerType(flow_data["trigger_type"]),
                parameters=flow_data["trigger_params"]
            )

            # Create actions
            actions = []
            for i, action_data in enumerate(flow_data["actions"]):
                next_idx = i + 1 if i < len(flow_data["actions"]) - 1 else None
                action = FlowAction(
                    service=action_data["service"],
                    method=action_data["method"],
                    parameters=action_data.get("parameters", {}),
                    next_on_success=next_idx,
                    next_on_failure=None
                )
                actions.append(action)

            # Create flow
            flow = self.flow_engine.create_flow(
                name=flow_data["name"],
                trigger=trigger,
                actions=actions,
                user_id=user_id
            )

            # Clean up
            del self.temp_flows[user_id]

            await query.edit_message_text(
                "✅ *Flow Created*\n\n"
                f"Your flow '{flow_data['name']}' has been created successfully!",
                parse_mode="Markdown"
            )

            # Return to flow menu
            return await self.flow_command(update, context)

        except Exception as e:
            logger.error(f"Error creating flow: {e}")

            await query.edit_message_text(
                "❌ *Error*\n\n"
                f"An error occurred while creating your flow: {str(e)}",
                parse_mode="Markdown"
            )

            return ConversationHandler.END

    async def flow_execute_select(self, update: Update, context: CallbackContext) -> int:
        """Select a flow to execute."""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)
        flows = self.flow_engine.list_flows(user_id)

        if not flows:
            keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "▶️ *Execute Flow*\n\n"
                "You don't have any flows yet. Create one with the 'Create Flow' option.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

            return FLOW_EXECUTE

        text = "▶️ *Execute Flow*\n\n"
        text += "Select a flow to execute:"

        keyboard = []
        for flow in flows:
            if flow.status == FlowStatus.ACTIVE:
                keyboard.append([
                    InlineKeyboardButton(
                        f"▶️ {flow.name}",
                        callback_data=f"execute_{flow.flow_id}"
                    )
                ])

        if not keyboard:
            text += "\n\nYou don't have any active flows. Activate a flow first."

        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_EXECUTE

    async def flow_execute(self, update: Update, context: CallbackContext) -> int:
        """Execute a flow."""
        query = update.callback_query
        await query.answer()

        flow_id = query.data.split("_")[1]

        try:
            flow = self.flow_engine.get_flow(flow_id)
            result = self.flow_engine.execute_flow(flow_id)

            if result.success:
                await query.edit_message_text(
                    "✅ *Flow Executed*\n\n"
                    f"Flow '{flow.name}' executed successfully!\n\n"
                    f"Actions executed: {len(result.actions_executed)}\n"
                    f"Execution time: {(result.end_time - result.start_time).total_seconds():.2f} seconds",
                    parse_mode="Markdown"
                )
            else:
                await query.edit_message_text(
                    "❌ *Execution Error*\n\n"
                    f"An error occurred while executing flow '{flow.name}':\n"
                    f"{result.error_message}",
                    parse_mode="Markdown"
                )

            # Return to flow menu
            return await self.flow_command(update, context)

        except Exception as e:
            logger.error(f"Error executing flow: {e}")

            await query.edit_message_text(
                "❌ *Error*\n\n"
                f"An error occurred while executing the flow: {str(e)}",
                parse_mode="Markdown"
            )

            return ConversationHandler.END

    async def flow_details_select(self, update: Update, context: CallbackContext) -> int:
        """Select a flow to view details."""
        query = update.callback_query
        await query.answer()

        user_id = str(update.effective_user.id)
        flows = self.flow_engine.list_flows(user_id)

        if not flows:
            keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "ℹ️ *Flow Details*\n\n"
                "You don't have any flows yet. Create one with the 'Create Flow' option.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

            return FLOW_DETAILS

        text = "ℹ️ *Flow Details*\n\n"
        text += "Select a flow to view details:"

        keyboard = []
        for flow in flows:
            keyboard.append([
                InlineKeyboardButton(
                    f"ℹ️ {flow.name}",
                    callback_data=f"flow_details_{flow.flow_id}"
                )
            ])

        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

        return FLOW_DETAILS

    async def flow_details(self, update: Update, context: CallbackContext) -> int:
        """Show flow details."""
        query = update.callback_query
        await query.answer()

        flow_id = query.data.split("_")[2]

        try:
            flow = self.flow_engine.get_flow(flow_id)

            text = f"ℹ️ *Flow Details: {flow.name}*\n\n"
            text += f"Status: {'Active' if flow.status == FlowStatus.ACTIVE else 'Inactive'}\n"
            text += f"Created: {flow.created_at.strftime('%Y-%m-%d %H:%M')}\n"

            if flow.last_run:
                text += f"Last Run: {flow.last_run.strftime('%Y-%m-%d %H:%M')}\n"

            text += "\nTrigger:\n"
            text += f"Type: {flow.trigger.type.value.capitalize()}\n"
            text += f"Parameters: {json.dumps(flow.trigger.parameters, indent=2)}\n\n"

            text += "Actions:\n"
            for i, action in enumerate(flow.actions, 1):
                text += f"{i}. Service: {action.service}\n"
                text += f"   Method: {action.method}\n"
                text += f"   Parameters: {json.dumps(action.parameters, indent=2)}\n"
                if action.next_on_success is not None:
                    text += f"   Next on success: Action {action.next_on_success + 1}\n"
                if action.next_on_failure is not None:
                    text += f"   Next on failure: Action {action.next_on_failure + 1}\n"
                text += "\n"

            keyboard = [
                [
                    InlineKeyboardButton(
                        "✏️ Edit",
                        callback_data=f"flow_edit_{flow_id}"
                    ),
                    InlineKeyboardButton(
                        "🗑️ Delete",
                        callback_data=f"flow_delete_{flow_id}"
                    )
                ],
                [InlineKeyboardButton("⬅️ Back", callback_data="back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

            return FLOW_DETAILS

        except Exception as e:
            logger.error(f"Error getting flow details: {e}")

            await query.edit_message_text(
                "❌ *Error*\n\n"
                f"An error occurred while getting flow details: {str(e)}",
                parse_mode="Markdown"
            )

            return ConversationHandler.END

    async def flow_edit_select(self, update: Update, context: CallbackContext) -> int:
        """Select a flow to edit."""
        query = update.callback_query
        await query.answer()

        # For now, just return to flow list
        # Editing flows is more complex and would require a separate implementation
        await query.edit_message_text(
            "✏️ *Edit Flow*\n\n"
            "Flow editing is not implemented yet.",
            parse_mode="Markdown"
        )

        return await self.flow_list(update, context)

    async def flow_delete_confirm(self, update: Update, context: CallbackContext) -> int:
        """Confirm flow deletion."""
        query = update.callback_query
        await query.answer()

        flow_id = query.data.split("_")[2]

        try:
            flow = self.flow_engine.get_flow(flow_id)

            keyboard = [
                [InlineKeyboardButton("✅ Confirm", callback_data="confirm")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Store flow ID in context
            context.user_data["delete_flow_id"] = flow_id

            await query.edit_message_text(
                "🗑️ *Delete Flow*\n\n"
                f"Are you sure you want to delete the flow '{flow.name}'?\n\n"
                "This action cannot be undone.",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )

            return FLOW_DELETE

        except Exception as e:
            logger.error(f"Error preparing flow deletion: {e}")

            await query.edit_message_text(
                "❌ *Error*\n\n"
                f"An error occurred while preparing flow deletion: {str(e)}",
                parse_mode="Markdown"
            )

            return ConversationHandler.END

    async def flow_delete(self, update: Update, context: CallbackContext) -> int:
        """Delete a flow."""
        query = update.callback_query
        await query.answer()

        flow_id = context.user_data.get("delete_flow_id")
        if not flow_id:
            await query.edit_message_text(
                "❌ *Error*\n\n"
                "Flow ID not found in context.",
                parse_mode="Markdown"
            )
            return ConversationHandler.END

        try:
            flow = self.flow_engine.get_flow(flow_id)
            flow_name = flow.name

            self.flow_engine.delete_flow(flow_id)

            await query.edit_message_text(
                "✅ *Flow Deleted*\n\n"
                f"Flow '{flow_name}' has been deleted successfully.",
                parse_mode="Markdown"
            )

            # Return to flow list
            return await self.flow_list(update, context)

        except Exception as e:
            logger.error(f"Error deleting flow: {e}")

            await query.edit_message_text(
                "❌ *Error*\n\n"
                f"An error occurred while deleting the flow: {str(e)}",
                parse_mode="Markdown"
            )

            return ConversationHandler.END

    async def flow_activate(self, update: Update, context: CallbackContext) -> int:
        """Activate a flow."""
        query = update.callback_query
        await query.answer()

        flow_id = query.data.split("_")[2]

        try:
            flow = self.flow_engine.activate_flow(flow_id)

            await query.edit_message_text(
                "✅ *Flow Activated*\n\n"
                f"Flow '{flow.name}' has been activated successfully.",
                parse_mode="Markdown"
            )

            # Return to flow list
            return await self.flow_list(update, context)

        except Exception as e:
            logger.error(f"Error activating flow: {e}")

            await query.edit_message_text(
                "❌ *Error*\n\n"
                f"An error occurred while activating the flow: {str(e)}",
                parse_mode="Markdown"
            )

            return ConversationHandler.END

    async def flow_deactivate(self, update: Update, context: CallbackContext) -> int:
        """Deactivate a flow."""
        query = update.callback_query
        await query.answer()

        flow_id = query.data.split("_")[2]

        try:
            flow = self.flow_engine.deactivate_flow(flow_id)

            await query.edit_message_text(
                "✅ *Flow Deactivated*\n\n"
                f"Flow '{flow.name}' has been deactivated successfully.",
                parse_mode="Markdown"
            )

            # Return to flow list
            return await self.flow_list(update, context)

        except Exception as e:
            logger.error(f"Error deactivating flow: {e}")

            await query.edit_message_text(
                "❌ *Error*\n\n"
                f"An error occurred while deactivating the flow: {str(e)}",
                parse_mode="Markdown"
            )

            return ConversationHandler.END

    async def cancel(self, update: Update, context: CallbackContext) -> int:
        """Cancel the conversation."""
        user_id = str(update.effective_user.id)
        if user_id in self.temp_flows:
            del self.temp_flows[user_id]

        await update.message.reply_text(
            "❌ Operation cancelled."
        )

        return ConversationHandler.END
