# 🎵 JhoomMusic Bot

An advanced Telegram music bot with high-quality streaming, multi-platform support, and self-repair capabilities.

## ✨ Features

- **High-Quality Streaming**: Crystal clear audio with optimized FFmpeg configuration
- **Multi-Platform Support**: YouTube, Spotify, M3U8 streams, and radio stations
- **Interactive Controls**: Advanced player panel with real-time controls
- **Self-Repair System**: Automatic troubleshooting and problem resolution
- **Queue Management**: Advanced queue system with shuffle and loop options
- **Thumbnail Generation**: Beautiful custom thumbnails for now playing
- **Admin Controls**: Comprehensive admin panel with user management
- **Performance Optimized**: Multi-threaded processing with Redis caching
- **24/7 Support**: Continuous playback with health monitoring

## 🚀 Quick Setup

### Prerequisites

- Python 3.8+
- MongoDB
- Redis (optional but recommended)
- FFmpeg

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/jhoommusic-bot.git
cd jhoommusic-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run the bot**
```bash
python main.py
```

### Quick Test Commands

After setup, test the bot with these commands:

```bash
# Test basic functionality
python test_simple_play.py

# Test streaming
python test_streaming.py

# Test TgCaller
python test_tgcaller.py
```

### Bot Commands for Testing

- `/testplay [song name]` - Simple test play command (no auth required)
- `/play [song name]` - Regular play command
- `/join` - Join voice chat
- `/leave` - Leave voice chat
- `/pause` - Pause playback
- `/resume` - Resume playback
- `/stop` - Stop playback

## ⚙️ Configuration

### Required Environment Variables

```env
# Bot Configuration
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# Database
MONGO_URI=mongodb://localhost:27017/jhoommusic

# Admin Configuration
SUDO_USERS=123456789,987654321
SUPER_GROUP_ID=-1001234567890
SUPER_GROUP_USERNAME=JhoomMusicSupport
```

### Optional Configuration

```env
# Redis Cache (recommended)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Spotify Integration
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# Performance Settings
FFMPEG_PROCESSES=4
MAX_PLAYLIST_SIZE=100
MAX_QUEUE_SIZE=50
```

## 📱 Commands

### Basic Commands
- `/start` - Start the bot and show main menu
- `/play [song name/URL]` - Play music
- `/vplay [video name/URL]` - Play video
- `/pause` - Pause playback
- `/resume` - Resume playback
- `/skip` - Skip current track
- `/stop` - Stop playback and clear queue
- `/queue` - Show current queue
- `/player` - Show interactive player panel

### Advanced Commands
- `/loop [enable/disable/1-10]` - Control loop mode
- `/shuffle` - Shuffle the queue
- `/playlist` - Manage playlists
- `/settings` - Bot settings
- `/ping` - Check bot status

### Admin Commands
- `/auth [user_id]` - Authorize user
- `/unauth [user_id]` - Remove authorization
- `/gban [user_id]` - Global ban user
- `/broadcast [message]` - Broadcast message
- `/logs` - Get bot logs
- `/stats` - Show bot statistics

### Troubleshooting Commands
- `/fixbot` - Auto-repair common issues
- `/diagnose` - Run diagnostics
- `/fixproblem` - Admin repair menu (super group only)

## 🏗️ Architecture

### Core Components

- **Bot Core** (`jhoommusic/core/`): Main bot functionality
  - `bot.py` - Pyrogram client and PyTgCalls initialization
  - `config.py` - Configuration management
  - `database.py` - MongoDB operations
  - `connection.py` - Voice chat connection management
  - `queue.py` - Music queue management
  - `playback.py` - Music playback control
  - `media.py` - Media extraction from various sources
  - `thumbnail.py` - Thumbnail generation
  - `troubleshoot.py` - Self-repair system

- **Plugins** (`jhoommusic/plugins/`): Command and callback handlers
  - `commands/` - Command handlers
  - `callbacks/` - Callback query handlers

- **Utils** (`jhoommusic/utils/`): Utility functions
  - `helpers.py` - Helper functions
  - `cache.py` - Redis caching
  - `ui.py` - UI generation

### Database Schema

The bot uses MongoDB with the following collections:
- `users` - User information
- `chats` - Chat information
- `auth_users` - Authorized users
- `gbanned_users` - Globally banned users
- `playlists` - User playlists
- `channel_queues` - Music queues
- `troubleshooting_logs` - Repair logs

## 🔧 Self-Repair System

The bot includes an advanced self-repair system that can:
- Automatically fix voice connection issues
- Restart failed playback
- Check and request missing permissions
- Monitor system health
- Generate diagnostic reports

## 🎨 UI/UX Features

- **Interactive Menus**: Beautiful inline keyboard menus
- **Custom Thumbnails**: Generated thumbnails with album art
- **Progress Indicators**: Real-time playback progress
- **Status Updates**: Live status updates during operations
- **Error Handling**: User-friendly error messages

## 📊 Performance Features

- **Multi-threading**: Concurrent FFmpeg processes
- **Caching**: Redis-based caching for thumbnails and metadata
- **Resource Management**: Dynamic process adjustment based on load
- **Memory Optimization**: Efficient memory usage patterns

## 🛡️ Security Features

- **User Authorization**: Multi-level user authorization system
- **Global Bans**: Global ban system across all chats
- **Permission Checks**: Automatic permission validation
- **Rate Limiting**: Built-in rate limiting for commands

## 🔄 Deployment

### Docker Deployment (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Systemd Service

```ini
[Unit]
Description=JhoomMusic Bot
After=network.target

[Service]
Type=simple
User=musicbot
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Telegram Support**: [@JhoomMusicSupport](https://t.me/JhoomMusicSupport)
- **Updates Channel**: [@JhoomMusicUpdates](https://t.me/JhoomMusicUpdates)
- **Issues**: [GitHub Issues](https://github.com/yourusername/jhoommusic-bot/issues)

## 🙏 Acknowledgments

- [Pyrogram](https://github.com/pyrogram/pyrogram) - Telegram client library
- [TgCaller](https://github.com/TgCaller/TgCaller) - Modern voice chat streaming
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Media extraction
- [Spotipy](https://github.com/plamere/spotipy) - Spotify integration

---

**Made with ❤️ by JhoomMusic Team**