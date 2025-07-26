#!/usr/bin/env python3
"""
Simple video update script that provides proper statistics
This script will update videos and output the correct stats format
"""

import sys
import os
import json
import subprocess
import time
from datetime import datetime

def load_video_data():
    """Load existing video data from JSON file"""
    try:
        with open('tiktok_videos.json', 'r') as f:
            data = json.load(f)
        return data.get('videos', [])
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_video_data(videos):
    """Save video data to JSON file"""
    data = {
        'videos': videos,
        'last_updated': datetime.now().isoformat(),
        'total_count': len(videos)
    }
    
    with open('tiktok_videos.json', 'w') as f:
        json.dump(data, f, indent=2)

def get_latest_videos_ytdlp(limit=200):
    """Get latest videos using yt-dlp"""
    try:
        # Try to run yt-dlp to get video metadata with view counts
        cmd = [
            'yt-dlp',
            '--flat-playlist',
            '--print', '%(id)s|%(title)s|%(upload_date)s|%(view_count)s|%(like_count)s|%(comment_count)s',
            '--playlist-end', str(limit),
            'https://www.tiktok.com/@minigolfeveryday'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            print(f"yt-dlp failed: {result.stderr}")
            return []
        
        videos = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                try:
                    parts = line.split('|', 5)  # Split into max 6 parts
                    if len(parts) >= 3:
                        video_id = parts[0]
                        title = parts[1]
                        upload_date = parts[2]
                        view_count = parts[3] if len(parts) > 3 else '0'
                        like_count = parts[4] if len(parts) > 4 else '0'
                        comment_count = parts[5] if len(parts) > 5 else '0'
                        
                        # Convert counts to integers, defaulting to 0
                        try:
                            view_count = int(view_count) if view_count.isdigit() else 0
                            like_count = int(like_count) if like_count.isdigit() else 0
                            comment_count = int(comment_count) if comment_count.isdigit() else 0
                        except ValueError:
                            view_count = like_count = comment_count = 0
                        
                        videos.append({
                            'video_id': video_id,
                            'title': title,
                            'upload_date': upload_date,
                            'view_count': view_count,
                            'like_count': like_count,
                            'comment_count': comment_count,
                            'url': f'https://www.tiktok.com/@minigolfeveryday/video/{video_id}'
                        })
                except Exception as e:
                    print(f"Error parsing line: {line}, error: {e}")
                    continue
        
        return videos
        
    except subprocess.TimeoutExpired:
        print("yt-dlp timed out")
        return []
    except Exception as e:
        print(f"Error running yt-dlp: {e}")
        return []

def update_videos():
    """Update videos and return statistics"""
    print("🎬 Mini Golf Every Day - Video Update")
    print("=" * 50)
    
    # Load existing videos
    print("📊 Loading existing video database...")
    current_videos = load_video_data()
    current_count = len(current_videos)
    print(f"   Current videos in database: {current_count}")
    
    # Get current video IDs for comparison
    current_ids = set(video['video_id'] for video in current_videos)
    
    # Fetch latest videos
    print("\n🔍 Fetching latest videos from @minigolfeveryday...")
    latest_videos = get_latest_videos_ytdlp()
    
    if not latest_videos:
        print("❌ Failed to fetch videos")
        return {
            'processed': 0,
            'new': 0,
            'updated': 0,
            'success': False
        }
    
    # Compare and find new/updated videos
    new_videos = []
    updated_videos = []
    
    for video in latest_videos:
        video_id = video['video_id']
        if video_id not in current_ids:
            new_videos.append(video)
        else:
            # Check if existing video needs updating (title might have changed)
            existing_video = next((v for v in current_videos if v['video_id'] == video_id), None)
            if existing_video and existing_video.get('title') != video.get('title'):
                updated_videos.append(video)
    
    # Merge all videos (latest videos take precedence)
    merged_videos = latest_videos
    
    # Save updated data
    print(f"\n💾 Saving {len(merged_videos)} videos to database...")
    save_video_data(merged_videos)
    
    # Update database
    print("🗄️  Updating MySQL database...")
    try:
        result = subprocess.run(['python3', 'migrate_videos_to_db.py'], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✅ MySQL database updated successfully")
        else:
            print(f"⚠️  Database update failed: {result.stderr}")
    except Exception as e:
        print(f"⚠️  Could not run database migration: {e}")
    
    # Calculate statistics
    stats = {
        'processed': len(merged_videos),
        'new': len(new_videos),
        'updated': len(updated_videos),
        'success': True
    }
    
    # Output statistics in the format expected by the server
    print(f"\n📈 Update Statistics:")
    print(f"   Processed: {stats['processed']} videos")
    print(f"   New: {stats['new']} videos")
    print(f"   Updated: {stats['updated']} videos")
    
    if new_videos:
        print(f"\n🆕 New videos found:")
        for video in new_videos[:5]:  # Show first 5 new videos
            print(f"   - {video['title'][:60]}...")
    
    if updated_videos:
        print(f"\n🔄 Updated videos:")
        for video in updated_videos[:5]:  # Show first 5 updated videos
            print(f"   - {video['title'][:60]}...")
    
    print(f"\n🎉 Update complete! Database now has {len(merged_videos)} videos")
    
    return stats

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Update TikTok videos with proper statistics')
    parser.add_argument('--yes', '-y', action='store_true', 
                       help='Skip confirmation prompt and proceed automatically')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Reduce output verbosity')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print("This script will update TikTok videos from @minigolfeveryday")
        print("and provide proper statistics.\n")
    
    if args.yes:
        proceed = True
        if not args.quiet:
            print("Auto-proceeding due to --yes flag...")
    else:
        response = input("Do you want to proceed? (y/N): ").lower().strip()
        proceed = response in ['y', 'yes']
    
    if proceed:
        stats = update_videos()
        if stats['success']:
            if not args.quiet:
                print(f"\n✅ Update completed successfully")
                print(f"   Processed: {stats['processed']} videos")
                print(f"   New: {stats['new']} videos") 
                print(f"   Updated: {stats['updated']} videos")
            return 0
        else:
            print("\n❌ Update failed. Please try again or check the issues above.")
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
