#!/usr/bin/env python3
"""
GitHub Actions script to update TikTok videos using yt-dlp
This runs in the cloud and commits changes back to the repo
"""

import json
import os
import subprocess
import sys
from datetime import datetime

def run_ytdlp(username="minigolfeveryday", limit=50):
    """Use yt-dlp to fetch video information"""
    try:
        profile_url = f"https://www.tiktok.com/@{username}"
        
        print(f"🌐 Fetching videos from: {profile_url}")
        
        # Use yt-dlp to extract video info with view counts
        cmd = [
            'yt-dlp',
            '--flat-playlist',
            '--print', '%(id)s|%(title)s|%(upload_date)s|%(view_count)s|%(like_count)s|%(comment_count)s',
            '--playlist-end', str(limit),
            profile_url
        ]
        
        print(f"🚀 Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            print(f"❌ yt-dlp error: {result.stderr}")
            return []
        
        videos = []
        print(f"📋 Raw yt-dlp output:")
        print(result.stdout)
        
        for line in result.stdout.strip().split('\n'):
            if '|' in line and line.strip():
                parts = line.split('|', 5)  # Split into max 6 parts
                if len(parts) >= 3:
                    video_id = parts[0].strip()
                    title = parts[1].strip() if len(parts) > 1 else f"TikTok Video {video_id}"
                    upload_date = parts[2].strip() if len(parts) > 2 else datetime.now().strftime('%Y%m%d')
                    view_count = parts[3].strip() if len(parts) > 3 else '0'
                    like_count = parts[4].strip() if len(parts) > 4 else '0'
                    comment_count = parts[5].strip() if len(parts) > 5 else '0'
                    
                    # Fix empty titles
                    if not title or title.strip() == '':
                        title = f"TikTok Video {video_id}"
                        print(f"  ⚠️  Empty title for {video_id}, using fallback: {title}")
                    
                    # Convert counts to integers, defaulting to 0
                    try:
                        view_count = int(view_count) if view_count.isdigit() else 0
                        like_count = int(like_count) if like_count.isdigit() else 0
                        comment_count = int(comment_count) if comment_count.isdigit() else 0
                    except ValueError:
                        view_count = like_count = comment_count = 0
                    
                    # Basic validation
                    if video_id and video_id.isdigit() and len(video_id) >= 15:
                        videos.append({
                            'video_id': video_id,
                            'title': title,
                            'upload_date': upload_date,
                            'view_count': view_count,
                            'like_count': like_count,
                            'comment_count': comment_count,
                            'url': f"https://www.tiktok.com/@{username}/video/{video_id}"
                        })
                    else:
                        print(f"  ⚠️  Skipping invalid video_id: {video_id}")
                else:
                    print(f"  ⚠️  Skipping line with insufficient parts: {line[:50]}...")
        
        print(f"✅ Successfully parsed {len(videos)} videos")
        for i, video in enumerate(videos[:5]):  # Show first 5
            print(f"  {i+1}. {video['video_id']} - {video['title'][:50]}...")
        
        return videos
        
    except subprocess.TimeoutExpired:
        print("❌ yt-dlp timed out after 5 minutes")
        return []
    except Exception as e:
        print(f"❌ Error running yt-dlp: {e}")
        return []

def load_existing_videos():
    """Load existing video database"""
    if os.path.exists('tiktok_videos.json'):
        try:
            with open('tiktok_videos.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('videos', [])
        except Exception as e:
            print(f"⚠️  Error loading existing videos: {e}")
    return []

def save_videos(videos):
    """Save videos to JSON file"""
    try:
        data = {
            'videos': videos,
            'last_updated': datetime.now().isoformat(),
            'total_count': len(videos)
        }
        
        with open('tiktok_videos.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(videos)} videos to tiktok_videos.json")
        return True
        
    except Exception as e:
        print(f"❌ Error saving videos: {e}")
        return False

def main():
    print("🤖 GitHub Actions TikTok Video Updater")
    print("=" * 50)
    
    # Load existing videos
    existing_videos = load_existing_videos()
    existing_ids = set(v['video_id'] for v in existing_videos)
    print(f"📚 Loaded {len(existing_videos)} existing videos")
    
    if existing_videos:
        print(f"🎬 Most recent: {existing_videos[0].get('title', 'Unknown')[:60]}...")
    
    # Fetch latest videos with yt-dlp
    print("\nFetching latest videos...")
    new_videos = run_ytdlp()
    
    if not new_videos:
        print("❌ No videos fetched - keeping existing database unchanged")
        return
    
    # Find truly new videos
    truly_new = [v for v in new_videos if v['video_id'] not in existing_ids]
    print(f"🆕 Found {len(truly_new)} new videos")
    
    if truly_new:
        for video in truly_new:
            print(f"  ➕ {video['video_id']} - {video['title'][:50]}...")
    
    # Merge: put new videos at the start, keep existing videos
    # This preserves the order and ensures new videos appear first
    all_videos = truly_new + existing_videos
    
    # Safety check: never save an empty video list if we had existing videos
    if not all_videos and existing_videos:
        print("❌ SAFETY CHECK: Refusing to save empty video list when existing videos exist!")
        print("❌ This suggests a parsing error. Keeping existing database unchanged.")
        return
    
    # Limit to most recent 200 videos to prevent file from growing too large
    if len(all_videos) > 200:
        all_videos = all_videos[:200]
        print(f"📉 Trimmed to most recent 200 videos")
    
    print(f"📊 Total videos after update: {len(all_videos)}")
    
    # Final safety check before saving
    if len(all_videos) == 0:
        print("❌ SAFETY CHECK: Refusing to save empty video list!")
        return
    
    # Save updated database
    if save_videos(all_videos):
        if truly_new:
            print(f"🎉 Successfully added {len(truly_new)} new videos!")
            print(f"🎬 Newest video: {all_videos[0].get('title', 'Unknown')[:60]}...")
        else:
            print("ℹ️  No new videos found - database is up to date")
    else:
        print("❌ Failed to save videos")
        sys.exit(1)

if __name__ == "__main__":
    main()
