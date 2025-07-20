import logging
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ...core.bot import app
from ...core.stream_manager import stream_manager
from ...core.media_extractor import universal_extractor
from ...constants.images import UI_IMAGES
from ...utils.helpers import is_admin_or_sudo, save_user_to_db, save_chat_to_db

logger = logging.getLogger(__name__)

@app.on_message(filters.command(["uplay", "universal"]) & filters.group)
async def universal_play(_, message: Message):
    """Universal play command for any media source"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        if len(message.command) < 2:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="**Usage:** `/uplay [URL or search query]`\n\n"
                "**Supported:**\n"
                "• YouTube (videos/music)\n"
                "• Spotify (converts to YouTube)\n"
                "• SoundCloud\n"
                "• Instagram\n"
                "• TikTok\n"
                "• Twitter\n"
                "• Facebook\n"
                "• Direct media URLs\n"
                "• Any yt-dlp supported site"
            )
            return
        
        chat_id = message.chat.id
        query = " ".join(message.command[1:])
        
        # Show processing message
        processing_msg = await message.reply_photo(
            photo=UI_IMAGES["player"],
            caption="🔍 **Processing media...**\n"
            f"**Source:** {query[:50]}{'...' if len(query) > 50 else ''}\n"
            "**Status:** Extracting media information..."
        )
        
        # Extract media info
        media_info = await universal_extractor.extract(query)
        
        if not media_info:
            await processing_msg.edit_caption(
                caption="❌ **Extraction Failed**\n"
                "Could not extract media from the provided source.\n"
                "Please check the URL or try a different source."
            )
            return
        
        # Handle playlist
        if isinstance(media_info, list):
            if not media_info:
                await processing_msg.edit_caption(
                    caption="❌ **Empty Playlist**\n"
                    "The playlist contains no playable tracks."
                )
                return
            
            # Show playlist options
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🎵 Audio Only", callback_data=f"uplay_audio_{chat_id}"),
                    InlineKeyboardButton("🎬 Video", callback_data=f"uplay_video_{chat_id}")
                ],
                [
                    InlineKeyboardButton("📋 Show Playlist", callback_data=f"uplay_list_{chat_id}")
                ]
            ])
            
            await processing_msg.edit_caption(
                caption=f"📋 **Playlist Detected**\n"
                f"**Tracks:** {len(media_info)}\n"
                f"**First Track:** {media_info[0]['title']}\n"
                f"**Source:** {media_info[0]['source'].title()}\n\n"
                "Choose playback mode:",
                reply_markup=buttons
            )
            
            # Store playlist data temporarily
            app.playlist_cache = app.playlist_cache if hasattr(app, 'playlist_cache') else {}
            app.playlist_cache[chat_id] = media_info
            return
        
        # Single track - show options
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎵 Audio", callback_data=f"uplay_single_audio_{chat_id}"),
                InlineKeyboardButton("🎬 Video", callback_data=f"uplay_single_video_{chat_id}")
            ],
            [
                InlineKeyboardButton("ℹ️ Info", callback_data=f"uplay_info_{chat_id}")
            ]
        ])
        
        await processing_msg.edit_caption(
            caption=f"🎯 **Media Ready**\n"
            f"**Title:** {media_info['title']}\n"
            f"**Artist:** {media_info.get('artist', 'Unknown')}\n"
            f"**Source:** {media_info['source'].title()}\n"
            f"**Duration:** {_format_duration(media_info.get('duration', 0))}\n\n"
            "Choose playback mode:",
            reply_markup=buttons
        )
        
        # Store single track data
        app.track_cache = app.track_cache if hasattr(app, 'track_cache') else {}
        app.track_cache[chat_id] = media_info
        
        logger.info(f"Universal play used by {message.from_user.id} in {chat_id}: {query}")
        
    except Exception as e:
        logger.error(f"Error in universal play: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ **Error:** {str(e)}"
        )

@app.on_callback_query(filters.regex("^uplay_"))
async def handle_uplay_callbacks(_, query):
    """Handle universal play callbacks"""
    try:
        data_parts = query.data.split("_")
        action = data_parts[1]
        chat_id = int(data_parts[2]) if len(data_parts) > 2 else query.message.chat.id
        
        if action == "audio":
            # Play playlist as audio
            playlist = getattr(app, 'playlist_cache', {}).get(chat_id, [])
            if playlist:
                await query.answer("🎵 Starting audio playback...")
                success = await stream_manager.start_stream(chat_id, playlist[0]['url'], video=False)
                
                if success:
                    await query.message.edit_caption(
                        caption=f"🎵 **Now Playing (Audio)**\n"
                        f"**Title:** {playlist[0]['title']}\n"
                        f"**Artist:** {playlist[0].get('artist', 'Unknown')}\n"
                        f"**Playlist:** {len(playlist)} tracks"
                    )
                else:
                    await query.answer("❌ Failed to start playback", show_alert=True)
        
        elif action == "video":
            # Play playlist as video
            playlist = getattr(app, 'playlist_cache', {}).get(chat_id, [])
            if playlist:
                await query.answer("🎬 Starting video playback...")
                success = await stream_manager.start_stream(chat_id, playlist[0]['url'], video=True)
                
                if success:
                    await query.message.edit_caption(
                        caption=f"🎬 **Now Playing (Video)**\n"
                        f"**Title:** {playlist[0]['title']}\n"
                        f"**Artist:** {playlist[0].get('artist', 'Unknown')}\n"
                        f"**Playlist:** {len(playlist)} tracks"
                    )
                else:
                    await query.answer("❌ Failed to start playback", show_alert=True)
        
        elif action == "single":
            # Play single track
            mode = data_parts[2]  # audio or video
            track = getattr(app, 'track_cache', {}).get(chat_id)
            
            if track:
                is_video = mode == "video"
                await query.answer(f"{'🎬' if is_video else '🎵'} Starting playback...")
                
                success = await stream_manager.start_stream(chat_id, track['url'], video=is_video)
                
                if success:
                    await query.message.edit_caption(
                        caption=f"{'🎬' if is_video else '🎵'} **Now Playing**\n"
                        f"**Title:** {track['title']}\n"
                        f"**Artist:** {track.get('artist', 'Unknown')}\n"
                        f"**Source:** {track['source'].title()}\n"
                        f"**Mode:** {'Video' if is_video else 'Audio'}"
                    )
                else:
                    await query.answer("❌ Failed to start playback", show_alert=True)
        
        elif action == "info":
            # Show detailed info
            track = getattr(app, 'track_cache', {}).get(chat_id)
            if track:
                info_text = f"ℹ️ **Media Information**\n\n"
                info_text += f"**Title:** {track['title']}\n"
                info_text += f"**Artist:** {track.get('artist', 'Unknown')}\n"
                info_text += f"**Duration:** {_format_duration(track.get('duration', 0))}\n"
                info_text += f"**Source:** {track['source'].title()}\n"
                info_text += f"**Quality:** {track.get('quality', 'Unknown')}\n"
                info_text += f"**Views:** {track.get('views', 0):,}\n" if track.get('views') else ""
                info_text += f"**Upload Date:** {track.get('upload_date', 'Unknown')}\n"
                
                await query.answer(info_text, show_alert=True)
        
        elif action == "list":
            # Show playlist
            playlist = getattr(app, 'playlist_cache', {}).get(chat_id, [])
            if playlist:
                list_text = f"📋 **Playlist ({len(playlist)} tracks)**\n\n"
                for i, track in enumerate(playlist[:10], 1):
                    list_text += f"{i}. {track['title']}\n"
                
                if len(playlist) > 10:
                    list_text += f"\n... and {len(playlist) - 10} more tracks"
                
                await query.answer(list_text, show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in uplay callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)

def _format_duration(seconds: int) -> str:
    """Format duration in seconds to readable format"""
    if seconds == 0:
        return "Live"
    
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"