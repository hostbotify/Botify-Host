from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ..constants.images import UI_IMAGES
from ..constants.commands import COMMAND_DETAILS
from .helpers import get_current_time, get_uptime

def create_start_menu() -> tuple[str, InlineKeyboardMarkup]:
    """Create start menu UI"""
    current_time = get_current_time()
    text = f"""
🎵 **JHOOM MUSIC BOT**
HEY THERE, I'M JHOOM MUSIC - AN ADVANCED AI MUSIC PLAYER...

⚡ **FEATURES**:
• High-quality music streaming
• Supported platforms: YouTube, Spotify, M3U8
• Interactive player controls
• 24/7 playback support
• Multi-threaded performance
• Optimized FFmpeg configuration
• Self-repair capabilities

🕒 {current_time}
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ADD TO GROUP", url="https://t.me/JhoomMusicBot?startgroup=true")],
        [
            InlineKeyboardButton("📜 HELP", callback_data="show_commands"),
            InlineKeyboardButton("🎛 PLAYER", callback_data="show_player")
        ],
        [
            InlineKeyboardButton("⚙️ SETTINGS", callback_data="settings_menu"),
            InlineKeyboardButton("⚙️ SYSTEM-UNIT", callback_data="system_info")
        ],
        [
            InlineKeyboardButton("🔧 QUICK FIX", callback_data="quick_fix_menu")
        ]
    ])
    
    return text, buttons

def create_commands_menu() -> tuple[str, InlineKeyboardMarkup]:
    """Create commands menu UI"""
    current_time = get_current_time()
    text = f"""
# JhoomMusic bot

## COMMANDS OF JHOOM MUSIC BOT

THERE ARE DIFFERENT TYPES OF COMMAND OF JHOOM MUSIC SOME OF THEM ARE ONLY FOR ADMINS AND SOME OF THEM ARE FOR ELITEUSERS.

- HOW TO USE COMMANDS?  
  - CLICK ON BUTTONS BELOW TO KNOW MORE.  
  - CHECK FEATURES LIKE ELITEUSERS ETC.  
  - / :- USE ALL FEATURES WITH THIS HANDLER.  

🕒 {current_time}
"""
    
    buttons = InlineKeyboardMarkup([
        [   
            InlineKeyboardButton("SULTAN", callback_data="cmd_sultan"),
            InlineKeyboardButton("LICENSE", callback_data="cmd_license"),
            InlineKeyboardButton("BROADCAST", callback_data="cmd_broadcast")
        ],
        [   
            InlineKeyboardButton("BL-CHAT", callback_data="cmd_blacklist"),
            InlineKeyboardButton("BL-USER", callback_data="cmd_block"),
            InlineKeyboardButton("CH-PLAY", callback_data="cmd_channel")
        ],
        [   
            InlineKeyboardButton("G-BANS", callback_data="cmd_gbans"),
            InlineKeyboardButton("SPIRAL", callback_data="cmd_spiral"),
            InlineKeyboardButton("REVAMP", callback_data="cmd_revamp")
        ],
        [   
            InlineKeyboardButton("PING", callback_data="cmd_ping"),
            InlineKeyboardButton("PLAY", callback_data="cmd_play"),
            InlineKeyboardButton("SHUFFLE", callback_data="cmd_shuffle")
        ],
        [   
            InlineKeyboardButton("SEEK", callback_data="cmd_seek"),
            InlineKeyboardButton("SONG", callback_data="cmd_song"),
            InlineKeyboardButton("SPEED", callback_data="cmd_speed")
        ],
        [   
            InlineKeyboardButton("VIDEO", callback_data="cmd_vplay"),
            InlineKeyboardButton("QUEUE", callback_data="cmd_queue")
        ],
        [   
            InlineKeyboardButton("REPAIR", callback_data="cmd_troubleshoot"),
            InlineKeyboardButton("RADIO", callback_data="cmd_radio")
        ],
        [   
            InlineKeyboardButton("🔙 BACK", callback_data="back_to_start")
        ]
    ])
    
    return text, buttons

def create_player_ui(chat_id: int, current_track: dict = None, queue_size: int = 0) -> tuple[str, InlineKeyboardMarkup]:
    """Create player control UI"""
    if not current_track:
        current_track = {}
    
    text = f"""
