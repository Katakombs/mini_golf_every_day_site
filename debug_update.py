#!/usr/bin/env python3
"""
Debug version of the TikTok video updater to identify issues
"""

import json
import os
import subprocess
import sys
from datetime import datetime

def debug_environment():
    """Debug the current environment"""
    print("🔍 Environment Debug Info:")
    print(f"  Python version: {sys.version}")
    print(f"  Current directory: {os.getcwd()}")
    print(f"  Files in directory: {os.listdir('.')}")
    
    # Check if tiktok_videos.json exists
    if os.path.exists('tiktok_videos.json'):
        try:
            with open('tiktok_videos.json', 'r') as f:
                data = json.load(f)
                print(f"  Current video count: {len(data.get('videos', []))}")
                if data.get('videos'):
                    print(f"  Most recent: {data['videos'][0].get('title', 'Unknown')[:50]}...")
        except Exception as e:
            print(f"  Error reading tiktok_videos.json: {e}")
    else:
        print("  tiktok_videos.json does not exist")
    
    # Check yt-dlp
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True, timeout=10)
        print(f"  yt-dlp version: {result.stdout.strip()}")
    except Exception as e:
        print(f"  yt-dlp error: {e}")

def test_ytdlp_simple():
    """Test yt-dlp with a simple command"""
    print("\n🧪 Testing yt-dlp basic functionality...")
    
    try:
        # Test with a simple single video first
        cmd = [
            'yt-dlp',
            '--flat-playlist',
            '--print', '%(id)s|%(title)s|%(upload_date)s',
            '--playlist-end', '3',  # Just get 3 videos for testing
            'https://www.tiktok.com/@minigolfeveryday'
        ]
        
        print(f"🚀 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.strip().split('\n')
            print(f"✅ Got {len(lines)} video lines")
            return True
        else:
            print("❌ yt-dlp failed or returned no output")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ yt-dlp timed out")
        return False
    except Exception as e:
        print(f"❌ Error running yt-dlp: {e}")
        return False

def backup_current_file():
    """Backup current tiktok_videos.json"""
    if os.path.exists('tiktok_videos.json'):
        backup_name = f"tiktok_videos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open('tiktok_videos.json', 'r') as src:
                with open(backup_name, 'w') as dst:
                    dst.write(src.read())
            print(f"✅ Created backup: {backup_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return False
    return True

def main():
    print("🔍 TikTok Video Updater - DEBUG MODE")
    print("=" * 50)
    
    # Debug environment
    debug_environment()
    
    # Backup current file
    if not backup_current_file():
        print("❌ Failed to backup current file - stopping")
        return
    
    # Test yt-dlp
    if test_ytdlp_simple():
        print("\n✅ yt-dlp test passed - the tool is working")
        print("🔄 Now running the full update...")
        
        # Import and run the main updater
        try:
            import sys
            sys.path.append('.github/workflows')
            from update_videos import main as update_main
            update_main()
        except Exception as e:
            print(f"❌ Error running main updater: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n❌ yt-dlp test failed - there's an issue with the environment")
        print("🔍 This explains why the production run might be failing")

if __name__ == "__main__":
    main()
