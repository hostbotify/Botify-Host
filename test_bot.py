#!/usr/bin/env python3
"""
Test script for JhoomMusic Bot
"""

import asyncio
import logging
from jhoommusic.core.bot import app
from jhoommusic.core.media_extractor import universal_extractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_media_extraction():
    """Test media extraction functionality"""
    test_queries = [
        "Imagine Dragons Believer",
        "https://www.youtube.com/watch?v=7wtfhZwyrcc",
        "Arijit Singh songs"
    ]
    
    for query in test_queries:
        logger.info(f"Testing: {query}")
        try:
            result = await universal_extractor.extract(query)
            if result:
                if isinstance(result, list):
                    logger.info(f"✅ Found {len(result)} tracks")
                    for i, track in enumerate(result[:3]):  # Show first 3
                        logger.info(f"  {i+1}. {track.get('title', 'Unknown')}")
                else:
                    logger.info(f"✅ Found: {result.get('title', 'Unknown')}")
            else:
                logger.error(f"❌ No results for: {query}")
        except Exception as e:
            logger.error(f"❌ Error with {query}: {e}")
        
        await asyncio.sleep(1)

async def main():
    """Main test function"""
    logger.info("🧪 Starting JhoomMusic Bot tests...")
    
    try:
        # Start the bot
        await app.start()
        logger.info("✅ Bot started for testing")
        
        # Test media extraction
        await test_media_extraction()
        
        logger.info("✅ All tests completed")
        
    except Exception as e:
        logger.error(f"❌ Test error: {e}")
    finally:
        await app.stop()
        logger.info("🛑 Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())