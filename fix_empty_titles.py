#!/usr/bin/env python3
"""
Fix existing videos with empty titles in the database
"""

import json
from datetime import datetime

def fix_empty_titles():
    """Fix videos with empty titles in the current database"""
    
    print("🔧 Fixing empty titles in tiktok_videos.json...")
    
    # Load current data
    with open('tiktok_videos.json', 'r') as f:
        data = json.load(f)
    
    videos = data.get('videos', [])
    print(f"📊 Total videos: {len(videos)}")
    
    # Find videos with empty titles
    empty_title_videos = []
    fixed_count = 0
    
    for video in videos:
        if not video.get('title') or video['title'].strip() == '':
            empty_title_videos.append(video)
            # Fix the title
            video['title'] = f"TikTok Video {video['video_id']}"
            fixed_count += 1
            print(f"  ✅ Fixed: {video['video_id']} -> {video['title']}")
    
    if fixed_count > 0:
        print(f"🔧 Fixed {fixed_count} videos with empty titles")
        
        # Update the last_updated timestamp
        data['last_updated'] = datetime.now().isoformat()
        
        # Save the fixed data
        with open('tiktok_videos.json', 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("✅ Saved fixed database")
    else:
        print("ℹ️  No videos with empty titles found")
    
    return fixed_count

if __name__ == "__main__":
    fix_empty_titles()
