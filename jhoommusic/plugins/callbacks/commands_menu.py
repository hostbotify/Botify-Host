import logging
from pyrogram import filters
from pyrogram.types import CallbackQuery, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from ...core.bot import app
from ...constants.images import UI_IMAGES
from ...constants.commands import COMMAND_DETAILS
from ...utils.ui import format_command_info

logger = logging.getLogger(__name__)

@app.on_callback_query(filters.regex("^cmd_"))
async def show_command_info(_, query: CallbackQuery):
    """Handle command info callbacks"""
    try:
        command_type = query.data.split("_")[1]
        
        if command_type in COMMAND_DETAILS:
            text = format_command_info(command_type)
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 BACK", callback_data="show_commands")]
            ])
            
            await query.message.edit_media(
                media=InputMediaPhoto(UI_IMAGES["commands_menu"]),
                reply_markup=buttons
            )
            await query.message.edit_caption(
                caption=text,
                reply_markup=buttons
            )
        else:
            await query.answer("❌ Command not found", show_alert=True)
            return
        
        await query.answer()
        
        logger.info(f"Command info shown to {query.from_user.id}: {command_type}")
        
    except Exception as e:
        logger.error(f"Error in cmd callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)