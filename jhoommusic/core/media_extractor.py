import asyncio
import logging
import re
import json
from typing import Dict, List, Optional, Union, Any
from urllib.parse import urlparse, parse_qs
import yt_dlp
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class UniversalMediaExtractor:
    """Advanced media extractor with async support"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Optimized yt-dlp options for TgCaller
        self.base_ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'socket_timeout': 30,
            'http_headers': self.session.headers,
            'format': 'best[height<=720]/best',
            'noplaylist': True,
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_client': ['android', 'web']
                }
            }
        }
    
    async def extract(self, query: str, **kwargs) -> Optional[Union[Dict, List[Dict]]]:
        """Main extraction method with async support"""
        try:
            logger.info(f"🔍 MEDIA EXTRACTOR: Starting extraction for: {query}")
            
            # Detect if it's a URL or search query
            if self._is_url(query):
                logger.info(f"🔍 MEDIA EXTRACTOR: Detected URL")
                result = await self._extract_from_url(query, **kwargs)
            else:
                logger.info(f"🔍 MEDIA EXTRACTOR: Detected search query")
                result = await self._search_and_extract(query, **kwargs)
            
            if result:
                if isinstance(result, list):
                    logger.info(f"✅ MEDIA EXTRACTOR: Extracted {len(result)} items")
                else:
                    logger.info(f"✅ MEDIA EXTRACTOR: Extracted: {result.get('title', 'Unknown')}")
                    logger.info(f"✅ MEDIA EXTRACTOR: URL: {result.get('url', 'No URL')[:100]}...")
            else:
                logger.error(f"❌ MEDIA EXTRACTOR: No results for: {query}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ MEDIA EXTRACTOR: Extraction failed for {query}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _is_url(self, text: str) -> bool:
        """Check if text is a URL"""
        return bool(re.match(r'https?://', text))
    
    async def _extract_from_url(self, url: str, **kwargs) -> Optional[Union[Dict, List[Dict]]]:
        """Extract from URL"""
        platform = self._detect_platform(url)
        logger.info(f"🌐 Detected platform: {platform}")
        
        if platform == 'spotify':
            return await self._extract_spotify(url, **kwargs)
        else:
            return await self._extract_with_ytdlp(url, **kwargs)
    
    async def _search_and_extract(self, query: str, **kwargs) -> Optional[Dict]:
        """Search YouTube and extract first result"""
        try:
            search_query = f"ytsearch1:{query}"
            result = await self._extract_with_ytdlp(search_query, **kwargs)
            
            if isinstance(result, list) and result:
                return result[0]
            return result
            
        except Exception as e:
            logger.error(f"❌ Search extraction error: {e}")
            return None
    
    async def _extract_with_ytdlp(self, url: str, **kwargs) -> Optional[Union[Dict, List[Dict]]]:
        """Extract using yt-dlp with async support"""
        audio_only = kwargs.get('audio_only', True)
        
        logger.info(f"🔍 YT-DLP: Starting extraction for: {url[:100]}...")
        logger.info(f"🔍 YT-DLP: Audio only: {audio_only}")
        
        ydl_opts = self.base_ydl_opts.copy()
        ydl_opts.update({
            'format': self._get_format_selector(audio_only),
            'noplaylist': not kwargs.get('playlist', False)
        })
        
        try:
            loop = asyncio.get_event_loop()
            logger.info(f"🔍 YT-DLP: Running extraction...")
            
            # Run yt-dlp in executor to avoid blocking
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(None, ydl.extract_info, url, False)
                logger.info(f"🔍 YT-DLP: Extraction completed successfully")
                
                if 'entries' in info:
                    logger.info(f"🔍 YT-DLP: Found playlist with {len(info['entries'])} entries")
                    # Playlist
                    tracks = []
                    max_items = kwargs.get('max_playlist', 50)
                    for entry in info['entries'][:max_items]:
                        if entry:
                            tracks.append(self._format_track_info(entry))
                    return tracks
                else:
                    logger.info(f"🔍 YT-DLP: Found single item: {info.get('title', 'Unknown')}")
                    # Single item
                    return self._format_track_info(info)
                    
        except Exception as e:
            logger.error(f"❌ YT-DLP: Extraction error: {e}")
            import traceback
            traceback.print_exc()
            return await self._fallback_extract(url, **kwargs)
    
    async def _fallback_extract(self, url: str, **kwargs) -> Optional[Dict]:
        """Fallback extraction with different options"""
        try:
            logger.info(f"🔄 Trying fallback extraction...")
            
            fallback_opts = self.base_ydl_opts.copy()
            fallback_opts.update({
                'format': 'best[height<=480]/worst',
                'noplaylist': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android_embedded', 'android_music'],
                        'skip': ['webpage']
                    }
                }
            })
            
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                info = await loop.run_in_executor(None, ydl.extract_info, url, False)
                return self._format_track_info(info)
                
        except Exception as e:
            logger.error(f"❌ Fallback extraction failed: {e}")
            return None
    
    def _get_format_selector(self, audio_only: bool) -> str:
        """Get format selector for yt-dlp optimized for TgCaller"""
        if audio_only:
            # Prefer formats that work well with TgCaller
            return 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio/best[height<=480]'
        else:
            # Video formats optimized for streaming
            return 'best[height<=720][ext=mp4]/best[height<=480][ext=mp4]/best[ext=mp4]/best'
    
    def _detect_platform(self, url: str) -> str:
        """Detect platform from URL"""
        domain = urlparse(url).netloc.lower()
        
        platform_patterns = {
            'youtube': ['youtube.com', 'youtu.be', 'music.youtube.com'],
            'spotify': ['spotify.com', 'open.spotify.com'],
            'soundcloud': ['soundcloud.com'],
            'instagram': ['instagram.com', 'instagr.am'],
            'tiktok': ['tiktok.com', 'vm.tiktok.com'],
            'twitter': ['twitter.com', 'x.com', 't.co'],
            'facebook': ['facebook.com', 'fb.watch'],
            'vimeo': ['vimeo.com'],
            'dailymotion': ['dailymotion.com', 'dai.ly'],
            'twitch': ['twitch.tv', 'clips.twitch.tv']
        }
        
        for platform, domains in platform_patterns.items():
            if any(d in domain for d in domains):
                return platform
        
        return 'generic'
    
    async def _extract_spotify(self, url: str, **kwargs) -> Optional[Union[Dict, List[Dict]]]:
        """Extract Spotify (convert to YouTube search)"""
        try:
            logger.info(f"🎵 Converting Spotify to YouTube search...")
            
            # Extract Spotify metadata (simplified)
            track_info = await self._get_spotify_metadata(url)
            if not track_info:
                return None
            
            if isinstance(track_info, list):
                # Playlist
                results = []
                for track in track_info[:kwargs.get('max_playlist', 50)]:
                    search_query = f"{track['name']} {track['artist']}"
                    youtube_result = await self._search_and_extract(search_query)
                    if youtube_result:
                        youtube_result.update({
                            'original_title': track['name'],
                            'original_artist': track['artist'],
                            'source': 'spotify'
                        })
                        results.append(youtube_result)
                return results
            else:
                # Single track
                search_query = f"{track_info['name']} {track_info['artist']}"
                youtube_result = await self._search_and_extract(search_query)
                if youtube_result:
                    youtube_result.update({
                        'original_title': track_info['name'],
                        'original_artist': track_info['artist'],
                        'source': 'spotify'
                    })
                return youtube_result
                
        except Exception as e:
            logger.error(f"❌ Spotify extraction error: {e}")
            return None
    
    async def _get_spotify_metadata(self, url: str) -> Optional[Union[Dict, List[Dict]]]:
        """Get Spotify metadata (placeholder implementation)"""
        # This is a simplified implementation
        # In production, you'd use Spotify Web API or web scraping
        return {
            'name': 'Unknown Track',
            'artist': 'Unknown Artist'
        }
    
    def _format_track_info(self, info: Dict) -> Dict:
        """Format track information consistently"""
        # Get the best quality URL
        url = info.get('url', '')
        
        # For YouTube, prefer direct stream URLs
        if 'formats' in info:
            formats = info['formats']
            # Try to find the best audio format
            audio_formats = [f for f in formats if f.get('acodec') != 'none']
            if audio_formats:
                # Sort by quality and prefer m4a/webm
                audio_formats.sort(key=lambda x: (
                    x.get('abr', 0),
                    1 if x.get('ext') in ['m4a', 'webm'] else 0
                ), reverse=True)
                url = audio_formats[0].get('url', url)
        
        return {
            'title': info.get('title', 'Unknown Track'),
            'artist': info.get('uploader', info.get('creator', 'Unknown Artist')),
            'duration': info.get('duration', 0),
            'url': url,
            'thumbnail': info.get('thumbnail'),
            'source': 'youtube',
            'is_video': info.get('vcodec') != 'none',
            'quality': info.get('format_note', 'Unknown'),
            'views': info.get('view_count', 0),
            'upload_date': info.get('upload_date'),
            'description': info.get('description', ''),
            'webpage_url': info.get('webpage_url', ''),
            'extractor': info.get('extractor', 'youtube')
        }

# Global extractor instance
universal_extractor = UniversalMediaExtractor()