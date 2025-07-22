import asyncio
import logging
from typing import Dict, Optional, Any
from .bot import tgcaller, app
from .media_extractor import universal_extractor

logger = logging.getLogger(__name__)

class StreamManager:
    """Advanced stream manager with quality control and fallback"""
    
    def __init__(self):
        self.active_streams: Dict[int, Dict] = {}
        self.stream_configs = {
            'audio_low': {'bitrate': 128},
            'audio_medium': {'bitrate': 256},
            'audio_high': {'bitrate': 320},
            'video_low': {'width': 640, 'height': 480, 'bitrate': 500},
            'video_medium': {'width': 1280, 'height': 720, 'bitrate': 1000},
            'video_high': {'width': 1920, 'height': 1080, 'bitrate': 2000}
        }
    
    async def start_stream(self, chat_id: int, source: str, **options) -> bool:
        """Start streaming with smart quality selection"""
        try:
            # Extract media info
            media_info = await universal_extractor.extract(source, **options)
            if not media_info:
                logger.error(f"Failed to extract media info for: {source}")
                return False
            
            # Handle playlist
            if isinstance(media_info, list):
                if not media_info:
                    return False
                media_info = media_info[0]  # Use first track
            
            # Determine stream type and quality
            is_video = media_info.get('is_video', False) or options.get('video', False)
            quality = options.get('quality', 'medium')
            
            # Get stream URL
            stream_url = media_info['url']
            if not stream_url:
                logger.error("No stream URL found")
                return False
            
            # Start streaming based on type
            if is_video:
                success = await self._start_video_stream(chat_id, stream_url, quality)
            else:
                success = await self._start_audio_stream(chat_id, stream_url, quality)
            
            if success:
                self.active_streams[chat_id] = {
                    'info': media_info,
                    'type': 'video' if is_video else 'audio',
                    'quality': quality,
                    'url': stream_url
                }
                logger.info(f"Stream started in {chat_id}: {media_info['title']}")
            
            return success
            
        except Exception as e:
            logger.error(f"Stream start error: {e}")
            return False
    
    async def _start_audio_stream(self, chat_id: int, url: str, quality: str) -> bool:
        """Start audio stream with quality config"""
        try:
            # Join call first if not already joined
            try:
                await tgcaller.join(chat_id)
            except Exception as e:
                if "already joined" not in str(e).lower():
                    raise e
            
            # Stream audio
            if any(domain in url for domain in ['youtube.com', 'youtu.be', 'music.youtube.com']):
                await tgcaller.play(chat_id, url, video=False)
            else:
                await tgcaller.play(chat_id, url, video=False)
            
            return True
            
        except Exception as e:
            logger.error(f"Audio stream error: {e}")
            return False
    
    async def _start_video_stream(self, chat_id: int, url: str, quality: str) -> bool:
        """Start video stream with quality config"""
        try:
            # Join call first if not already joined
            try:
                await tgcaller.join(chat_id)
            except Exception as e:
                if "already joined" not in str(e).lower():
                    raise e
            
            # Stream video
            if any(domain in url for domain in ['youtube.com', 'youtu.be', 'music.youtube.com']):
                await tgcaller.play(chat_id, url, video=True)
            else:
                await tgcaller.play(chat_id, url, video=True)
            
            return True
            
        except Exception as e:
            logger.error(f"Video stream error: {e}")
            return False
    
    async def pause_stream(self, chat_id: int) -> bool:
        """Pause active stream"""
        try:
            await tgcaller.pause(chat_id)
            return True
        except Exception as e:
            logger.error(f"Pause error: {e}")
            return False
    
    async def resume_stream(self, chat_id: int) -> bool:
        """Resume paused stream"""
        try:
            await tgcaller.resume(chat_id)
            return True
        except Exception as e:
            logger.error(f"Resume error: {e}")
            return False
    
    async def stop_stream(self, chat_id: int) -> bool:
        """Stop active stream"""
        try:
            await tgcaller.stop(chat_id)
            await tgcaller.leave(chat_id)
            
            if chat_id in self.active_streams:
                del self.active_streams[chat_id]
            
            return True
        except Exception as e:
            logger.error(f"Stop error: {e}")
            return False
    
    def get_stream_info(self, chat_id: int) -> Optional[Dict]:
        """Get current stream info"""
        return self.active_streams.get(chat_id)
    
    def is_streaming(self, chat_id: int) -> bool:
        """Check if streaming in chat"""
        return chat_id in self.active_streams

# Global stream manager
stream_manager = StreamManager()