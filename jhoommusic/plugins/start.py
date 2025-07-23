"""
Start command plugin - Root level for proper loading
"""

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
        logger.info(f"🚀 Start command from {message.from_user.id} in {message.chat.id}")
        
        # Save user and chat to database
        await save_user_to_db(message.from_user)
        if message.chat.type != "private":
            await save_chat_to_db(message.chat)
        
        current_time = get_current_time()
        
        # Create start menu with working buttons
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
        
        # Send start message
        await message.reply_text(
            text=text,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
        
        logger.info(f"✅ Start command completed for {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"❌ Error in start command: {e}")
        await message.reply_text(
            "🎵 **JhoomMusic Bot**\n\n"
            "✅ Bot is online and ready!\n"
            "Use /play [song name] to start playing music."
        )