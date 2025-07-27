#!/bin/bash

# Process monitoring script for shared hosting
echo "🔍 Checking running processes..."
echo "================================"

# Check total process count
echo "📊 Total processes:"
ps aux | wc -l

# Check Python processes specifically
echo ""
echo "🐍 Python processes:"
ps aux | grep python | grep -v grep

# Check for any hanging processes
echo ""
echo "⏰ Long-running processes (>10 minutes):"
ps -eo pid,ppid,cmd,etime | grep -E "(python|php|perl)" | awk '$4 ~ /[0-9]+:[0-9]+:[0-9]+/'

# Check for processes using high memory
echo ""
echo "💾 High memory usage processes:"
ps aux --sort=-%mem | head -10

# Check for processes using high CPU
echo ""
echo "⚡ High CPU usage processes:"
ps aux --sort=-%cpu | head -10

# Check for any cron-related processes
echo ""
echo "⏰ Cron-related processes:"
ps aux | grep -E "(cron|github_sync)" | grep -v grep

echo ""
echo "🎯 To kill specific processes, use:"
echo "   kill -9 <PID>"
echo ""
echo "💡 To kill all Python processes (be careful!):"
echo "   pkill -f python" 