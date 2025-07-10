#!/bin/bash

# GitHub Video Sync Script
# This script runs on your cPanel server and pulls the latest video data from GitHub
# GitHub Actions does the heavy lifting with yt-dlp, this just syncs the results

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_FILE="$SCRIPT_DIR/github_sync.log"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_message "=== Starting GitHub video sync ==="

# Your GitHub repository URL (raw file) - Public repository
GITHUB_RAW_URL="https://raw.githubusercontent.com/Katakombs/mini_golf_every_day_site/refs/heads/main/tiktok_videos.json"

log_message "Using GitHub URL: $GITHUB_RAW_URL"

# Backup current file if it exists
if [ -f "tiktok_videos.json" ]; then
    cp tiktok_videos.json "tiktok_videos_backup_$(date +%Y%m%d_%H%M%S).json"
    log_message "Created backup of current file"
    
    # Get current video count
    CURRENT_COUNT=$(python -c "import json; data=json.load(open('tiktok_videos.json')); print(len(data.get('videos', [])))" 2>/dev/null || echo "0")
    log_message "Current video count: $CURRENT_COUNT"
else
    log_message "No existing file found"
    CURRENT_COUNT=0
fi

# Download latest file from GitHub
log_message "Downloading latest video data from GitHub..."
if curl -s -f "$GITHUB_RAW_URL" -o "tiktok_videos_new.json"; then
    log_message "✅ Successfully downloaded from GitHub"
    
    # Verify the downloaded file is valid JSON
    if python -c "import json; json.load(open('tiktok_videos_new.json'))" 2>/dev/null; then
        log_message "✅ Downloaded file is valid JSON"
        
        # Get new video count
        NEW_COUNT=$(python -c "import json; data=json.load(open('tiktok_videos_new.json')); print(len(data.get('videos', [])))" 2>/dev/null || echo "0")
        log_message "New video count: $NEW_COUNT"
        
        # Replace old file with new one
        mv "tiktok_videos_new.json" "tiktok_videos.json"
        log_message "✅ Updated video database"
        
        # Show update summary
        if [ "$NEW_COUNT" -gt "$CURRENT_COUNT" ]; then
            ADDED=$((NEW_COUNT - CURRENT_COUNT))
            log_message "🆕 Added $ADDED new videos"
        elif [ "$NEW_COUNT" -eq "$CURRENT_COUNT" ]; then
            log_message "ℹ️  No new videos (database up to date)"
        else
            log_message "⚠️  Video count decreased (possibly cleaned up old videos)"
        fi
        
        # Show most recent video
        LATEST_TITLE=$(python -c "import json; data=json.load(open('tiktok_videos.json')); print(data['videos'][0]['title'][:60] if data['videos'] else 'None')" 2>/dev/null || echo "Unknown")
        log_message "Most recent video: $LATEST_TITLE..."
        
    else
        log_message "❌ Downloaded file is not valid JSON"
        rm -f "tiktok_videos_new.json"
        exit 1
    fi
else
    log_message "❌ Failed to download from GitHub"
    exit 1
fi

# Cleanup old backup files (keep last 7 days)
find "$SCRIPT_DIR" -name "tiktok_videos_backup_*.json" -mtime +7 -delete 2>/dev/null

log_message "=== GitHub sync completed ==="
