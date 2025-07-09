import asyncio
import logging
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime
from .database import db
from .config import Config

logger = logging.getLogger(__name__)

class QueueManager:
    """Manages music queues for different chats"""
    
    def __init__(self):
        self.queues: Dict[int, List[Dict]] = defaultdict(list)
        self.locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
    
    async def add_to_queue(self, chat_id: int, track: Dict) -> None:
        """Add track to queue"""
        async with self.locks[chat_id]:
            if len(self.queues[chat_id]) >= Config.MAX_QUEUE_SIZE:
                raise Exception(f"Queue limit reached ({Config.MAX_QUEUE_SIZE} tracks)")
            
            self.queues[chat_id].append(track)
            
            # Save to database
            await db.channel_queues.insert_one({
                "chat_id": chat_id,
                "track": track,
                "timestamp": datetime.utcnow()
            })
            
            logger.info(f"Added track to queue {chat_id}: {track.get('title', 'Unknown')}")
    
    async def get_next_track(self, chat_id: int) -> Optional[Dict]:
        """Get next track from queue"""
        async with self.locks[chat_id]:
            # Try memory queue first
            if chat_id in self.queues and self.queues[chat_id]:
                track = self.queues[chat_id].pop(0)
                await self._remove_from_db(chat_id, track)
                return track
            
            # Try database queue
            db_track = await db.channel_queues.find_one(
                {"chat_id": chat_id},
                sort=[("timestamp", 1)]
            )
            
            if db_track:
                await db.channel_queues.delete_one({"_id": db_track["_id"]})
                return db_track['track']
            
            return None
    
    async def clear_queue(self, chat_id: int) -> int:
        """Clear all tracks from queue"""
        async with self.locks[chat_id]:
            # Clear memory queue
            queue_size = len(self.queues.get(chat_id, []))
            if chat_id in self.queues:
                self.queues[chat_id].clear()
            
            # Clear database queue
            result = await db.channel_queues.delete_many({"chat_id": chat_id})
            
            logger.info(f"Cleared queue for chat {chat_id}: {queue_size + result.deleted_count} tracks")
            return queue_size + result.deleted_count
    
    async def get_queue(self, chat_id: int, limit: int = 10) -> List[Dict]:
        """Get current queue"""
        async with self.locks[chat_id]:
            memory_queue = self.queues.get(chat_id, [])[:limit]
            
            if len(memory_queue) < limit:
                # Get additional tracks from database
                remaining = limit - len(memory_queue)
                db_tracks = await db.channel_queues.find(
                    {"chat_id": chat_id},
                    sort=[("timestamp", 1)]
                ).limit(remaining).to_list(remaining)
                
                db_queue = [track['track'] for track in db_tracks]
                return memory_queue + db_queue
            
            return memory_queue
    
    async def shuffle_queue(self, chat_id: int) -> bool:
        """Shuffle the queue"""
        async with self.locks[chat_id]:
            if chat_id in self.queues and self.queues[chat_id]:
                import random
                random.shuffle(self.queues[chat_id])
                logger.info(f"Shuffled queue for chat {chat_id}")
                return True
            return False
    
    async def _remove_from_db(self, chat_id: int, track: Dict):
        """Remove track from database"""
        try:
            await db.channel_queues.delete_one({
                "chat_id": chat_id,
                "track.title": track.get('title', '')
            })
        except Exception as e:
            logger.error(f"Error removing track from DB: {e}")
    
    def get_queue_size(self, chat_id: int) -> int:
        """Get queue size"""
        return len(self.queues.get(chat_id, []))

# Global queue manager instance
queue_manager = QueueManager()
