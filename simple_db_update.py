#!/usr/bin/env python3
"""
Simple Database Update Script
Minimal script to update database from JSON - avoids complex modules
"""

import os
import sys
import json

def main():
    print("Simple Database Update")
    print("=" * 30)
    
    try:
        # Load JSON data
        if not os.path.exists('tiktok_videos.json'):
            print("tiktok_videos.json not found")
            return 1
        
        with open('tiktok_videos.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        videos = data.get('videos', [])
        print(f"Loaded {len(videos)} videos from JSON")
        
        if not videos:
            print("No videos found in JSON")
            return 1
        
        # Try to run the migration script
        print("Running database migration...")
        
        # Try different Python executables
        python_execs = [
            'python3',
            'python',
            '/usr/bin/python3',
            '/usr/bin/python',
            '/opt/alt/python39/bin/python3'
        ]
        
        success = False
        for python_exec in python_execs:
            try:
                print(f"Trying {python_exec}...")
                
                # Use os.system for simpler execution
                cmd = f"{python_exec} migrate_videos_to_db.py"
                result = os.system(cmd)
                
                if result == 0:
                    print("Database updated successfully!")
                    success = True
                    break
                else:
                    print(f"Failed with {python_exec} (exit code: {result})")
                    
            except Exception as e:
                print(f"Error with {python_exec}: {e}")
                continue
        
        if success:
            print(f"Updated {len(videos)} videos in database")
            return 0
        else:
            print("All Python executables failed")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 