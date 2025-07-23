import logging
from pyrogram import filters
from pyrogram.types import Message
from ..core.bot import app
from ..core.stream_manager import stream_manager
from ..utils.helpers import save_user_to_db, save_chat_to_db

logger = logging.getLogger(__name__)

@app.on_message(filters.command(["play", "p"]) & filters.group)
async def play_music(_, message: Message):
    """Handle /play command"""
    try:
        logger.info(f"🎵 PLAY COMMAND from {message.from_user.id} in {message.chat.id}")
        
        # Save user and chat to database
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        # Check if query is provided
        if len(message.command) < 2 and not message.reply_to_message:
            await message.reply_text("**Usage:** `/play [song name or URL]` or reply to an audio file")
            return
        
        chat_id = message.chat.id
        logger.info(f"🔍 Processing play request for chat {chat_id}")
        
        # Handle replied audio/video files
        if message.reply_to_message and (message.reply_to_message.audio or message.reply_to_message.video):
            file = message.reply_to_message.audio or message.reply_to_message.video
            
            processing_msg = await message.reply_text("🔄 **Processing file...**")
            
            try:
                file_path = await app.download_media(file)
                logger.info(f"📁 Downloaded file: {file_path}")
                
                success = await stream_manager.start_stream(
                    chat_id, 
                    file_path,
                    audio_only=not bool(message.reply_to_message.video)
                )
                
                if success:
                    await processing_msg.edit_text(
                        f"▶️ **Now Playing**\n\n"
                        f"**Title:** {file.title or file.file_name or 'Telegram Media'}\n"
                        f"**Type:** {'Video' if message.reply_to_message.video else 'Audio'}\n"
                        f"**Requested by:** {message.from_user.mention}"
                    )
                else:
                    await processing_msg.edit_text("❌ Failed to start playback. Check if bot has proper permissions.")
                
            except Exception as e:
                logger.error(f"❌ File processing error: {e}")
                import traceback
                traceback.print_exc()
                await processing_msg.edit_text(f"❌ Error processing file: {str(e)}")
            
            return
        
        # Extract query from command
        query = " ".join(message.command[1:])
        logger.info(f"🔍 SEARCH QUERY: {query}")
        
        # Send processing message
        processing_msg = await message.reply_text("🔄 **Searching and processing...**")
        
        try:
            logger.info(f"🎵 Starting stream for: {query}")
            
            success = await stream_manager.start_stream(
                chat_id, 
                query,
                audio_only=True
            )
            
            logger.info(f"🎵 Stream start result: {success}")
            
            if success:
                stream_info = stream_manager.get_stream_info(chat_id)
                if stream_info:
                    info = stream_info['info']
                    await processing_msg.edit_text(
                        f"▶️ **Now Playing**\n\n"
                        f"**Title:** {info.get('title', 'Unknown')}\n"
                        f"**Artist:** {info.get('artist', 'Unknown')}\n"
                        f"**Duration:** {info.get('duration', 0)} seconds\n"
                        f"**Source:** {info.get('source', 'Unknown').title()}\n"
                        f"**Requested by:** {message.from_user.mention}\n\n"
                        f"**Controls:** Use /pause, /resume, /stop, /player"
                    )
                else:
                    await processing_msg.edit_text("▶️ **Playback started!**\n\nUse /player for controls.")
            else:
                await processing_msg.edit_text(
                    "❌ **Failed to start playback**\n\n"
                    "**Possible issues:**\n"
                    "• Bot needs admin rights in the group\n"
                    "• Voice chat must be active\n"
                    "• Check if the song/URL is valid\n\n"
                    "Try: /join first, then /play again"
                )
        
        except Exception as e:
            logger.error(f"❌ Play command error: {e}")
            import traceback
            traceback.print_exc()
            await processing_msg.edit_text(
                f"❌ **Error occurred**\n\n"
                f"**Details:** {str(e)[:200]}\n\n"
                f"**Try:**\n"
                f"• /join to connect to voice chat\n"
                f"• Check bot permissions\n"
                f"• Use a different song/URL"
            )
        
        logger.info(f"✅ PLAY COMMAND completed for {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Critical error in play command: {e}")
        import traceback
        traceback.print_exc()
        await message.reply_text(f"❌ Critical error: {str(e)}")

@app.on_message(filters.command(["testplay"]) & filters.group)
async def test_play_music(_, message: Message):
    """Handle /testplay command - simplified version for testing"""
    try:
        logger.info(f"🧪 TESTPLAY COMMAND from {message.from_user.id} in {message.chat.id}")
        
        if len(message.command) < 2:
            await message.reply_text("**Usage:** `/testplay [song name or URL]`")
            return
        
        query = " ".join(message.command[1:])
        chat_id = message.chat.id
        
        logger.info(f"🔍 TEST SEARCH QUERY: {query}")
        
        processing_msg = await message.reply_text("🔄 **Testing playback...**")
        
        try:
            logger.info(f"🧪 Starting test stream for: {query}")
            
            success = await stream_manager.start_stream(
                chat_id, 
                query,
                audio_only=True
            )
            
            logger.info(f"🧪 Test stream result: {success}")
            
            if success:
                await processing_msg.edit_text(
                    f"✅ **Test Playback Started!**\n\n"
                    f"**Query:** {query}\n"
                    f"**Chat:** {chat_id}\n"
                    f"**User:** {message.from_user.mention}\n\n"
                    f"Use /pause, /resume, /stop for controls"
                )
            else:
                await processing_msg.edit_text(
                    "❌ **Test playback failed**\n\n"
                    "Check:\n"
                    "• Bot has admin rights\n"
                    "• Voice chat is active\n"
                    "• Try /join first"
                )
        
        except Exception as e:
            logger.error(f"❌ Test play error: {e}")
            import traceback
            traceback.print_exc()
            await processing_msg.edit_text(f"❌ **Test error:** {str(e)[:200]}")
        
    except Exception as e:
        logger.error(f"❌ Critical test play error: {e}")
        import traceback
        traceback.print_exc()
        await message.reply_text(f"❌ Critical error: {str(e)}")

