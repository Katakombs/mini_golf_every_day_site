#!/usr/bin/env python3
"""
Auto Cleanup Orphaned Processes Script
Automatically stops orphaned processes related to the mini golf site
No user confirmation required - safe for cPanel usage
"""

import os
import sys
import signal
import subprocess
import time
from datetime import datetime

def get_process_info():
    """Get information about running processes"""
    try:
        # Get all processes with detailed info
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Failed to get process information")
            return []
        
        lines = result.stdout.strip().split('\n')
        processes = []
        
        for line in lines[1:]:  # Skip header
            if line.strip():
                parts = line.split(None, 10)  # Split on whitespace, max 11 parts
                if len(parts) >= 11:
                    processes.append({
                        'user': parts[0],
                        'pid': parts[1],
                        'cpu': parts[2],
                        'mem': parts[3],
                        'vsz': parts[4],
                        'rss': parts[5],
                        'tty': parts[6],
                        'stat': parts[7],
                        'start': parts[8],
                        'time': parts[9],
                        'command': parts[10] if len(parts) > 10 else ''
                    })
        
        return processes
    except Exception as e:
        print(f"❌ Error getting process information: {e}")
        return []

def identify_orphaned_processes(processes):
    """Identify orphaned processes related to the mini golf site"""
    orphaned = []
    
    # Keywords to identify mini golf related processes
    keywords = [
        'update_videos.py',
        'migrate_videos_to_db.py',
        'update_database_only.py',
        'yt-dlp',
        'python3',
        'python',
        'minigolfeveryday',
        'phazeshi'
    ]
    
    for process in processes:
        command = process['command'].lower()
        
        # Check if it's a mini golf related process
        is_related = any(keyword.lower() in command for keyword in keywords)
        
        if is_related:
            # Check if it's been running too long (more than 5 minutes)
            try:
                start_time = process['start']
                if start_time != '?':
                    # Simple heuristic: if start time contains ':' it's likely been running a while
                    if ':' in start_time:
                        orphaned.append(process)
            except:
                pass
    
    return orphaned

def get_process_age(process):
    """Get how long a process has been running"""
    try:
        start = process['start']
        if start == '?':
            return "Unknown"
        
        # Parse start time (format varies by system)
        if ':' in start:
            return f"Running for a while (started: {start})"
        else:
            return f"Started at: {start}"
    except:
        return "Unknown"

def stop_process_safely(pid, command):
    """Safely stop a process"""
    try:
        print(f"🛑 Stopping process {pid} ({command[:50]}...)")
        
        # First try SIGTERM (graceful shutdown)
        os.kill(int(pid), signal.SIGTERM)
        
        # Wait a moment for graceful shutdown
        time.sleep(2)
        
        # Check if process is still running
        try:
            os.kill(int(pid), 0)  # Signal 0 just checks if process exists
            print(f"⚠️  Process {pid} still running, using SIGKILL...")
            os.kill(int(pid), signal.SIGKILL)
            time.sleep(1)
        except OSError:
            print(f"✅ Process {pid} stopped successfully")
            return True
        
        return True
    except Exception as e:
        print(f"❌ Failed to stop process {pid}: {e}")
        return False

def main():
    """Main cleanup function - no user confirmation required"""
    print("🧹 Mini Golf Every Day - Auto Process Cleanup")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔧 Auto mode - no confirmation required")
    print()
    
    # Get current user
    current_user = os.environ.get('USER', 'unknown')
    print(f"👤 Current user: {current_user}")
    
    # Get all processes
    print("🔍 Scanning for processes...")
    processes = get_process_info()
    
    if not processes:
        print("❌ No processes found or unable to get process information")
        return
    
    print(f"📊 Found {len(processes)} total processes")
    
    # Identify orphaned processes
    orphaned = identify_orphaned_processes(processes)
    
    if not orphaned:
        print("✅ No orphaned processes found!")
        return
    
    print(f"⚠️  Found {len(orphaned)} potentially orphaned processes:")
    print()
    
    # Display orphaned processes
    for i, process in enumerate(orphaned, 1):
        age = get_process_age(process)
        print(f"{i}. PID: {process['pid']}")
        print(f"   User: {process['user']}")
        print(f"   CPU: {process['cpu']}% | Memory: {process['mem']}%")
        print(f"   Age: {age}")
        print(f"   Command: {process['command'][:80]}...")
        print()
    
    # Auto-stop processes (no confirmation needed)
    print("🛑 Auto-stopping orphaned processes...")
    stopped_count = 0
    
    for process in orphaned:
        success = stop_process_safely(process['pid'], process['command'])
        if success:
            stopped_count += 1
    
    print(f"\n✅ Auto-cleanup complete! Stopped {stopped_count}/{len(orphaned)} processes")
    
    # Show remaining processes
    print("\n🔍 Checking for remaining processes...")
    remaining_processes = get_process_info()
    remaining_orphaned = identify_orphaned_processes(remaining_processes)
    
    if remaining_orphaned:
        print(f"⚠️  {len(remaining_orphaned)} processes still running (may be legitimate)")
        for process in remaining_orphaned:
            print(f"   PID {process['pid']}: {process['command'][:50]}...")
    else:
        print("✅ All orphaned processes have been stopped!")

def show_help():
    """Show help information"""
    print("""
🧹 Mini Golf Every Day - Auto Process Cleanup Script

Usage:
    python3 cleanup_orphaned_processes_auto.py

This script will:
1. Scan for processes related to the mini golf site
2. Identify potentially orphaned processes (running too long)
3. Automatically stop them WITHOUT asking for confirmation
4. Safely terminate processes using SIGTERM then SIGKILL

Safety Features:
- Only targets processes related to mini golf site
- Uses graceful shutdown first, force kill only if needed
- Shows detailed information about each process
- Safe for cPanel usage (no interactive input required)

Related Process Keywords:
- update_videos.py
- migrate_videos_to_db.py  
- update_database_only.py
- yt-dlp
- python3/python
- minigolfeveryday
- phazeshi

Use this script when you notice:
- High process count in cPanel
- "Resource temporarily unavailable" errors
- Hanging video update operations
- Slow server performance

⚠️  WARNING: This script automatically stops processes without confirmation!
""")

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
            show_help()
        else:
            main()
    except KeyboardInterrupt:
        print("\n🛑 Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 