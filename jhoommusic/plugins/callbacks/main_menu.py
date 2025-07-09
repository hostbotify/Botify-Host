import logging
from pyrogram import filters
from pyrogram.types import CallbackQuery, InputMediaPhoto
from ...core.bot import app
from ...constants.images import UI_IMAGES
from ...utils.ui import create_start_menu, create_commands_menu, create_quick_fix_menu

logger = logging.getLogger(__name__)

@app.on_callback_query(filters.regex("^back_to_start$"))
async def back_to_start(_, query: CallbackQuery):
    """Handle back to start callback"""
    try:
        text, buttons = create_start_menu()
        await query.message.edit_media(
            media=InputMediaPhoto(UI_IMAGES["main_menu"]),
            reply_markup=buttons
        )
        await query.message.edit_caption(
            caption=text,
            reply_markup=buttons
        )
        await query.answer()
        
        logger.info(f"Back to start used by {query.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in back_to_start callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)

@app.on_callback_query(filters.regex("^show_commands$"))
async def show_commands_menu(_, query: CallbackQuery):
    """Handle show commands callback"""
    try:
        text, buttons = create_commands_menu()
        await query.message.edit_media(
            media=InputMediaPhoto(UI_IMAGES["commands_menu"]),
            reply_markup=buttons
        )
        await query.message.edit_caption(
            caption=text,
            reply_markup=buttons
        )
        await query.answer()
        
        logger.info(f"Commands menu shown to {query.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in show_commands callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)

@app.on_callback_query(filters.regex("^quick_fix_menu$"))
async def show_quick_fix_menu(_, query: CallbackQuery):
    """Handle quick fix menu callback"""
    try:
        text, buttons = create_quick_fix_menu()
        await query.message.edit_media(
            media=InputMediaPhoto(UI_IMAGES["diagnostics"]),
            reply_markup=buttons
        )
        await query.message.edit_caption(
            caption=text,
            reply_markup=buttons
        )
        await query.answer()
        
        logger.info(f"Quick fix menu shown to {query.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error in quick_fix_menu callback: {e}")
        await query.answer("❌ An error occurred", show_alert=True)