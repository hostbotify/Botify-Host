#!/usr/bin/env python3
"""
Jhoom Music Bot - Advanced Telegram Music Bot
Copyright (c) 2025 Jhoom Music. All rights reserved.

Main entry point for the bot.
"""

import asyncio
import logging
import signal
import sys
from _music.core.bot import app, pytgcalls
from _music.core.database import db
from _music.core.config import Config
from _music.core.troubleshoot import troubleshoot_manager
from _music.constants.images import UI_IMAGES

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def startup():
    """Bot startup tasks"""
    try:
        logger.info("🎵 Starting Jhoom Music Bot...")
        
        # Connect to database
        await db.connect()
        logger.info("✅ Database connected")
        
        # Start PyTgCalls
        await pytgcalls.start()
        logger.info("✅ PyTgCalls started")
        
        # Send startup notification
        try:
            await app.send_photo(
                Config.SUPER_GROUP_ID,
                UI_IMAGES["startup"],
                caption="⚡ **Jhoom Music Bot is now online!**\n"
                f"**Version:** 1.0\n"
                f"**Features:** All systems operational"
            )
        except Exception as e:
            logger.warning(f"Could not send startup notification: {e}")
        
        # Start periodic maintenance
        asyncio.create_task(periodic_maintenance())
        
        logger.info("🚀 Jhoom Music Bot started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

async def shutdown():
    """Bot shutdown tasks"""
    try:
        logger.info("🛑 Shutting down Jhoom Music Bot...")
        
        # Send shutdown notification
        try:
            await app.send_message(
                Config.SUPER_GROUP_ID,
                "🛑 **Jhoom Music Bot is shutting down...**"
            )
        except Exception:
            pass
        
        # Stop PyTgCalls
        await pytgcalls.stop()
        
        # Close database connection
        await db.close()
        
        logger.info("✅ Bot shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

async def periodic_maintenance():
    """Periodic maintenance tasks"""
    while True:
        try:
            # Run health checks every 5 minutes
            await troubleshoot_manager.health_check_all_chats()
            await asyncio.sleep(300)  # 5 minutes
        except Exception as e:
            logger.error(f"Maintenance error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}")
    asyncio.create_task(shutdown())
    sys.exit(0)

async def main():
    """Main function"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run startup tasks
    await startup()
    
    # Start the bot
    try:
        await app.start()
        logger.info("✅ Pyrogram client started")
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)