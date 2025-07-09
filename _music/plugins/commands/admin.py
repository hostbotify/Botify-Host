import logging
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message
from ...core.bot import app
from ...core.database import db
from ...core.config import Config
from ...constants.images import UI_IMAGES
from ...utils.helpers import save_user_to_db

logger = logging.getLogger(__name__)

@app.on_message(filters.command("auth") & filters.user(Config.SUDO_USERS))
async def auth_user(_, message: Message):
    """Handle /auth command"""
    try:
        await save_user_to_db(message.from_user)
        
        if len(message.command) < 2:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="**Usage:** `/auth user_id`"
            )
            return
        
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Invalid user ID"
            )
            return
        
        # Add user to auth list
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
        
        await message.reply_photo(
            photo=UI_IMAGES["license"],
            caption=f"✅ **User {user_id} added to auth list**"
        )
        
        logger.info(f"User {user_id} authorized by {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in auth command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command("unauth") & filters.user(Config.SUDO_USERS))
async def unauth_user(_, message: Message):
    """Handle /unauth command"""
    try:
        await save_user_to_db(message.from_user)
        
        if len(message.command) < 2:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="**Usage:** `/unauth user_id`"
            )
            return
        
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Invalid user ID"
            )
            return
        
        # Remove user from auth list
        result = await db.auth_users.delete_one({"user_id": user_id})
        
        if result.deleted_count > 0:
            await message.reply_photo(
                photo=UI_IMAGES["license"],
                caption=f"✅ **User {user_id} removed from auth list**"
            )
        else:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption=f"❌ User {user_id} not found in auth list"
            )
        
        logger.info(f"User {user_id} unauthorized by {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in unauth command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command("authusers") & filters.user(Config.SUDO_USERS))
async def show_auth_users(_, message: Message):
    """Handle /authusers command"""
    try:
        await save_user_to_db(message.from_user)
        
        # Get all authorized users
        auth_users_list = await db.auth_users.find().to_list(None)
        
        if not auth_users_list:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ No authorized users found"
            )
            return
        
        # Format user list
        text = "🔐 **Authorized Users:**\n\n"
        for i, user in enumerate(auth_users_list, 1):
            text += f"{i}. **User ID:** `{user['user_id']}`\n"
            if 'authorized_at' in user:
                text += f"   **Date:** {user['authorized_at'].strftime('%Y-%m-%d %H:%M')}\n"
            text += "\n"
        
        await message.reply_photo(
            photo=UI_IMAGES["license"],
            caption=text
        )
        
        logger.info(f"Auth users list requested by {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in authusers command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command(["gban", "globalban"]) & filters.user(Config.SUDO_USERS))
async def global_ban_user(_, message: Message):
    """Handle /gban command"""
    try:
        await save_user_to_db(message.from_user)
        
        if len(message.command) < 2:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="**Usage:** `/gban user_id [reason]`"
            )
            return
        
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Invalid user ID"
            )
            return
        
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided"
        
        # Add user to global ban list
        await db.gbanned_users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "reason": reason,
                    "banned_by": message.from_user.id,
                    "banned_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        await message.reply_photo(
            photo=UI_IMAGES["gbans"],
            caption=f"🔨 **User {user_id} has been globally banned**\n**Reason:** {reason}"
        )
        
        logger.info(f"User {user_id} globally banned by {message.from_user.id}: {reason}")
        
    except Exception as e:
        logger.error(f"Error in gban command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command(["ungban", "unglobalban"]) & filters.user(Config.SUDO_USERS))
async def global_unban_user(_, message: Message):
    """Handle /ungban command"""
    try:
        await save_user_to_db(message.from_user)
        
        if len(message.command) < 2:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="**Usage:** `/ungban user_id`"
            )
            return
        
        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Invalid user ID"
            )
            return
        
        # Remove user from global ban list
        result = await db.gbanned_users.delete_one({"user_id": user_id})
        
        if result.deleted_count > 0:
            await message.reply_photo(
                photo=UI_IMAGES["gbans"],
                caption=f"✅ **User {user_id} has been globally unbanned**"
            )
        else:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption=f"❌ User {user_id} was not globally banned"
            )
        
        logger.info(f"User {user_id} globally unbanned by {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in ungban command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command(["gbannedusers", "globalbans"]) & filters.user(Config.SUDO_USERS))
async def show_global_bans(_, message: Message):
    """Handle /gbannedusers command"""
    try:
        await save_user_to_db(message.from_user)
        
        # Get all globally banned users
        banned_users = await db.gbanned_users.find().to_list(None)
        
        if not banned_users:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ No users are currently globally banned"
            )
            return
        
        # Format banned users list
        text = "🔨 **Globally Banned Users:**\n\n"
        for i, user in enumerate(banned_users, 1):
            text += f"{i}. **User ID:** `{user['user_id']}`\n"
            text += f"   **Reason:** {user.get('reason', 'Not specified')}\n"
            text += f"   **Banned by:** {user.get('banned_by', 'Unknown')}\n"
            if 'banned_at' in user:
                text += f"   **Date:** {user['banned_at'].strftime('%Y-%m-%d %H:%M')}\n"
            text += "\n"
        
        await message.reply_photo(
            photo=UI_IMAGES["gbans"],
            caption=text
        )
        
        logger.info(f"Global bans list requested by {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in gbannedusers command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command("broadcast") & filters.user(Config.SUDO_USERS))
async def broadcast_message(_, message: Message):
    """Handle /broadcast command"""
    try:
        await save_user_to_db(message.from_user)
        
        if len(message.command) < 2:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="**Usage:** `/broadcast [-options] message`\n\n**Options:**\n• `-pin` - Pin message\n• `-user` - Broadcast to users only"
            )
            return
        
        # Parse options and message
        parts = message.text.split()
        options = [p for p in parts if p.startswith('-')]
        broadcast_msg = ' '.join([p for p in parts if not p.startswith('-')][1:])
        
        if not broadcast_msg:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ No message to broadcast"
            )
            return
        
        # Get all chats
        all_chats = await db.chats.find().to_list(None)
        
        if not all_chats:
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ No chats found to broadcast"
            )
            return
        
        pin_message = '-pin' in options
        to_users = '-user' in options
        
        success = 0
        failed = 0
        total = len(all_chats)
        
        # Send progress message
        progress = await message.reply_photo(
            photo=UI_IMAGES["broadcast"],
            caption=f"📢 **Starting broadcast to {total} chats...**"
        )
        
        # Broadcast to all chats
        for chat in all_chats:
            try:
                chat_id = chat['chat_id']
                
                # Filter by user preference
                if to_users and chat_id < 0:  # Skip groups if user-only
                    continue
                elif not to_users and chat_id > 0:  # Skip users if not user-only
                    continue
                
                # Send message
                sent_msg = await app.send_message(chat_id, broadcast_msg)
                success += 1
                
                # Pin message if requested
                if pin_message and chat_id < 0:  # Only pin in groups
                    try:
                        await app.pin_chat_message(chat_id, sent_msg.id)
                    except Exception:
                        pass
                
                # Update progress every 10 messages
                if (success + failed) % 10 == 0:
                    await progress.edit_caption(
                        caption=f"📢 **Broadcasting...**\n**Success:** {success}\n**Failed:** {failed}\n**Remaining:** {total - success - failed}"
                    )
                
            except Exception as e:
                logger.error(f"Error broadcasting to {chat['chat_id']}: {e}")
                failed += 1
        
        # Final progress update
        await progress.edit_caption(
            caption=f"📢 **Broadcast completed!**\n**Success:** {success}\n**Failed:** {failed}"
        )
        
        logger.info(f"Broadcast completed by {message.from_user.id}: {success} success, {failed} failed")
        
    except Exception as e:
        logger.error(f"Error in broadcast command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command(["logs", "log"]) & filters.user(Config.SUDO_USERS))
async def send_logs(_, message: Message):
    """Handle /logs command"""
    try:
        await save_user_to_db(message.from_user)
        
        # Send log file
        await message.reply_document(
            document=Config.LOG_FILE,
            caption="📜 **Bot logs**"
        )
        
        logger.info(f"Logs requested by {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in logs command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ Error sending logs: {str(e)}"
        )