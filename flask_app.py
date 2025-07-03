#!/usr/bin/env python3
"""
Flask web application for Mini Golf Every Day
Serves static files and provides TikTok automation
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import json
import sys
from datetime import datetime

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
                with open('tiktok_videos.json', 'r') as f:
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
            with open('tiktok_videos.json', 'r') as f:
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

@app.route('/api/add/<video_id>')
def api_add_video(video_id):
    """Add a single video - DISABLED for safety"""
    return jsonify({
        'status': 'error', 
        'error': 'This endpoint is disabled to prevent database corruption. Use /api/update instead.'
    })

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
    app.run(debug=True)
