#!/usr/bin/env python3
"""
Dependency installer and environment checker for JhoomMusic Bot
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    
    print("✅ Python version is compatible")
    return True

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
            return True
        else:
            print("❌ FFmpeg not found")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found")
        return False

def install_ffmpeg():
    """Install FFmpeg based on OS"""
    system = platform.system().lower()
    
    if system == "linux":
        # Try different package managers
        if run_command("which apt", "Checking apt"):
            return run_command("sudo apt update && sudo apt install -y ffmpeg", "Installing FFmpeg with apt")
        elif run_command("which yum", "Checking yum"):
            return run_command("sudo yum install -y ffmpeg", "Installing FFmpeg with yum")
        elif run_command("which pacman", "Checking pacman"):
            return run_command("sudo pacman -S ffmpeg", "Installing FFmpeg with pacman")
    elif system == "darwin":  # macOS
        if run_command("which brew", "Checking Homebrew"):
            return run_command("brew install ffmpeg", "Installing FFmpeg with Homebrew")
    elif system == "windows":
        print("⚠️ Please install FFmpeg manually on Windows")
        print("📥 Download from: https://ffmpeg.org/download.html")
        return False
    
    print(f"❌ Unsupported system: {system}")
    return False

def install_python_deps():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# Bot Configuration
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token

# Database
MONGO_URI=mongodb://localhost:27017/jhoommusic

# Redis Cache
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
        print("✅ .env file created")
        print("⚠️ Please edit .env file with your configuration")
    else:
        print("✅ .env file already exists")

def main():
    """Main installation function"""
    print("🎵 JhoomMusic Bot - Dependency Installer")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check FFmpeg
    if not check_ffmpeg():
        print("🔧 FFmpeg not found. Attempting to install...")
        if not install_ffmpeg():
            print("❌ Failed to install FFmpeg. Please install manually.")
            sys.exit(1)
    
    # Install Python dependencies
    if not install_python_deps():
        print("❌ Failed to install Python dependencies")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your bot configuration")
    print("2. Run: python main.py")
    print("\n🆘 Need help? Check the README.md file")

if __name__ == "__main__":
    main()