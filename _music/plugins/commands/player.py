import logging
from pyrogram import filters
from pyrogram.types import Message
from ...core.bot import app
from ...core.playback import playback_manager
from ...core.queue import queue_manager
from ...constants.images import UI_IMAGES
from ...utils.ui import create_player_ui
from ...utils.helpers import save_user_to_db, save_chat_to_db

logger = logging.getLogger(__name__)

@app.on_message(filters.command(["player", "control"]) & filters.group)
async def show_player_panel(_, message: Message):
    """Handle /player command"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        
        # Check if music is playing
        if not playback_manager.is_playing(chat_id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ No active playback to control"
            )
            return
        
        # Get current track and queue info
        current_track = playback_manager.get_current_track(chat_id)
        queue_size = queue_manager.get_queue_size(chat_id)
        
        # Create player UI
        text, buttons = create_player_ui(chat_id, current_track, queue_size)
        
        await message.reply_photo(
            photo=UI_IMAGES["player"],
            caption=text,
            reply_markup=buttons
        )
        
        logger.info(f"Player command used by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in player command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )