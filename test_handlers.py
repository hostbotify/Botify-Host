#!/usr/bin/env python3
"""
Test script to verify handlers are registered
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from jhoommusic.core.bot import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_handlers():
    """Test if handlers are registered"""
    try:
        # Import handlers to register them
        from jhoommusic.handlers import (
            start_handler,
            play_handler,
            control_handler,
            admin_handler,
            callback_handler
        )
        
        # Start the bot
        await app.start()
        logger.info("✅ Bot started for testing")
        
        # Get bot info
        me = await app.get_me()
        logger.info(f"✅ Bot info: @{me.username}")
        
        # Check if handlers are registered
        handlers = app.dispatcher.groups
        logger.info(f"✅ Handler groups: {len(handlers)}")
        
        total_handlers = 0
        for group_id, group in handlers.items():
            group_count = len(group)
            total_handlers += group_count
            logger.info(f"  Group {group_id}: {group_count} handlers")
            
            # Show some handler details
            for i, handler in enumerate(group[:3]):  # Show first 3 handlers
                logger.info(f"    {i+1}. {type(handler).__name__}")
        
        logger.info(f"✅ Total handlers registered: {total_handlers}")
        
        if total_handlers > 0:
            logger.info("🎉 SUCCESS: Handlers are properly registered!")
            logger.info("🎵 Bot should now respond to commands like /start, /play, /ping")
        else:
            logger.error("❌ FAILURE: No handlers registered!")
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await app.stop()
        logger.info("🛑 Bot stopped")

if __name__ == "__main__":
    asyncio.run(test_handlers())