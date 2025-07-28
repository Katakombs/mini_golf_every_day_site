#!/usr/bin/env python3
"""
Simple Process Cleanup for cPanel
Basic script to stop orphaned mini golf processes
"""

import os
import sys
import signal
import subprocess

def main():
    print("🧹 Mini Golf Process Cleanup")
    print("=" * 30)
    
    try:
        # Get all processes
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Failed to get processes")
            return
        
        lines = result.stdout.strip().split('\n')
        print(f"📊 Found {len(lines)} total processes")
        
        # Look for mini golf related processes
        targets = []
        for line in lines[1:]:  # Skip header
            if line.strip():
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    pid = parts[1]
                    command = parts[10] if len(parts) > 10 else ''
                    
                    # Check if it's a mini golf related process
                    keywords = ['update_videos.py', 'migrate_videos_to_db.py', 'yt-dlp', 'minigolfeveryday']
                    is_target = any(keyword.lower() in command.lower() for keyword in keywords)
                    
                    if is_target and 'cleanup' not in command.lower():
                        targets.append((pid, command))
        
        if not targets:
            print("✅ No orphaned processes found!")
            return
        
        print(f"⚠️  Found {len(targets)} processes to stop:")
        for pid, command in targets:
            print(f"   PID {pid}: {command[:60]}...")
        
        # Stop processes
        print("\n🛑 Stopping processes...")
        stopped = 0
        
        for pid, command in targets:
            try:
                print(f"   Stopping PID {pid}...")
                os.kill(int(pid), signal.SIGTERM)
                stopped += 1
            except Exception as e:
                print(f"   Failed to stop PID {pid}: {e}")
        
        print(f"\n✅ Stopped {stopped}/{len(targets)} processes")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 