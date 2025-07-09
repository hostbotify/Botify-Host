import asyncio
import logging
from typing import Dict, List, Optional, Union
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from .config import Config
from .process import process_manager

logger = logging.getLogger(__name__)

# Initialize Spotify client
spotify = None
if Config.SPOTIFY_CLIENT_ID and Config.SPOTIFY_CLIENT_SECRET:
    spotify = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET
        )
    )

class MediaExtractor:
    """Extract media information from various sources"""
    
    @staticmethod
    async def extract_youtube_info(query: str, audio_only: bool = True) -> Optional[Dict]:
        """Extract info from YouTube"""
        try:
            ydl_opts = {
                'format': 'bestaudio/best' if audio_only else 'best',
                'quiet': True,
                'extract_flat': False,
                'noplaylist': True,
                'socket_timeout': 10,
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash', 'hls']
                    }
                }
            }
            
            executor = await process_manager.get_executor()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: ydl.extract_info(query, download=False)
                )
                
                if 'entries' in info:
                    info = info['entries'][0]
                
                return {
                    'title': info.get('title', 'Unknown Track'),
                    'duration': info.get('duration', 0),
                    'url': info['url'],
                    'thumbnail': info.get('thumbnail'),
                    'artist': info.get('uploader', 'Unknown Artist'),
                    'source': 'youtube',
                    'is_video': not audio_only,
                    'views': info.get('view_count', 0)
                }
        except Exception as e:
            logger.error(f"YouTube extraction error: {e}")
            return None
    
    @staticmethod
    async def extract_spotify_info(url: str) -> Optional[Union[Dict, List[Dict]]]:
        """Extract info from Spotify"""
        if not spotify:
            return None
        
        try:
            executor = await process_manager.get_executor()
            
            if 'track' in url:
                track = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: spotify.track(url)
                )
                
                # Search for YouTube equivalent
                search_query = f"{track['name']} {track['artists'][0]['name']}"
                youtube_info = await MediaExtractor.extract_youtube_info(f"ytsearch:{search_query}")
                
                if not youtube_info:
                    return None
                
                return {
                    'title': track['name'],
                    'duration': track['duration_ms'] // 1000,
                    'url': youtube_info['url'],
                    'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'artist': track['artists'][0]['name'],
                    'source': 'spotify',
                    'album': track['album']['name']
                }
            
            elif 'playlist' in url:
                results = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: spotify.playlist_tracks(url)
                )
                
                tracks = []
                for item in results['items'][:Config.MAX_PLAYLIST_SIZE]:
                    track = item['track']
                    search_query = f"{track['name']} {track['artists'][0]['name']}"
                    youtube_info = await MediaExtractor.extract_youtube_info(f"ytsearch:{search_query}")
                    
                    if youtube_info:
                        tracks.append({
                            'title': track['name'],
                            'duration': track['duration_ms'] // 1000,
                            'url': youtube_info['url'],
                            'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else None,
                            'artist': track['artists'][0]['name'],
                            'source': 'spotify',
                            'album': track['album']['name']
                        })
                
                return tracks if tracks else None
                
        except Exception as e:
            logger.error(f"Spotify extraction error: {e}")
            return None
    
    @staticmethod
    async def extract_radio_info(url: str) -> Optional[Dict]:
        """Extract info from radio streams"""
        try:
            return {
                'title': "Live Radio Stream",
                'duration': 0,
                'url': url,
                'thumbnail': "https://i.imgur.com/radio.png",
                'artist': "Live Radio",
                'source': 'radio',
                'is_live': True
            }
        except Exception as e:
            logger.error(f"Radio extraction error: {e}")
            return None
    
    @staticmethod
    async def extract_info(query: str, audio_only: bool = True) -> Optional[Union[Dict, List[Dict]]]:
        """Extract media info from various sources"""
        try:
            # Determine source type
            if 'spotify.com' in query:
                return await MediaExtractor.extract_spotify_info(query)
            elif any(x in query.lower() for x in ['radio', '.pls', '.m3u', 'stream']):
                return await MediaExtractor.extract_radio_info(query)
            else:
                # Default to YouTube
                if not query.startswith('http'):
                    query = f"ytsearch:{query}"
                return await MediaExtractor.extract_youtube_info(query, audio_only)
        except Exception as e:
            logger.error(f"Media extraction error: {e}")
            return None

# Global media extractor instance
media_extractor = MediaExtractor()