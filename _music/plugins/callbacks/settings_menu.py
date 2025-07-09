import logging
from pyrogram import filters
from pyrogram.types import CallbackQuery, InputMediaPhoto
from ...core.bot import app
from ...constants.images import UI_IMAGES
from ...utils.ui import create_settings_menu

logger = logging.getLogger(__name__)

@app.on_callback_query(filters.regex("^settings_menu$"))
async def show_settings_menu(_, query: CallbackQuery):
    """Handle settings menu callback"""
    try:
        chat_id = query.message.chat.id
        text, buttons = create_settings_menu(chat_id)
        
        await query.message.edit_media(
            media=InputMediaPhoto(UI_IMAGES["settings"]),
            reply_markup=buttons
        )
        await query.message.edit_caption(
            caption=text,
            reply_markup=buttons
        )
        await query.answer()
        
        logger.info(f"Settings menu shown to {query.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in settings_menu callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)

@app.on_callback_query(filters.regex("^settings_"))
async def handle_settings_callbacks(_, query: CallbackQuery):
    """Handle settings callbacks"""
    try:
        parts = query.data.split("_")
        action = parts[1]
        chat_id = int(parts[2]) if len(parts) > 2 else query.message.chat.id
        
        if action == "volume":
            await query.answer("🔊 Volume control coming soon", show_alert=True)
        elif action == "quality":
            await query.answer("🎚 Quality settings coming soon", show_alert=True)
        elif action == "lang":
            await query.answer("🌐 Language settings coming soon", show_alert=True)
        elif action == "notify":
            await query.answer("🔔 Notification settings coming soon", show_alert=True)
        
        # Return to settings menu
        text, buttons = create_settings_menu(chat_id)
        await query.message.edit_media(
            media=InputMediaPhoto(UI_IMAGES["settings"]),
            reply_markup=buttons
        )
        await query.message.edit_caption(
            caption=text,
            reply_markup=buttons
        )
        
        logger.info(f"Settings callback handled by {query.from_user.id}: {action}")
        
    except Exception as e:
        logger.error(f"Error in settings callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)

@app.on_callback_query(filters.regex("^system_info$"))
async def show_system_info(_, query: CallbackQuery):
    """Handle system info callback"""
    try:
        # Import here to avoid circular imports
        from ...plugins.commands.system import show_stats
        
        # Create a mock message object for the stats function
        class MockMessage:
            def __init__(self, user):
                self.from_user = user
                self.reply_photo = query.message.edit_media
        
        mock_message = MockMessage(query.from_user)
        
        # This is a simplified version - in a real implementation,
        # you'd want to create a proper system info display
        await query.answer("📊 System information coming soon", show_alert=True)
        
        logger.info(f"System info requested by {query.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in system_info callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)