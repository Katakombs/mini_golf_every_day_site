#!/bin/bash
# Script to switch between static and dynamic HTML versions
# Usage: ./switch_to_dynamic.sh [backup|restore]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

backup_and_switch() {
    echo "🔄 Switching to dynamic HTML versions..."
    
    # Backup current versions
    if [ -f "$SCRIPT_DIR/index.html" ]; then
        echo "📦 Backing up current index.html to index_static.html"
        cp "$SCRIPT_DIR/index.html" "$SCRIPT_DIR/index_static.html"
    fi
    
    if [ -f "$SCRIPT_DIR/watch.html" ]; then
        echo "📦 Backing up current watch.html to watch_static.html"
        cp "$SCRIPT_DIR/watch.html" "$SCRIPT_DIR/watch_static.html"
    fi
    
    # Switch to dynamic versions
    if [ -f "$SCRIPT_DIR/index_dynamic.html" ]; then
        echo "✅ Switching index.html to dynamic version"
        cp "$SCRIPT_DIR/index_dynamic.html" "$SCRIPT_DIR/index.html"
    else
        echo "❌ index_dynamic.html not found!"
        exit 1
    fi
    
    if [ -f "$SCRIPT_DIR/watch_dynamic.html" ]; then
        echo "✅ Switching watch.html to dynamic version"
        cp "$SCRIPT_DIR/watch_dynamic.html" "$SCRIPT_DIR/watch.html"
    else
        echo "❌ watch_dynamic.html not found!"
        exit 1
    fi
    
    echo ""
    echo "🎉 Successfully switched to dynamic HTML versions!"
    echo ""
    echo "📋 What's new:"
    echo "  ✨ Live video counts from your API"
    echo "  🔍 Search and filter functionality"
    echo "  📱 Automatic loading of latest videos"
    echo "  🎯 Better mobile experience"
    echo "  ⚡ Real-time updates from your automation"
    echo ""
    echo "🔗 Test your dynamic site:"
    echo "  - Homepage: https://minigolfevery.day/"
    echo "  - Videos:   https://minigolfevery.day/watch.html"
    echo "  - API:      https://minigolfevery.day/api/status"
}

restore_static() {
    echo "🔄 Restoring static HTML versions..."
    
    if [ -f "$SCRIPT_DIR/index_static.html" ]; then
        echo "✅ Restoring index.html from backup"
        cp "$SCRIPT_DIR/index_static.html" "$SCRIPT_DIR/index.html"
    else
        echo "❌ No backup found for index.html"
    fi
    
    if [ -f "$SCRIPT_DIR/watch_static.html" ]; then
        echo "✅ Restoring watch.html from backup"
        cp "$SCRIPT_DIR/watch_static.html" "$SCRIPT_DIR/watch.html"
    else
        echo "❌ No backup found for watch.html"
    fi
    
    echo "✅ Restored to static versions"
}

show_help() {
    echo "Mini Golf Every Day - HTML Version Switcher"
    echo ""
    echo "Usage:"
    echo "  ./switch_to_dynamic.sh            Switch to dynamic versions (default)"
    echo "  ./switch_to_dynamic.sh backup     Same as above"
    echo "  ./switch_to_dynamic.sh restore    Restore static versions"
    echo "  ./switch_to_dynamic.sh help       Show this help"
    echo ""
    echo "What's the difference?"
    echo ""
    echo "📊 Static HTML (current):"
    echo "  - Fixed TikTok embeds"
    echo "  - Manual video management"
    echo "  - No live stats"
    echo ""
    echo "⚡ Dynamic HTML (new):"
    echo "  - Automatic video loading from API"
    echo "  - Live video counts and stats"
    echo "  - Search and filter functionality"
    echo "  - Always up-to-date with automation"
    echo "  - Better user experience"
}

case "${1:-backup}" in
    "backup")
        backup_and_switch
        ;;
    "restore")
        restore_static
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
