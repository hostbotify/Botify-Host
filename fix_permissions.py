#!/usr/bin/env python3
"""
Fix file permissions and setup script
"""

import os
import stat
import subprocess
import sys

def make_executable(file_path):
    """Make a file executable"""
    try:
        current_permissions = os.stat(file_path).st_mode
        os.chmod(file_path, current_permissions | stat.S_IEXEC)
        print(f"✅ Made executable: {file_path}")
    except Exception as e:
        print(f"❌ Error making {file_path} executable: {e}")

def main():
    """Fix permissions and setup"""
    print("🔧 Fixing permissions and setting up JhoomMusic Bot...")
    
    # Make scripts executable
    scripts = [
        "main.py",
        "test_streaming.py",
        "test_tgcaller.py",
        "install_deps.py",
        "run_bot.sh"
    ]
    
    for script in scripts:
        if os.path.exists(script):
            make_executable(script)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, capture_output=True)
        print("✅ pip is available")
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        return False
    
    # Install requirements
    print("📦 Installing requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    
    # Check FFmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
        print("✅ FFmpeg is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg not found")
        print("Install FFmpeg:")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  CentOS/RHEL: sudo yum install ffmpeg")
        print("  macOS: brew install ffmpeg")
        return False
    
    # Check .env file
    if not os.path.exists(".env"):
        print("⚠️ .env file not found")
        print("Creating .env template...")
        with open(".env", "w") as f:
            f.write("""# Bot Configuration
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# Database
MONGO_URI=mongodb://localhost:27017/jhoommusic

# Redis Cache (Optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Admin Configuration
SUDO_USERS=123456789,987654321
SUPER_GROUP_ID=-1001234567890
SUPER_GROUP_USERNAME=JhoomMusicSupport

# Performance Settings
FFMPEG_PROCESSES=4
MAX_PLAYLIST_SIZE=100
MAX_QUEUE_SIZE=50
""")
        print("✅ .env template created")
        print("📝 Please edit .env file with your configuration")
    else:
        print("✅ .env file exists")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your bot configuration")
    print("2. Run: python3 test_streaming.py (to test)")
    print("3. Run: python3 main.py (to start the bot)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)