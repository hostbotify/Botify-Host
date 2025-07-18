import logging
from motor.motor_asyncio import AsyncIOMotorClient
from .config import Config

logger = logging.getLogger(__name__)

class Database:
    """Database manager for MongoDB operations"""

    def __init__(self):
        self.client = None
        self.db = None
        self._collections = {}
        self.enabled = False

    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(Config.MONGO_URI)
            self.db = self.client.jhoommusic

            # Test connection
            await self.client.admin.command('ping')
            logger.info("✅ Connected to MongoDB successfully")
            self.enabled = True

            # Initialize collections
            await self._init_collections()
            await self._create_indexes()

        except Exception as e:
            logger.warning(f"⚠️ MongoDB connection failed: {e}")
            logger.warning("⚠️ Bot will run without database functionality")
            self.enabled = False
            # Don't raise exception, allow bot to continue without DB

    async def _init_collections(self):
        """Initialize database collections"""
        if not self.enabled:
            return
            
        collection_names = [
            'users', 'chats', 'blocked_users', 'blacklisted_chats',
            'auth_users', 'channel_connections', 'channel_queues',
            'gbanned_users', 'playlists', 'user_settings',
            'thumbnails', 'troubleshooting_logs'
        ]

        for name in collection_names:
            self._collections[name] = self.db[name]

    async def _create_indexes(self):
        """Create database indexes for better performance"""
        if not self.enabled:
            return
            
        try:
            await self._collections['users'].create_index("user_id", unique=True)
            await self._collections['chats'].create_index("chat_id", unique=True)
            await self._collections['blocked_users'].create_index("user_id", unique=True)
            await self._collections['auth_users'].create_index("user_id", unique=True)
            await self._collections['gbanned_users'].create_index("user_id", unique=True)
            await self._collections['playlists'].create_index([("user_id", 1), ("name", 1)], unique=True)
            await self._collections['channel_queues'].create_index([("chat_id", 1), ("timestamp", -1)])
            await self._collections['user_settings'].create_index([("chat_id", 1), ("user_id", 1)])
            await self._collections['thumbnails'].create_index("key", unique=True)
            await self._collections['troubleshooting_logs'].create_index([("chat_id", 1), ("timestamp", -1)])

            logger.info("✅ Database indexes created successfully")
        except Exception as e:
            logger.error(f"⚠️ Error creating database indexes: {e}")

    def __getattr__(self, name):
        """Allow direct access to collections"""
        if not self.enabled:
            raise AttributeError(f"Database not enabled. Cannot access collection '{name}'")
        if name in self._collections:
            return self._collections[name]
        raise AttributeError(f"Collection '{name}' not found")

    async def close(self):
        """Close database connection"""
        if self.client and self.enabled:
            self.client.close()
            logger.info("🔒 Database connection closed")

# Global database instance
db = Database()
