#!/bin/bash

# cPanel Environment Diagnostic Script
# Run this on your cPanel server to check if everything is set up correctly

echo "=== cPanel Environment Diagnostic ==="
echo "Date: $(date)"
echo ""

# Check Python versions
echo "🐍 Python Versions Available:"
for py_cmd in "python3.11" "python3.10" "python3.9" "python3.8" "python3" "python"; do
    if command -v "$py_cmd" &> /dev/null; then
        version=$($py_cmd --version 2>&1)
        echo "  ✅ $py_cmd: $version"
        PYTHON_FOUND="$py_cmd"
    else
        echo "  ❌ $py_cmd: not found"
    fi
done

echo ""

# Check pip versions
echo "📦 Pip Versions Available:"
for pip_cmd in "pip3.11" "pip3.10" "pip3.9" "pip3.8" "pip3" "pip"; do
    if command -v "$pip_cmd" &> /dev/null; then
        version=$($pip_cmd --version 2>&1)
        echo "  ✅ $pip_cmd: $version"
        PIP_FOUND="$pip_cmd"
    else
        echo "  ❌ $pip_cmd: not found"
    fi
done

echo ""

# Test yt-dlp installation
echo "🎬 Testing yt-dlp:"
if [ -n "$PYTHON_FOUND" ]; then
    if $PYTHON_FOUND -c "import yt_dlp; print('yt-dlp version:', yt_dlp.version.__version__)" 2>/dev/null; then
        echo "  ✅ yt-dlp is installed and working"
        
        # Test a simple yt-dlp command
        echo "  🧪 Testing yt-dlp with TikTok..."
        timeout 30 $PYTHON_FOUND -m yt_dlp --version &>/dev/null
        if [ $? -eq 0 ]; then
            echo "  ✅ yt-dlp command works"
        else
            echo "  ⚠️  yt-dlp command may have issues"
        fi
    else
        echo "  ❌ yt-dlp not installed"
        
        if [ -n "$PIP_FOUND" ]; then
            echo "  💡 Try installing with: $PIP_FOUND install yt-dlp --user"
        else
            echo "  ❌ Cannot install yt-dlp - no pip found"
        fi
    fi
else
    echo "  ❌ No Python found - cannot test yt-dlp"
fi

echo ""

# Check file permissions and paths
echo "📁 File System Checks:"
echo "  Current directory: $(pwd)"
echo "  User: $(whoami)"
echo "  Home directory: $HOME"

if [ -f "tiktok_videos.json" ]; then
    echo "  ✅ tiktok_videos.json exists"
    video_count=$(grep -o '"video_id"' tiktok_videos.json | wc -l)
    echo "  📊 Contains approximately $video_count videos"
else
    echo "  ❌ tiktok_videos.json not found"
fi

if [ -f "cron_wrapper.sh" ]; then
    echo "  ✅ cron_wrapper.sh exists"
    perms=$(ls -la cron_wrapper.sh | cut -d' ' -f1)
    echo "  🔒 Permissions: $perms"
    if [[ "$perms" == *"x"* ]]; then
        echo "  ✅ Script is executable"
    else
        echo "  ❌ Script is not executable - run: chmod 755 cron_wrapper.sh"
    fi
else
    echo "  ❌ cron_wrapper.sh not found"
fi

echo ""

# Network connectivity test
echo "🌐 Network Tests:"
if command -v curl &> /dev/null; then
    echo "  Testing TikTok connectivity..."
    if curl -s --connect-timeout 10 https://www.tiktok.com/@minigolfeveryday > /dev/null; then
        echo "  ✅ Can reach TikTok"
    else
        echo "  ❌ Cannot reach TikTok (may be blocked)"
    fi
else
    echo "  ❌ curl not available - cannot test connectivity"
fi

echo ""
echo "=== Diagnostic Complete ==="

# Summary and recommendations
echo ""
echo "🔧 RECOMMENDATIONS:"

if [ -z "$PYTHON_FOUND" ]; then
    echo "  ❌ CRITICAL: Install Python 3"
elif [ -z "$PIP_FOUND" ]; then
    echo "  ❌ CRITICAL: Install pip for Python package management"
elif ! $PYTHON_FOUND -c "import yt_dlp" 2>/dev/null; then
    echo "  ⚠️  IMPORTANT: Install yt-dlp with: $PIP_FOUND install yt-dlp --user"
else
    echo "  ✅ Environment looks good! Ready to run cron job."
fi

echo ""
echo "📋 Next steps:"
echo "  1. Fix any CRITICAL issues above"
echo "  2. Upload cron_wrapper.sh and set permissions to 755"
echo "  3. Set up cron job in cPanel"
echo "  4. Check cron.log after the first run"
