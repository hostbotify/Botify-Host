import logging
from pyrogram import Client
from pytgcalls import PyTgCalls
from .config import Config

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

# Validate configuration
if not Config.validate():
    logger.error("Configuration validation failed. Exiting...")
    exit(1)

# Initialize Pyrogram client
app = Client(
    "JhoomMusicBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    plugins=dict(root="jhoommusic.plugins")
)

# Initialize PyTgCalls
pytgcalls = PyTgCalls(app)

logger.info("Bot and PyTgCalls initialized successfully")