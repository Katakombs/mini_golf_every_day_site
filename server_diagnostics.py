#!/usr/bin/env python3
"""
Diagnostic script to check the server's TikTok video data
"""

import json
import os
import sys
from datetime import datetime

def check_video_data():
    """Check the current state of video data"""
    print("🔍 Mini Golf Every Day - Server Diagnostics")
    print("=" * 50)
    
    # Check if file exists
    video_file = 'tiktok_videos.json'
    if not os.path.exists(video_file):
        print(f"❌ {video_file} does not exist!")
        return False
    
    print(f"✅ {video_file} exists")
    
    # Check file size
    file_size = os.path.getsize(video_file)
    print(f"📊 File size: {file_size:,} bytes")
    
    if file_size == 0:
        print("❌ File is empty!")
        return False
    
    # Try to load JSON
    try:
        with open(video_file, 'r') as f:
            data = json.load(f)
        print("✅ JSON file is valid")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Check video data
    videos = data.get('videos', [])
    video_count = len(videos)
    print(f"📊 Video count: {video_count}")
    
    if video_count == 0:
        print("❌ No videos found in database!")
        return False
    
    # Check recent videos
    print(f"✅ {video_count} videos found")
    
    # Show most recent videos
    print("\n📱 Most recent videos:")
    for i, video in enumerate(videos[:5]):
        title = video.get('title', 'No title')[:50]
        video_id = video.get('video_id', 'No ID')
        upload_date = video.get('upload_date', 'No date')
        print(f"  {i+1}. {title}... (ID: {video_id}, Date: {upload_date})")
    
    # Check last updated
    last_updated = data.get('last_updated')
    if last_updated:
        print(f"\n🕐 Last updated: {last_updated}")
        
        # Parse and check if it's recent
        try:
            updated_time = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            now = datetime.now()
            age = now - updated_time.replace(tzinfo=None)
            print(f"🕐 Age: {age.days} days, {age.seconds // 3600} hours ago")
        except:
            print(f"🕐 Could not parse timestamp: {last_updated}")
    else:
        print("⚠️  No last_updated timestamp found")
    
    return True

def test_api_endpoints():
    """Test the Flask API endpoints"""
    print("\n🔍 Testing API Endpoints")
    print("=" * 30)
    
    try:
        # Import Flask app
        from flask_app import app
        
        with app.test_client() as client:
            # Test status endpoint
            response = client.get('/api/status')
            print(f"📡 /api/status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Video count: {data.get('video_count', 0)}")
                print(f"   Videos file exists: {data.get('videos_file_exists', False)}")
                print(f"   Last updated: {data.get('last_updated', 'Unknown')}")
            else:
                print(f"   Error: {response.get_data(as_text=True)}")
            
            # Test videos endpoint
            response = client.get('/api/videos')
            print(f"📡 /api/videos: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"   Video count: {data.get('count', 0)}")
                print(f"   Status: {data.get('status', 'Unknown')}")
            else:
                print(f"   Error: {response.get_data(as_text=True)}")
                
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    # Check video data
    if check_video_data():
        # Test API endpoints
        test_api_endpoints()
        print("\n✅ Diagnostics complete!")
    else:
        print("\n❌ Critical issues found with video data!")
        sys.exit(1)
