"""
Calendar conversation handler configuration.
"""
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from personal_automation_bot.bot.commands.calendar import (
    calendar_commands,
    CALENDAR_MAIN_MENU,
    VIEW_EVENTS,
    CREATE_EVENT_TITLE,
    CREATE_EVENT_DATE,
    CREATE_EVENT_TIME,
    CREATE_EVENT_DESCRIPTION,
    DELETE_EVENT_SELECT,
    DELETE_EVENT_CONFIRM,
    UPDATE_EVENT_SELECT,
    UPDATE_EVENT_FIELD,
    UPDATE_EVENT_VALUE
)


def get_calendar_conversation_handler() -> ConversationHandler:
    """
    Create and return the calendar conversation handler.

    Returns:
        ConversationHandler: Configured conversation handler for calendar operations
    """
    return ConversationHandler(
        entry_points=[
            CommandHandler('calendar', calendar_commands.calendar_command),
            CommandHandler('calendario', calendar_commands.calendar_command),  # Spanish alias
        ],
        states={
            CALENDAR_MAIN_MENU: [
                CallbackQueryHandler(
                    calendar_commands.view_events_callback,
                    pattern=r'^cal_view_(upcoming|today|week)$'
                ),
                CallbackQueryHandler(
                    calendar_commands.create_event_callback,
                    pattern=r'^cal_create$'
                ),
                CallbackQueryHandler(
                    calendar_commands.update_event_callback,
                    pattern=r'^cal_update$'
                ),
                CallbackQueryHandler(
                    calendar_commands.delete_event_callback,
                    pattern=r'^cal_delete$'
                ),
                CallbackQueryHandler(
                    calendar_commands.search_events_callback,
                    pattern=r'^cal_search$'
                ),
                CallbackQueryHandler(
                    calendar_commands.back_to_menu_callback,
                    pattern=r'^cal_back_to_menu$'
                ),
                CallbackQueryHandler(
                    calendar_commands.cancel_callback,
                    pattern=r'^cancel$'
                ),
            ],
            VIEW_EVENTS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    calendar_commands.handle_search_query
                ),
                CallbackQueryHandler(
                    calendar_commands.back_to_menu_callback,
                    pattern=r'^cal_back_to_menu$'
                ),
            ],
            CREATE_EVENT_TITLE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    calendar_commands.handle_event_title
                ),
                CallbackQueryHandler(
                    calendar_commands.cancel_callback,
                    pattern=r'^cancel$'
                ),
            ],
            CREATE_EVENT_DATE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    calendar_commands.handle_event_date
                ),
                CallbackQueryHandler(
                    calendar_commands.cancel_callback,
                    pattern=r'^cancel$'
                ),
            ],
            CREATE_EVENT_TIME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    calendar_commands.handle_event_time
                ),
                CallbackQueryHandler(
                    calendar_commands.cancel_callback,
                    pattern=r'^cancel$'
                ),
            ],
            CREATE_EVENT_DESCRIPTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    calendar_commands.handle_event_description
                ),
                CallbackQueryHandler(
                    calendar_commands.cancel_callback,
                    pattern=r'^cancel$'
                ),
            ],
            UPDATE_EVENT_SELECT: [
                CallbackQueryHandler(
                    calendar_commands.handle_update_event_select,
                    pattern=r'^upd_event_\d+$'
                ),
                CallbackQueryHandler(
                    calendar_commands.back_to_menu_callback,
                    pattern=r'^cal_back_to_menu$'
                ),
            ],
            UPDATE_EVENT_FIELD: [
                CallbackQueryHandler(
                    calendar_commands.handle_update_field_select,
                    pattern=r'^update_(title|date|time|description|location)$'
                ),
                CallbackQueryHandler(
                    calendar_commands.back_to_menu_callback,
                    pattern=r'^cal_back_to_menu$'
                ),
            ],
            UPDATE_EVENT_VALUE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    calendar_commands.handle_update_value_input
                ),
                CallbackQueryHandler(
                    calendar_commands.cancel_callback,
                    pattern=r'^cancel$'
                ),
            ],
            DELETE_EVENT_SELECT: [
                CallbackQueryHandler(
                    calendar_commands.handle_delete_event_select,
                    pattern=r'^del_event_\d+$'
                ),
                CallbackQueryHandler(
                    calendar_commands.back_to_menu_callback,
                    pattern=r'^cal_back_to_menu$'
                ),
            ],
            DELETE_EVENT_CONFIRM: [
                CallbackQueryHandler(
                    calendar_commands.handle_delete_confirmation,
                    pattern=r'^(confirm_delete|cancel_delete)$'
                ),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', calendar_commands.cancel_command),
            CommandHandler('cancelar', calendar_commands.cancel_command),  # Spanish alias
        ],
        name="calendar_conversation",
        persistent=False
    )
