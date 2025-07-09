import time
import psutil
import platform
import logging
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from ...core.bot import app
from ...core.database import db
from ...core.config import Config
from ...constants.images import UI_IMAGES
from ...utils.helpers import get_uptime, save_user_to_db, save_chat_to_db
from ...utils.cache import get_cache_stats

logger = logging.getLogger(__name__)

@app.on_message(filters.command(["ping", "speed"]) & filters.group)
async def ping_pong(_, message: Message):
    """Handle /ping command"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        start = time.time()
        msg = await message.reply_photo(
            photo=UI_IMAGES["ping"],
            caption="🏓 **Pong!**"
        )
        end = time.time()
        
        await msg.edit_caption(
            caption=f"🏓 **Pong!**\n⏱ **Response time:** `{(end - start) * 1000:.2f} ms`"
        )
        
        logger.info(f"Ping command used by {message.from_user.id} in {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Error in ping command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command(["uptime", "up"]) & filters.group)
async def show_uptime(_, message: Message):
    """Handle /uptime command"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        uptime = get_uptime()
        await message.reply_photo(
            photo=UI_IMAGES["ping"],
            caption=f"⏱ **Bot Uptime:** `{uptime}`"
        )
        
        logger.info(f"Uptime command used by {message.from_user.id} in {message.chat.id}")
        
    except Exception as e:
        logger.error(f"Error in uptime command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command("stats") & filters.user(Config.SUDO_USERS))
async def show_stats(_, message: Message):
    """Handle /stats command"""
    try:
        await save_user_to_db(message.from_user)
        
        # Get system stats
        ram = psutil.virtual_memory().used // (1024 * 1024)  # MB
        cpu = psutil.cpu_percent()
        uptime = get_uptime()
        
        # Get database stats
        total_chats = await db.chats.count_documents({})
        total_users = await db.users.count_documents({})
        auth_users = await db.auth_users.count_documents({})
        gbanned_users = await db.gbanned_users.count_documents({})
        
        # Get cache stats
        cache_stats = await get_cache_stats()
        
        # System info
        os_name = f"{platform.system()} {platform.release()}"
        python_version = platform.python_version()
        
        # Format stats message
        text = f"""
📊 **JHOOM MUSIC STATISTICS**

**🖥 System Stats:**
• **RAM Usage:** `{ram} MB`
• **CPU Usage:** `{cpu}%`
• **Uptime:** `{uptime}`
• **OS:** `{os_name}`
• **Python:** `{python_version}`

**📊 Database Stats:**
• **Total Chats:** `{total_chats}`
• **Total Users:** `{total_users}`
• **Auth Users:** `{auth_users}`
• **Banned Users:** `{gbanned_users}`

**💾 Cache Stats:**
• **Status:** `{cache_stats.get('status', 'Unknown')}`
• **Keys:** `{cache_stats.get('keys', 0)}`
• **Memory:** `{cache_stats.get('memory_used', 'Unknown')}`

**📅 Generated:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
"""
        
        await message.reply_photo(
            photo=UI_IMAGES["admin"],
            caption=text
        )
        
        logger.info(f"Stats command used by {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )