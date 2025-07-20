"""
Enhanced Media Extractor with Universal Support
Now supports all platforms with advanced bypass capabilities
"""
from .media_extractor import universal_extractor

class MediaExtractor:
    """Legacy wrapper for backward compatibility"""
    
    @staticmethod
    async def extract_info(query: str, audio_only: bool = True):
        """Extract media info with universal support"""
        return await universal_extractor.extract(query, audio_only=audio_only)
    
    @staticmethod
    async def extract_youtube_info(query: str, audio_only: bool = True):
        """Extract YouTube info with advanced bypass"""
        return await universal_extractor.extract(query, audio_only=audio_only)
    
    @staticmethod
    async def extract_spotify_info(url: str):
        """Extract Spotify info (converts to YouTube)"""
        return await universal_extractor.extract(url)
    
    @staticmethod
    async def extract_radio_info(url: str):
        """Extract radio stream info"""
        return await universal_extractor.extract(url)

# Global instance for backward compatibility
media_extractor = MediaExtractor()