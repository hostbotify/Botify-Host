import asyncio
import logging
from typing import Dict

from TgCaller import AudioConfig

from .bot import tgcaller

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
                # Join voice chat
                await tgcaller.join_call(chat_id)
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
                    await tgcaller.leave_call(chat_id)
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
                    # Check if call is still active
                    if not await tgcaller.is_connected(chat_id):
                        inactive_chats.append(chat_id)
                except Exception:
                    inactive_chats.append(chat_id)
            
            for chat_id in inactive_chats:
                await self.release_connection(chat_id)

# Global connection manager instance
connection_manager = ConnectionManager()
