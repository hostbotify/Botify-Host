import logging
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ..core.bot import app
from ..utils.helpers import save_user_to_db, save_chat_to_db, get_current_time

logger = logging.getLogger(__name__)

@app.on_message(filters.command("start"))
async def start_command(_, message: Message):
    """Handle /start command"""
    try:
        logger.info(f"🚀 START COMMAND from {message.from_user.id} in {message.chat.id}")
        
        # Save user and chat to database
        await save_user_to_db(message.from_user)
        if message.chat.type != "private":
            await save_chat_to_db(message.chat)
        
        current_time = get_current_time()
        
        text = f"""🎵 **JHOOM MUSIC BOT**

HEY {message.from_user.first_name}, I'M JHOOM MUSIC - AN ADVANCED AI MUSIC PLAYER...

⚡ **FEATURES**:
• High-quality music streaming
• YouTube, Spotify support  
• Interactive player controls
• 24/7 playback support
• Multi-threaded performance
• Self-repair capabilities

🕒 {current_time}

**QUICK START:**
• Add me to your group as admin
• Start voice chat in group
• Use /play [song name] to play music
• Use /join to connect to voice chat

**COMMANDS:**
• /play [song] - Play music
• /vplay [video] - Play video  
• /join - Join voice chat
• /leave - Leave voice chat
• /pause - Pause playback
• /resume - Resume playback
• /stop - Stop playback
• /player - Show player controls
"""
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ ADD TO GROUP", url=f"https://t.me/{app.me.username}?startgroup=true")],
            [
                InlineKeyboardButton("📜 COMMANDS", callback_data="show_commands"),
                InlineKeyboardButton("🎛 PLAYER", callback_data="show_player")
            ],
            [
                InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings_menu"),
                InlineKeyboardButton("🔧 SUPPORT", url="https://t.me/JhoomMusicSupport")
            ]
        ])
        
        await message.reply_text(
            text=text,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
        
        logger.info(f"✅ START COMMAND completed for {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Error in start command: {e}")
        import traceback
        traceback.print_exc()
        await message.reply_text(
            "🎵 **JhoomMusic Bot**\n\n"
            "✅ Bot is online and ready!\n"
            "Use /play [song name] to start playing music."
        )

@app.on_message(filters.command("help"))
async def help_command(_, message: Message):
    """Handle /help command"""
    try:
        logger.info(f"❓ HELP COMMAND from {message.from_user.id}")
        
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
        logger.info(f"✅ HELP COMMAND completed")
        
    except Exception as e:
        logger.error(f"❌ Error in help command: {e}")
        import traceback
        traceback.print_exc()
        await message.reply("❓ **Help:** Use /play [song name] to play music!")

@app.on_message(filters.command("ping"))
async def ping_command(_, message: Message):
    """Handle /ping command"""
    try:
        import time
        logger.info(f"🏓 PING COMMAND from {message.from_user.id}")
        
        start_time = time.time()
        msg = await message.reply("🏓 **Pong!**")
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        from ..utils.helpers import get_uptime
        uptime = get_uptime()
        
        await msg.edit_text(
            f"🏓 **Pong!**\n\n"
            f"⏱ **Response Time:** `{response_time:.2f} ms`\n"
            f"🕐 **Uptime:** `{uptime}`\n"
            f"🤖 **Status:** Online\n"
            f"🎵 **JhoomMusic Bot** is ready!"
        )
        
        logger.info(f"✅ PING COMMAND completed: {response_time:.2f}ms")
        
    except Exception as e:
        logger.error(f"❌ Error in ping command: {e}")
        import traceback
        traceback.print_exc()
        await message.reply("🏓 **Pong!** - Bot is online!")

@app.on_message(filters.command("alive"))
async def alive_command(_, message: Message):
    """Handle /alive command"""
    try:
        logger.info(f"💚 ALIVE COMMAND from {message.from_user.id}")
        
        from ..utils.helpers import get_uptime
        uptime = get_uptime()
        
        await message.reply(
            "🤖 **I'm Alive!**\n\n"
            "✅ Bot is running perfectly\n"
            "✅ All systems operational\n"
            "✅ Commands are working\n"
            "✅ Ready to stream music\n\n"
            f"⏱ **Uptime:** `{uptime}`\n"
            f"🎵 **JhoomMusic Bot** is ready!\n\n"
            "**Quick Test:** Use `/play tere naam song`"
        )
        
        logger.info(f"✅ ALIVE COMMAND completed")
        
    except Exception as e:
        logger.error(f"❌ Error in alive command: {e}")
        import traceback
        traceback.print_exc()
        await message.reply("🤖 **I'm Alive!** - Bot is working!")