@app.on_message(filters.command(["vplay", "vp"]) & filters.group)
async def video_play(_, message: Message):
    """Handle /vplay command for video playback"""
    try:
        logger.info(f"📺 VPLAY COMMAND from {message.from_user.id} in {message.chat.id}")
        
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        if len(message.command) < 2:
            await message.reply_text("**Usage:** `/vplay [video name or URL]`")
            return
        
        query = " ".join(message.command[1:])
        chat_id = message.chat.id
        
        logger.info(f"🔍 Video search query: {query}")
        
        processing_msg = await message.reply("🔄 **Searching and processing video...**")
        
        try:
            success = await stream_manager.start_stream(
                chat_id, 
                query,
                video=True,
                audio_only=False
            )
            
            if success:
                stream_info = stream_manager.get_stream_info(chat_id)
                if stream_info:
                    info = stream_info['info']
                    await processing_msg.edit_text(
                        f"📺 **Now Playing Video**\n\n"
                        f"**Title:** {info.get('title', 'Unknown')}\n"
                        f"**Artist:** {info.get('artist', 'Unknown')}\n"
                        f"**Duration:** {info.get('duration', 0)} seconds\n"
                        f"**Source:** {info.get('source', 'Unknown').title()}\n"
                        f"**Requested by:** {message.from_user.mention}\n\n"
                        f"**Controls:** Use /pause, /resume, /stop, /player"
                    )
                else:
                    await processing_msg.edit_text("📺 **Video playback started!**\n\nUse /player for controls.")
            else:
                await processing_msg.edit_text(
                    "❌ **Failed to start video playback**\n\n"
                    "**Possible issues:**\n"
                    "• Bot needs admin rights in the group\n"
                    "• Voice chat must be active\n"
                    "• Check if the video/URL is valid\n\n"
                    "Try: /join first, then /vplay again"
                )
        
        except Exception as e:
            logger.error(f"❌ VPlay command error: {e}")
            import traceback
            traceback.print_exc()
            await processing_msg.edit_text(
                f"❌ **Video error occurred**\n\n"
                f"**Details:** {str(e)[:200]}\n\n"
                f"**Try:**\n"
                f"• /join to connect to voice chat\n"
                f"• Check bot permissions\n"
                f"• Use a different video/URL"
            )
        
        logger.info(f"✅ VPLAY COMMAND completed for {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Critical error in vplay command: {e}")
        import traceback
        traceback.print_exc()
        await message.reply(f"❌ Critical error: {str(e)}")

@app.on_message(filters.command(["join"]) & filters.group)
async def join_command(_, message: Message):
    """Handle /join command"""
    try:
        logger.info(f"📞 JOIN COMMAND from {message.from_user.id} in {message.chat.id}")
        
        chat_id = message.chat.id
        
        processing_msg = await message.reply_text("🔄 **Joining voice chat...**")
        
        logger.info(f"📞 Attempting to join voice chat in {chat_id}")
        success = await stream_manager.join_call(chat_id)
        logger.info(f"📞 Join result: {success}")
        
        if success:
            await processing_msg.edit_text(
                "✅ **Successfully joined voice chat!**\n\n"
                "Now you can use:\n"
                "• `/play [song]` - Play music\n"
                "• `/vplay [video]` - Play video\n"
                "• `/player` - Show controls"
            )
        else:
            await processing_msg.edit_text(
                "❌ **Failed to join voice chat**\n\n"
                "**Make sure:**\n"
                "• Voice chat is active in the group\n"
                "• Bot has admin permissions\n"
                "• Bot can manage voice chats"
            )
        
        logger.info(f"✅ JOIN COMMAND completed: {success}")
        
    except Exception as e:
        logger.error(f"❌ Join command error: {e}")
        import traceback
        traceback.print_exc()
        await message.reply_text(f"❌ Error: {str(e)}")

@app.on_message(filters.command(["leave"]) & filters.group)
async def leave_command(_, message: Message):
    """Handle /leave command"""
    try:
        logger.info(f"👋 LEAVE COMMAND from {message.from_user.id} in {message.chat.id}")
        
        chat_id = message.chat.id
        
        processing_msg = await message.reply("🔄 **Leaving voice chat...**")
        
        success = await stream_manager.leave_call(chat_id)
        
        if success:
            await processing_msg.edit_text("👋 **Left voice chat successfully!**")
        else:
            await processing_msg.edit_text("❌ **Failed to leave voice chat.**")
        
        logger.info(f"✅ LEAVE COMMAND completed: {success}")
        
    except Exception as e:
        logger.error(f"❌ Leave command error: {e}")
        import traceback
        traceback.print_exc()
        await message.reply(f"❌ Error: {str(e)}")