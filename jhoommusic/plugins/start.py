import logging
from pyrogram import filters
from pyrogram.types import Message
from ..core.bot import app
from ..constants.images import UI_IMAGES
from ..utils.ui import create_start_menu
from ..utils.helpers import save_user_to_db, save_chat_to_db

logger = logging.getLogger(__name__)

@app.on_message(filters.command("start"))
async def start_command(_, message: Message):
    """Handle /start command"""
    try:
        # Save user and chat to database
        await save_user_to_db(message.from_user)
        if message.chat.type != "private":
            await save_chat_to_db(message.chat)
        
        # Create start menu
        text, buttons = create_start_menu()
        
        # Send start message
        await message.reply_photo(
            photo=UI_IMAGES["main_menu"],
            caption=text,
            reply_markup=buttons
        )
        
        logger.info(f"Start command used by {message.from_user.id} in {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await message.reply_text("❌ An error occurred. Please try again later.")
