#!/usr/bin/env python3
"""
JhoomMusic Bot - Main Entry Point
Copyright (c) 2025 JhoomMusic. All rights reserved.
"""

import os
import sys
import asyncio
import logging
import importlib
import signal
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from jhoommusic.core.config import Config
from jhoommusic.core.bot import app, tgcaller
from jhoommusic.core.database import db

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

def load_plugins():
    """Load all plugins from jhoommusic/plugins directory"""
    plugins_path = os.path.join(os.path.dirname(__file__), "jhoommusic", "plugins")
    
    if not os.path.exists(plugins_path):
        logger.error(f"❌ Plugins directory not found: {plugins_path}")
        return
    
    # Load command plugins
    commands_path = os.path.join(plugins_path, "commands")
    if os.path.exists(commands_path):
        for file in os.listdir(commands_path):
            if file.endswith(".py") and not file.startswith("__"):
                plugin_name = file[:-3]
                try:
                    importlib.import_module(f"jhoommusic.plugins.commands.{plugin_name}")
                    logger.info(f"✅ Command plugin loaded: {plugin_name}.py")
                except Exception as e:
                    logger.error(f"❌ Failed to load command plugin {plugin_name}: {e}")
    
    # Load callback plugins
    callbacks_path = os.path.join(plugins_path, "callbacks")
    if os.path.exists(callbacks_path):
        for file in os.listdir(callbacks_path):
            if file.endswith(".py") and not file.startswith("__"):
                plugin_name = file[:-3]
                try:
                    importlib.import_module(f"jhoommusic.plugins.callbacks.{plugin_name}")
                    logger.info(f"✅ Callback plugin loaded: {plugin_name}.py")
                except Exception as e:
                    logger.error(f"❌ Failed to load callback plugin {plugin_name}: {e}")
    
    # Load root level plugins
    for file in os.listdir(plugins_path):
        if file.endswith(".py") and not file.startswith("__"):
            plugin_name = file[:-3]
            try:
                importlib.import_module(f"jhoommusic.plugins.{plugin_name}")
                logger.info(f"✅ Plugin loaded: {plugin_name}.py")
            except Exception as e:
                logger.error(f"❌ Failed to load plugin {plugin_name}: {e}")

async def startup_tasks():
    """Initialize all core components"""
    try:
        # Connect to database
        await db.connect()
        logger.info("✅ Database connected")
        
        # Start TgCaller
        await tgcaller.start()
        logger.info("✅ TgCaller started")
        
        # Send startup message to super group if configured
        if Config.SUPER_GROUP_ID and Config.SUPER_GROUP_ID != 0:
            try:
                await app.send_message(
                    Config.SUPER_GROUP_ID,
                    "🎵 **JhoomMusic Bot Started!**\n\n"
                    "✅ All systems operational\n"
                    "✅ Ready to stream music"
                )
                logger.info("✅ Startup message sent")
            except Exception as e:
                logger.warning(f"⚠️ Failed to send startup message: {e}")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")

async def shutdown_tasks():
    """Cleanup tasks on shutdown"""
    try:
        logger.info("🛑 Shutting down JhoomMusic Bot...")
        
        # Stop TgCaller
        try:
            await tgcaller.stop()
            logger.info("✅ TgCaller stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping TgCaller: {e}")
        
        # Close database connection
        await db.close()
        logger.info("✅ Database connection closed")
        
        # Stop the bot
        await app.stop()
        logger.info("✅ Bot stopped")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"📡 Received signal {signum}")
    # Create new event loop for shutdown if current one is closed
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(shutdown_tasks())
    except Exception as e:
        logger.error(f"❌ Error in signal handler: {e}")

async def main():
    """Main function to start the bot"""
    try:
        logger.info("🎵 Starting JhoomMusic Bot...")
        
        # Validate configuration
        if not Config.validate():
            logger.error("❌ Configuration validation failed. Exiting...")
            return
        
        # Load all plugins
        load_plugins()
        
        # Start the bot
        logger.info("🤖 Bot starting...")
        await app.start()
        logger.info("✅ Bot started successfully!")
        
        # Initialize core components
        await startup_tasks()
        
        logger.info("🚀 JhoomMusic Bot started successfully!")
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
    finally:
        await shutdown_tasks()

if __name__ == "__main__":
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the bot
    asyncio.run(main())
