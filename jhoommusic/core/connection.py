import asyncio
import logging
from typing import Dict

from pytgcalls.types.input_streams import AudioPiped
from pytgcalls.types.input_streams.quality import HighQualityAudio
from pytgcalls.exceptions import NoActiveGroupCall

from .bot import pytgcalls

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages voice chat connections"""
    
    def __init__(self):
        self.active_connections: Dict[int, bool] = {}
        self.lock = asyncio.Lock()
    
    async def get_connection(self, chat_id: int) -> bool:
        """Get or create a voice chat connection"""
        async with self.lock:
            if chat_id in self.active_connections:
                return True
            
            try:
                # Join voice chat with a dummy stream
                await pytgcalls.join_group_call(
                    chat_id,
                    AudioPiped("http://example.com/dummy.mp3", HighQualityAudio())
                )
                self.active_connections[chat_id] = True
                logger.info(f"Connected to voice chat: {chat_id}")
                return True
            except Exception as e:
                logger.error(f"Connection error for {chat_id}: {e}")
                return False
    
    async def release_connection(self, chat_id: int) -> None:
        """Release voice chat connection"""
        async with self.lock:
            if chat_id in self.active_connections:
                try:
                    await pytgcalls.leave_group_call(chat_id)
                    logger.info(f"Left voice chat: {chat_id}")
                except Exception as e:
                    logger.error(f"Error leaving call {chat_id}: {e}")
                finally:
                    del self.active_connections[chat_id]
    
    def is_connected(self, chat_id: int) -> bool:
        """Check if connected to voice chat"""
        return chat_id in self.active_connections
    
    async def cleanup_inactive_connections(self):
        """Clean up inactive connections"""
        async with self.lock:
            inactive_chats = []
            for chat_id in list(self.active_connections.keys()):
                try:
                    participants = await pytgcalls.get_participants(chat_id)
                    if len(participants) <= 1:  # Only bot in call
                        inactive_chats.append(chat_id)
                except Exception:
                    inactive_chats.append(chat_id)
            
            for chat_id in inactive_chats:
                await self.release_connection(chat_id)

# Global connection manager instance
connection_manager = ConnectionManager()
