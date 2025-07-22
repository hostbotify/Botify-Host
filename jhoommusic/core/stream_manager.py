import asyncio
import logging
import subprocess
from typing import Dict, Optional, Any
from .bot import tgcaller, app
from .media_extractor import universal_extractor

logger = logging.getLogger(__name__)

class StreamManager:
    """Advanced stream manager with TgCaller integration"""
    
    def __init__(self):
        self.active_streams: Dict[int, Dict] = {}
        self.ffmpeg_processes: Dict[int, subprocess.Popen] = {}
        self.stream_lock = asyncio.Lock()
    
    async def start_stream(self, chat_id: int, source: str, **options) -> bool:
        """Start streaming with TgCaller"""
        async with self.stream_lock:
            try:
                logger.info(f"🎵 Starting stream in chat {chat_id}: {source}")
                
                # Extract media info
                media_info = await universal_extractor.extract(source, **options)
                if not media_info:
                    logger.error(f"❌ Failed to extract media info for: {source}")
                    return False
                
                # Handle playlist
                if isinstance(media_info, list):
                    if not media_info:
                        return False
                    media_info = media_info[0]  # Use first track
                
                # Get stream URL
                stream_url = media_info.get('url')
                if not stream_url:
                    logger.error("❌ No stream URL found")
                    return False
                
                # Determine stream type
                is_video = media_info.get('is_video', False) or options.get('video', False)
                
                logger.info(f"🔗 Stream URL: {stream_url[:100]}...")
                logger.info(f"📺 Video mode: {is_video}")
                
                # Join voice chat first
                try:
                    await tgcaller.join_group_call(chat_id)
                    logger.info(f"✅ Joined voice chat: {chat_id}")
                except Exception as e:
                    if "already joined" not in str(e).lower():
                        logger.error(f"❌ Failed to join voice chat: {e}")
                        return False
                    logger.info(f"ℹ️ Already in voice chat: {chat_id}")
                
                # Start streaming with proper format
                success = await self._start_stream_with_format(chat_id, stream_url, media_info, is_video)
                
                if success:
                    self.active_streams[chat_id] = {
                        'info': media_info,
                        'type': 'video' if is_video else 'audio',
                        'url': stream_url,
                        'source': source
                    }
                    logger.info(f"✅ Stream started successfully: {media_info['title']}")
                else:
                    logger.error(f"❌ Failed to start stream")
                
                return success
                
            except Exception as e:
                logger.error(f"❌ Stream start error: {e}")
                return False
    
    async def _start_stream_with_format(self, chat_id: int, url: str, info: Dict, is_video: bool) -> bool:
        """Start stream with proper format handling"""
        try:
            if is_video:
                # Video streaming
                return await self._start_video_stream(chat_id, url, info)
            else:
                # Audio streaming
                return await self._start_audio_stream(chat_id, url, info)
                
        except Exception as e:
            logger.error(f"❌ Format stream error: {e}")
            return False
    
    async def _start_audio_stream(self, chat_id: int, url: str, info: Dict) -> bool:
        """Start audio stream using TgCaller with FFmpeg pipe"""
        try:
            logger.info(f"🎵 Starting audio stream: {info.get('title', 'Unknown')}")
            
            # FFmpeg command for audio processing
            ffmpeg_cmd = [
                'ffmpeg',
                '-i', url,
                '-f', 's16le',
                '-ac', '2',
                '-ar', '48000',
                '-acodec', 'pcm_s16le',
                '-loglevel', 'error',
                '-'
            ]
            
            logger.info(f"🔧 FFmpeg command: {' '.join(ffmpeg_cmd[:4])}...")
            
            # Start ffmpeg process
            process = await asyncio.create_subprocess_exec(
                *ffmpeg_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.ffmpeg_processes[chat_id] = process
            
            # Stream to TgCaller using the stdout pipe
            await tgcaller.play(chat_id, process.stdout)
            logger.info(f"✅ Audio stream started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Audio stream error: {e}")
            # Try direct URL as fallback
            try:
                logger.info(f"🔄 Trying direct URL fallback...")
                await tgcaller.play(chat_id, url)
                logger.info(f"✅ Direct URL fallback successful")
                return True
            except Exception as e2:
                logger.error(f"❌ Direct URL fallback failed: {e2}")
                return False
    
    async def _start_video_stream(self, chat_id: int, url: str, info: Dict) -> bool:
        """Start video stream using TgCaller with FFmpeg pipe"""
        try:
            logger.info(f"📺 Starting video stream: {info.get('title', 'Unknown')}")
            
            # FFmpeg command for video processing
            ffmpeg_cmd = [
                'ffmpeg',
                '-i', url,
                '-f', 'rawvideo',
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=640:480',
                '-r', '30',
                '-loglevel', 'error',
                '-'
            ]
            
            logger.info(f"🔧 FFmpeg video command: {' '.join(ffmpeg_cmd[:4])}...")
            
            # Start ffmpeg process
            process = await asyncio.create_subprocess_exec(
                *ffmpeg_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.ffmpeg_processes[chat_id] = process
            
            # Stream to TgCaller using the stdout pipe
            await tgcaller.play(chat_id, process.stdout, video=True)
            logger.info(f"✅ Video stream started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Video stream error: {e}")
            # Try direct URL as fallback
            try:
                logger.info(f"🔄 Trying direct video URL fallback...")
                await tgcaller.play(chat_id, url, video=True)
                logger.info(f"✅ Direct video URL fallback successful")
                return True
            except Exception as e2:
                logger.error(f"❌ Direct video URL fallback failed: {e2}")
                return False
    
    async def pause_stream(self, chat_id: int) -> bool:
        """Pause active stream"""
        try:
            await tgcaller.pause(chat_id)
            logger.info(f"⏸️ Stream paused: {chat_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Pause error: {e}")
            return False
    
    async def resume_stream(self, chat_id: int) -> bool:
        """Resume paused stream"""
        try:
            await tgcaller.resume(chat_id)
            logger.info(f"▶️ Stream resumed: {chat_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Resume error: {e}")
            return False
    
    async def stop_stream(self, chat_id: int) -> bool:
        """Stop active stream"""
        try:
            # Stop TgCaller stream
            await tgcaller.stop(chat_id)
            
            # Kill ffmpeg process if exists
            if chat_id in self.ffmpeg_processes:
                process = self.ffmpeg_processes[chat_id]
                if process and process.returncode is None:
                    process.terminate()
                    try:
                        await asyncio.wait_for(process.wait(), timeout=5.0)
                    except asyncio.TimeoutError:
                        process.kill()
                del self.ffmpeg_processes[chat_id]
            
            # Leave voice chat
            try:
                await tgcaller.leave_group_call(chat_id)
            except Exception as e:
                logger.warning(f"⚠️ Leave call error (may be normal): {e}")
            
            # Clean up stream info
            if chat_id in self.active_streams:
                del self.active_streams[chat_id]
            
            logger.info(f"⏹️ Stream stopped: {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Stop error: {e}")
            return False
    
    async def join_call(self, chat_id: int) -> bool:
        """Join voice chat"""
        try:
            await tgcaller.join_group_call(chat_id)
            logger.info(f"✅ Joined call: {chat_id}")
            return True
        except Exception as e:
            if "already joined" in str(e).lower():
                logger.info(f"ℹ️ Already in call: {chat_id}")
                return True
            logger.error(f"❌ Join call error: {e}")
            return False
    
    async def leave_call(self, chat_id: int) -> bool:
        """Leave voice chat"""
        try:
            await tgcaller.leave_group_call(chat_id)
            logger.info(f"👋 Left call: {chat_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Leave call error: {e}")
            return False
    
    def get_stream_info(self, chat_id: int) -> Optional[Dict]:
        """Get current stream info"""
        return self.active_streams.get(chat_id)
    
    def is_streaming(self, chat_id: int) -> bool:
        """Check if streaming in chat"""
        return chat_id in self.active_streams
    
    async def cleanup_all(self):
        """Cleanup all streams"""
        logger.info("🧹 Cleaning up all streams...")
        for chat_id in list(self.active_streams.keys()):
            await self.stop_stream(chat_id)
        logger.info("✅ All streams cleaned up")

# Global stream manager
stream_manager = StreamManager()