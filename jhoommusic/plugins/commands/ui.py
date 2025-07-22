import logging
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ...core.bot import app
from ...core.stream_manager import stream_manager
from ...constants.images import UI_IMAGES
from ...utils.helpers import save_user_to_db, save_chat_to_db

logger = logging.getLogger(__name__)

@app.on_message(filters.command(["settings", "config"]) & filters.group)
async def settings_command(_, message: Message):
    """Handle /settings command"""
    try:
        logger.info(f"⚙️ Settings command from {message.from_user.id} in {message.chat.id}")
        
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        is_streaming = stream_manager.is_streaming(chat_id)
        
        # Create settings keyboard
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎵 Audio Mode", callback_data=f"mode_audio_{chat_id}"),
                InlineKeyboardButton("📺 Video Mode", callback_data=f"mode_video_{chat_id}")
            ],
            [
                InlineKeyboardButton("🔊 Volume", callback_data=f"volume_{chat_id}"),
                InlineKeyboardButton("🎚️ Quality", callback_data=f"quality_{chat_id}")
            ],
            [
                InlineKeyboardButton("📊 Status", callback_data=f"status_{chat_id}"),
                InlineKeyboardButton("❌ Close", callback_data=f"close_{chat_id}")
            ]
        ])
        
        status_text = "🟢 Streaming" if is_streaming else "🔴 Not streaming"
        
        await message.reply_photo(
            photo=UI_IMAGES["settings"],
            caption=f"⚙️ **Bot Settings**\n\n"
                   f"**Chat:** {message.chat.title}\n"
                   f"**Status:** {status_text}\n\n"
                   f"Select an option below:",
            reply_markup=keyboard
        )
        
        logger.info(f"✅ Settings menu shown")
        
    except Exception as e:
        logger.error(f"❌ Settings command error: {e}")
        await message.reply(f"❌ Error: {str(e)}")

@app.on_callback_query(filters.regex(r"^mode_"))
async def mode_callback(_, query):
    """Handle mode selection callbacks"""
    try:
        data = query.data.split("_")
        mode = data[1]  # audio or video
        chat_id = int(data[2])
        
        logger.info(f"🔄 Mode change to {mode} for chat {chat_id}")
        
        await query.answer(f"🎛️ Mode set to {mode.title()}")
        
        # Update the message
        await query.message.edit_caption(
            f"⚙️ **Bot Settings**\n\n"
            f"**Mode:** {mode.title()} 📺 if mode == 'video' else 🎵\n"
            f"**Status:** {'🟢 Streaming' if stream_manager.is_streaming(chat_id) else '🔴 Not streaming'}\n\n"
            f"Mode updated successfully!"
        )
        
    except Exception as e:
        logger.error(f"❌ Mode callback error: {e}")
        await query.answer("❌ Error occurred", show_alert=True)

@app.on_callback_query(filters.regex(r"^volume_"))
async def volume_callback(_, query):
    """Handle volume callbacks"""
    try:
        await query.answer("🔊 Volume control coming soon!", show_alert=True)
    except Exception as e:
        logger.error(f"❌ Volume callback error: {e}")

@app.on_callback_query(filters.regex(r"^quality_"))
async def quality_callback(_, query):
    """Handle quality callbacks"""
    try:
        await query.answer("🎚️ Quality control coming soon!", show_alert=True)
    except Exception as e:
        logger.error(f"❌ Quality callback error: {e}")

@app.on_callback_query(filters.regex(r"^status_"))
async def status_callback(_, query):
    """Handle status callbacks"""
    try:
        data = query.data.split("_")
        chat_id = int(data[1])
        
        if stream_manager.is_streaming(chat_id):
            stream_info = stream_manager.get_stream_info(chat_id)
            if stream_info:
                info = stream_info['info']
                status_text = (
                    f"📊 **Current Status**\n\n"
                    f"**Status:** 🟢 Streaming\n"
                    f"**Title:** {info.get('title', 'Unknown')}\n"
                    f"**Type:** {stream_info['type'].title()}\n"
                    f"**Source:** {info.get('source', 'Unknown').title()}"
                )
            else:
                status_text = "📊 **Status:** 🟢 Streaming (No info available)"
        else:
            status_text = "📊 **Status:** 🔴 Not streaming"
        
        await query.answer(status_text, show_alert=True)
        
    except Exception as e:
        logger.error(f"❌ Status callback error: {e}")
        await query.answer("❌ Error occurred", show_alert=True)

@app.on_callback_query(filters.regex(r"^close_"))
async def close_callback(_, query):
    """Handle close callbacks"""
    try:
        await query.message.delete()
    except Exception as e:
        logger.error(f"❌ Close callback error: {e}")