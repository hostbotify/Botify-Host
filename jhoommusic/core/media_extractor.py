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
    """Advanced media extractor with bypass capabilities"""
    
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
        
        # Platform-specific extractors
        self.extractors = {
            'youtube': self._extract_youtube,
            'spotify': self._extract_spotify,
            'soundcloud': self._extract_soundcloud,
            'instagram': self._extract_instagram,
            'tiktok': self._extract_tiktok,
            'twitter': self._extract_twitter,
            'facebook': self._extract_facebook,
            'vimeo': self._extract_vimeo,
            'dailymotion': self._extract_dailymotion,
            'twitch': self._extract_twitch,
            'generic': self._extract_generic
        }
    
    async def extract(self, url: str, **kwargs) -> Optional[Union[Dict, List[Dict]]]:
        """Main extraction method with smart platform detection"""
        try:
            platform = self._detect_platform(url)
            extractor = self.extractors.get(platform, self.extractors['generic'])
            
            logger.info(f"Extracting from {platform}: {url}")
            result = await extractor(url, **kwargs)
            
            if result:
                logger.info(f"Successfully extracted: {result.get('title', 'Unknown') if isinstance(result, dict) else f'{len(result)} items'}")
            
            return result
            
        except Exception as e:
            logger.error(f"Extraction failed for {url}: {e}")
            return None
    
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
    
    async def _extract_youtube(self, url: str, **kwargs) -> Optional[Union[Dict, List[Dict]]]:
        """Enhanced YouTube extraction with advanced bypass"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': kwargs.get('format', 'bestaudio[ext=m4a]/bestaudio/best'),
            'noplaylist': not kwargs.get('playlist', False),
            'extract_flat': False,
            'age_limit': 99,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'] if kwargs.get('audio_only', True) else [],
                    'player_client': ['android', 'web', 'android_embedded'],
                    'player_skip': ['configs']
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate'
            }
        }
        
        # Add cookies if available
        if kwargs.get('cookies'):
            ydl_opts['cookiefile'] = kwargs['cookies']
        
        try:
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(None, ydl.extract_info, url, False)
                
                if 'entries' in info:
                    # Playlist
                    tracks = []
                    for entry in info['entries'][:kwargs.get('max_playlist', 50)]:
                        if entry:
                            tracks.append(self._format_track_info(entry, 'youtube'))
                    return tracks
                else:
                    # Single video
                    return self._format_track_info(info, 'youtube')
                    
        except Exception as e:
            logger.error(f"YouTube extraction error: {e}")
            return await self._fallback_youtube_extract(url, **kwargs)
    
    async def _fallback_youtube_extract(self, url: str, **kwargs) -> Optional[Dict]:
        """Fallback YouTube extraction using alternative methods"""
        try:
            # Try with different user agents and bypass methods
            fallback_opts = {
                'quiet': True,
                'format': 'worst[ext=mp4]/worst',  # Use worst quality as fallback
                'noplaylist': True,
                'age_limit': 99,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android_embedded', 'android_music', 'android_creator'],
                        'skip': ['webpage']
                    }
                }
            }
            
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                info = await loop.run_in_executor(None, ydl.extract_info, url, False)
                return self._format_track_info(info, 'youtube')
                
        except Exception as e:
            logger.error(f"Fallback YouTube extraction failed: {e}")
            return None
    
    async def _extract_spotify(self, url: str, **kwargs) -> Optional[Union[Dict, List[Dict]]]:
        """Spotify extraction (converts to YouTube search)"""
        try:
            # Extract Spotify metadata
            spotify_id = self._extract_spotify_id(url)
            if not spotify_id:
                return None
            
            # Use Spotify Web API or scraping to get track info
            track_info = await self._get_spotify_metadata(spotify_id, url)
            if not track_info:
                return None
            
            # Search on YouTube
            if isinstance(track_info, list):
                # Playlist
                results = []
                for track in track_info[:kwargs.get('max_playlist', 50)]:
                    search_query = f"{track['name']} {track['artist']}"
                    youtube_result = await self._search_youtube(search_query)
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
                youtube_result = await self._search_youtube(search_query)
                if youtube_result:
                    youtube_result.update({
                        'original_title': track_info['name'],
                        'original_artist': track_info['artist'],
                        'source': 'spotify'
                    })
                return youtube_result
                
        except Exception as e:
            logger.error(f"Spotify extraction error: {e}")
            return None
    
    async def _extract_generic(self, url: str, **kwargs) -> Optional[Dict]:
        """Generic extraction for unknown platforms"""
        ydl_opts = {
            'quiet': True,
            'format': 'best[ext=mp4]/best',
            'noplaylist': True,
            'age_limit': 99,
            'geo_bypass': True,
            'http_headers': self.session.headers
        }
        
        try:
            loop = asyncio.get_event_loop()
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await loop.run_in_executor(None, ydl.extract_info, url, False)
                return self._format_track_info(info, 'generic')
                
        except Exception as e:
            logger.error(f"Generic extraction error: {e}")
            return await self._direct_url_extract(url)
    
    async def _direct_url_extract(self, url: str) -> Optional[Dict]:
        """Direct URL extraction for media files"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.session.head, url
            )
            
            content_type = response.headers.get('content-type', '').lower()
            if any(media_type in content_type for media_type in ['audio', 'video']):
                return {
                    'title': url.split('/')[-1],
                    'url': url,
                    'duration': 0,
                    'source': 'direct',
                    'is_video': 'video' in content_type
                }
        except Exception as e:
            logger.error(f"Direct URL extraction error: {e}")
        
        return None
    
    def _format_track_info(self, info: Dict, source: str) -> Dict:
        """Format track information consistently"""
        return {
            'title': info.get('title', 'Unknown Track'),
            'artist': info.get('uploader', info.get('creator', 'Unknown Artist')),
            'duration': info.get('duration', 0),
            'url': info.get('url', ''),
            'thumbnail': info.get('thumbnail'),
            'source': source,
            'is_video': info.get('vcodec') != 'none',
            'quality': info.get('format_note', 'Unknown'),
            'views': info.get('view_count', 0),
            'upload_date': info.get('upload_date'),
            'description': info.get('description', ''),
            'webpage_url': info.get('webpage_url', ''),
            'extractor': info.get('extractor', source)
        }
    
    async def _search_youtube(self, query: str) -> Optional[Dict]:
        """Search YouTube and return first result"""
        try:
            search_url = f"ytsearch1:{query}"
            result = await self._extract_youtube(search_url, audio_only=True)
            if isinstance(result, list) and result:
                return result[0]
            return result
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
            return None
    
    def _extract_spotify_id(self, url: str) -> Optional[str]:
        """Extract Spotify ID from URL"""
        patterns = [
            r'spotify\.com/track/([a-zA-Z0-9]+)',
            r'spotify\.com/playlist/([a-zA-Z0-9]+)',
            r'spotify\.com/album/([a-zA-Z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    async def _get_spotify_metadata(self, spotify_id: str, url: str) -> Optional[Union[Dict, List[Dict]]]:
        """Get Spotify metadata (placeholder - implement with Spotify API or scraping)"""
        # This would typically use Spotify Web API or web scraping
        # For now, return a basic structure
        return {
            'name': 'Unknown Track',
            'artist': 'Unknown Artist'
        }
    
    # Placeholder methods for other platforms
    async def _extract_soundcloud(self, url: str, **kwargs) -> Optional[Dict]:
        return await self._extract_generic(url, **kwargs)
    
    async def _extract_instagram(self, url: str, **kwargs) -> Optional[Dict]:
        return await self._extract_generic(url, **kwargs)
    
    async def _extract_tiktok(self, url: str, **kwargs) -> Optional[Dict]:
        return await self._extract_generic(url, **kwargs)
    
    async def _extract_twitter(self, url: str, **kwargs) -> Optional[Dict]:
        return await self._extract_generic(url, **kwargs)
    
    async def _extract_facebook(self, url: str, **kwargs) -> Optional[Dict]:
        return await self._extract_generic(url, **kwargs)
    
    async def _extract_vimeo(self, url: str, **kwargs) -> Optional[Dict]:
        return await self._extract_generic(url, **kwargs)
    
    async def _extract_dailymotion(self, url: str, **kwargs) -> Optional[Dict]:
        return await self._extract_generic(url, **kwargs)
    
    async def _extract_twitch(self, url: str, **kwargs) -> Optional[Dict]:
        return await self._extract_generic(url, **kwargs)

# Global extractor instance
universal_extractor = UniversalMediaExtractor()