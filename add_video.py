#!/usr/bin/env python3
"""
Simple script to add new TikTok videos to your watch page
Usage: python add_video.py VIDEO_ID_OR_URL [TITLE]
"""

import sys
import re
from tiktok_automation import TikTokVideoManager

def extract_video_id(input_str: str) -> str:
    """Extract video ID from URL or return as-is if already an ID"""
    # Pattern to match TikTok video URLs
    url_pattern = r'https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/(\d+)'
    match = re.search(url_pattern, input_str)
    
    if match:
        return match.group(1)
    
    # Check if it's already a video ID (sequence of digits)
    if re.match(r'^\d+$', input_str):
        return input_str
    
    raise ValueError(f"Invalid video ID or URL: {input_str}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python add_video.py VIDEO_ID_OR_URL [TITLE]")
        print("Examples:")
        print("  python add_video.py 7522583834320260365")
        print("  python add_video.py https://www.tiktok.com/@minigolfeveryday/video/7522583834320260365")
        sys.exit(1)
    
    video_input = sys.argv[1]
    title = sys.argv[2] if len(sys.argv) > 2 else ""
    
    try:
        video_id = extract_video_id(video_input)
        
        manager = TikTokVideoManager()
        
        # Load existing videos
        existing_videos = manager.load_video_data()
        
        # Check if video already exists
        existing_ids = [v['video_id'] for v in existing_videos]
        if video_id in existing_ids:
            print(f"⚠️  Video {video_id} already exists in the list")
            return
        
        # Add new video to the beginning of the list
        new_video = {
            'video_id': video_id,
            'title': title,
            'upload_date': '',
            'url': f"https://www.tiktok.com/@minigolfeveryday/video/{video_id}"
        }
        
        updated_videos = [new_video] + existing_videos[:29]  # Keep max 30 videos
        
        # Save and update HTML
        manager.save_video_data(updated_videos)
        success = manager.update_watch_html(updated_videos)
        
        if success:
            print(f"✅ Successfully added video {video_id}")
            print(f"📊 Total videos: {len(updated_videos)}")
        else:
            print("❌ Failed to update watch.html")
            
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
