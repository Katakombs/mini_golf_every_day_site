#!/bin/bash
# Cron wrapper script for Mini Golf Every Day automated updates
# This script handles environment setup and error recovery

# Configuration - UPDATE THESE PATHS FOR YOUR SERVER
SCRIPT_DIR="/home/phazeshi/minigolfeveryday"  # Update this to your server path
PYTHON_BIN="/home/phazeshi/virtualenv/minigolfeveryday/3.8/bin/python3.8"  # Update this to your Python path
LOG_FILE="$SCRIPT_DIR/cron_wrapper.log"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to check if required files exist
check_files() {
    local missing_files=()
    
    if [[ ! -f "$SCRIPT_DIR/cron_update.py" ]]; then
        missing_files+=("cron_update.py")
    fi
    
    if [[ ! -f "$SCRIPT_DIR/flask_app.py" ]]; then
        missing_files+=("flask_app.py")
    fi
    
    if [[ ! -f "$SCRIPT_DIR/tiktok_automation.py" ]]; then
        missing_files+=("tiktok_automation.py")
    fi
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        log "❌ Missing required files: ${missing_files[*]}"
        return 1
    fi
    
    return 0
}

# Function to check Python dependencies
check_dependencies() {
    if ! "$PYTHON_BIN" -c "import flask, requests, yt_dlp" 2>/dev/null; then
        log "❌ Python dependencies missing. Installing..."
        "$PYTHON_BIN" -m pip install flask requests yt-dlp --user
        if [[ $? -ne 0 ]]; then
            log "❌ Failed to install dependencies"
            return 1
        fi
        log "✅ Dependencies installed successfully"
    fi
    return 0
}

# Main execution
main() {
    log "🚀 Starting Mini Golf Every Day cron job"
    log "Script directory: $SCRIPT_DIR"
    log "Python binary: $PYTHON_BIN"
    
    # Change to script directory
    cd "$SCRIPT_DIR" || {
        log "❌ Failed to change to script directory: $SCRIPT_DIR"
        exit 1
    }
    
    # Check if Python binary exists
    if [[ ! -f "$PYTHON_BIN" ]]; then
        log "❌ Python binary not found: $PYTHON_BIN"
        exit 1
    fi
    
    # Check required files
    if ! check_files; then
        log "❌ File check failed"
        exit 1
    fi
    
    # Check dependencies
    if ! check_dependencies; then
        log "❌ Dependency check failed"
        exit 1
    fi
    
    # Run the update script
    log "▶️  Running video update..."
    "$PYTHON_BIN" "$SCRIPT_DIR/cron_update.py"
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        log "✅ Cron job completed successfully"
    else
        log "❌ Cron job failed with exit code: $exit_code"
    fi
    
    # Clean up old log files (keep last 30 days)
    find "$SCRIPT_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null
    
    log "🏁 Cron job finished"
    return $exit_code
}

# Execute main function
main "$@"
