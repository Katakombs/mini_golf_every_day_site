#!/usr/bin/env python3
"""
Lightweight database update script for shared hosting
This script only updates the database from existing JSON data
"""

import os
import json
import subprocess
import gc
import sys
from datetime import datetime

def load_video_data():
    """Load existing video data from JSON file"""
    try:
        if os.path.exists('tiktok_videos.json'):
            with open('tiktok_videos.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            videos = data.get('videos', [])
            print(f"✅ Loaded {len(videos)} videos from JSON file")
            return videos
        else:
            print("❌ tiktok_videos.json not found")
            return []
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return []

def update_database_only():
    """Update database from JSON without fetching new videos"""
    print("🗄️  Database Update Only - Shared Hosting Mode")
    print("=" * 50)
    
    # Load videos from JSON
    videos = load_video_data()
    if not videos:
        print("❌ No videos found in JSON file")
        return False
    
    # Update database
    print("🗄️  Updating MySQL database...")
    try:
        result = subprocess.run(['python3', 'migrate_videos_to_db.py'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ MySQL database updated successfully")
            print(f"   Updated {len(videos)} videos in database")
            return True
        else:
            print(f"⚠️  Database update failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠️  Could not run database migration: {e}")
        return False
    finally:
        # Force garbage collection
        gc.collect()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Update database from JSON data only')
    parser.add_argument('--yes', '-y', action='store_true', 
                       help='Skip confirmation prompt and proceed automatically')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("This script will update the database from existing JSON data.")
        print("This is optimized for shared hosting environments.\n")
    
    if args.yes:
        proceed = True
        if not args.quiet:
            print("Auto-proceeding due to --yes flag...")
    else:
        response = input("Do you want to proceed? (y/N): ").lower().strip()
        proceed = response in ['y', 'yes']
    
    if proceed:
        success = update_database_only()
        if success:
            if not args.quiet:
                print(f"\n✅ Database update completed successfully")
            return 0
        else:
            print("\n❌ Database update failed. Please check the issues above.")
            return 1
    else:
        if not args.quiet:
            print("Operation cancelled.")
        return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 