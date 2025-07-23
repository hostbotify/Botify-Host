import logging
from pyrogram import filters
from pyrogram.types import CallbackQuery
from ..core.bot import app

logger = logging.getLogger(__name__)

@app.on_callback_query(filters.regex("^show_commands$"))
async def show_commands_callback(_, query: CallbackQuery):
    """Handle show commands callback"""
    try:
        await query.answer("📜 Commands menu coming soon!", show_alert=True)
        logger.info(f"Commands callback from {query.from_user.id}")
    except Exception as e:
        logger.error(f"Error in commands callback: {e}")
        await query.answer("❌ Error occurred", show_alert=True)

@app.on_callback_query(filters.regex("^show_player$"))
async def show_player_callback(_, query: CallbackQuery):
    """Handle show player callback"""
    try:
        await query.answer("🎛 Player panel coming soon!", show_alert=True)
        logger.info(f"Player callback from {query.from_user.id}")
    except Exception as e:
        logger.error(f"Error in player callback: {e}")
        await query.answer("❌ Error occurred", show_alert=True)

@app.on_callback_query(filters.regex("^settings_menu$"))
async def settings_callback(_, query: CallbackQuery):
    """Handle settings callback"""
    try:
        await query.answer("⚙️ Settings menu coming soon!", show_alert=True)
        logger.info(f"Settings callback from {query.from_user.id}")
    except Exception as e:
        logger.error(f"Error in settings callback: {e}")
        await query.answer("❌ Error occurred", show_alert=True)