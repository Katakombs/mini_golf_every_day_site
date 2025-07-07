#!/bin/bash

# Mini Golf Every Day - Cron Wrapper Script
# This script safely updates TikTok videos without losing history
# Created: July 6, 2025
# Production ready for cPanel shared hosting
#
# SETUP INSTRUCTIONS FOR CPANEL:
# 1. Upload this file to your website's root directory
# 2. Set file permissions to 755: chmod 755 cron_wrapper.sh
# 3. In cPanel Cron Jobs, add:
#    Command: /home/username/public_html/cron_wrapper.sh
#    (Replace 'username' with your actual cPanel username)
#
# RECOMMENDED CRON SCHEDULE:
# - Every 2 hours: 0 */2 * * *
# - Every 4 hours: 0 */4 * * *
# - Daily at 9 AM: 0 9 * * *
#
# LOGS:
# - Check cron.log for execution logs
# - Backups are created automatically before updates

# Set script directory (production ready)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables if .env file exists (but don't override existing ones)
if [ -f ".env" ]; then
    while IFS='=' read -r key value; do
        if [[ ! "$key" =~ ^# ]] && [[ -n "$key" ]] && [[ -z "${!key}" ]]; then
            export "$key"="$value"
        fi
    done < .env
fi

# Set PATH for cPanel (important for shared hosting)
export PATH="/usr/local/bin:/usr/bin:/bin:/home/$USER/.local/bin:$PATH"

# Try to find Python executables
PYTHON_CMD=""
for py_cmd in "python3.11" "python3.10" "python3.9" "python3.8" "python3" "python"; do
    if command -v "$py_cmd" &> /dev/null; then
        PYTHON_CMD="$py_cmd"
        break
    fi
done

# Try to find pip
PIP_CMD=""
for pip_cmd in "pip3.11" "pip3.10" "pip3.9" "pip3.8" "pip3" "pip"; do
    if command -v "$pip_cmd" &> /dev/null; then
        PIP_CMD="$pip_cmd"
        break
    fi
done

# Use full paths for Python on cPanel
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
elif [ -f "venv/bin/python" ]; then
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
fi

# Log file
LOG_FILE="$SCRIPT_DIR/cron.log"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Start logging
log_message "=== Starting TikTok video update process ==="

# Debug: Log current environment variables
log_message "Environment check - MGED_DOMAIN: ${MGED_DOMAIN:-'not set'}"
log_message "Environment check - MGED_API_KEY: ${MGED_API_KEY:-'not set'}"

# Check if virtual environment exists
if [ -d ".venv" ]; then
    log_message "Using virtual environment: .venv"
    source .venv/bin/activate
elif [ -d "venv" ]; then
    log_message "Using virtual environment: venv"
    source venv/bin/activate
else
    log_message "No virtual environment found - using system Python"
    # On cPanel, system Python might be sufficient
fi

# Verify Python and required packages
if [ -z "$PYTHON_CMD" ]; then
    log_message "ERROR: No Python executable found"
    exit 1
fi

log_message "Using Python: $PYTHON_CMD"

# Only need requests library (usually available on most servers)
if ! $PYTHON_CMD -c "import requests" 2>/dev/null; then
    log_message "ERROR: requests library not available"
    log_message "Please install with: pip install requests"
    exit 1
fi

log_message "✅ Required libraries available"

# Check file permissions and ownership
if [ -f "tiktok_videos.json" ]; then
    log_message "JSON file exists - checking permissions..."
    ls -la tiktok_videos.json | tee -a "$LOG_FILE"
    
    # Test if we can write to the file
    if [ -w "tiktok_videos.json" ]; then
        log_message "✅ JSON file is writable"
    else
        log_message "❌ JSON file is NOT writable - fixing permissions..."
        chmod 664 tiktok_videos.json
        if [ -w "tiktok_videos.json" ]; then
            log_message "✅ Fixed JSON file permissions"
        else
            log_message "❌ Could not fix JSON file permissions"
        fi
    fi
else
    log_message "JSON file does not exist - will be created"
fi

# Check directory permissions
log_message "Directory permissions:"
ls -la . | grep -E "(tiktok_videos|flask_app)" | tee -a "$LOG_FILE"

# Test write permissions in current directory
if touch test_write_permission.tmp 2>/dev/null; then
    rm test_write_permission.tmp
    log_message "✅ Directory is writable"
else
    log_message "❌ Directory is NOT writable"
fi

# Backup current JSON file
if [ -f "tiktok_videos.json" ]; then
    cp tiktok_videos.json "tiktok_videos_backup_$(date +%Y%m%d_%H%M%S).json"
    log_message "Created backup of current JSON file"
fi

# Run the smart update script using your existing API
log_message "Running smart TikTok video update via API..."

# Set environment variables for the Python script
export MGED_API_KEY="${MGED_API_KEY:-default_dev_key}"

# Determine the correct domain to use
if [ -n "$MGED_DOMAIN" ]; then
    # Use the environment variable if it's set
    log_message "Using domain from environment: $MGED_DOMAIN"
else
    # Default fallback logic
    if [ -f "/home" ] && [ ! -f "/Users" ]; then
        # Likely a Linux server (cPanel)
        export MGED_DOMAIN="https://minigolfevery.day"
        log_message "Auto-detected production server, using: $MGED_DOMAIN"
    else
        # Local development
        export MGED_DOMAIN="http://localhost:5001"
        log_message "Auto-detected local development, using: $MGED_DOMAIN"
    fi
fi

log_message "Final domain: $MGED_DOMAIN"
log_message "Final API key: ${MGED_API_KEY:0:8}..."

$PYTHON_CMD << 'EOF'
import json
import os
import requests
from datetime import datetime
import re

def get_latest_video_ids_simple(username="minigolfeveryday", limit=5):
    """Simple method to get latest video IDs from TikTok profile page"""
    try:
        print(f"� Checking @{username} for new videos...")
        
        profile_url = f"https://www.tiktok.com/@{username}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(profile_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch profile page: {response.status_code}")
            return []
        
        # Extract video IDs using regex patterns
        content = response.text
        
        # Look for video ID patterns in the HTML/JavaScript
        patterns = [
            r'/video/(\d{19})',  # Standard TikTok video ID pattern
            r'"id":"(\d{19})"',   # JSON embedded video IDs
            r'video/(\d{19})',    # Alternative pattern
        ]
        
        video_ids = set()
        for pattern in patterns:
            matches = re.findall(pattern, content)
            video_ids.update(matches)
        
        # Convert to sorted list (newest typically appear first)
        video_ids = sorted(list(video_ids), reverse=True)[:limit]
        
        print(f"📊 Found {len(video_ids)} video IDs: {video_ids}")
        return video_ids
        
    except Exception as e:
        print(f"❌ Error fetching video IDs: {e}")
        return []

def add_video_via_api(video_id, api_key, domain):
    """Add a video using your existing Flask API"""
    try:
        url = f"{domain}/api/add/{video_id}"
        
        headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        print(f"🚀 Adding video {video_id} via API...")
        response = requests.post(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                print(f"✅ Successfully added video {video_id}")
                return True
            else:
                print(f"⚠️  API returned: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ API error details: {error_data}")
            except:
                print(f"❌ API response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error calling API: {e}")
        return False

# Get environment variables
api_key = os.environ.get('MGED_API_KEY', 'default_dev_key')
domain = os.environ.get('MGED_DOMAIN', 'https://minigolfevery.day')

print(f"🌐 Using domain: {domain}")
print(f"🔑 Using API key: {api_key[:8]}...")

# Get current video count from local file
current_videos = []
if os.path.exists('tiktok_videos.json'):
    with open('tiktok_videos.json', 'r') as f:
        data = json.load(f)
        current_videos = data.get('videos', [])

current_ids = {v['video_id'] for v in current_videos}
print(f"📚 Current database has {len(current_videos)} videos")

if current_videos:
    print(f"🎬 Most recent video: {current_videos[0].get('title', 'Unknown')[:60]}...")

# Get latest video IDs from TikTok
latest_video_ids = get_latest_video_ids_simple()

if not latest_video_ids:
    print("❌ Could not fetch any video IDs")
    exit(1)

# Find new videos
new_video_ids = [vid for vid in latest_video_ids if vid not in current_ids]

if new_video_ids:
    print(f"🆕 Found {len(new_video_ids)} new video(s): {new_video_ids}")
    
    success_count = 0
    for video_id in new_video_ids:
        if add_video_via_api(video_id, api_key, domain):
            success_count += 1
        else:
            print(f"⚠️  Failed to add video {video_id}")
    
    if success_count > 0:
        print(f"✅ Successfully added {success_count} new video(s)")
        
        # Reload the updated JSON file to get new count
        if os.path.exists('tiktok_videos.json'):
            with open('tiktok_videos.json', 'r') as f:
                updated_data = json.load(f)
                updated_videos = updated_data.get('videos', [])
                print(f"📊 Database now has {len(updated_videos)} total videos")
                
                if updated_videos:
                    print(f"🎬 Newest video: {updated_videos[0].get('title', 'Unknown')[:60]}...")
    else:
        print("❌ No videos were added successfully")
else:
    print("ℹ️  No new videos found")

EOF

# Check if the process was successful
if [ $? -eq 0 ]; then
    log_message "TikTok video update completed successfully"
    
    # Get current video count
    if [ -f "tiktok_videos.json" ]; then
        VIDEO_COUNT=$($PYTHON_CMD -c "import json; data=json.load(open('tiktok_videos.json')); print(len(data.get('videos', [])))")
        log_message "Total videos in database: $VIDEO_COUNT"
        
        # Get the most recent video
        LATEST_VIDEO=$($PYTHON_CMD -c "import json; data=json.load(open('tiktok_videos.json')); print(data['videos'][0]['title'][:60] if data['videos'] else 'None')")
        log_message "Most recent video: $LATEST_VIDEO..."
    fi
    
    log_message "=== Update process completed successfully ==="
else
    log_message "ERROR: TikTok video update failed"
    exit 1
fi

# Cleanup old backup files (keep last 7 days)
find "$SCRIPT_DIR" -name "tiktok_videos_backup_*.json" -mtime +7 -delete 2>/dev/null

# Cleanup old log files (keep last 30 days)
find "$SCRIPT_DIR" -name "cron*.log" -mtime +30 -delete 2>/dev/null

log_message "=== Cron job completed ==="
