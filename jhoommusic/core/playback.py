import logging
from typing import Dict, Optional
from collections import defaultdict
from .bot import tgcaller, app
from .connection import connection_manager
from .queue import queue_manager
from .stream_manager import stream_manager
from .thumbnail import generate_thumbnail
from ..constants.images import UI_IMAGES
from ..utils.helpers import format_duration

logger = logging.getLogger(__name__)

class PlaybackManager:
    """Manages music playback across different chats"""
    
    def __init__(self):
        self.current_streams: Dict[int, Dict] = {}
        self.loop_status: Dict[int, Dict] = {}
        self.shuffle_status: Dict[int, bool] = {}
        self.message_history: Dict[int, list] = defaultdict(list)
    
    async def play_track(self, chat_id: int, track: Dict, same_track: bool = False):
        """Play a track in the specified chat"""
        try:
            if not same_track:
                self.current_streams[chat_id] = track
            
            # Use stream manager for playback
            success = await stream_manager.start_stream(
                chat_id, 
                track['url'], 
                video=track.get('is_video', False)
            )
            
            if not success:
                await app.send_message(chat_id, "❌ Failed to start playback")
                return False
            
            # Send now playing message
            thumb = await generate_thumbnail(
                title=track['title'],
                artist=track.get('artist', 'Unknown Artist'),
                duration=track.get('duration', 0),
                cover_url=track.get('thumbnail'),
                requester_id=track.get('user_id')
            )
            
            caption = self._format_now_playing(track)
            msg = await app.send_photo(
                chat_id,
                photo=thumb,
                caption=caption
            )
            
            # Track message for cleanup
            self.message_history[chat_id].append(msg.id)
            await self._cleanup_old_messages(chat_id)
            
            logger.info(f"Now playing in {chat_id}: {track['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Playback error in chat {chat_id}: {e}")
            await app.send_message(chat_id, f"❌ Playback error: {str(e)}")
            return False
    
    async def play_next_track(self, chat_id: int, same_track: bool = False):
        """Play the next track in queue"""
        try:
            if same_track and chat_id in self.current_streams:
                track = self.current_streams[chat_id]
            else:
                track = await queue_manager.get_next_track(chat_id)
                if not track:
                    await self._handle_playback_end(chat_id)
                    return
            
            await self.play_track(chat_id, track, same_track)
            
        except Exception as e:
            logger.error(f"Error playing next track in {chat_id}: {e}")
            await app.send_message(chat_id, f"❌ Error playing next track: {str(e)}")
    
    async def pause_playback(self, chat_id: int) -> bool:
        """Pause playback"""
        return await stream_manager.pause_stream(chat_id)
    
    async def resume_playback(self, chat_id: int) -> bool:
        """Resume playback"""
        return await stream_manager.resume_stream(chat_id)
    
    async def stop_playback(self, chat_id: int) -> bool:
        """Stop playback and clear queue"""
        success = await stream_manager.stop_stream(chat_id)
        if success:
            if chat_id in self.current_streams:
                del self.current_streams[chat_id]
            await queue_manager.clear_queue(chat_id)
        return success
    
    async def skip_track(self, chat_id: int) -> bool:
        """Skip current track"""
        if chat_id in self.current_streams:
            await self.play_next_track(chat_id)
            return True
        return False
    
    def get_current_track(self, chat_id: int) -> Optional[Dict]:
        """Get currently playing track"""
        return self.current_streams.get(chat_id)
    
    def is_playing(self, chat_id: int) -> bool:
        """Check if music is playing"""
        return chat_id in self.current_streams
    
    async def set_loop(self, chat_id: int, loop_type: str, count: int = 1):
        """Set loop mode"""
        self.loop_status[chat_id] = {
            'type': loop_type,  # 'track' or 'queue'
            'count': count
        }
    
    def clear_loop(self, chat_id: int):
        """Clear loop mode"""
        self.loop_status.pop(chat_id, None)
    
    async def _handle_playback_end(self, chat_id: int):
        """Handle end of playback"""
        if chat_id in self.current_streams:
            del self.current_streams[chat_id]
        
        if chat_id not in self.loop_status or self.loop_status[chat_id]['count'] == 0:
            await connection_manager.release_connection(chat_id)
            await app.send_photo(
                chat_id,
                UI_IMAGES["player"],
                caption="⏹ Playback ended"
            )
        
        if chat_id in self.loop_status:
            del self.loop_status[chat_id]
    
    def _format_now_playing(self, track: Dict) -> str:
        """Format now playing message"""
        return (
            f"🎵 **Now Playing**\n\n"
            f"**Title**: {track['title']}\n"
            f"**Artist**: {track.get('artist', 'Unknown')}\n"
            f"**Duration**: {format_duration(track.get('duration', 0))}\n"
            f"**Source**: {track.get('source', 'Unknown').capitalize()}"
        )
    
    async def _cleanup_old_messages(self, chat_id: int, keep_last: int = 5):
        """Clean up old messages"""
        if chat_id in self.message_history and len(self.message_history[chat_id]) > keep_last:
            for msg_id in self.message_history[chat_id][:-keep_last]:
                try:
                    await app.delete_messages(chat_id, msg_id)
                except Exception:
                    pass
            self.message_history[chat_id] = self.message_history[chat_id][-keep_last:]

# Global playback manager instance
playback_manager = PlaybackManager()
