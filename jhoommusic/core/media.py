"""
Legacy wrapper for backward compatibility with enhanced universal support
"""
from .media_extractor import universal_extractor

class MediaExtractor:
    """Legacy wrapper for backward compatibility"""
    
    @staticmethod
    async def extract_info(query: str, audio_only: bool = True):
        """Extract media info using universal extractor"""
        return await universal_extractor.extract(query, audio_only=audio_only)
    
    @staticmethod
    async def extract_youtube_info(query: str, audio_only: bool = True):
        """Extract YouTube info using universal extractor"""
        return await universal_extractor.extract(query, audio_only=audio_only)
    
    @staticmethod
    async def extract_spotify_info(url: str):
        """Extract Spotify info using universal extractor"""
        return await universal_extractor.extract(url)
    
    @staticmethod
    async def extract_radio_info(url: str):
        """Extract radio stream info using universal extractor"""
        return await universal_extractor.extract(url)

# Global instance for backward compatibility
media_extractor = MediaExtractor()