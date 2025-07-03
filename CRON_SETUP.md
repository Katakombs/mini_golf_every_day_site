# Mini Golf Every Day - Cron Job Setup Guide

## 📋 Overview
This guide helps you set up automated TikTok video updates for your Mini Golf Every Day website using cron jobs.

## 🗂️ Files Created
- `cron_update.py` - Main Python script that calls your API
- `cron_wrapper.sh` - Shell wrapper that handles environment setup
- `cron_config.txt` - Sample cron job configurations
- `CRON_SETUP.md` - This guide

## 🚀 Setup Instructions

### Step 1: Update Configuration Files

1. **Update cron_wrapper.sh** with your server paths:
   ```bash
   # Edit these lines in cron_wrapper.sh:
   SCRIPT_DIR="/home/phazeshi/minigolfeveryday"  # Your server directory
   PYTHON_BIN="/home/phazeshi/virtualenv/minigolfeveryday/3.8/bin/python3.8"  # Your Python path
   ```

2. **Update cron_update.py** with your domain:
   ```python
   # Edit this line in cron_update.py:
   DOMAIN = "https://yourdomain.com"  # Your actual domain
   ```

### Step 2: Upload Files to Server

Upload these files to your server:
- `cron_update.py`
- `cron_wrapper.sh`

Make sure they're in the same directory as your other Python files.

### Step 3: Make Scripts Executable

SSH into your server and run:
```bash
chmod +x /home/phazeshi/minigolfeveryday/cron_wrapper.sh
```

### Step 4: Test the Scripts

Test the cron script manually first:
```bash
# SSH into your server and run:
cd /home/phazeshi/minigolfeveryday
./cron_wrapper.sh
```

You should see output like:
```
2025-07-03 14:30:00 - 🚀 Starting Mini Golf Every Day cron job
2025-07-03 14:30:01 - ✅ Dependencies installed successfully
2025-07-03 14:30:02 - ▶️  Running video update...
2025-07-03 14:30:15 - ✅ Cron job completed successfully
```

### Step 5: Set Up Cron Job

1. **Edit your cron jobs:**
   ```bash
   crontab -e
   ```

2. **Add one of these lines** (choose based on how often you want updates):

   **Every 2 hours (Recommended):**
   ```
   0 */2 * * * /home/phazeshi/minigolfeveryday/cron_wrapper.sh >> /home/phazeshi/minigolfeveryday/cron.log 2>&1
   ```

   **Twice daily (8 AM and 8 PM):**
   ```
   0 8,20 * * * /home/phazeshi/minigolfeveryday/cron_wrapper.sh >> /home/phazeshi/minigolfeveryday/cron.log 2>&1
   ```

   **Once daily (9 AM):**
   ```
   0 9 * * * /home/phazeshi/minigolfeveryday/cron_wrapper.sh >> /home/phazeshi/minigolfeveryday/cron.log 2>&1
   ```

3. **Save and exit** (usually Ctrl+X, then Y, then Enter)

### Step 6: Verify Cron Job

1. **Check that cron job was saved:**
   ```bash
   crontab -l
   ```

2. **Monitor the logs:**
   ```bash
   tail -f /home/phazeshi/minigolfeveryday/cron.log
   ```

## 📊 Monitoring

### Log Files
- `cron.log` - Overall cron job output
- `cron_wrapper.log` - Wrapper script logs
- `cron_update.log` - Detailed update logs

### Check Status
You can always check your API status manually:
```bash
curl https://yourdomain.com/api/status
```

## 🔧 Troubleshooting

### Common Issues

1. **"Python binary not found"**
   - Update PYTHON_BIN path in cron_wrapper.sh
   - Find your Python path: `which python3`

2. **"Missing required files"**
   - Make sure all Python files are uploaded
   - Check file permissions: `ls -la *.py`

3. **"API status check failed"**
   - Verify your domain is correct in cron_update.py
   - Test your API manually: `curl https://yourdomain.com/api/status`

4. **"Dependencies missing"**
   - The script will try to install them automatically
   - Or install manually: `pip install flask requests yt-dlp --user`

### Disable Cron Job
To stop automatic updates:
```bash
crontab -e
# Comment out the line by adding # at the beginning
# 0 */2 * * * /home/phazeshi/minigolfeveryday/cron_wrapper.sh >> /home/phazeshi/minigolfeveryday/cron.log 2>&1
```

Or remove all cron jobs:
```bash
crontab -r
```

## 📝 What the Automation Does

1. **Checks API Status** - Ensures your website is responding
2. **Gets Current Video Count** - Tracks how many videos you have
3. **Triggers Update** - Calls your `/api/update` endpoint
4. **Logs Results** - Records success/failure and new video count
5. **Cleans Up** - Removes old log files automatically

## 🎯 Expected Behavior

- **New Videos Found**: Logs will show "Added X new video(s)!"
- **No New Videos**: Logs will show "No new videos found"
- **Errors**: Detailed error messages in logs for troubleshooting

## 📞 Support

If you encounter issues:
1. Check the log files for detailed error messages
2. Test the API endpoints manually
3. Verify all file paths and permissions
4. Make sure your Python environment has all required packages
