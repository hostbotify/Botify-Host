#!/usr/bin/env python3
"""
Test script to verify all commands are working
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

async def test_commands():
    """Test if commands are registered"""
    try:
        # Start the bot
        await app.start()
        logger.info("✅ Bot started for testing")
        
        # Get bot info
        me = await app.get_me()
        logger.info(f"✅ Bot info: @{me.username}")
        
        # Check if handlers are registered
        handlers = app.dispatcher.groups
        logger.info(f"✅ Handler groups: {len(handlers)}")
        
        for group_id, group in handlers.items():
            logger.info(f"  Group {group_id}: {len(group)} handlers")
            for handler in group[:5]:  # Show first 5 handlers
                logger.info(f"    - {type(handler).__name__}")
        
        logger.info("✅ Command registration test completed")
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await app.stop()
        logger.info("🛑 Bot stopped")

if __name__ == "__main__":
    asyncio.run(test_commands())