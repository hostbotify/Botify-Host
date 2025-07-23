import logging
import asyncio
from pyrogram import Client
from tgcaller import TgCaller
from .config import Config

# Configure logging with colors
import colorlog

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    handlers=[
        handler,
        logging.FileHandler(Config.LOG_FILE)
    ]
)

logger = logging.getLogger(__name__)

# Validate configuration
if not Config.validate():
    logger.error("❌ Configuration validation failed. Exiting...")
    exit(1)

logger.info("🎵 Initializing JhoomMusic Bot...")

# Initialize Pyrogram client WITHOUT plugins (we'll register manually)
app = Client(
    "JhoomMusicBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# Initialize TgCaller
tgcaller = TgCaller(
    app, 
    log_level=logging.INFO,
    ffmpeg_parameters={
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn -preset ultrafast -tune zerolatency'
    }
)

logger.info("✅ Bot and TgCaller initialized successfully")