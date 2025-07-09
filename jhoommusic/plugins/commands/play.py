import logging
from pyrogram import filters
from pyrogram.types import Message
from ...core.bot import app
from ...core.media import media_extractor
from ...core.playback import playback_manager
from ...core.queue import queue_manager
from ...core.thumbnail import generate_thumbnail
from ...constants.images import UI_IMAGES
from ...utils.helpers import is_user_gbanned, check_user_auth, save_user_to_db, save_chat_to_db

logger = logging.getLogger(__name__)

@app.on_message(filters.command(["play", "p"]) & filters.group)
async def play_music(_, message: Message):
    """Handle /play command"""
    try:
        # Save user and chat to database
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        # Check if user is banned
        if await is_user_gbanned(message.from_user.id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="🚫 You are banned from using this bot."
            )
            return
        
        # Check if user is authorized
        if not await check_user_auth(message.from_user.id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="🔒 You need to be authorized to use this command."
            )
            return
        
        # Check if query is provided
        if len(message.command) < 2 and not message.reply_to_message:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="**Usage:** `/play [song name or URL]` or reply to an audio file"
            )
            return
        
        chat_id = message.chat.id
        
        # Handle replied audio/video files
        if message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.video):
            file = message.reply_to_message.audio or message.reply_to_message.video
            file_path = await app.download_media(file)
            
            track = {
                'title': file.title or file.file_name or "Telegram Media",
                'artist': 'Telegram Media',
                'duration': file.duration or 0,
                'url': file_path,
                'source': 'telegram',
                'is_video': bool(message.reply_to_message.video),
                'user_id': message.from_user.id,
                'thumbnail': None
            }
        else:
            # Extract query from command
            query = " ".join(message.command[1:])
            
            # Extract media info
            track_info = await media_extractor.extract_info(query)
            if not track_info:
                await message.reply_photo(
                    photo=UI_IMAGES["error"],
                    caption="❌ Could not find the requested track"
                )
                return
            
            # Handle playlist
            if isinstance(track_info, list):
                if not track_info:
                    await message.reply_photo(
                        photo=UI_IMAGES["error"],
                        caption="❌ No tracks found in playlist"
                    )
                    return
                
                # Add user_id to all tracks
                for track in track_info:
                    track['user_id'] = message.from_user.id
                
                # Play first track or add to queue
                if playback_manager.is_playing(chat_id):
                    for track in track_info:
                        await queue_manager.add_to_queue(chat_id, track)
                    
                    await message.reply_photo(
                        photo=UI_IMAGES["success"],
                        caption=f"🎧 Added {len(track_info)} tracks to queue"
                    )
                else:
                    # Play first track
                    await playback_manager.play_track(chat_id, track_info[0])
                    
                    # Add remaining tracks to queue
                    for track in track_info[1:]:
                        await queue_manager.add_to_queue(chat_id, track)
                    
                    await message.reply_photo(
                        photo=UI_IMAGES["success"],
                        caption=f"▶️ Now Playing: {track_info[0]['title']}\n🎧 Added {len(track_info)-1} more tracks to queue"
                    )
                return
            
            # Single track
            track = track_info
            track['user_id'] = message.from_user.id
        
        # Generate thumbnail
        thumb = await generate_thumbnail(
            title=track['title'],
            artist=track.get('artist', 'Unknown Artist'),
            duration=track.get('duration', 0),
            cover_url=track.get('thumbnail'),
            requester_id=message.from_user.id
        )
        
        # Play or add to queue
        if playback_manager.is_playing(chat_id):
            await queue_manager.add_to_queue(chat_id, track)
            await message.reply_photo(
                photo=thumb,
                caption=f"🎧 **Added to queue**\n\n**Title:** {track['title']}\n**Artist:** {track.get('artist', 'Unknown')}"
            )
        else:
            await playback_manager.play_track(chat_id, track)
            await message.reply_photo(
                photo=thumb,
                caption=f"▶️ **Now Playing**\n\n**Title:** {track['title']}\n**Artist:** {track.get('artist', 'Unknown')}"
            )
        
        logger.info(f"Play command used by {message.from_user.id} in {chat_id}: {track['title']}")
        
    except Exception as e:
        logger.error(f"Error in play command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command(["vplay", "vp"]) & filters.group)
async def video_play(_, message: Message):
    """Handle /vplay command for video playback"""
    try:
        # Save user and chat to database
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        # Check if user is banned
        if await is_user_gbanned(message.from_user.id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="🚫 You are banned from using this bot."
            )
            return
        
        # Check if user is authorized
        if not await check_user_auth(message.from_user.id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="🔒 You need to be authorized to use this command."
            )
            return
        
        # Check if query is provided
        if len(message.command) < 2:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="**Usage:** `/vplay [video name or URL]`"
            )
            return
        
        query = " ".join(message.command[1:])
        chat_id = message.chat.id
        
        # Extract video info
        video_info = await media_extractor.extract_info(query, audio_only=False)
        if not video_info:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Could not find the requested video"
            )
            return
        
        video_info['is_video'] = True
        video_info['user_id'] = message.from_user.id
        
        # Generate thumbnail
        thumb = await generate_thumbnail(
            title=video_info['title'],
            artist=video_info.get('artist', 'Unknown Artist'),
            duration=video_info.get('duration', 0),
            cover_url=video_info.get('thumbnail'),
            requester_id=message.from_user.id
        )
        
        # Play or add to queue
        if playback_manager.is_playing(chat_id):
            await queue_manager.add_to_queue(chat_id, video_info)
            await message.reply_photo(
                photo=thumb,
                caption=f"🎬 **Added to queue**\n\n**Title:** {video_info['title']}\n**Artist:** {video_info.get('artist', 'Unknown')}"
            )
        else:
            await playback_manager.play_track(chat_id, video_info)
            await message.reply_photo(
                photo=thumb,
                caption=f"🎬 **Now Playing**\n\n**Title:** {video_info['title']}\n**Artist:** {video_info.get('artist', 'Unknown')}"
            )
        
        logger.info(f"VPlay command used by {message.from_user.id} in {chat_id}: {video_info['title']}")
        
    except Exception as e:
        logger.error(f"Error in vplay command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )