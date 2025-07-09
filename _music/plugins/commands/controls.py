import logging
from pyrogram import filters
from pyrogram.types import Message
from ...core.bot import app
from ...core.playback import playback_manager
from ...core.queue import queue_manager
from ...constants.images import UI_IMAGES
from ...utils.helpers import is_admin_or_sudo, save_user_to_db, save_chat_to_db

logger = logging.getLogger(__name__)

@app.on_message(filters.command(["pause", "pa"]) & filters.group)
async def pause_music(_, message: Message):
    """Handle /pause command"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        
        # Check if user is admin
        if not await is_admin_or_sudo(chat_id, message.from_user.id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Only admins can use this command"
            )
            return
        
        # Pause playback
        if await playback_manager.pause_playback(chat_id):
            await message.reply_photo(
                photo=UI_IMAGES["sultan"],
                caption="⏸ **Playback paused**"
            )
        else:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ No active playback to pause"
            )
        
        logger.info(f"Pause command used by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in pause command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command(["resume", "r"]) & filters.group)
async def resume_music(_, message: Message):
    """Handle /resume command"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        
        # Check if user is admin
        if not await is_admin_or_sudo(chat_id, message.from_user.id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Only admins can use this command"
            )
            return
        
        # Resume playback
        if await playback_manager.resume_playback(chat_id):
            await message.reply_photo(
                photo=UI_IMAGES["sultan"],
                caption="▶️ **Playback resumed**"
            )
        else:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ No paused playback to resume"
            )
        
        logger.info(f"Resume command used by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in resume command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command(["skip", "s"]) & filters.group)
async def skip_music(_, message: Message):
    """Handle /skip command"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        
        # Check if user is admin
        if not await is_admin_or_sudo(chat_id, message.from_user.id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Only admins can use this command"
            )
            return
        
        # Skip track
        if await playback_manager.skip_track(chat_id):
            await message.reply_photo(
                photo=UI_IMAGES["sultan"],
                caption="⏭ **Skipped to next track**"
            )
        else:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ No active playback to skip"
            )
        
        logger.info(f"Skip command used by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in skip command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command(["stop", "end"]) & filters.group)
async def stop_music(_, message: Message):
    """Handle /stop command"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        
        # Check if user is admin
        if not await is_admin_or_sudo(chat_id, message.from_user.id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Only admins can use this command"
            )
            return
        
        # Stop playback
        if await playback_manager.stop_playback(chat_id):
            await message.reply_photo(
                photo=UI_IMAGES["sultan"],
                caption="⏹ **Playback stopped and queue cleared**"
            )
        else:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ No active playback to stop"
            )
        
        logger.info(f"Stop command used by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in stop command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command(["queue", "q"]) & filters.group)
async def show_queue(_, message: Message):
    """Handle /queue command"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        
        # Get current track and queue
        current_track = playback_manager.get_current_track(chat_id)
        queue = await queue_manager.get_queue(chat_id, limit=10)
        
        if not current_track and not queue:
            await message.reply_photo(
                photo=UI_IMAGES["queue"],
                caption="📜 **Queue is empty**\n\nUse `/play [song name]` to add tracks"
            )
            return
        
        # Format queue message
        text = "📜 **Current Queue**\n\n"
        
        if current_track:
            text += f"🎵 **Now Playing:**\n"
            text += f"└ {current_track['title']} - {current_track.get('artist', 'Unknown')}\n\n"
        
        if queue:
            text += f"📋 **Up Next ({len(queue)} tracks):**\n"
            for i, track in enumerate(queue, 1):
                text += f"{i}. {track['title']} - {track.get('artist', 'Unknown')}\n"
        
        await message.reply_photo(
            photo=UI_IMAGES["queue"],
            caption=text
        )
        
        logger.info(f"Queue command used by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in queue command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command(["shuffle"]) & filters.group)
async def shuffle_queue(_, message: Message):
    """Handle /shuffle command"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        
        # Check if user is admin
        if not await is_admin_or_sudo(chat_id, message.from_user.id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Only admins can use this command"
            )
            return
        
        # Shuffle queue
        if await queue_manager.shuffle_queue(chat_id):
            await message.reply_photo(
                photo=UI_IMAGES["shuffle"],
                caption="🔀 **Queue shuffled successfully**"
            )
        else:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ No tracks in queue to shuffle"
            )
        
        logger.info(f"Shuffle command used by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in shuffle command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command(["loop", "spiral"]) & filters.group)
async def loop_control(_, message: Message):
    """Handle /loop command"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        
        # Check if user is admin
        if not await is_admin_or_sudo(chat_id, message.from_user.id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Only admins can use this command"
            )
            return
        
        if len(message.command) < 2:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="**Usage:** `/loop [enable/disable/track/queue]` or `/loop [1-10]`"
            )
            return
        
        arg = message.command[1].lower()
        
        if arg in ["enable", "track"]:
            await playback_manager.set_loop(chat_id, "track", 1)
            await message.reply_photo(
                photo=UI_IMAGES["spiral"],
                caption="🔁 **Track loop enabled**"
            )
        elif arg == "queue":
            await playback_manager.set_loop(chat_id, "queue", 1)
            await message.reply_photo(
                photo=UI_IMAGES["spiral"],
                caption="🔁 **Queue loop enabled**"
            )
        elif arg == "disable":
            playback_manager.clear_loop(chat_id)
            await message.reply_photo(
                photo=UI_IMAGES["spiral"],
                caption="🔁 **Loop disabled**"
            )
        elif arg.isdigit() and 1 <= int(arg) <= 10:
            await playback_manager.set_loop(chat_id, "track", int(arg))
            await message.reply_photo(
                photo=UI_IMAGES["spiral"],
                caption=f"🔁 **Loop set to {arg} times**"
            )
        else:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Invalid loop command"
            )
        
        logger.info(f"Loop command used by {message.from_user.id} in {chat_id}: {arg}")
        
    except Exception as e:
        logger.error(f"Error in loop command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )