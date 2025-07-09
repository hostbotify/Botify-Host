import asyncio
import logging
import redis
from typing import Optional
from ..core.config import Config

logger = logging.getLogger(__name__)

# Initialize Redis client
redis_client = None
try:
    redis_client = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        socket_timeout=5,
        socket_connect_timeout=5,
        decode_responses=False
    )
    redis_client.ping()
    logger.info("Redis connected successfully")
except Exception as e:
    logger.error(f"Redis connection error: {e}")
    redis_client = None

async def get_cached_data(key: str) -> Optional[bytes]:
    """Get cached data from Redis"""
    if not redis_client:
        return None
    
    try:
        data = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: redis_client.get(key)
        )
        return data if data else None
    except Exception as e:
        logger.error(f"Cache get error: {e}")
        return None

async def set_cached_data(key: str, data: bytes, expire: int = 3600) -> bool:
    """Set data in Redis cache"""
    if not redis_client:
        return False
    
    try:
        return await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: redis_client.setex(key, expire, data)
        )
    except Exception as e:
        logger.error(f"Cache set error: {e}")
        return False

async def delete_cached_data(key: str) -> bool:
    """Delete cached data"""
    if not redis_client:
        return False
    
    try:
        return await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: redis_client.delete(key)
        )
    except Exception as e:
        logger.error(f"Cache delete error: {e}")
        return False

async def get_cache_stats() -> dict:
    """Get cache statistics"""
    if not redis_client:
        return {"status": "disconnected"}
    
    try:
        info = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: redis_client.info()
        )
        
        return {
            "status": "connected",
            "keys": redis_client.dbsize(),
            "memory_used": info.get("used_memory_human", "Unknown"),
            "uptime": info.get("uptime_in_seconds", 0)
        }
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return {"status": "error", "error": str(e)}