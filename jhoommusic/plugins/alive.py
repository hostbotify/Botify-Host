"""
Alive command plugin - Root level for proper loading
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
        logger.info(f"💚 Alive command from {message.from_user.id}")
        
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
        
        logger.info(f"✅ Alive command completed")
        
    except Exception as e:
        logger.error(f"❌ Error in alive command: {e}")
        await message.reply("🤖 **I'm Alive!** - Bot is working!")