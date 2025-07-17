#!/bin/bash

# 🧹 Project Cleanup Script for GitHub
# Mini Golf Every Day - Clean up before committing to GitHub

echo "🧹 CLEANING UP PROJECT FOR GITHUB"
echo "=================================="

# Create directories for organization
mkdir -p .archive/{debug,backups,temp,docs,old_guides}

echo "📁 Creating organization directories..."

# Archive debug and diagnostic files
echo "🔍 Archiving debug files..."
mv debug_*.py .archive/debug/ 2>/dev/null || true
mv debug_*.html .archive/debug/ 2>/dev/null || true
mv diagnose_*.py .archive/debug/ 2>/dev/null || true
mv test_*.py .archive/debug/ 2>/dev/null || true
mv test_*.html .archive/debug/ 2>/dev/null || true
mv troubleshoot.py .archive/debug/ 2>/dev/null || true
mv simple_*.html .archive/debug/ 2>/dev/null || true
mv *_test.html .archive/debug/ 2>/dev/null || true
mv console_debug.html .archive/debug/ 2>/dev/null || true
mv embed_system_test.html .archive/debug/ 2>/dev/null || true
mv fresh_watch_test.html .archive/debug/ 2>/dev/null || true
mv mged_test.html .archive/debug/ 2>/dev/null || true

# Archive backup files
echo "💾 Archiving backup files..."
mv *backup* .archive/backups/ 2>/dev/null || true
mv deployment_backup_* .archive/backups/ 2>/dev/null || true
mv tiktok_videos_backup_*.json .archive/backups/ 2>/dev/null || true
mv server.py.pre_db_migration.backup .archive/backups/ 2>/dev/null || true

# Archive temporary and experimental files
echo "🧪 Archiving temporary files..."
mv *_temp.* .archive/temp/ 2>/dev/null || true
mv temp_* .archive/temp/ 2>/dev/null || true
mv quick_*.py .archive/temp/ 2>/dev/null || true
mv quick_*.sh .archive/temp/ 2>/dev/null || true
mv simple_*.py .archive/temp/ 2>/dev/null || true
mv emergency_*.py .archive/temp/ 2>/dev/null || true
mv fix_*.py .archive/temp/ 2>/dev/null || true
mv cleanup_*.py .archive/temp/ 2>/dev/null || true
mv package_deployment.py .archive/temp/ 2>/dev/null || true
mv remote_init_db.py .archive/temp/ 2>/dev/null || true

# Archive old documentation and guides
echo "📚 Archiving old documentation..."
mv ALTERNATIVE_SETUP_METHODS.md .archive/docs/ 2>/dev/null || true
mv BLOG_SEPARATION_COMPLETE.md .archive/docs/ 2>/dev/null || true
mv BLOG_SETUP_COMPLETE.md .archive/docs/ 2>/dev/null || true
mv DATABASE_TROUBLESHOOTING.md .archive/docs/ 2>/dev/null || true
mv EMBED_DIAGNOSIS.md .archive/docs/ 2>/dev/null || true
mv FINAL_SETUP.md .archive/docs/ 2>/dev/null || true
mv HTML_UPGRADE_GUIDE.md .archive/docs/ 2>/dev/null || true
mv PRODUCTION_500_ERROR_SOLUTION.md .archive/docs/ 2>/dev/null || true
mv PRODUCTION_DB_SETUP.md .archive/docs/ 2>/dev/null || true
mv PRODUCTION_DEPLOYMENT.md .archive/docs/ 2>/dev/null || true
mv PRODUCTION_FILES_CHECKLIST.md .archive/docs/ 2>/dev/null || true
mv PRODUCTION_READY.md .archive/docs/ 2>/dev/null || true
mv PRODUCTION_READY_STATUS.md .archive/docs/ 2>/dev/null || true
mv PRODUCTION_SETUP.md .archive/docs/ 2>/dev/null || true
mv QUICK_DEPLOY.md .archive/docs/ 2>/dev/null || true
mv SECURE_API_DOCS.md .archive/docs/ 2>/dev/null || true
mv SERVER_LOG_GUIDE.md .archive/docs/ 2>/dev/null || true
mv SERVER_SETUP.md .archive/docs/ 2>/dev/null || true
mv SERVER_UPLOAD_CHECKLIST.md .archive/docs/ 2>/dev/null || true
mv SETUP_GUIDE.md .archive/docs/ 2>/dev/null || true
mv SHARED_HOSTING_SETUP.md .archive/docs/ 2>/dev/null || true
mv SSH_ACCESS_GUIDE.md .archive/docs/ 2>/dev/null || true
mv STATIC_HOSTING_GUIDE.md .archive/docs/ 2>/dev/null || true
mv TROUBLESHOOT_FILE_ENDPOINTS.md .archive/docs/ 2>/dev/null || true
mv URGENT_FIX_BLOG_API.md .archive/docs/ 2>/dev/null || true
mv VIDEOS_ENDPOINT_SOLUTION.md .archive/docs/ 2>/dev/null || true