🎵 **Now Playing** 🎵
┌ Title: {current_track.get('title', 'Nothing')}
├ Artist: {current_track.get('artist', 'Unknown')}
├ Duration: {current_track.get('duration', 'Unknown')}
├ Source: {current_track.get('source', 'Unknown')}
└ Queue: {queue_size} tracks waiting

🕒 {get_current_time()}
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏮ Previous", callback_data="player_previous"),
            InlineKeyboardButton("⏸ Pause", callback_data="player_pause"),
            InlineKeyboardButton("⏭ Next", callback_data="player_next")
        ],
        [
            InlineKeyboardButton("🔁 Loop", callback_data="player_loop"),
            InlineKeyboardButton("🔀 Shuffle", callback_data="player_shuffle"),
            InlineKeyboardButton("🔊 Volume", callback_data="player_volume")
        ],
        [
            InlineKeyboardButton("📜 Queue", callback_data="player_queue"),
            InlineKeyboardButton("🛑 Stop", callback_data="player_stop")
        ],
        [
            InlineKeyboardButton("🎛 Close Panel", callback_data="player_close")
        ]
    ])
    
    return text, buttons

def create_settings_menu(chat_id: int) -> tuple[str, InlineKeyboardMarkup]:
    """Create settings menu UI"""
    current_time = get_current_time()
    text = f"""
⚙️ **JHOOM MUSIC SETTINGS**

CUSTOMIZE YOUR BOT EXPERIENCE WITH THESE OPTIONS:

• Volume: 100%
• Quality: High
• Language: English
• Notifications: On

🕒 {current_time}
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔊 Volume", callback_data=f"settings_volume_{chat_id}")],
        [InlineKeyboardButton("🎚 Quality", callback_data=f"settings_quality_{chat_id}")],
        [InlineKeyboardButton("🌐 Language", callback_data=f"settings_lang_{chat_id}")],
        [InlineKeyboardButton("🔔 Notifications", callback_data=f"settings_notify_{chat_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ])
    
    return text, buttons

def create_quick_fix_menu() -> tuple[str, InlineKeyboardMarkup]:
    """Create quick fix menu UI"""
    current_time = get_current_time()
    text = f"""
# JhoomMusic  
bot  

## {datetime.now().strftime('%B %d')}  
JHOOM MUSIC  

IF YOU WANT MORE INFORMATION ABOUT ME THEN CHECK THE BELOW BUTTONS !!  

- **PYROGRAM VERSION** = 2.0.106  
- **JHOOM MUSIC VERSION** = 1.0  
- **SELF-REPAIR SYSTEM** = ACTIVE  

🕒 {current_time}
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🆘 SUPPORT", url="https://t.me/JhoomMusicSupport")],
        [InlineKeyboardButton("🔄 UPDATES", url="https://t.me/JhoomMusicUpdates")],
        [InlineKeyboardButton("⚙️ SYSTEM-UNIT", callback_data="system_info")],
        [InlineKeyboardButton("🔧 RUN DIAGNOSTICS", callback_data="run_diagnostics")],
        [InlineKeyboardButton("🔙 BACK", callback_data="back_to_start")]
    ])
    
    return text, buttons

def format_command_info(command_type: str) -> str:
    """Format command information"""
    if command_type not in COMMAND_DETAILS:
        return "Command not found"
    
    detail = COMMAND_DETAILS[command_type]
    current_date = datetime.now().strftime("%B %d")
    
    text = f"# JhoomMusic\nbot\n\n"
    text += f"## {current_date}\n"
    text += f"JHOOM MUSIC\n\n"
    text += f"### INFO ABOUT COMMANDS\n\n"
    text += f"- **{detail['title']}**\n"
    text += "______\n"
    
    for cmd in detail['commands']:
        text += f"{cmd}\n"
    
    text += f"\n🕒 {get_current_time()}\n\n"
    text += "______\n\n"
    text += "### BACK\n\n"
    text += "JHOOM MUSIC\n\n"
    text += "### INFO ABOUT AI-FEATURES\n"
    
    return text