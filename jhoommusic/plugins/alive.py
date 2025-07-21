"""
Alive command plugin for status checking
"""

import logging
from pyrogram import filters
from pyrogram.types import Message
from ..core.bot import app
from ..utils.helpers import get_uptime

logger = logging.getLogger(__name__)

@app.on_message(filters.command("alive"))
async def alive_command(_, message: Message):
    """Handle /alive command"""
    try:
        uptime = get_uptime()
        
        await message.reply(
            "🤖 **I'm Alive!**\n\n"
            "✅ Bot is running\n"
            "✅ Commands are working\n"
            "✅ Plugins are loaded\n\n"
            f"⏱ **Uptime:** `{uptime}`\n"
            "🎵 **JhoomMusic Bot** is ready!"
        )
        
        logger.info(f"Alive command used by {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in alive command: {e}")
        await message.reply("❌ Error in alive command")
