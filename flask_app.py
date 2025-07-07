#!/usr/bin/env python3
"""
Flask web application for Mini Golf Every Day
Serves static files and provides TikTok automation
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import json
import sys
import re
from datetime import datetime

# Load environment variables from .env file if it exists
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from tiktok_automation import TikTokVideoManager
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False
    TikTokVideoManager = None

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/api/status')
def api_status():
    """Get system status"""
    try:
        videos_exist = os.path.exists('tiktok_videos.json')
        video_count = 0
        last_updated = None
        
        if videos_exist:
            try:
                with open('tiktok_videos.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    video_count = len(data.get('videos', []))
                    last_updated = data.get('last_updated')
            except:
                pass
        
        return jsonify({
            'status': 'ok',
            'python_version': sys.version,
            'videos_file_exists': videos_exist,
            'video_count': video_count,
            'last_updated': last_updated,
            'automation_available': AUTOMATION_AVAILABLE
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@app.route('/api/videos')
def api_videos():
    """Get current videos"""
    try:
        if os.path.exists('tiktok_videos.json'):
            with open('tiktok_videos.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify({
                    'status': 'ok',
                    'videos': data.get('videos', []),
                    'count': len(data.get('videos', []))
                })
        else:
            return jsonify({'status': 'error', 'error': 'No videos file found'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

def get_video_info_fallback(video_id):
    """
    Get video info using direct web scraping (no yt-dlp needed)
    Note: TikTok now uses heavy JavaScript, so this may not work reliably
    """
    try:
        import requests
        
        video_url = f"https://www.tiktok.com/@minigolfeveryday/video/{video_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'identity',  # No compression
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(video_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # TikTok now uses heavy JavaScript, so basic scraping often fails
            # Look for any useful patterns in the HTML, but don't expect much
            title_patterns = [
                r'<meta name="description" content="([^"]*)"',
                r'<meta property="og:title" content="([^"]*)"',
                r'<meta property="og:description" content="([^"]*)"',
                r'"desc":"([^"]*)"',
                r'"title":"([^"]*)"',
            ]
            
            for pattern in title_patterns:
                match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                if match:
                    title = match.group(1).strip()
                    # Filter out generic TikTok titles
                    if title and len(title) > 10 and 'TikTok' not in title and 'Make Your Day' not in title:
                        # Clean up title
                        title = re.sub(r'\s*\|\s*TikTok$', '', title)
                        title = re.sub(r'\s*-\s*TikTok$', '', title)
                        title = title.strip()
                        
                        return {
                            'title': title,
                            'upload_date': datetime.now().strftime('%Y%m%d'),
                            'id': video_id,
                            'url': video_url
                        }
            
            # If we reach here, scraping failed (which is common now)
            print(f"[DEBUG] Web scraping failed for {video_id} - TikTok likely using JavaScript")
            return None
        
        return None
        
    except Exception as e:
        print(f"[DEBUG] Web scraping failed for {video_id}: {e}")
        return None

@app.route('/api/add/<video_id>', methods=['POST'])
def api_add_video(video_id):
    """Add a single video with security measures"""
    try:
        # Security check: Only allow POST requests
        if request.method != 'POST':
            return jsonify({'status': 'error', 'error': 'Only POST requests allowed'}), 405
        
        # Security check: Basic authentication via header or query param
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if not api_key or api_key != os.environ.get('MGED_API_KEY', 'default_dev_key'):
            return jsonify({'status': 'error', 'error': 'Invalid or missing API key'}), 401
        
        # Validate video ID format
        if not video_id.isdigit() or len(video_id) < 15:
            return jsonify({'status': 'error', 'error': 'Invalid video ID format'}), 400
        
        # Load existing videos (direct file access, no manager needed)
        existing_videos = []
        if os.path.exists('tiktok_videos.json'):
            try:
                with open('tiktok_videos.json', 'r') as f:
                    data = json.load(f)
                    existing_videos = data.get('videos', [])
            except Exception as e:
                print(f"[DEBUG] Error loading existing videos: {e}")
        
        # Check if video already exists
        existing_ids = [v['video_id'] for v in existing_videos]
        if video_id in existing_ids:
            return jsonify({
                'status': 'ok',
                'message': 'Video already exists',
                'video_id': video_id
            })
        
        # Try to get video info with multiple fallback methods
        video_info = None
        
        # Method 1: Try yt-dlp if available
        if AUTOMATION_AVAILABLE:
            try:
                manager = TikTokVideoManager()
                video_info = manager.get_video_info(video_id)
                if video_info:
                    print(f"[DEBUG] Successfully got video info via yt-dlp for {video_id}")
            except Exception as e:
                print(f"[DEBUG] yt-dlp failed for {video_id}: {e}")
        
        # Method 2: Try web scraping fallback
        if not video_info:
            print(f"[DEBUG] Trying web scraping fallback for {video_id}")
            video_info = get_video_info_fallback(video_id)
            if video_info:
                print(f"[DEBUG] Successfully got video info via web scraping for {video_id}")
        
        # Method 3: Create simple fallback based on existing videos
        if not video_info:
            print(f"[DEBUG] Creating simple fallback for {video_id}")
            
            # Try to guess the day number based on existing videos
            day_number = len(existing_videos) + 1
            if existing_videos:
                # Look for day pattern in most recent video
                recent_title = existing_videos[0].get('title', '')
                day_match = re.search(r'Day (\d+)', recent_title)
                if day_match:
                    day_number = int(day_match.group(1)) + 1
            
            video_info = {
                'title': f'Day {day_number}. Mini Golf Every Day',
                'upload_date': datetime.now().strftime('%Y%m%d'),
                'id': video_id
            }
        
        # Add new video to the beginning of the list
        new_video = {
            'video_id': video_id,
            'title': video_info.get('title', ''),
            'upload_date': video_info.get('upload_date', ''),
            'url': f"https://www.tiktok.com/@minigolfeveryday/video/{video_id}"
        }
        
        # Keep only the most recent 200 videos to prevent unlimited growth
        updated_videos = [new_video] + existing_videos[:199]
        
        # Save updated data (direct file access, no manager needed)
        try:
            video_data = {
                'videos': updated_videos,
                'last_updated': datetime.now().isoformat(),
                'total_count': len(updated_videos)
            }
            
            with open('tiktok_videos.json', 'w') as f:
                json.dump(video_data, f, indent=2, ensure_ascii=False)
            
            print(f"[DEBUG] Successfully saved {len(updated_videos)} videos to JSON file")
            
        except Exception as e:
            print(f"[DEBUG] Error saving videos: {e}")
            return jsonify({'status': 'error', 'error': f'Failed to save video data: {str(e)}'}), 500
        
        return jsonify({
            'status': 'ok',
            'message': 'Video added successfully',
            'video': new_video,
            'total_videos': len(updated_videos)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/api/update', methods=['GET', 'POST'])
def api_update():
    """Update all videos"""
    try:
        if not AUTOMATION_AVAILABLE:
            return jsonify({'status': 'error', 'error': 'TikTok automation not available'})
        
        manager = TikTokVideoManager()
        
        # Load existing videos first
        existing_videos = manager.load_video_data()
        print(f"[DEBUG] Existing videos in database: {len(existing_videos)}")
        
        # Try to get latest videos (increased limit to catch all videos)
        videos = manager.get_latest_videos_ytdlp(200)
        print(f"[DEBUG] Videos fetched from yt-dlp: {len(videos) if videos else 0}")
        
        # If yt-dlp fails, DO NOT fall back to manual list
        # Instead, just return early with no changes
        if not videos:
            print("[DEBUG] yt-dlp failed, preserving existing database")
            return jsonify({
                'status': 'ok',
                'message': 'No new videos fetched (yt-dlp failed, database preserved)',
                'total_videos': len(existing_videos),
                'new_videos': 0,
                'new_video_ids': []
            })
        
        # Find new videos
        existing_ids = set(v['video_id'] for v in existing_videos)
        new_videos = [v for v in videos if v['video_id'] not in existing_ids]
        print(f"[DEBUG] New videos found: {len(new_videos)}")
        
        # Merge all videos (existing + new)
        all_videos = existing_videos + new_videos
        print(f"[DEBUG] Total videos after merge: {len(all_videos)}")
        
        # Save merged data (skip HTML update for dynamic site)
        manager.save_video_data(all_videos)
        
        return jsonify({
            'status': 'ok',
            'message': 'Videos updated successfully',
            'total_videos': len(all_videos),
            'new_videos': len(new_videos),
            'new_video_ids': [v['video_id'] for v in new_videos]
        })
            
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
