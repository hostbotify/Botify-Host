"""
Ping command plugin for quick testing
"""

import time
import logging
from pyrogram import filters
from pyrogram.types import Message
from ..core.bot import app

logger = logging.getLogger(__name__)

@app.on_message(filters.command("ping"))
async def ping_command(_, message: Message):
    """Handle /ping command"""
    try:
        start_time = time.time()
        msg = await message.reply("🏓 **Pong!**")
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000
        
        await msg.edit_text(
            f"🏓 **Pong!**\n"
            f"⏱ **Response Time:** `{response_time:.2f} ms`\n"
            f"🤖 **Bot Status:** Online"
        )
        
        logger.info(f"Ping command used by {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in ping command: {e}")
        await message.reply("❌ An error occurred while processing ping command")
