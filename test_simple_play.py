#!/usr/bin/env python3
"""
Simple test script for play functionality
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from jhoommusic.core.bot import app, tgcaller
from jhoommusic.core.stream_manager import stream_manager
from jhoommusic.core.media_extractor import universal_extractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_extraction():
    """Test simple media extraction"""
    logger.info("🧪 Testing simple extraction...")
    
    test_query = "tere naam song"
    logger.info(f"🔍 Testing: {test_query}")
    
    try:
        result = await universal_extractor.extract(test_query)
        if result:
            logger.info(f"✅ Found: {result.get('title', 'Unknown')}")
            logger.info(f"   URL: {result.get('url', 'No URL')[:100]}...")
            logger.info(f"   Duration: {result.get('duration', 0)} seconds")
            return result
        else:
            logger.error(f"❌ No results for: {test_query}")
            return None
    except Exception as e:
        logger.error(f"❌ Error with {test_query}: {e}")
        return None

async def test_tgcaller_basic():
    """Test basic TgCaller functionality"""
    logger.info("🧪 Testing TgCaller basic functionality...")
    
    try:
        # Start TgCaller
        await tgcaller.start()
        logger.info("✅ TgCaller started")
        
        # Test if methods exist
        methods = ['join_group_call', 'leave_group_call', 'play', 'pause', 'resume', 'stop']
        for method in methods:
            if hasattr(tgcaller, method):
                logger.info(f"✅ Method available: {method}")
            else:
                logger.error(f"❌ Method missing: {method}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TgCaller test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🧪 Starting Simple Play Test...")
    logger.info("=" * 50)
    
    try:
        # Start the bot
        await app.start()
        logger.info("✅ Bot started for testing")
        
        # Test TgCaller
        tgcaller_ok = await test_tgcaller_basic()
        
        # Test extraction
        result = await test_simple_extraction()
        
        if tgcaller_ok and result:
            logger.info("\n🎉 Basic tests passed!")
            logger.info("🚀 Try using /testplay command in your group")
            logger.info("\nSteps to test:")
            logger.info("1. Add bot to group as admin")
            logger.info("2. Start voice chat in group")
            logger.info("3. Use /testplay tere naam song")
        else:
            logger.error("\n❌ Some tests failed")
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await tgcaller.stop()
            await app.stop()
            logger.info("🛑 Test cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")

if __name__ == "__main__":
    asyncio.run(main())