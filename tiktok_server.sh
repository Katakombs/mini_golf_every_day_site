#!/bin/bash

# TikTok Video Management Script for Shared Hosting
# Update these paths for your server

# Auto-detect common Python locations
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python or update the PYTHON_CMD variable."
    exit 1
fi

# Use current directory as script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR" || exit 1

case "$1" in
    "add")
        if [ -z "$2" ]; then
            echo "Usage: ./tiktok.sh add VIDEO_ID_OR_URL [TITLE]"
            echo "Example: ./tiktok.sh add 7522583834320260365"
            echo "Example: ./tiktok.sh add https://www.tiktok.com/@minigolfeveryday/video/7522583834320260365"
            exit 1
        fi
        $PYTHON_CMD add_video.py "$2" "$3"
        ;;
    "update")
        echo "🔄 Updating all videos..."
        $PYTHON_CMD tiktok_automation.py
        ;;
    "test")
        echo "🧪 Testing system..."
        $PYTHON_CMD test_detection.py
        ;;
    "status")
        echo "📊 Current video status:"
        echo "Python command: $PYTHON_CMD"
        echo "Script directory: $SCRIPT_DIR"
        if [ -f "tiktok_videos.json" ]; then
            echo "Video data file exists"
            videos_count=$(grep -o '"video_id"' tiktok_videos.json | wc -l | tr -d ' ')
            echo "Number of videos: $videos_count"
            last_updated=$(grep '"last_updated"' tiktok_videos.json | cut -d'"' -f4)
            echo "Last updated: $last_updated"
        else
            echo "No video data file found"
        fi
        
        # Test Python packages
        echo ""
        echo "📦 Testing Python packages..."
        $PYTHON_CMD -c "import requests; print('✅ requests')" 2>/dev/null || echo "❌ requests"
        $PYTHON_CMD -c "import bs4; print('✅ beautifulsoup4')" 2>/dev/null || echo "❌ beautifulsoup4"
        $PYTHON_CMD -c "import subprocess; subprocess.run(['yt-dlp', '--version'], capture_output=True); print('✅ yt-dlp')" 2>/dev/null || echo "❌ yt-dlp"
        ;;
    "backup")
        backup_name="watch_backup_$(date +%Y%m%d_%H%M%S).html"
        cp watch.html "$backup_name"
        echo "✅ Backup saved as: $backup_name"
        ;;
    "install")
        echo "🔧 Installing Python packages..."
        $PYTHON_CMD -m pip install --user yt-dlp requests beautifulsoup4 python-dotenv
        if [ $? -eq 0 ]; then
            echo "✅ Packages installed successfully"
        else
            echo "❌ Installation failed. Try manually:"
            echo "   pip install --user yt-dlp requests beautifulsoup4 python-dotenv"
        fi
        ;;
    *)
        echo "TikTok Video Management Commands:"
        echo ""
        echo "  ./tiktok.sh add VIDEO_ID     - Add a new video"
        echo "  ./tiktok.sh update           - Update all videos"
        echo "  ./tiktok.sh test             - Test system capabilities"
        echo "  ./tiktok.sh status           - Show current status"
        echo "  ./tiktok.sh backup           - Create backup of watch.html"
        echo "  ./tiktok.sh install          - Install Python packages"
        echo ""
        echo "Examples:"
        echo "  ./tiktok.sh add 7522583834320260365"
        echo "  ./tiktok.sh add https://www.tiktok.com/@minigolfeveryday/video/7522583834320260365"
        ;;
esac