# Archive old setup and deployment scripts
echo "🚀 Archiving old deployment scripts..."
mv cpanel_diagnostic.sh .archive/temp/ 2>/dev/null || true
mv database_fix_deployment.sh .archive/temp/ 2>/dev/null || true
mv deploy_production.sh .archive/temp/ 2>/dev/null || true
mv final_database_fix.sh .archive/temp/ 2>/dev/null || true
mv mysql_credentials_help.sh .archive/temp/ 2>/dev/null || true
mv mysql_final_deployment.sh .archive/temp/ 2>/dev/null || true
mv phppgadmin_connection_guide.sh .archive/temp/ 2>/dev/null || true
mv phppgadmin_fix_deployment.sh .archive/temp/ 2>/dev/null || true
mv upload_to_production.sh .archive/temp/ 2>/dev/null || true
mv upload_checklist.sh .archive/temp/ 2>/dev/null || true

# Archive old Python scripts
echo "🐍 Archiving old Python scripts..."
mv add_endpoint_logging.py .archive/temp/ 2>/dev/null || true
mv add_video.py .archive/temp/ 2>/dev/null || true
mv fetch_all_videos.py .archive/temp/ 2>/dev/null || true
mv fetch_tiktok_videos.py .archive/temp/ 2>/dev/null || true
mv ftp_update.py .archive/temp/ 2>/dev/null || true
mv generate_sql_dump.py .archive/temp/ 2>/dev/null || true
mv init_db.py .archive/temp/ 2>/dev/null || true
mv production_database_fix.py .archive/temp/ 2>/dev/null || true
mv production_sync.py .archive/temp/ 2>/dev/null || true
mv production_test.py .archive/temp/ 2>/dev/null || true
mv server_diagnostics.py .archive/temp/ 2>/dev/null || true
mv setup_api.py .archive/temp/ 2>/dev/null || true
mv setup_blog_db.py .archive/temp/ 2>/dev/null || true
mv setup_local_mysql.py .archive/temp/ 2>/dev/null || true
mv setup_mysql.py .archive/temp/ 2>/dev/null || true
mv setup_production_db.py .archive/temp/ 2>/dev/null || true
mv simple_db_setup.py .archive/temp/ 2>/dev/null || true
mv simple_wsgi.py .archive/temp/ 2>/dev/null || true
mv status.py .archive/temp/ 2>/dev/null || true
mv tiktok_automation.py .archive/temp/ 2>/dev/null || true
mv video_scheduler.py .archive/temp/ 2>/dev/null || true
mv web_setup.py .archive/temp/ 2>/dev/null || true

# Archive old shell scripts
echo "📜 Archiving shell scripts..."
mv cleanup.sh .archive/temp/ 2>/dev/null || true
mv cron_update.sh .archive/temp/ 2>/dev/null || true
mv cron_wrapper.sh .archive/temp/ 2>/dev/null || true
mv github_sync.sh .archive/temp/ 2>/dev/null || true
mv install_packages.sh .archive/temp/ 2>/dev/null || true
mv local_update.sh .archive/temp/ 2>/dev/null || true
mv server_init.sh .archive/temp/ 2>/dev/null || true
mv start_server.sh .archive/temp/ 2>/dev/null || true
mv switch_to_dynamic.sh .archive/temp/ 2>/dev/null || true
mv test_api_curl.sh .archive/temp/ 2>/dev/null || true
mv test_env.sh .archive/temp/ 2>/dev/null || true
mv test_production_full.sh .archive/temp/ 2>/dev/null || true
mv tiktok.sh .archive/temp/ 2>/dev/null || true
mv tiktok_server.sh .archive/temp/ 2>/dev/null || true

# Archive old HTML files (keep main ones)
echo "🌐 Archiving old HTML files..."
mv api_test.html .archive/temp/ 2>/dev/null || true
mv index_dynamic.html .archive/temp/ 2>/dev/null || true
mv video_manager.html .archive/temp/ 2>/dev/null || true
mv watch_debug.html .archive/temp/ 2>/dev/null || true
mv watch_debug_full.html .archive/temp/ 2>/dev/null || true
mv watch_dynamic.html .archive/temp/ 2>/dev/null || true
mv watch_fixed.html .archive/temp/ 2>/dev/null || true

