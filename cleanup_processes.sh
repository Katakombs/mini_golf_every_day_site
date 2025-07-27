#!/bin/bash

# Safe process cleanup script for shared hosting
echo "🧹 Cleaning up processes..."

# Kill any hanging Python processes
echo "🐍 Killing Python processes..."
pkill -f python 2>/dev/null

# Wait a moment
sleep 2

# Kill any remaining hanging processes
echo "🔍 Checking for remaining processes..."
ps aux | grep -E "(passenger|server\.py)" | grep -v grep

# Kill any cron-related processes that might be stuck
echo "⏰ Killing any stuck cron processes..."
pkill -f "github_sync" 2>/dev/null

# Clean up any temporary files
echo "🗑️  Cleaning temporary files..."
find /tmp -name "*.pyc" -delete 2>/dev/null
find /tmp -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# Restart the application
echo "🔄 Restarting application..."
touch passenger_wsgi.py

echo "✅ Cleanup complete!"
echo "📊 Current process count:"
ps aux | wc -l 