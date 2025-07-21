#!/usr/bin/env python3
"""
JhoomMusic Bot - Advanced Telegram Music Bot
Copyright (c) 2025 JhoomMusic. All rights reserved.

Main entry point for the bot.
"""

import asyncio
import logging
import signal
import sys
from jhoommusic.core.bot import app, tgcaller
from jhoommusic.core.database import db
from jhoommusic.core.config import Config
from jhoommusic.core.troubleshoot import troubleshoot_manager
from jhoommusic.constants.images import UI_IMAGES

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
        logger.info("🎵 Starting JhoomMusic Bot...")
        
        # Connect to database
        await db.connect()
        if db.enabled:
            logger.info("✅ Database connected")
        else:
            logger.info("⚠️ Running without database")
        
        # Start TgCaller
        await tgcaller.start()
        logger.info("✅ TgCaller started")
        
        # Send startup notification
        if Config.SUPER_GROUP_ID and Config.SUPER_GROUP_ID != 0:
            try:
                await app.send_photo(
                    Config.SUPER_GROUP_ID,
                    UI_IMAGES["startup"],
                    caption="⚡ **JhoomMusic Bot is now online!**\n"
                    f"**Version:** 1.0\n"
                    f"**Features:** All systems operational"
                )
            except Exception as e:
                logger.warning(f"Could not send startup notification: {e}")
        
        # Start periodic maintenance
        asyncio.create_task(periodic_maintenance())
        
        logger.info("🚀 JhoomMusic Bot started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

async def shutdown():
    """Bot shutdown tasks"""
    try:
        logger.info("🛑 Shutting down JhoomMusic Bot...")
        
        # Send shutdown notification
        if Config.SUPER_GROUP_ID and Config.SUPER_GROUP_ID != 0:
            try:
                await app.send_message(
                    Config.SUPER_GROUP_ID,
                    "🛑 **JhoomMusic Bot is shutting down...**"
                )
            except Exception:
                pass
        
        # Stop TgCaller
        try:
            await tgcaller.stop()
        except Exception as e:
            logger.error(f"Error stopping TgCaller: {e}")
        
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
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(shutdown())
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
        if not app.is_connected:
            await app.start()
        logger.info("✅ Pyrogram client started")
        
        # Keep the bot running
        stop_event = asyncio.Event()
        await stop_event.wait()
        
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
