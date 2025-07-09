import logging
from pyrogram import filters
from pyrogram.types import CallbackQuery
from ...core.bot import app
from ...core.troubleshoot import troubleshoot_manager
from ...utils.helpers import extract_chat_id

logger = logging.getLogger(__name__)

@app.on_callback_query(filters.regex("^fix_"))
async def handle_fix_callbacks(_, query: CallbackQuery):
    """Handle fix callbacks from user commands"""
    try:
        parts = query.data.split("_")
        action = parts[1]
        chat_id = int(parts[2]) if len(parts) > 2 else query.message.chat.id
        
        if action == "voice":
            await query.answer("🔄 Fixing voice connection...")
            success = await troubleshoot_manager.fix_voice_connection(chat_id)
            if success:
                await query.message.edit_caption(
                    caption="✅ **Voice connection fixed successfully!**"
                )
            else:
                await query.message.edit_caption(
                    caption="❌ **Failed to fix voice connection. Please try again or contact support.**"
                )
                
        elif action == "playback":
            await query.answer("🔄 Restarting playback...")
            success = await troubleshoot_manager.restart_playback(chat_id)
            if success:
                await query.message.edit_caption(
                    caption="✅ **Playback restarted successfully!**"
                )
            else:
                await query.message.edit_caption(
                    caption="❌ **Failed to restart playback. Please try again or contact support.**"
                )
                
        elif action == "perms":
            await query.answer("🔍 Checking permissions...")
            perm_result = await troubleshoot_manager.check_permissions(chat_id)
            
            if perm_result["status"] == "success":
                await query.message.edit_caption(
                    caption="✅ **All required permissions are available!**"
                )
            elif perm_result["status"] == "missing_perms":
                missing = ", ".join(perm_result["missing"])
                await query.message.edit_caption(
                    caption=f"⚠️ **Missing Permissions:**\n\n{missing}\n\nPlease grant these permissions to the bot."
                )
            else:
                await query.message.edit_caption(
                    caption=f"❌ **Permission check failed:** {perm_result['error']}"
                )
                
        elif action == "diagnose":
            await query.answer("🔍 Running diagnostics...")
            report = await troubleshoot_manager.run_diagnostics(chat_id)
            await query.message.edit_caption(caption=report)
        
        logger.info(f"Fix callback handled by {query.from_user.id}: {action} for chat {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in fix callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)

@app.on_callback_query(filters.regex("^admin_fix_"))
async def handle_admin_fix_callbacks(_, query: CallbackQuery):
    """Handle admin fix callbacks from supergroup"""
    try:
        action = query.data.split("_")[2]
        
        # Extract chat ID from replied message or ask for it
        chat_id = extract_chat_id(query.message)
        
        if action == "voice":
            await query.answer("🔄 Fixing voice connection...")
            success = await troubleshoot_manager.fix_voice_connection(chat_id)
            status = "✅ Fixed" if success else "❌ Failed"
            await query.message.edit_caption(
                caption=f"**Voice Connection Fix**\n**Chat ID:** {chat_id}\n**Status:** {status}"
            )
            
        elif action == "playback":
            await query.answer("🔄 Restarting playback...")
            success = await troubleshoot_manager.restart_playback(chat_id)
            status = "✅ Fixed" if success else "❌ Failed"
            await query.message.edit_caption(
                caption=f"**Playback Restart**\n**Chat ID:** {chat_id}\n**Status:** {status}"
            )
            
        elif action == "permission":
            await query.answer("🔍 Checking permissions...")
            perm_result = await troubleshoot_manager.check_permissions(chat_id)
            await query.message.edit_caption(
                caption=f"**Permission Check**\n**Chat ID:** {chat_id}\n**Status:** {perm_result['status']}"
            )
            
        elif action == "diagnose":
            await query.answer("🔍 Running diagnostics...")
            report = await troubleshoot_manager.run_diagnostics(chat_id)
            await query.message.edit_caption(
                caption=f"**Diagnostics for Chat {chat_id}**\n\n{report}"
            )
        
        logger.info(f"Admin fix callback handled by {query.from_user.id}: {action} for chat {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in admin fix callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)

@app.on_callback_query(filters.regex("^run_diagnostics$"))
async def run_diagnostics_callback(_, query: CallbackQuery):
    """Handle run diagnostics callback"""
    try:
        chat_id = query.message.chat.id
        await query.answer("🔍 Running diagnostics...")
        
        report = await troubleshoot_manager.run_diagnostics(chat_id)
        
        await query.message.edit_caption(
            caption=report,
            reply_markup=query.message.reply_markup
        )
        
        logger.info(f"Diagnostics run by {query.from_user.id} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Error in run_diagnostics callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)