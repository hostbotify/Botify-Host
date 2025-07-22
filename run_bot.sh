#!/bin/bash

# JhoomMusic Bot Runner Script
echo "🎵 JhoomMusic Bot - Startup Script"
echo "=================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found"
    echo "🔧 Running dependency installer..."
    python3 install_deps.py
    echo "📝 Please edit .env file with your configuration and run this script again"
    exit 1
fi

# Install/update dependencies
echo "📦 Installing dependencies..."
python3 install_deps.py

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo "❌ Dependency installation failed"
    exit 1
fi

# Run tests
echo "🧪 Running tests..."
python3 test_tgcaller.py

# Start the bot
echo "🚀 Starting JhoomMusic Bot..."
python3 main.py