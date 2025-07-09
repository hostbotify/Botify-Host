import logging
from pyrogram import filters
from pyrogram.types import CallbackQuery, InputMediaPhoto
from ...core.bot import app
from ...core.playback import playback_manager
from ...core.queue import queue_manager
from ...constants.images import UI_IMAGES
from ...utils.ui import create_player_ui

logger = logging.getLogger(__name__)

@app.on_callback_query(filters.regex("^show_player$"))
async def show_player_menu(_, query: CallbackQuery):
    """Handle show player callback"""
    try:
        chat_id = query.message.chat.id
        
        if not playback_manager.is_playing(chat_id):
            await query.answer("❌ No active playback", show_alert=True)
            return
        
        # Get current track and queue info
        current_track = playback_manager.get_current_track(chat_id)
        queue_size = queue_manager.get_queue_size(chat_id)
        
        # Create player UI
        text, buttons = create_player_ui(chat_id, current_track, queue_size)
        
        await query.message.edit_media(
            media=InputMediaPhoto(UI_IMAGES["player"]),
            reply_markup=buttons
        )
        await query.message.edit_caption(
            caption=text,
            reply_markup=buttons
        )
        await query.answer()
        
        logger.info(f"Player menu shown to {query.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in show_player callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)

@app.on_callback_query(filters.regex("^player_"))
async def handle_player_controls(_, query: CallbackQuery):
    """Handle player control callbacks"""
    try:
        chat_id = query.message.chat.id
        action = query.data.split("_")[1]
        
        if not playback_manager.is_playing(chat_id):
            await query.answer("❌ No active playback", show_alert=True)
            return
        
        # Handle different actions
        if action == "pause":
            if await playback_manager.pause_playback(chat_id):
                await query.answer("⏸ Playback paused")
            else:
                await query.answer("❌ Failed to pause", show_alert=True)
                
        elif action == "resume":
            if await playback_manager.resume_playback(chat_id):
                await query.answer("▶️ Playback resumed")
            else:
                await query.answer("❌ Failed to resume", show_alert=True)
                
        elif action == "next":
            if await playback_manager.skip_track(chat_id):
                await query.answer("⏭ Skipped to next track")
            else:
                await query.answer("❌ No next track", show_alert=True)
                
        elif action == "previous":
            await query.answer("⏮ Previous track not implemented yet", show_alert=True)
            
        elif action == "loop":
            await playback_manager.set_loop(chat_id, "track", 3)
            await query.answer("🔁 Loop enabled (3 times)")
            
        elif action == "shuffle":
            if await queue_manager.shuffle_queue(chat_id):
                await query.answer("🔀 Queue shuffled")
            else:
                await query.answer("❌ No tracks to shuffle", show_alert=True)
                
        elif action == "volume":
            await query.answer("🔊 Volume control coming soon", show_alert=True)
            
        elif action == "queue":
            queue = await queue_manager.get_queue(chat_id, limit=5)
            if queue:
                queue_text = "🎧 **Next in queue:**\n\n" + "\n".join(
                    f"{i+1}. {track['title']}" 
                    for i, track in enumerate(queue)
                )
                await query.answer(queue_text, show_alert=True)
            else:
                await query.answer("📜 Queue is empty", show_alert=True)
                
        elif action == "stop":
            if await playback_manager.stop_playback(chat_id):
                await query.answer("⏹ Playback stopped")
                await query.message.delete()
                return
            else:
                await query.answer("❌ Failed to stop", show_alert=True)
                
        elif action == "close":
            await query.message.delete()
            return
        
        # Update player UI
        current_track = playback_manager.get_current_track(chat_id)
        queue_size = queue_manager.get_queue_size(chat_id)
        text, buttons = create_player_ui(chat_id, current_track, queue_size)
        
        await query.message.edit_media(
            media=InputMediaPhoto(UI_IMAGES["player"]),
            reply_markup=buttons
        )
        await query.message.edit_caption(
            caption=text,
            reply_markup=buttons
        )
        
        logger.info(f"Player control used by {query.from_user.id} in {chat_id}: {action}")
        
    except Exception as e:
        logger.error(f"Error in player control callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)