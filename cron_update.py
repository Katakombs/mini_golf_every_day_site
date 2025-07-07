#!/usr/bin/env python3
"""
Automated TikTok video update script for cron jobs
This script updates the video database and logs the results
"""

import sys
import os
import json
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add current directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Load environment variables from .env file if it exists
env_file = os.path.join(script_dir, '.env')
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Configuration
DOMAIN = os.environ.get('MGED_DOMAIN', "https://minigolfevery.day")
API_KEY = os.environ.get('MGED_API_KEY', 'default_dev_key')
LOG_FILE = os.path.join(script_dir, "cron_update.log")
MAX_LOG_SIZE = 1024 * 1024  # 1MB

def setup_logging():
    """Set up logging with rotation"""
    # Rotate log if it gets too large
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        backup_log = LOG_FILE + ".old"
        if os.path.exists(backup_log):
            os.remove(backup_log)
        os.rename(LOG_FILE, backup_log)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def check_api_status(domain):
    """Check if the API is responding"""
    try:
        response = requests.get(f"{domain}/api/status", timeout=30)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def update_videos(domain):
    """Trigger the video update endpoint"""
    try:
        response = requests.post(f"{domain}/api/update", timeout=300)  # 5 minute timeout
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def get_video_count(domain):
    """Get current video count"""
    try:
        response = requests.get(f"{domain}/api/videos", timeout=30)
        if response.status_code == 200:
            data = response.json()
            return len(data.get('videos', []))
        else:
            return None
    except Exception as e:
        return None

def make_secure_api_call(endpoint, method='GET', timeout=30):
    """Make a secure API call with proper authentication"""
    headers = {'X-API-Key': API_KEY}
    url = f"{DOMAIN}{endpoint}"
    
    try:
        if method.upper() == 'POST':
            response = requests.post(url, headers=headers, timeout=timeout)
        else:
            response = requests.get(url, headers=headers, timeout=timeout)
        
        return response.status_code == 200, response.json() if response.status_code == 200 else response.text
    except Exception as e:
        return False, str(e)

def main():
    logger = setup_logging()
    
    logger.info("="*60)
    logger.info("🤖 Mini Golf Every Day - Automated Update Started")
    logger.info("="*60)
    
    # Check if API is available
    logger.info("🔍 Checking API status...")
    status_ok, status_data = check_api_status(DOMAIN)
    
    if not status_ok:
        logger.error(f"❌ API status check failed: {status_data}")
        return 1
    
    logger.info("✅ API is responding")
    if isinstance(status_data, dict):
        logger.info(f"   Current video count: {status_data.get('video_count', 'unknown')}")
        logger.info(f"   Last updated: {status_data.get('last_updated', 'unknown')}")
        logger.info(f"   Automation available: {status_data.get('automation_available', 'unknown')}")
    
    # Get current video count
    initial_count = get_video_count(DOMAIN)
    logger.info(f"📊 Initial video count: {initial_count}")
    
    # Trigger update
    logger.info("🔄 Starting video update...")
    update_ok, update_data = update_videos(DOMAIN)
    
    if not update_ok:
        logger.error(f"❌ Video update failed: {update_data}")
        return 1
    
    logger.info("✅ Video update completed successfully")
    if isinstance(update_data, dict):
        logger.info(f"   Videos processed: {update_data.get('videos_processed', 'unknown')}")
        logger.info(f"   Videos updated: {update_data.get('videos_updated', 'unknown')}")
        logger.info(f"   Message: {update_data.get('message', 'No message')}")
    
    # Get final video count
    final_count = get_video_count(DOMAIN)
    logger.info(f"📊 Final video count: {final_count}")
    
    if initial_count is not None and final_count is not None:
        new_videos = final_count - initial_count
        if new_videos > 0:
            logger.info(f"🎉 Added {new_videos} new video(s)!")
        elif new_videos == 0:
            logger.info("ℹ️  No new videos found")
        else:
            logger.warning(f"⚠️  Video count decreased by {abs(new_videos)}")
    
    logger.info("="*60)
    logger.info("✅ Automated update completed successfully")
    logger.info("="*60)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Update interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"💥 Unexpected error: {e}")
        sys.exit(1)
