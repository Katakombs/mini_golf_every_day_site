#!/usr/bin/env python3
"""
Project Cleanup Script
Removes temporary files, test files, and development artifacts
"""

import os
import shutil
import glob
from pathlib import Path
import sys

class ProjectCleaner:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.removed_files = []
        self.removed_dirs = []
        self.errors = []
        
    def log(self, message, level="INFO"):
        prefix = "🧹" if level == "INFO" else "❌" if level == "ERROR" else "⚠️"
        print(f"{prefix} {message}")
    
    def remove_file(self, file_path):
        """Remove a single file"""
        try:
            if self.dry_run:
                self.log(f"Would remove file: {file_path}")
            else:
                os.remove(file_path)
                self.removed_files.append(file_path)
                self.log(f"Removed file: {file_path}")
        except Exception as e:
            self.errors.append(f"Failed to remove {file_path}: {e}")
            self.log(f"Failed to remove {file_path}: {e}", "ERROR")
    
    def remove_directory(self, dir_path):
        """Remove a directory and all its contents"""
        try:
            if self.dry_run:
                self.log(f"Would remove directory: {dir_path}")
            else:
                shutil.rmtree(dir_path)
                self.removed_dirs.append(dir_path)
                self.log(f"Removed directory: {dir_path}")
        except Exception as e:
            self.errors.append(f"Failed to remove {dir_path}: {e}")
            self.log(f"Failed to remove {dir_path}: {e}", "ERROR")
    
    def clean_python_cache(self):
        """Remove Python cache files and directories"""
        self.log("Cleaning Python cache files...")
        
        # Remove __pycache__ directories
        for pycache_dir in glob.glob("**/__pycache__", recursive=True):
            self.remove_directory(pycache_dir)
        
        # Remove .pyc files
        for pyc_file in glob.glob("**/*.pyc", recursive=True):
            self.remove_file(pyc_file)
        
        # Remove .pyo files
        for pyo_file in glob.glob("**/*.pyo", recursive=True):
            self.remove_file(pyo_file)
    
    def clean_system_files(self):
        """Remove system-generated files"""
        self.log("Cleaning system files...")
        
        # Remove .DS_Store files (macOS)
        for ds_store in glob.glob("**/.DS_Store", recursive=True):
            self.remove_file(ds_store)
        
        # Remove Thumbs.db files (Windows)
        for thumbs in glob.glob("**/Thumbs.db", recursive=True):
            self.remove_file(thumbs)
        
        # Remove desktop.ini files (Windows)
        for desktop_ini in glob.glob("**/desktop.ini", recursive=True):
            self.remove_file(desktop_ini)
    
    def clean_test_files(self):
        """Remove test and debug files"""
        self.log("Cleaning test and debug files...")
        
        test_files = [
            # Test HTML files
            "test_embed.html",
            "simple_embed_test.html",
            "embed_system_test.html",
            "console_debug.html",
            "debug.html",
            "mged_test.html",
            "simple_test.html",
            
            # Debug variations
            "watch_debug.html",
            "watch_debug_full.html",
            "index_static.html",
            "index_dynamic.html",
            "watch_static.html",
            "watch_dynamic.html",
            
            # Backup HTML files
            "watch_backup_20250703_143144.html",
            "watch_backup_20250703_163100.html",
            
            # Test scripts
            "test_secure_api.py",
            "test_api.py",
            "test_detection.py",
            "debug.py",
            "status.py",
            "diagnose_tiktok.py",
            "diagnose_production.py",
            "production_sync.py",
            "setup_api.py",
            
            # Backup JSON files
            "tiktok_videos_backup_20250703_163100.json",
        ]
        
        for test_file in test_files:
            if os.path.exists(test_file):
                self.remove_file(test_file)
    
    def clean_deployment_artifacts(self):
        """Remove deployment packages and temporary directories"""
        self.log("Cleaning deployment artifacts...")
        
        # Remove deployment directories
        for deployment_dir in glob.glob("deployment_*"):
            if os.path.isdir(deployment_dir):
                self.remove_directory(deployment_dir)
        
        # Remove deployment zip files
        for deployment_zip in glob.glob("deployment_*.zip"):
            self.remove_file(deployment_zip)
        
        # Remove packaging script
        if os.path.exists("package_deployment.py"):
            self.remove_file("package_deployment.py")
    
    def clean_backup_files(self):
        """Remove backup and temporary files"""
        self.log("Cleaning backup and temporary files...")
        
        backup_patterns = [
            "*.bak",
            "*.tmp",
            "*~",
            "*.orig",
            "*.save",
            "*_backup",
            "*_old",
        ]
        
        for pattern in backup_patterns:
            for backup_file in glob.glob(f"**/{pattern}", recursive=True):
                self.remove_file(backup_file)
    
    def clean_documentation_extras(self):
        """Remove extra documentation files (keep essentials)"""
        self.log("Cleaning extra documentation...")
        
        extra_docs = [
            "EMBED_DIAGNOSIS.md",
            "FINAL_SETUP.md",
            "DEPLOYMENT_CHECKLIST.md",
            "SERVER_UPLOAD_CHECKLIST.md",
            "CRON_SETUP.md",
            "QUICK_DEPLOY.md",
            "PRODUCTION_DEPLOYMENT.md",
            "SECURE_API_DOCS.md",
        ]
        
        for doc in extra_docs:
            if os.path.exists(doc):
                self.remove_file(doc)
    
    def clean_shell_scripts(self):
        """Remove development shell scripts"""
        self.log("Cleaning shell scripts...")
        
        shell_scripts = [
            "upload_checklist.sh",
            "tiktok_server.sh",
            "tiktok.sh",
            "cron_wrapper.sh",
            "test_api_curl.sh",
            "switch_to_dynamic.sh",
        ]
        
        for script in shell_scripts:
            if os.path.exists(script):
                self.remove_file(script)
    
    def clean_virtual_environments(self):
        """Remove virtual environments (be careful!)"""
        self.log("Checking virtual environments...")
        
        venv_dirs = ["py311env", "venv", ".venv", "env"]
        
        for venv_dir in venv_dirs:
            if os.path.exists(venv_dir) and os.path.isdir(venv_dir):
                self.log(f"Found virtual environment: {venv_dir}")
                if not self.dry_run:
                    confirm = input(f"Remove virtual environment '{venv_dir}'? (y/N): ")
                    if confirm.lower() == 'y':
                        self.remove_directory(venv_dir)
                    else:
                        self.log(f"Keeping virtual environment: {venv_dir}")
    
    def clean_config_files(self):
        """Remove temporary config files"""
        self.log("Cleaning temporary config files...")
        
        config_files = [
            "cron_config.txt",
            ".env.backup",
            ".env.old",
            "config.json.tmp",
        ]
        
        for config in config_files:
            if os.path.exists(config):
                self.remove_file(config)
    
    def clean_log_files(self):
        """Remove log files"""
        self.log("Cleaning log files...")
        
        log_patterns = [
            "*.log",
            "*.log.*",
            "cron_update.log",
            "cron_update.log.old",
        ]
        
        for pattern in log_patterns:
            for log_file in glob.glob(pattern):
                if os.path.exists(log_file):
                    self.log(f"Found log file: {log_file}")
                    if not self.dry_run:
                        confirm = input(f"Remove log file '{log_file}'? (y/N): ")
                        if confirm.lower() == 'y':
                            self.remove_file(log_file)
                        else:
                            self.log(f"Keeping log file: {log_file}")
                    else:
                        self.log(f"Would remove log file: {log_file}")
    
    def cleanup_all(self):
        """Run all cleanup operations"""
        self.log("🧹 Starting Mini Golf Every Day Project Cleanup")
        self.log("=" * 60)
        
        # Run cleanup operations
        self.clean_python_cache()
        self.clean_system_files()
        self.clean_test_files()
        self.clean_deployment_artifacts()
        self.clean_backup_files()
        self.clean_documentation_extras()
        self.clean_shell_scripts()
        self.clean_config_files()
        self.clean_log_files()
        self.clean_virtual_environments()
        
        # Summary
        self.log("=" * 60)
        self.log("🎯 Cleanup Summary")
        self.log("=" * 60)
        self.log(f"Files removed: {len(self.removed_files)}")
        self.log(f"Directories removed: {len(self.removed_dirs)}")
        self.log(f"Errors: {len(self.errors)}")
        
        if self.errors:
            self.log("\n❌ Errors encountered:")
            for error in self.errors:
                self.log(f"  • {error}")
        
        if self.dry_run:
            self.log("\n⚠️  This was a DRY RUN - no files were actually removed")
            self.log("Run with --force to actually remove files")
        else:
            self.log("\n✅ Cleanup completed!")
        
        # Show what's left
        essential_files = [
            "index.html", "watch.html", "about.html", "blog.html", "contact.html",
            "flask_app.py", "tiktok_automation.py", "cron_update.py",
            "tiktok_videos.json", "passenger_wsgi.py",
            ".gitignore", "README.md", "requirements.txt", "favicon.ico",
            "MJLights.mov", "css/", "js/", "images/", ".env"
        ]
        
        self.log("\n📋 Essential files that should remain:")
        for file in essential_files:
            if os.path.exists(file):
                self.log(f"  ✅ {file}")
            else:
                self.log(f"  ❓ {file} (not found)")
                
        # Add self-cleanup option
        if not self.dry_run:
            self.log("\n🧹 Self-cleanup option:")
            confirm = input("Remove this cleanup script as well? (y/N): ")
            if confirm.lower() == 'y':
                self.remove_file("cleanup_project.py")
                self.log("✅ Cleanup script removed - project is fully cleaned!")

def main():
    dry_run = True
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("Project Cleanup Script")
            print("Usage:")
            print("  python cleanup_project.py           # Dry run (preview)")
            print("  python cleanup_project.py --force   # Actually remove files")
            return
        elif sys.argv[1] == '--force':
            dry_run = False
    
    if dry_run:
        print("🔍 Running in DRY RUN mode - no files will be removed")
        print("Run with --force to actually remove files")
        print()
    
    cleaner = ProjectCleaner(dry_run=dry_run)
    cleaner.cleanup_all()

if __name__ == "__main__":
    main()
