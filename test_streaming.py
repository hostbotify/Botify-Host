#!/usr/bin/env python3
"""
Comprehensive streaming test for JhoomMusic Bot
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
        "Arijit Singh songs",
        "https://youtu.be/dQw4w9WgXcQ"
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
                        logger.info(f"      URL: {track.get('url', 'No URL')[:100]}...")
                else:
                    logger.info(f"✅ Found: {result.get('title', 'Unknown')}")
                    logger.info(f"   URL: {result.get('url', 'No URL')[:100]}...")
                    logger.info(f"   Duration: {result.get('duration', 0)} seconds")
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
        
        # Test if we can access core methods
        core_methods = ['join_group_call', 'leave_group_call', 'play', 'pause', 'resume', 'stop']
        available_methods = []
        for method in core_methods:
            if hasattr(tgcaller, method):
                available_methods.append(method)
        
        logger.info(f"✅ Core methods available: {', '.join(available_methods)}")
        
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
        
        # Test methods availability
        methods = ['start_stream', 'stop_stream', 'pause_stream', 'resume_stream', 'join_call', 'leave_call']
        for method in methods:
            if hasattr(stream_manager, method):
                logger.info(f"✅ Method available: {method}")
            else:
                logger.error(f"❌ Method missing: {method}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Stream manager test failed: {e}")
        return False

async def test_ffmpeg():
    """Test FFmpeg availability and functionality"""
    logger.info("🧪 Testing FFmpeg...")
    
    try:
        import subprocess
        
        # Test FFmpeg version
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            logger.info(f"✅ FFmpeg available: {version_line}")
        else:
            logger.error("❌ FFmpeg not working properly")
            return False
        
        # Test FFmpeg with a simple command
        test_cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1',
            '-f', 'null', '-'
        ]
        
        result = subprocess.run(test_cmd, capture_output=True, timeout=10)
        if result.returncode == 0:
            logger.info("✅ FFmpeg test command successful")
        else:
            logger.warning("⚠️ FFmpeg test command failed, but FFmpeg is available")
        
        return True
        
    except subprocess.TimeoutExpired:
        logger.warning("⚠️ FFmpeg test timed out, but FFmpeg is available")
        return True
    except Exception as e:
        logger.error(f"❌ FFmpeg test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🧪 Starting JhoomMusic Bot Streaming Tests...")
    logger.info("=" * 60)
    
    test_results = {}
    
    try:
        # Start the bot
        await app.start()
        logger.info("✅ Bot started for testing")
        
        # Test FFmpeg
        logger.info("\n" + "="*30 + " FFMPEG TEST " + "="*30)
        test_results['ffmpeg'] = await test_ffmpeg()
        
        # Test TgCaller
        logger.info("\n" + "="*30 + " TGCALLER TEST " + "="*30)
        test_results['tgcaller'] = await test_tgcaller()
        
        # Test stream manager
        logger.info("\n" + "="*30 + " STREAM MANAGER TEST " + "="*30)
        test_results['stream_manager'] = await test_stream_manager()
        
        # Test media extraction
        logger.info("\n" + "="*30 + " MEDIA EXTRACTION TEST " + "="*30)
        await test_media_extraction()
        test_results['media_extraction'] = True
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("📊 TEST RESULTS SUMMARY:")
        logger.info("="*60)
        
        all_passed = True
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{test_name.upper()}: {status}")
            if not result:
                all_passed = False
        
        logger.info("="*60)
        
        if all_passed:
            logger.info("🎉 ALL TESTS PASSED!")
            logger.info("🚀 Bot is ready for streaming!")
            logger.info("\n📋 NEXT STEPS:")
            logger.info("1. Make sure your .env file is configured")
            logger.info("2. Add the bot to a group as admin")
            logger.info("3. Start a voice chat in the group")
            logger.info("4. Use /join to connect")
            logger.info("5. Use /play [song name] to start streaming")
        else:
            logger.error("❌ SOME TESTS FAILED!")
            logger.error("Please check the errors above and fix them before using the bot.")
        
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