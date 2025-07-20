# Legacy media extractor - now using universal_extractor
from .media_extractor import universal_extractor as media_extractor

# Backward compatibility
class MediaExtractor:
    @staticmethod
    async def extract_info(query: str, audio_only: bool = True):
        return await media_extractor.extract(query, audio_only=audio_only)
    
    @staticmethod
    async def extract_youtube_info(query: str, audio_only: bool = True):
        return await media_extractor.extract(query, audio_only=audio_only)
    
    @staticmethod
    async def extract_spotify_info(url: str):
        return await media_extractor.extract(url)
    
    @staticmethod
    async def extract_radio_info(url: str):
        return await media_extractor.extract(url)
