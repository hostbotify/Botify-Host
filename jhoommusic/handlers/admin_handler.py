import logging
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from ..core.bot import app
from ..core.database import db
from ..core.config import Config
from ..utils.helpers import save_user_to_db

logger = logging.getLogger(__name__)

@app.on_message(filters.command("auth") & filters.user(Config.SUDO_USERS))
async def auth_user(_, message: Message):
    """Handle /auth command"""
    try:
        await save_user_to_db(message.from_user)
        
        if len(message.command) < 2:
            await message.reply("**Usage:** `/auth user_id`")
            return
        
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply("❌ Invalid user ID")
            return
        
        if db.enabled:
            await db.auth_users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "user_id": user_id,
                        "authorized_by": message.from_user.id,
                        "authorized_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
        
        await message.reply(f"✅ **User {user_id} added to auth list**")
        logger.info(f"User {user_id} authorized by {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in auth command: {e}")
        await message.reply(f"❌ An error occurred: {str(e)}")

@app.on_message(filters.command("broadcast") & filters.user(Config.SUDO_USERS))
async def broadcast_message(_, message: Message):
    """Handle /broadcast command"""
    try:
        await save_user_to_db(message.from_user)
        
        if len(message.command) < 2:
            await message.reply("**Usage:** `/broadcast message`")
            return
        
        broadcast_msg = ' '.join(message.command[1:])
        
        if not db.enabled:
            await message.reply("❌ Database not available for broadcast")
            return
        
        all_chats = await db.chats.find().to_list(None)
        
        if not all_chats:
            await message.reply("❌ No chats found to broadcast")
            return
        
        success = 0
        failed = 0
        total = len(all_chats)
        
        progress = await message.reply(f"📢 **Starting broadcast to {total} chats...**")
        
        for chat in all_chats:
            try:
                chat_id = chat['chat_id']
                await app.send_message(chat_id, broadcast_msg)
                success += 1
                
                if (success + failed) % 10 == 0:
                    await progress.edit_text(
                        f"📢 **Broadcasting...**\n**Success:** {success}\n**Failed:** {failed}\n**Remaining:** {total - success - failed}"
                    )
                
            except Exception as e:
                logger.error(f"Error broadcasting to {chat['chat_id']}: {e}")
                failed += 1
        
        await progress.edit_text(
            f"📢 **Broadcast completed!**\n**Success:** {success}\n**Failed:** {failed}"
        )
        
        logger.info(f"Broadcast completed by {message.from_user.id}: {success} success, {failed} failed")
        
    except Exception as e:
        logger.error(f"Error in broadcast command: {e}")
        await message.reply(f"❌ An error occurred: {str(e)}")