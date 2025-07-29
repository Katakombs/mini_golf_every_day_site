#!/usr/bin/env python3
"""
One-time script to fetch ALL videos from @minigolfeveryday TikTok channel
This will replace your current 30-video database with all 177+ videos
"""

import sys
import os
import json
import glob
import time
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tiktok_automation import TikTokVideoManager

def cleanup_old_backups(keep_days=3):
    """Clean up old backup files to save disk space"""
    try:
        cutoff_time = time.time() - (keep_days * 24 * 60 * 60)
        backup_files = glob.glob('tiktok_videos_backup_*.json')
        
        deleted_count = 0
        for backup_file in backup_files:
            if os.path.getmtime(backup_file) < cutoff_time:
                os.remove(backup_file)
                deleted_count += 1
        
        if deleted_count > 0:
            print(f"🧹 Cleaned up {deleted_count} old backup files")
    except Exception as e:
        print(f"⚠️  Could not cleanup old backups: {e}")

def fetch_all_videos():
    """Fetch all videos from the TikTok channel"""
    print("🎬 Mini Golf Every Day - Full Video Fetch")
    print("=" * 50)
    
    manager = TikTokVideoManager()
    
    print("📊 Current database status:")
    try:
        current_videos = manager.load_video_data()
        print(f"   Current videos in database: {len(current_videos)}")
    except:
        print("   No existing database found")
        current_videos = []
    
    print("\n🔍 Fetching ALL videos from @minigolfeveryday...")
    print("   This may take 2-3 minutes...")
    
    # Fetch a large number to ensure we get everything
    # TikTok channels rarely have more than 500 videos
    all_videos = manager.get_latest_videos_ytdlp(limit=500)
    
    if not all_videos:
        print("❌ Failed to fetch videos with yt-dlp. Trying fallback method...")
        all_videos = manager.manual_video_list()
    
    if all_videos:
        print(f"\n✅ Successfully fetched {len(all_videos)} videos!")
        
        # Show some sample videos
        print(f"\n📝 Sample videos found:")
        for i, video in enumerate(all_videos[:5]):
            day_match = video['title'].lower().find('day')
            day_info = ""
            if day_match != -1:
                try:
                    import re
                    day_num = re.search(r'day (\d+)', video['title'].lower())
                    if day_num:
                        day_info = f" (Day {day_num.group(1)})"
                except:
                    pass
            print(f"   {i+1}. {video['title'][:60]}...{day_info}")
        
        if len(all_videos) > 5:
            print(f"   ... and {len(all_videos) - 5} more videos")
        
        # Backup current data (disabled to prevent excessive backup files)
        # Comment out this section if backups are being created too frequently
        """
        if current_videos:
            backup_file = f"tiktok_videos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(backup_file, 'w') as f:
                    json.dump({
                        'last_updated': datetime.now().isoformat(),
                        'videos': current_videos
                    }, f, indent=2)
                print(f"\n💾 Backed up current database to: {backup_file}")
                
                # Cleanup old backup files (keep last 3 days)
                cleanup_old_backups()
                
            except Exception as e:
                print(f"⚠️  Could not create backup: {e}")
        """
        
        # Save all videos
        print(f"\n💾 Saving {len(all_videos)} videos to database...")
        manager.save_video_data(all_videos)
        
        # Update MySQL database
        print("🗄️  Updating MySQL database...")
        try:
            import subprocess
            result = subprocess.run(['python', 'migrate_videos_to_db.py'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Database updated successfully")
            else:
                print(f"⚠️  Database update failed: {result.stderr}")
                print("   JSON file is still updated and website will work")
        except Exception as e:
            print(f"⚠️  Could not run database migration: {e}")
            print("   JSON file is updated, manually run: python migrate_videos_to_db.py")
        
        # Update HTML
        print("Updating watch.html with all videos...")
        success = manager.update_watch_html(all_videos)
        
        if success:
            print("✅ Successfully updated watch.html")
        else:
            print("⚠️  Watch.html update had issues (but videos are saved)")
        
        print(f"\n🎉 Complete! Your database now has {len(all_videos)} videos")
        print(f"📈 Increase from {len(current_videos)} to {len(all_videos)} videos")
        
        # Show oldest and newest
        if len(all_videos) >= 2:
            oldest = min(all_videos, key=lambda x: x.get('upload_date', ''))
            newest = max(all_videos, key=lambda x: x.get('upload_date', ''))
            
            print(f"\n📅 Date range:")
            print(f"   Oldest: {oldest['title'][:50]}... ({oldest.get('upload_date', 'Unknown')})")
            print(f"   Newest: {newest['title'][:50]}... ({newest.get('upload_date', 'Unknown')})")
        
        return True
        
    else:
        print("❌ Failed to fetch videos. Please check:")
        print("   1. Internet connection")
        print("   2. TikTok channel @minigolfeveryday is accessible")
        print("   3. yt-dlp is properly installed")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch all videos from @minigolfeveryday TikTok channel')
    parser.add_argument('--yes', '-y', action='store_true', 
                       help='Skip confirmation prompt and proceed automatically')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("This script will fetch ALL videos from @minigolfeveryday")
        print("and replace your current 30-video database.\n")
    
    if args.yes:
        proceed = True
        if not args.quiet:
            print("Auto-proceeding due to --yes flag...")
    else:
        response = input("Do you want to proceed? (y/N): ").lower().strip()
        proceed = response in ['y', 'yes']
    
    if proceed:
        success = fetch_all_videos()
        if success:
            if not args.quiet:
                print("\n🚀 Next steps:")
                print("   1. Upload the updated tiktok_videos.json to your server")
                print("   2. Your automation will now maintain all 177+ videos")
                print("   3. Your website will show the complete video collection")
            return 0
        else:
            print("\n❌ Fetch failed. Please try again or check the issues above.")
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
