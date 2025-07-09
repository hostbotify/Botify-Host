import os
import logging
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for JhoomMusic Bot"""
    
    # Bot Configuration
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # Database Configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/jhoommusic")
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # Spotify Configuration
    SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
    
    # Admin Configuration
    SUDO_USERS: List[int] = [int(x) for x in os.getenv("SUDO_USERS", "").split(",") if x.strip()]
    SUPER_GROUP_ID: int = int(os.getenv("SUPER_GROUP_ID", "0"))
    SUPER_GROUP_USERNAME: str = os.getenv("SUPER_GROUP_USERNAME", "")
    
    # Performance Settings
    FFMPEG_PROCESSES: int = int(os.getenv("FFMPEG_PROCESSES", "4"))
    MAX_PLAYLIST_SIZE: int = int(os.getenv("MAX_PLAYLIST_SIZE", "100"))
    MAX_QUEUE_SIZE: int = int(os.getenv("MAX_QUEUE_SIZE", "50"))
    MAX_HISTORY_SIZE: int = int(os.getenv("MAX_HISTORY_SIZE", "20"))
    MAX_THUMBNAIL_CACHE: int = int(os.getenv("MAX_THUMBNAIL_CACHE", "100"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "jhoommusic.log")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        required_vars = [
            ("API_ID", cls.API_ID),
            ("API_HASH", cls.API_HASH),
            ("BOT_TOKEN", cls.BOT_TOKEN),
            ("MONGO_URI", cls.MONGO_URI),
            ("SUPER_GROUP_ID", cls.SUPER_GROUP_ID),
            ("SUPER_GROUP_USERNAME", cls.SUPER_GROUP_USERNAME)
        ]
        
        missing = []
        for var_name, var_value in required_vars:
            if not var_value or (isinstance(var_value, int) and var_value == 0):
                missing.append(var_name)
        
        if missing:
            logging.error(f"Missing required environment variables: {', '.join(missing)}")
            return False
        
        return True