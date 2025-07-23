"""
Calendar command handlers for the Telegram bot.
"""
import logging
from datetime import datetime, timedelta
from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from personal_automation_bot.services.calendar import CalendarService, CalendarEvent
from personal_automation_bot.utils.auth import google_auth_manager

logger = logging.getLogger(__name__)

# Conversation states
CALENDAR_MAIN_MENU = 0
VIEW_EVENTS = 1
CREATE_EVENT_TITLE = 2
CREATE_EVENT_DATE = 3
CREATE_EVENT_TIME = 4
CREATE_EVENT_DESCRIPTION = 5
DELETE_EVENT_SELECT = 6
DELETE_EVENT_CONFIRM = 7
UPDATE_EVENT_SELECT = 8
UPDATE_EVENT_FIELD = 9
UPDATE_EVENT_VALUE = 10

class CalendarCommands:
    """Calendar command handlers."""

    def __init__(self):
        self.calendar_service = CalendarService()

    async def calendar_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /calendar command - show calendar main menu."""
        user_id = update.effective_user.id

        # Check if user is authenticated
        if not google_auth_manager.is_user_authenticated(user_id):
            await update.message.reply_text(
                "❌ No estás autenticado con Google.\n"
                "Usa /auth para autenticarte primero."
            )
            return ConversationHandler.END

        keyboard = [
            [InlineKeyboardButton("📅 Ver eventos próximos", callback_data="cal_view_upcoming")],
            [InlineKeyboardButton("📅 Ver eventos de hoy", callback_data="cal_view_today")],
            [InlineKeyboardButton("📅 Ver eventos de esta semana", callback_data="cal_view_week")],
            [InlineKeyboardButton("➕ Crear evento", callback_data="cal_create")],
            [InlineKeyboardButton("✏️ Actualizar evento", callback_data="cal_update")],
            [InlineKeyboardButton("🗑️ Eliminar evento", callback_data="cal_delete")],
            [InlineKeyboardButton("🔍 Buscar eventos", callback_data="cal_search")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="cancel")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "📅 **Gestión de Calendario**\n\n"
            "¿Qué te gustaría hacer?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

        return CALENDAR_MAIN_MENU

    async def view_events_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle event viewing callbacks."""
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id
        data = query.data

        try:
            events = []

            if data == "cal_view_upcoming":
                # Next 7 days
                start_date = datetime.now()
                end_date = start_date + timedelta(days=7)
                events = self.calendar_service.get_events(user_id, start_date, end_date, max_results=10)
                title = "📅 **Eventos próximos (7 días)**"

            elif data == "cal_view_today":
                # Today only
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
                events = self.calendar_service.get_events(user_id, start_date, end_date)
                title = "📅 **Eventos de hoy**"

            elif data == "cal_view_week":
                # This week
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                # Get start of week (Monday)
                days_since_monday = start_date.weekday()
                start_date = start_date - timedelta(days=days_since_monday)
                end_date = start_date + timedelta(days=7)
                events = self.calendar_service.get_events(user_id, start_date, end_date, max_results=15)
                title = "📅 **Eventos de esta semana**"

            if not events:
                message = f"{title}\n\n📭 No hay eventos en este período."
            else:
                message_parts = [title, ""]

                for i, event in enumerate(events, 1):
                    message_parts.append(f"{i}. {event.format_for_display()}")
                    message_parts.append("")  # Empty line between events

                message = "\n".join(message_parts)

                # Truncate if too long
                if len(message) > 4000:
                    message = message[:3900] + "\n\n... (lista truncada)"

            # Add back button
            keyboard = [[InlineKeyboardButton("🔙 Volver al menú", callback_data="cal_back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error viewing events for user {user_id}: {e}")
            await query.edit_message_text(
                f"❌ Error al obtener eventos: {str(e)}\n\n"
                "Intenta de nuevo más tarde.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Volver", callback_data="cal_back_to_menu")
                ]])
            )

        return CALENDAR_MAIN_MENU

    async def search_events_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle search events callback."""
        query = update.callback_query
        await query.answer()

        await query.edit_message_text(
            "🔍 **Buscar eventos**\n\n"
            "Escribe el término de búsqueda (título, descripción, etc.):",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Cancelar", callback_data="cal_back_to_menu")
            ]])
        )

        return VIEW_EVENTS

    async def handle_search_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle search query input."""
        user_id = update.effective_user.id
        search_query = update.message.text.strip()

        if not search_query:
            await update.message.reply_text(
                "❌ Por favor, proporciona un término de búsqueda válido."
            )
            return VIEW_EVENTS

        try:
            events = self.calendar_service.search_events(user_id, search_query, max_results=10)

            if not events:
                message = f"🔍 **Resultados de búsqueda: '{search_query}'**\n\n📭 No se encontraron eventos."
            else:
                message_parts = [f"🔍 **Resultados de búsqueda: '{search_query}'**", ""]

                for i, event in enumerate(events, 1):
                    message_parts.append(f"{i}. {event.format_for_display()}")
                    message_parts.append("")  # Empty line between events

                message = "\n".join(message_parts)

                # Truncate if too long
                if len(message) > 4000:
                    message = message[:3900] + "\n\n... (lista truncada)"

            # Add back button
            keyboard = [[InlineKeyboardButton("🔙 Volver al menú", callback_data="cal_back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

        except Exception as e:
            logger.error(f"Error searching events for user {user_id}: {e}")
            await update.message.reply_text(
                f"❌ Error al buscar eventos: {str(e)}\n\n"
                "Intenta de nuevo más tarde."
            )

        return ConversationHandler.END

    async def back_to_menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle back to menu callback."""
        query = update.callback_query
        await query.answer()

        keyboard = [
            [InlineKeyboardButton("📅 Ver eventos próximos", callback_data="cal_view_upcoming")],
            [InlineKeyboardButton("📅 Ver eventos de hoy", callback_data="cal_view_today")],
            [InlineKeyboardButton("📅 Ver eventos de esta semana", callback_data="cal_view_week")],
            [InlineKeyboardButton("➕ Crear evento", callback_data="cal_create")],
            [InlineKeyboardButton("✏️ Actualizar evento", callback_data="cal_update")],
            [InlineKeyboardButton("🗑️ Eliminar evento", callback_data="cal_delete")],
            [InlineKeyboardButton("🔍 Buscar eventos", callback_data="cal_search")],
            [InlineKeyboardButton("❌ Cancelar", callback_data="cancel")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            "📅 **Gestión de Calendario**\n\n"
            "¿Qué te gustaría hacer?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

        return CALENDAR_MAIN_MENU

    async def cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle cancel callback."""
        query = update.callback_query
        await query.answer()

        await query.edit_message_text("❌ Operación cancelada.")
        return ConversationHandler.END

    async def create_event_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle create event callback."""
        query = update.callback_query
        await query.answer()

        # Initialize event data in context
        context.user_data['new_event'] = {}

        await query.edit_message_text(
            "➕ **Crear nuevo evento**\n\n"
            "📝 Escribe el título del evento:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel")
            ]])
        )

        return CREATE_EVENT_TITLE

    async def handle_event_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle event title input."""
        title = update.message.text.strip()

        if not title:
            await update.message.reply_text(
                "❌ El título no puede estar vacío. Intenta de nuevo:"
            )
            return CREATE_EVENT_TITLE

        context.user_data['new_event']['title'] = title

        await update.message.reply_text(
            f"✅ Título: {title}\n\n"
            "📅 Ahora escribe la fecha del evento.\n\n"
            "Formatos aceptados:\n"
            "• `hoy` - para hoy\n"
            "• `mañana` - para mañana\n"
            "• `DD/MM/YYYY` - fecha específica (ej: 25/12/2024)\n"
            "• `DD/MM` - este año (ej: 25/12)",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel")
            ]])
        )

        return CREATE_EVENT_DATE

    async def handle_event_date(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle event date input."""
        date_text = update.message.text.strip().lower()

        try:
            # Parse date
            event_date = self._parse_date(date_text)
            context.user_data['new_event']['date'] = event_date

            await update.message.reply_text(
                f"✅ Fecha: {event_date.strftime('%d/%m/%Y')}\n\n"
                "🕐 Ahora escribe la hora del evento.\n\n"
                "Formatos aceptados:\n"
                "• `todo el día` - evento de todo el día\n"
                "• `HH:MM` - hora específica (ej: 14:30)\n"
                "• `HH:MM-HH:MM` - hora de inicio y fin (ej: 14:30-16:00)",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ Cancelar", callback_data="cancel")
                ]])
            )

            return CREATE_EVENT_TIME

        except ValueError as e:
            await update.message.reply_text(
                f"❌ Fecha inválida: {str(e)}\n\n"
                "Intenta de nuevo con uno de los formatos aceptados."
            )
            return CREATE_EVENT_DATE

    async def handle_event_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle event time input."""
        time_text = update.message.text.strip().lower()
        event_date = context.user_data['new_event']['date']

        try:
            if time_text == "todo el día":
                # All-day event
                start_time = event_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_time = start_time + timedelta(days=1)
                context.user_data['new_event']['all_day'] = True
            else:
                # Parse time
                start_time, end_time = self._parse_time(time_text, event_date)
                context.user_data['new_event']['all_day'] = False

            context.user_data['new_event']['start_time'] = start_time
            context.user_data['new_event']['end_time'] = end_time

            time_display = "Todo el día" if context.user_data['new_event']['all_day'] else f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"

            await update.message.reply_text(
                f"✅ Hora: {time_display}\n\n"
                "📝 Escribe una descripción para el evento (opcional).\n\n"
                "Puedes escribir `/skip` para omitir la descripción.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("❌ Cancelar", callback_data="cancel")
                ]])
            )

            return CREATE_EVENT_DESCRIPTION

        except ValueError as e:
            await update.message.reply_text(
                f"❌ Hora inválida: {str(e)}\n\n"
                "Intenta de nuevo con uno de los formatos aceptados."
            )
            return CREATE_EVENT_TIME

    async def handle_event_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle event description input."""
        description_text = update.message.text.strip()

        if description_text.lower() == '/skip':
            description = None
        else:
            description = description_text if description_text else None

        context.user_data['new_event']['description'] = description

        # Create the event
        await self._create_event_final(update, context)

        return ConversationHandler.END

    async def _create_event_final(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create the final event."""
        user_id = update.effective_user.id
        event_data = context.user_data['new_event']

        try:
            # Create CalendarEvent object
            event = CalendarEvent(
                title=event_data['title'],
                description=event_data.get('description'),
                start_time=event_data['start_time'],
                end_time=event_data['end_time'],
                all_day=event_data.get('all_day', False)
            )

            # Create event via service
            created_event = self.calendar_service.create_event(user_id, event)

            # Format confirmation message
            message_parts = [
                "✅ **Evento creado exitosamente**",
                "",
                created_event.format_for_display()
            ]

            await update.message.reply_text(
                "\n".join(message_parts),
                parse_mode='Markdown'
            )

            logger.info(f"Event created successfully for user {user_id}: {created_event.id}")

        except Exception as e:
            logger.error(f"Error creating event for user {user_id}: {e}")
            await update.message.reply_text(
                f"❌ Error al crear el evento: {str(e)}\n\n"
                "Intenta de nuevo más tarde."
            )

        # Clean up context
        if 'new_event' in context.user_data:
            del context.user_data['new_event']

    def _parse_date(self, date_text: str) -> datetime:
        """Parse date from text input."""
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if date_text == "hoy":
            return today
        elif date_text == "mañana":
            return today + timedelta(days=1)
        else:
            # Try to parse DD/MM/YYYY or DD/MM format
            parts = date_text.split('/')
            if len(parts) == 2:
                # DD/MM format - use current year
                day, month = int(parts[0]), int(parts[1])
                year = today.year
            elif len(parts) == 3:
                # DD/MM/YYYY format
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            else:
                raise ValueError("Formato de fecha inválido")

            # Validate date
            try:
                parsed_date = datetime(year, month, day)
                if parsed_date < today:
                    raise ValueError("La fecha no puede ser en el pasado")
                return parsed_date
            except ValueError as e:
                if "day is out of range" in str(e) or "month must be" in str(e):
                    raise ValueError("Fecha inválida")
                raise

    def _parse_time(self, time_text: str, event_date: datetime) -> tuple:
        """Parse time from text input."""
        if '-' in time_text:
            # Start-end time format
            start_str, end_str = time_text.split('-', 1)
            start_time = self._parse_single_time(start_str.strip(), event_date)
            end_time = self._parse_single_time(end_str.strip(), event_date)

            if start_time >= end_time:
                raise ValueError("La hora de inicio debe ser anterior a la hora de fin")

            return start_time, end_time
        else:
            # Single time - assume 1 hour duration
            start_time = self._parse_single_time(time_text, event_date)
            end_time = start_time + timedelta(hours=1)
            return start_time, end_time

    def _parse_single_time(self, time_str: str, event_date: datetime) -> datetime:
        """Parse a single time string."""
        try:
            # Parse HH:MM format
            if ':' in time_str:
                hour_str, minute_str = time_str.split(':', 1)
                hour = int(hour_str)
                minute = int(minute_str)
            else:
                # Parse HH format
                hour = int(time_str)
                minute = 0

            if not (0 <= hour <= 23):
                raise ValueError("La hora debe estar entre 0 y 23")
            if not (0 <= minute <= 59):
                raise ValueError("Los minutos deben estar entre 0 y 59")

            return event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

        except ValueError:
            raise ValueError("Formato de hora inválido")

    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle cancel command."""
        await update.message.reply_text("❌ Operación cancelada.")

        # Clean up context
        if 'new_event' in context.user_data:
            del context.user_data['new_event']

        return ConversationHandler.END


    async def delete_event_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle delete event callback."""
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id

        try:
            # Get upcoming events for deletion
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30)  # Next 30 days
            events = self.calendar_service.get_events(user_id, start_date, end_date, max_results=10)

            if not events:
                await query.edit_message_text(
                    "📭 No hay eventos próximos para eliminar.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Volver al menú", callback_data="cal_back_to_menu")
                    ]])
                )
                return CALENDAR_MAIN_MENU

            # Store events in context for later reference
            context.user_data['events_to_delete'] = events

            # Create keyboard with events
            keyboard = []
            for i, event in enumerate(events):
                # Truncate title if too long
                title = event.title[:30] + "..." if len(event.title) > 30 else event.title
                date_str = event.start_time.strftime('%d/%m %H:%M') if not event.all_day else event.start_time.strftime('%d/%m')
                button_text = f"{title} - {date_str}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"del_event_{i}")])

            keyboard.append([InlineKeyboardButton("🔙 Volver al menú", callback_data="cal_back_to_menu")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "🗑️ **Eliminar evento**\n\n"
                "Selecciona el evento que deseas eliminar:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

            return DELETE_EVENT_SELECT

        except Exception as e:
            logger.error(f"Error getting events for deletion for user {user_id}: {e}")
            await query.edit_message_text(
                f"❌ Error al obtener eventos: {str(e)}\n\n"
                "Intenta de nuevo más tarde.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Volver", callback_data="cal_back_to_menu")
                ]])
            )
            return CALENDAR_MAIN_MENU

    async def handle_delete_event_select(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle event selection for deletion."""
        query = update.callback_query
        await query.answer()

        data = query.data

        if data == "cal_back_to_menu":
            return await self.back_to_menu_callback(update, context)

        if not data.startswith("del_event_"):
            return DELETE_EVENT_SELECT

        try:
            # Extract event index
            event_index = int(data.split("_")[-1])
            events = context.user_data.get('events_to_delete', [])

            if event_index >= len(events):
                await query.edit_message_text("❌ Evento no válido.")
                return ConversationHandler.END

            selected_event = events[event_index]
            context.user_data['event_to_delete'] = selected_event

            # Show confirmation
            keyboard = [
                [InlineKeyboardButton("✅ Sí, eliminar", callback_data="confirm_delete")],
                [InlineKeyboardButton("❌ No, cancelar", callback_data="cancel_delete")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"🗑️ **Confirmar eliminación**\n\n"
                f"{selected_event.format_for_display()}\n\n"
                f"¿Estás seguro de que deseas eliminar este evento?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

            return DELETE_EVENT_CONFIRM

        except (ValueError, IndexError) as e:
            logger.error(f"Error selecting event for deletion: {e}")
            await query.edit_message_text("❌ Error al seleccionar evento.")
            return ConversationHandler.END

    async def handle_delete_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle delete confirmation."""
        query = update.callback_query
        await query.answer()

        data = query.data
        user_id = update.effective_user.id

        if data == "cancel_delete":
            await query.edit_message_text("❌ Eliminación cancelada.")
            self._cleanup_delete_context(context)
            return ConversationHandler.END

        if data == "confirm_delete":
            try:
                event_to_delete = context.user_data.get('event_to_delete')
                if not event_to_delete or not event_to_delete.id:
                    await query.edit_message_text("❌ Error: evento no válido.")
                    return ConversationHandler.END

                # Delete the event
                success = self.calendar_service.delete_event(user_id, event_to_delete.id)

                if success:
                    await query.edit_message_text(
                        f"✅ **Evento eliminado exitosamente**\n\n"
                        f"📅 {event_to_delete.title}",
                        parse_mode='Markdown'
                    )
                    logger.info(f"Event {event_to_delete.id} deleted successfully for user {user_id}")
                else:
                    await query.edit_message_text("❌ Error al eliminar el evento.")

            except Exception as e:
                logger.error(f"Error deleting event for user {user_id}: {e}")
                await query.edit_message_text(
                    f"❌ Error al eliminar el evento: {str(e)}"
                )

            self._cleanup_delete_context(context)
            return ConversationHandler.END

        return DELETE_EVENT_CONFIRM

    def _cleanup_delete_context(self, context: ContextTypes.DEFAULT_TYPE):
        """Clean up deletion-related context data."""
        keys_to_remove = ['events_to_delete', 'event_to_delete']
        for key in keys_to_remove:
            if key in context.user_data:
                del context.user_data[key]

    async def update_event_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle update event callback."""
        query = update.callback_query
        await query.answer()

        user_id = update.effective_user.id

        try:
            # Get upcoming events for updating
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30)  # Next 30 days
            events = self.calendar_service.get_events(user_id, start_date, end_date, max_results=10)

            if not events:
                await query.edit_message_text(
                    "📭 No hay eventos próximos para actualizar.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Volver al menú", callback_data="cal_back_to_menu")
                    ]])
                )
                return CALENDAR_MAIN_MENU

            # Store events in context for later reference
            context.user_data['events_to_update'] = events

            # Create keyboard with events
            keyboard = []
            for i, event in enumerate(events):
                # Truncate title if too long
                title = event.title[:30] + "..." if len(event.title) > 30 else event.title
                date_str = event.start_time.strftime('%d/%m %H:%M') if not event.all_day else event.start_time.strftime('%d/%m')
                button_text = f"{title} - {date_str}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=f"upd_event_{i}")])

            keyboard.append([InlineKeyboardButton("🔙 Volver al menú", callback_data="cal_back_to_menu")])

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "✏️ **Actualizar evento**\n\n"
                "Selecciona el evento que deseas actualizar:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

            return UPDATE_EVENT_SELECT

        except Exception as e:
            logger.error(f"Error getting events for update for user {user_id}: {e}")
            await query.edit_message_text(
                f"❌ Error al obtener eventos: {str(e)}\n\n"
                "Intenta de nuevo más tarde.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Volver", callback_data="cal_back_to_menu")
                ]])
            )
            return CALENDAR_MAIN_MENU

    async def handle_update_event_select(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle event selection for updating."""
        query = update.callback_query
        await query.answer()

        data = query.data

        if data == "cal_back_to_menu":
            return await self.back_to_menu_callback(update, context)

        if not data.startswith("upd_event_"):
            return UPDATE_EVENT_SELECT

        try:
            # Extract event index
            event_index = int(data.split("_")[-1])
            events = context.user_data.get('events_to_update', [])

            if event_index >= len(events):
                await query.edit_message_text("❌ Evento no válido.")
                return ConversationHandler.END

            selected_event = events[event_index]
            context.user_data['event_to_update'] = selected_event

            # Show field selection
            keyboard = [
                [InlineKeyboardButton("📝 Título", callback_data="update_title")],
                [InlineKeyboardButton("📅 Fecha", callback_data="update_date")],
                [InlineKeyboardButton("🕐 Hora", callback_data="update_time")],
                [InlineKeyboardButton("📄 Descripción", callback_data="update_description")],
                [InlineKeyboardButton("📍 Ubicación", callback_data="update_location")],
                [InlineKeyboardButton("🔙 Volver", callback_data="cal_back_to_menu")]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"✏️ **Actualizar evento**\n\n"
                f"{selected_event.format_for_display()}\n\n"
                f"¿Qué campo deseas actualizar?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

            return UPDATE_EVENT_FIELD

        except (ValueError, IndexError) as e:
            logger.error(f"Error selecting event for update: {e}")
            await query.edit_message_text("❌ Error al seleccionar evento.")
            return ConversationHandler.END

    async def handle_update_field_select(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle field selection for updating."""
        query = update.callback_query
        await query.answer()

        data = query.data

        if data == "cal_back_to_menu":
            return await self.back_to_menu_callback(update, context)

        # Store the field to update
        context.user_data['update_field'] = data

        # Get current event
        event = context.user_data.get('event_to_update')
        if not event:
            await query.edit_message_text("❌ Error: evento no válido.")
            return ConversationHandler.END

        # Show appropriate input prompt based on field
        if data == "update_title":
            current_value = event.title
            prompt = f"📝 **Actualizar título**\n\nTítulo actual: {current_value}\n\nEscribe el nuevo título:"
        elif data == "update_date":
            current_value = event.start_time.strftime('%d/%m/%Y')
            prompt = (f"📅 **Actualizar fecha**\n\nFecha actual: {current_value}\n\n"
                     f"Escribe la nueva fecha:\n"
                     f"• `hoy` - para hoy\n"
                     f"• `mañana` - para mañana\n"
                     f"• `DD/MM/YYYY` - fecha específica\n"
                     f"• `DD/MM` - este año")
        elif data == "update_time":
            if event.all_day:
                current_value = "Todo el día"
            else:
                current_value = f"{event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}"
            prompt = (f"🕐 **Actualizar hora**\n\nHora actual: {current_value}\n\n"
                     f"Escribe la nueva hora:\n"
                     f"• `todo el día` - evento de todo el día\n"
                     f"• `HH:MM` - hora específica\n"
                     f"• `HH:MM-HH:MM` - hora de inicio y fin")
        elif data == "update_description":
            current_value = event.description or "Sin descripción"
            prompt = f"📄 **Actualizar descripción**\n\nDescripción actual: {current_value}\n\nEscribe la nueva descripción (o `/skip` para eliminar):"
        elif data == "update_location":
            current_value = event.location or "Sin ubicación"
            prompt = f"📍 **Actualizar ubicación**\n\nUbicación actual: {current_value}\n\nEscribe la nueva ubicación (o `/skip` para eliminar):"
        else:
            await query.edit_message_text("❌ Campo no válido.")
            return ConversationHandler.END

        await query.edit_message_text(
            prompt,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Cancelar", callback_data="cancel")
            ]])
        )

        return UPDATE_EVENT_VALUE

    async def handle_update_value_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new value input for updating."""
        user_id = update.effective_user.id
        new_value = update.message.text.strip()
        field = context.user_data.get('update_field')
        event = context.user_data.get('event_to_update')

        if not event or not field:
            await update.message.reply_text("❌ Error: datos de actualización no válidos.")
            return ConversationHandler.END

        try:
            # Update the event based on field
            if field == "update_title":
                if not new_value:
                    await update.message.reply_text("❌ El título no puede estar vacío.")
                    return UPDATE_EVENT_VALUE
                event.title = new_value

            elif field == "update_date":
                try:
                    new_date = self._parse_date(new_value.lower())
                    # Keep the same time, just change the date
                    if event.all_day:
                        event.start_time = new_date
                        event.end_time = new_date + timedelta(days=1)
                    else:
                        time_diff = event.end_time - event.start_time
                        event.start_time = new_date.replace(
                            hour=event.start_time.hour,
                            minute=event.start_time.minute
                        )
                        event.end_time = event.start_time + time_diff
                except ValueError as e:
                    await update.message.reply_text(f"❌ Fecha inválida: {str(e)}")
                    return UPDATE_EVENT_VALUE

            elif field == "update_time":
                try:
                    if new_value.lower() == "todo el día":
                        event.all_day = True
                        event.start_time = event.start_time.replace(hour=0, minute=0, second=0, microsecond=0)
                        event.end_time = event.start_time + timedelta(days=1)
                    else:
                        start_time, end_time = self._parse_time(new_value.lower(), event.start_time)
                        event.all_day = False
                        event.start_time = start_time
                        event.end_time = end_time
                except ValueError as e:
                    await update.message.reply_text(f"❌ Hora inválida: {str(e)}")
                    return UPDATE_EVENT_VALUE

            elif field == "update_description":
                if new_value.lower() == '/skip':
                    event.description = None
                else:
                    event.description = new_value if new_value else None

            elif field == "update_location":
                if new_value.lower() == '/skip':
                    event.location = None
                else:
                    event.location = new_value if new_value else None

            # Update the event via service
            updated_event = self.calendar_service.update_event(user_id, event)

            # Format confirmation message
            message_parts = [
                "✅ **Evento actualizado exitosamente**",
                "",
                updated_event.format_for_display()
            ]

            await update.message.reply_text(
                "\n".join(message_parts),
                parse_mode='Markdown'
            )

            logger.info(f"Event updated successfully for user {user_id}: {updated_event.id}")

        except Exception as e:
            logger.error(f"Error updating event for user {user_id}: {e}")
            await update.message.reply_text(
                f"❌ Error al actualizar el evento: {str(e)}\n\n"
                "Intenta de nuevo más tarde."
            )

        # Clean up context
        self._cleanup_update_context(context)
        return ConversationHandler.END

    def _cleanup_update_context(self, context: ContextTypes.DEFAULT_TYPE):
        """Clean up update-related context data."""
        keys_to_remove = ['events_to_update', 'event_to_update', 'update_field']
        for key in keys_to_remove:
            if key in context.user_data:
                del context.user_data[key]

# Create instance for use in handlers
calendar_commands = CalendarCommands()
