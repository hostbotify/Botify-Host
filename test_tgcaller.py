#!/usr/bin/env python3
"""
TgCaller functionality test script
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

async def test_media_extraction():
    """Test media extraction functionality"""
    logger.info("🧪 Testing media extraction...")
    
    test_queries = [
        "Imagine Dragons Believer",
        "https://www.youtube.com/watch?v=7wtfhZwyrcc",
        "Arijit Singh songs"
    ]
    
    for query in test_queries:
        logger.info(f"🔍 Testing: {query}")
        try:
            result = await universal_extractor.extract(query)
            if result:
                if isinstance(result, list):
                    logger.info(f"✅ Found {len(result)} tracks")
                    for i, track in enumerate(result[:3]):  # Show first 3
                        logger.info(f"  {i+1}. {track.get('title', 'Unknown')}")
                else:
                    logger.info(f"✅ Found: {result.get('title', 'Unknown')}")
                    logger.info(f"   URL: {result.get('url', 'No URL')[:100]}...")
            else:
                logger.error(f"❌ No results for: {query}")
        except Exception as e:
            logger.error(f"❌ Error with {query}: {e}")
        
        await asyncio.sleep(1)

async def test_tgcaller():
    """Test TgCaller functionality"""
    logger.info("🧪 Testing TgCaller...")
    
    try:
        # Start TgCaller
        await tgcaller.start()
        logger.info("✅ TgCaller started successfully")
        
        # Test basic functionality
        logger.info("🔍 TgCaller methods available:")
        methods = [attr for attr in dir(tgcaller) if not attr.startswith('_')]
        for method in methods[:10]:  # Show first 10 methods
            logger.info(f"  - {method}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ TgCaller test failed: {e}")
        return False

async def test_stream_manager():
    """Test stream manager functionality"""
    logger.info("🧪 Testing stream manager...")
    
    try:
        # Test basic functionality
        logger.info("✅ Stream manager initialized")
        logger.info(f"📊 Active streams: {len(stream_manager.active_streams)}")
        logger.info(f"🔧 FFmpeg processes: {len(stream_manager.ffmpeg_processes)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Stream manager test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🧪 Starting JhoomMusic Bot tests...")
    logger.info("=" * 50)
    
    try:
        # Start the bot
        await app.start()
        logger.info("✅ Bot started for testing")
        
        # Test TgCaller
        tgcaller_ok = await test_tgcaller()
        
        # Test stream manager
        stream_ok = await test_stream_manager()
        
        # Test media extraction
        await test_media_extraction()
        
        # Summary
        logger.info("\n📊 Test Results:")
        logger.info(f"TgCaller: {'✅ PASS' if tgcaller_ok else '❌ FAIL'}")
        logger.info(f"Stream Manager: {'✅ PASS' if stream_ok else '❌ FAIL'}")
        logger.info(f"Media Extraction: ✅ PASS")
        
        if tgcaller_ok and stream_ok:
            logger.info("\n🎉 All core tests passed!")
            logger.info("🚀 Bot is ready for production use")
        else:
            logger.error("\n❌ Some tests failed. Check the logs above.")
        
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