# Archive old configuration files
echo "⚙️  Archiving old config files..."
mv manual_commands.txt .archive/temp/ 2>/dev/null || true
mv phppgadmin_connection_template.txt .archive/temp/ 2>/dev/null || true
mv production_database_setup.sql .archive/temp/ 2>/dev/null || true
mv mysql_setup.sql .archive/temp/ 2>/dev/null || true

# Archive logs and temporary databases
echo "📋 Archiving logs..."
mv *.log .archive/temp/ 2>/dev/null || true
mv blog.db .archive/temp/ 2>/dev/null || true
mv MJLights.mov .archive/temp/ 2>/dev/null || true

# Archive environment files (keep .env.production for deployment)
echo "🔐 Organizing environment files..."
mv .env.blog .archive/temp/ 2>/dev/null || true
mv .env.local .archive/temp/ 2>/dev/null || true

# Archive Python cache and virtual environments
echo "🗑️  Cleaning Python cache..."
rm -rf __pycache__ 2>/dev/null || true
mv venv .archive/temp/ 2>/dev/null || true
mv .venv .archive/temp/ 2>/dev/null || true
mv instance .archive/temp/ 2>/dev/null || true

# Archive checklist files (keep main deployment ones)
echo "📋 Archiving old checklists..."
mv DEPLOYMENT_CHECKLIST.sh .archive/temp/ 2>/dev/null || true

# Remove .DS_Store files
echo "🍎 Removing .DS_Store files..."
find . -name ".DS_Store" -delete 2>/dev/null || true

echo ""
echo "✅ CLEANUP COMPLETE!"
echo "==================="

echo ""
echo "📁 CURRENT PROJECT STRUCTURE:"
echo "============================="
echo "Core Application Files:"
echo "  ✅ server.py (main Flask application)"
echo "  ✅ passenger_wsgi.py (WSGI configuration)"
echo "  ✅ requirements_blog.txt (Python dependencies)"
echo "  ✅ .env.production (production environment)"
echo "  ✅ .env (local development environment)"
echo ""

echo "Frontend Files:"
echo "  ✅ index.html (main page)"
echo "  ✅ blog.html (blog page)"
echo "  ✅ blog-admin.html (admin interface)"
echo "  ✅ about.html (about page)"
echo "  ✅ contact.html (contact page)"
echo "  ✅ watch.html (video page)"
echo "  ✅ css/ (stylesheets)"
echo "  ✅ js/ (JavaScript files)"
echo "  ✅ images/ (image assets)"
echo ""

echo "Database & Migration:"
echo "  ✅ add_videos_table.sql (video table schema)"
echo "  ✅ migrate_videos_to_db.py (migration script)"
echo "  ✅ tiktok_videos.json (video data + GitHub Actions)"
echo ""

echo "Deployment & Setup:"
echo "  ✅ DEPLOYMENT_CHECKLIST.md (step-by-step guide)"
echo "  ✅ PRODUCTION_DEPLOYMENT_GUIDE.md (detailed guide)"
echo "  ✅ deploy_video_database.sh (deployment script)"
echo "  ✅ mysql_migration_summary.sh (summary script)"
echo "  ✅ test_setup_endpoint.py (testing script)"
echo ""

echo "Documentation:"
echo "  ✅ README.md (project documentation)"
echo "  ✅ AUTOMATION_README.md (automation docs)"
echo "  ✅ CRON_SETUP.md (cron job setup)"
echo "  ✅ GITHUB_SETUP.md (GitHub Actions setup)"
echo "  ✅ MYSQL_DEPLOYMENT_GUIDE.md (MySQL guide)"
echo "  ✅ POST_EDITOR_GUIDE.md (blog editor guide)"
echo "  ✅ PYTHON_VERSION_DECISION.md (Python version guide)"
echo ""

echo "GitHub Actions:"
echo "  ✅ .github/workflows/ (GitHub Actions workflows)"
echo ""

echo "Archived Files:"
echo "  📦 .archive/debug/ (debug and test files)"
echo "  📦 .archive/backups/ (backup files)"
echo "  📦 .archive/temp/ (temporary files)"
echo "  📦 .archive/docs/ (old documentation)"
echo ""

echo "🎯 READY FOR GITHUB!"
echo "===================="
echo "The project is now clean and organized for GitHub."
echo "All essential files are in the root directory."
echo "All temporary/debug files are archived."
echo ""

echo "📝 NEXT STEPS:"
echo "1. Review the cleaned project structure"
echo "2. Update .gitignore if needed"
echo "3. Commit changes to GitHub"
echo "4. Deploy to production using the deployment guides"
