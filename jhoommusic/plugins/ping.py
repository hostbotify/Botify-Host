"""
Ping command plugin - Root level for proper loading
"""

import time
import logging
from pyrogram import filters
from pyrogram.types import Message
from ..core.bot import app
from ..utils.helpers import get_uptime

logger = logging.getLogger(__name__)

@app.on_message(filters.command("ping"))
async def ping_command(_, message: Message):
    """Handle /ping command"""
    try:
        logger.info(f"🏓 Ping command from {message.from_user.id}")
        
        start_time = time.time()
        msg = await message.reply("🏓 **Pong!**")
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        uptime = get_uptime()
        
        await msg.edit_text(
            f"🏓 **Pong!**\n\n"
            f"⏱ **Response Time:** `{response_time:.2f} ms`\n"
            f"🕐 **Uptime:** `{uptime}`\n"
            f"🤖 **Status:** Online\n"
            f"🎵 **JhoomMusic Bot** is ready!"
        )
        
        logger.info(f"✅ Ping command completed: {response_time:.2f}ms")
        
    except Exception as e:
        logger.error(f"❌ Error in ping command: {e}")
        await message.reply("🏓 **Pong!** - Bot is online!")

@app.on_message(filters.command("help"))
async def help_command(_, message: Message):
    """Handle /help command"""
    try:
        logger.info(f"❓ Help command from {message.from_user.id}")
        
        help_text = """🎵 **JHOOM MUSIC BOT - HELP**

**🎧 MUSIC COMMANDS:**
• `/play [song name]` - Play music from YouTube
• `/play [YouTube URL]` - Play from YouTube URL
• `/vplay [video name]` - Play video
• `/testplay [song]` - Test play (no auth needed)

**🎛 CONTROL COMMANDS:**
• `/join` - Join voice chat
• `/leave` - Leave voice chat  
• `/pause` - Pause current playback
• `/resume` - Resume playback
• `/stop` - Stop playback and clear queue
• `/player` - Show interactive player panel

**📊 INFO COMMANDS:**
• `/ping` - Check bot response time
• `/alive` - Check if bot is running
• `/status` - Show current playback status

**🔧 ADMIN COMMANDS:**
• `/fixbot` - Auto-repair bot issues
• `/diagnose` - Run diagnostics

**📝 USAGE EXAMPLE:**
1. Add bot to group as admin
2. Start voice chat in group
3. Use `/join` to connect
4. Use `/play tere naam song` to play

**🆘 SUPPORT:** @JhoomMusicSupport
"""
        
        await message.reply_text(help_text)
        logger.info(f"✅ Help command completed")
        
    except Exception as e:
        logger.error(f"❌ Error in help command: {e}")
        await message.reply("❓ **Help:** Use /play [song name] to play music!")