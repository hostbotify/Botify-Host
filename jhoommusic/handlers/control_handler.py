import logging
from pyrogram import filters
from pyrogram.types import Message
from ..core.bot import app
from ..core.stream_manager import stream_manager
from ..utils.helpers import is_admin_or_sudo, save_user_to_db, save_chat_to_db

logger = logging.getLogger(__name__)

@app.on_message(filters.command(["pause", "pa"]) & filters.group)
async def pause_music(_, message: Message):
    """Handle /pause command"""
    try:
        logger.info(f"⏸️ PAUSE COMMAND from {message.from_user.id} in {message.chat.id}")
        
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        
        if not stream_manager.is_streaming(chat_id):
            await message.reply("❌ No active stream to pause. Use /play [song] first.")
            return
        
        processing_msg = await message.reply("🔄 **Pausing playback...**")
        
        success = await stream_manager.pause_stream(chat_id)
        
        if success:
            await processing_msg.edit_text("⏸️ **Playback paused**")
        else:
            await processing_msg.edit_text("❌ **Failed to pause playback**")
        
        logger.info(f"✅ PAUSE COMMAND completed: {success}")
        
    except Exception as e:
        logger.error(f"❌ Pause command error: {e}")
        import traceback
        traceback.print_exc()
        await message.reply(f"❌ Error: {str(e)}")

@app.on_message(filters.command(["resume", "r"]) & filters.group)
async def resume_music(_, message: Message):
    """Handle /resume command"""
    try:
        logger.info(f"▶️ RESUME COMMAND from {message.from_user.id} in {message.chat.id}")
        
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        
        processing_msg = await message.reply("🔄 **Resuming playback...**")
        
        success = await stream_manager.resume_stream(chat_id)
        
        if success:
            await processing_msg.edit_text("▶️ **Playback resumed**")
        else:
            await processing_msg.edit_text("❌ **Failed to resume playback**")
        
        logger.info(f"✅ RESUME COMMAND completed: {success}")
        
    except Exception as e:
        logger.error(f"❌ Resume command error: {e}")
        import traceback
        traceback.print_exc()
        await message.reply(f"❌ Error: {str(e)}")

@app.on_message(filters.command(["stop", "end"]) & filters.group)
async def stop_music(_, message: Message):
    """Handle /stop command"""
    try:
        logger.info(f"⏹️ STOP COMMAND from {message.from_user.id} in {message.chat.id}")
        
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        
        processing_msg = await message.reply("🔄 **Stopping playback...**")
        
        success = await stream_manager.stop_stream(chat_id)
        
        if success:
            await processing_msg.edit_text("⏹️ **Playback stopped and left voice chat**")
        else:
            await processing_msg.edit_text("❌ **Failed to stop playback**")
        
        logger.info(f"✅ STOP COMMAND completed: {success}")
        
    except Exception as e:
        logger.error(f"❌ Stop command error: {e}")
        import traceback
        traceback.print_exc()
        await message.reply(f"❌ Error: {str(e)}")

@app.on_message(filters.command(["status", "current"]) & filters.group)
async def status_command(_, message: Message):
    """Handle /status command"""
    try:
        logger.info(f"📊 STATUS COMMAND from {message.from_user.id} in {message.chat.id}")
        
        chat_id = message.chat.id
        
        if stream_manager.is_streaming(chat_id):
            stream_info = stream_manager.get_stream_info(chat_id)
            if stream_info:
                info = stream_info['info']
                await message.reply(
                    f"📊 **Current Status**\n\n"
                    f"**Status:** 🟢 Streaming\n"
                    f"**Title:** {info.get('title', 'Unknown')}\n"
                    f"**Type:** {stream_info['type'].title()}\n"
                    f"**Source:** {info.get('source', 'Unknown').title()}"
                )
            else:
                await message.reply("📊 **Status:** 🟢 Streaming (No info available)")
        else:
            await message.reply("📊 **Status:** 🔴 Not streaming")
        
        logger.info(f"✅ STATUS COMMAND completed")
        
    except Exception as e:
        logger.error(f"❌ Status command error: {e}")
        import traceback
        traceback.print_exc()
        await message.reply(f"❌ Error: {str(e)}")