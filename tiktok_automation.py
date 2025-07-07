#!/usr/bin/env python3
"""
Alternative TikTok scraper using a more reliable approach
This version uses a simpler method that's less likely to break
"""

import json
import re
import os
from datetime import datetime
import subprocess
from typing import List, Dict

class TikTokVideoManager:
    def __init__(self, username="minigolfeveryday"):
        self.username = username
        self.video_data_file = "tiktok_videos.json"
        
    def get_latest_videos_ytdlp(self, limit=200) -> List[Dict]:
        """
        Use yt-dlp to fetch video information (most reliable method)
        """
        try:
            # Check if yt-dlp is installed
            result = subprocess.run(['which', 'yt-dlp'], capture_output=True, text=True)
            if result.returncode != 0:
                print("yt-dlp not found. Installing...")
                subprocess.run(['pip', 'install', 'yt-dlp'], check=True)
            
            profile_url = f"https://www.tiktok.com/@{self.username}"
            
            # Use yt-dlp to extract video info
            cmd = [
                'yt-dlp',
                '--flat-playlist',
                '--print', '%(id)s|%(title)s|%(upload_date)s',
                '--playlist-end', str(limit),
                profile_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"yt-dlp error: {result.stderr}")
                return []
            
            videos = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 1:
                        video_id = parts[0]
                        title = parts[1] if len(parts) > 1 else ""
                        upload_date = parts[2] if len(parts) > 2 else ""
                        
                        videos.append({
                            'video_id': video_id,
                            'title': title,
                            'upload_date': upload_date,
                            'url': f"https://www.tiktok.com/@{self.username}/video/{video_id}"
                        })
            
            return videos
            
        except Exception as e:
            print(f"Error with yt-dlp method: {e}")
            return []
    
    def manual_video_list(self) -> List[Dict]:
        """
        Fallback: manually maintained list of video IDs
        You can update this list when you post new videos
        """
        # Extract current video IDs from existing HTML as a starting point
        video_ids = [
            "7522583834320260365",
            "7521882226938744119", 
            "7521516808671710519",
            "7521176390096424247",
            "7520792307759648055",
            "7519988784516123918",
            "7519618835645893943",
            "7519234729237957901",
            "7518886602458844430",
            "7518510635437542711",
            "7518129001257323831",
            "7517718390451096846",
            "7517461554997054734",
            "7516914507663330573",
            "7516345442758577454",
            "7515968349596159275",
            "7515599136482430254",
            "7515160951574842667",
            "7514864210807983406",
            "7514503639554198826",
            "7514122934424800555",
            "7513756596833357099",
            "7513388481281035566",
            "7512980398356303146",
            "7512557659380469038",
            "7512135372537646378",
            "7511865094972919086"
        ]
        
        return [{'video_id': vid_id, 'title': '', 'upload_date': ''} for vid_id in video_ids]
    
    def save_video_data(self, videos: List[Dict]):
        """Save video data to JSON file for tracking"""
        with open(self.video_data_file, 'w') as f:
            json.dump({
                'last_updated': datetime.now().isoformat(),
                'videos': videos
            }, f, indent=2)
    
    def load_video_data(self) -> List[Dict]:
        """Load video data from JSON file"""
        try:
            with open(self.video_data_file, 'r') as f:
                data = json.load(f)
                return data.get('videos', [])
        except FileNotFoundError:
            return []
    
    def update_watch_html(self, videos: List[Dict], html_file='watch.html') -> bool:
        """Update the watch.html file with new video embeds"""
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the grid container
            grid_pattern = r'(<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-none">)(.*?)(</div>)'
            match = re.search(grid_pattern, content, re.DOTALL)
            
            if not match:
                print("Could not find grid container in HTML")
                return False
            
            # Generate new video embeds
            video_embeds = []
            for video in videos:
                video_id = video['video_id']
                embed_html = f'''    <div class="bg-white rounded-lg shadow-md p-4">
      <blockquote class="tiktok-embed" cite="https://www.tiktok.com/@{self.username}/video/{video_id}" data-video-id="{video_id}" data-autoplay="false" style="max-width: 100%;min-width: 325px;"><section>Loading...</section></blockquote>
    </div>'''
                video_embeds.append(embed_html)
            
            # Create new grid content
            new_grid_content = f'''{match.group(1)}   
  
{chr(10).join(video_embeds)}
  {match.group(3)}'''
            
            # Replace the grid content
            new_content = content[:match.start()] + new_grid_content + content[match.end():]
            
            # Create backup
            backup_file = f"watch_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Backup saved as: {backup_file}")
            
            # Write updated content
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Updated {html_file} with {len(videos)} videos")
            return True
            
        except Exception as e:
            print(f"Error updating HTML file: {e}")
            return False
    
    def get_video_info(self, video_id: str) -> Dict:
        """
        Get information for a specific video using yt-dlp
        """
        try:
            # Check if yt-dlp is installed
            result = subprocess.run(['which', 'yt-dlp'], capture_output=True, text=True)
            if result.returncode != 0:
                print("yt-dlp not found. Installing...")
                subprocess.run(['pip', 'install', 'yt-dlp'], check=True)
            
            video_url = f"https://www.tiktok.com/@{self.username}/video/{video_id}"
            
            # Use yt-dlp to extract video info
            cmd = [
                'yt-dlp',
                '--print', '%(id)s|%(title)s|%(upload_date)s',
                '--no-download',
                video_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"yt-dlp error for video {video_id}: {result.stderr}")
                return None
            
            output = result.stdout.strip()
            if '|' in output:
                parts = output.split('|')
                if len(parts) >= 3:
                    return {
                        'video_id': parts[0],
                        'title': parts[1],
                        'upload_date': parts[2]
                    }
            
            return None
            
        except Exception as e:
            print(f"Error fetching video info for {video_id}: {e}")
            return None

def main():
    """Main function to fetch and update TikTok videos"""
    manager = TikTokVideoManager()
    
    print("Fetching latest TikTok videos...")
    
    # Try yt-dlp method first
    videos = manager.get_latest_videos_ytdlp(30)
    
    if not videos:
        print("yt-dlp method failed, using manual list...")
        videos = manager.manual_video_list()
    
    if videos:
        # Load existing videos to compare
        existing_videos = manager.load_video_data()
        existing_ids = set(v['video_id'] for v in existing_videos)
        
        # Find new videos
        new_videos = [v for v in videos if v['video_id'] not in existing_ids]
        
        if new_videos:
            print(f"🆕 Found {len(new_videos)} new video(s):")
            for video in new_videos:
                print(f"   - {video['video_id']}: {video.get('title', 'No title')}")
        else:
            print("📋 No new videos found")
        
        # Save video data
        manager.save_video_data(videos)
        
        # Update HTML
        success = manager.update_watch_html(videos)
        if success:
            print("✅ Successfully updated watch.html")
            print(f"📊 Processed {len(videos)} videos")
            if new_videos:
                print(f"🎉 Added {len(new_videos)} new video(s) to the site")
        else:
            print("❌ Failed to update watch.html")
    else:
        print("❌ No videos found")

if __name__ == "__main__":
    main()
