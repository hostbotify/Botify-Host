import logging
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from ...core.bot import app
from ...core.troubleshoot import troubleshoot_manager
from ...core.config import Config
from ...constants.images import UI_IMAGES
from ...utils.helpers import is_admin_or_sudo, save_user_to_db, save_chat_to_db

logger = logging.getLogger(__name__)

@app.on_message(filters.command(["fixbot", "repair"]) & filters.group)
async def user_fix_command(_, message: Message):
    """Handle /fixbot command"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # Check if user is admin
        if not await is_admin_or_sudo(chat_id, user_id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Only admins can use this command"
            )
            return
        
        # Create fix options
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Fix Voice Connection", callback_data=f"fix_voice_{chat_id}")],
            [InlineKeyboardButton("🎧 Restart Playback", callback_data=f"fix_playback_{chat_id}")],
            [InlineKeyboardButton("📜 Check Permissions", callback_data=f"fix_perms_{chat_id}")],
            [InlineKeyboardButton("🔍 Run Diagnostics", callback_data=f"fix_diagnose_{chat_id}")],
            [InlineKeyboardButton("🚨 Report to Support", url=f"t.me/{Config.SUPER_GROUP_USERNAME}")]
        ])
        
        await message.reply_photo(
            photo=UI_IMAGES["diagnostics"],
            caption=f"🔧 **{message.from_user.mention}, select repair option:**\n\n"
            f"**Group:** {message.chat.title}\n"
            f"**Problem ID:** `{abs(hash(str(chat_id))) % 10000}`",
            reply_markup=buttons
        )
        
        logger.info(f"Fixbot command used by {user_id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in fixbot command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )

@app.on_message(filters.command("diagnose") & filters.group)
async def diagnose_command(_, message: Message):
    """Handle /diagnose command"""
    try:
        await save_user_to_db(message.from_user)
        await save_chat_to_db(message.chat)
        
        chat_id = message.chat.id
        
        # Check if user is admin
        if not await is_admin_or_sudo(chat_id, message.from_user.id):
            await message.reply_photo(
                photo=UI_IMAGES["error"],
                caption="❌ Only admins can use this command"
            )
            return
        
        # Run diagnostics
        report = await troubleshoot_manager.run_diagnostics(chat_id)
        
        await message.reply_photo(
            photo=UI_IMAGES["diagnostics"],
            caption=report
        )
        
        logger.info(f"Diagnose command used by {message.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in diagnose command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ Diagnostic failed: {str(e)[:200]}"
        )

@app.on_message(filters.command("fixproblem") & filters.chat(Config.SUPER_GROUP_ID))
async def problem_fix_menu(_, message: Message):
    """Handle /fixproblem command (admin only)"""
    try:
        await save_user_to_db(message.from_user)
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔊 Voice Connection", callback_data="admin_fix_voice")],
            [InlineKeyboardButton("🛑 Playback Stopped", callback_data="admin_fix_playback")],
            [InlineKeyboardButton("📛 Permissions Issue", callback_data="admin_fix_permission")],
            [InlineKeyboardButton("🔍 Run Diagnostics", callback_data="admin_fix_diagnose")]
        ])
        
        await message.reply_photo(
            photo=UI_IMAGES["admin"],
            caption="⚠️ **Select problem type to fix:**\n\nReply to a message from the affected chat or provide chat ID.",
            reply_markup=buttons
        )
        
        logger.info(f"Fix problem menu requested by {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in fixproblem command: {e}")
        await message.reply_photo(
            photo=UI_IMAGES["error"],
            caption=f"❌ An error occurred: {str(e)}"
        )