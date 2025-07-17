#!/bin/bash

# 🚀 Production Deployment Script
# Mini Golf Every Day - Video Database Migration Deployment

echo "🚀 MINI GOLF EVERY DAY - PRODUCTION DEPLOYMENT"
echo "=============================================="
echo "Deploying video database migration to production..."
echo ""

# Configuration
SITE_PATH="/home/username/public_html"  # Update this with your actual path
BACKUP_DIR="./deployment_backup_$(date +%Y%m%d_%H%M%S)"

echo "📋 DEPLOYMENT CHECKLIST:"
echo "========================"

# Check required files exist
echo "🔍 Checking required files..."
FILES_TO_DEPLOY=(
    "server.py"
    ".env.production"
    "requirements_blog.txt"
    "passenger_wsgi.py"
    "tiktok_videos.json"
    "migrate_videos_to_db.py"
    "add_videos_table.sql"
)

MISSING_FILES=()
for file in "${FILES_TO_DEPLOY[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING)"
        MISSING_FILES+=("$file")
    fi
done

if [[ ${#MISSING_FILES[@]} -gt 0 ]]; then
    echo ""
    echo "❌ DEPLOYMENT STOPPED - Missing required files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

echo ""
echo "✅ All required files present!"
echo ""

# Create backup directory
echo "💾 Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup current files (if they exist)
echo "📦 Backing up current files..."
if [[ -f "server.py" ]]; then
    cp server.py "$BACKUP_DIR/server.py.backup"
    echo "  ✅ Backed up server.py"
fi

if [[ -f ".env" ]]; then
    cp .env "$BACKUP_DIR/.env.backup"
    echo "  ✅ Backed up .env"
fi

echo ""
echo "📁 FILES READY FOR DEPLOYMENT:"
echo "=============================="

# Show file sizes and modification dates
for file in "${FILES_TO_DEPLOY[@]}"; do
    if [[ -f "$file" ]]; then
        size=$(ls -lh "$file" | awk '{print $5}')
        date=$(ls -l "$file" | awk '{print $6, $7, $8}')
        echo "  📄 $file ($size, modified: $date)"
    fi
done

echo ""
echo "🔧 DEPLOYMENT COMMANDS:"
echo "======================"
echo ""

echo "# 1. Upload files to your hosting account using FTP/SFTP:"
echo "#    Use your preferred method (FileZilla, scp, rsync, etc.)"
echo ""

echo "# 2. SSH into your hosting account and run:"
echo "ssh username@yourhost.com"
echo "cd $SITE_PATH"
echo ""

echo "# 3. Rename environment file:"
echo "mv .env.production .env"
echo ""

echo "# 4. Install Python dependencies:"
echo "pip install -r requirements_blog.txt --user"
echo "# OR if using Python 3 specifically:"
echo "pip3 install -r requirements_blog.txt --user"
echo ""

echo "# 5. OPTION A: One-command setup (RECOMMENDED):"
echo "curl https://minigolfevery.day/api/setup"
echo "# This will create all tables, migrate videos, and set up everything automatically"
echo ""

echo "# 5. OPTION B: Manual setup (if preferred):"
echo "# Create videos table in MySQL (run this SQL in phpMyAdmin):"
echo "# Copy contents of add_videos_table.sql and run in your MySQL interface"
echo "python migrate_videos_to_db.py"
echo "# OR if using Python 3:"
echo "python3 migrate_videos_to_db.py"
echo ""

echo "# 6. Restart your web application"
echo "# This varies by hosting provider - check your control panel"
echo ""

echo "# 7. Test the deployment:"
echo "curl https://minigolfevery.day/api/setup"
echo "curl https://minigolfevery.day/api/videos"
echo "curl https://minigolfevery.day/api/status"
echo ""

echo "🧪 TESTING CHECKLIST:"
echo "===================="
echo "After deployment, verify these work:"
echo "  [ ] GET /api/setup - Creates all tables and migrates videos"
echo "  [ ] GET /api/videos - Returns video list (should be faster)"
echo "  [ ] GET /api/status - Returns site statistics"
echo "  [ ] GET /api/blog/posts - Returns blog posts"
echo "  [ ] No 500 errors on any endpoint"
echo "  [ ] Videos table exists in MySQL with 181+ records"
echo "  [ ] GitHub Actions can still update tiktok_videos.json"
echo ""

echo "🔄 ROLLBACK INSTRUCTIONS:"
echo "========================"
echo "If something goes wrong, you can rollback using:"
echo "  1. Restore server.py from: $BACKUP_DIR/server.py.backup"
echo "  2. Restore .env from: $BACKUP_DIR/.env.backup"
echo "  3. Restart web application"
echo ""

echo "💡 IMPORTANT NOTES:"
echo "=================="
echo "  • GitHub Actions will continue working unchanged"
echo "  • Videos are now stored in database for better performance"
echo "  • JSON file is maintained for GitHub Actions compatibility"
echo "  • Database automatically syncs with JSON file"
echo ""

echo "✅ DEPLOYMENT PACKAGE READY!"
echo "=========================="
echo "All files are prepared and ready for production deployment."
echo "Follow the deployment commands above to complete the process."
echo ""
echo "📞 Support: Check PRODUCTION_DEPLOYMENT_GUIDE.md for detailed instructions"
