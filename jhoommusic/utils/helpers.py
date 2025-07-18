import time
import logging
from datetime import datetime, timedelta
from pyrogram.types import Message
from ..core.bot import app
from ..core.database import db
from ..core.config import Config

logger = logging.getLogger(__name__)

# Bot start time
start_time = time.time()

def format_duration(seconds: int) -> str:
    """Format duration in seconds to HH:MM:SS or MM:SS"""
    if seconds == 0:
        return "Live"
    
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def get_uptime() -> str:
    """Get bot uptime"""
    seconds = int(time.time() - start_time)
    periods = [
        ('day', 86400),
        ('hour', 3600), 
        ('minute', 60),
        ('second', 1)
    ]
    
    result = []
    for name, sec in periods:
        if seconds >= sec:
            val = seconds // sec
            seconds %= sec
            result.append(f"{val} {name}{'s' if val > 1 else ''}")
    
    return ", ".join(result) if result else "Just started"

def get_current_time() -> str:
    """Get current time in HH:MM format"""
    return datetime.now().strftime('%H:%M')

async def is_admin_or_sudo(chat_id: int, user_id: int) -> bool:
    """Check if user is admin or sudo user"""
    if user_id in Config.SUDO_USERS:
        return True
    
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False

async def is_user_gbanned(user_id: int) -> bool:
    """Check if user is globally banned"""
    if not db.enabled:
        return False
    try:
        return await db.gbanned_users.find_one({"user_id": user_id}) is not None
    except Exception:
        return False

async def check_user_auth(user_id: int) -> bool:
    """Check if user is authorized"""
    if user_id in Config.SUDO_USERS:
        return True
    if not db.enabled:
        return True  # Allow all users when DB is disabled
    try:
        return await db.auth_users.find_one({"user_id": user_id}) is not None
    except Exception:
        return True  # Allow on error

def extract_chat_id(message: Message) -> int:
    """Extract chat ID from message text or reply"""
    if message.reply_to_message:
        return message.reply_to_message.chat.id
    
    try:
        return int(message.text.split()[1])
    except (IndexError, ValueError):
        return message.chat.id

async def save_user_to_db(user):
    """Save user to database"""
    if not db.enabled:
        return
    try:
        await db.users.update_one(
            {"user_id": user.id},
            {
                "$set": {
                    "user_id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "last_seen": datetime.utcnow()
                }
            },
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error saving user to DB: {e}")

async def save_chat_to_db(chat):
    """Save chat to database"""
    if not db.enabled:
        return
    try:
        await db.chats.update_one(
            {"chat_id": chat.id},
            {
                "$set": {
                    "chat_id": chat.id,
                    "title": chat.title,
                    "type": chat.type,
                    "username": chat.username,
                    "last_active": datetime.utcnow()
                }
            },
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error saving chat to DB: {e}")