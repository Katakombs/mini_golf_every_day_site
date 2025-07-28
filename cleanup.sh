#!/bin/bash
# Simple Process Cleanup for cPanel
# Basic script to stop orphaned mini golf processes

echo "🧹 Mini Golf Process Cleanup"
echo "=============================="

# Get all processes and look for mini golf related ones
echo "📊 Scanning for processes..."

# Find processes related to mini golf
TARGETS=$(ps aux | grep -E "(update_videos\.py|migrate_videos_to_db\.py|yt-dlp|minigolfeveryday)" | grep -v grep | grep -v cleanup)

if [ -z "$TARGETS" ]; then
    echo "✅ No orphaned processes found!"
    exit 0
fi

echo "⚠️  Found processes to stop:"
echo "$TARGETS"

echo ""
echo "🛑 Stopping processes..."

# Extract PIDs and stop them
echo "$TARGETS" | awk '{print $2}' | while read pid; do
    if [ ! -z "$pid" ]; then
        echo "   Stopping PID $pid..."
        kill -TERM "$pid" 2>/dev/null
    fi
done

echo ""
echo "✅ Cleanup complete!" 