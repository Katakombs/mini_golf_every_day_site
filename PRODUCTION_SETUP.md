# Production Server Setup Guide

## Files to Upload to Your cPanel Server

### 1. **cron_wrapper.sh** 
- Upload to your website's root directory (same folder as your HTML files)
- Set permissions to **755** in cPanel File Manager
- This script uses your existing Flask API (no yt-dlp needed!)

### 2. **Environment Variables**
Make sure your `.env` file on the server has:
```
MGED_API_KEY=your_api_key_here
MGED_DOMAIN=https://minigolfevery.day
```

### 3. **NO yt-dlp Installation Needed!**
The new approach uses your existing `/api/add/<video_id>` endpoint, so no additional packages are required on your server.

**Steps:**
1. Log into cPanel
2. Go to "Cron Jobs" 
3. Add a new cron job with these settings:

**Command:**
```
/home/YOUR_USERNAME/public_html/cron_wrapper.sh
```
(Replace YOUR_USERNAME with your actual cPanel username)

### 4. **Set Up Cron Job in cPanel**

**Steps:**
1. Log into cPanel
2. Go to "Cron Jobs" 
3. Add a new cron job with these settings:

**Command:**
```
/home/YOUR_USERNAME/public_html/cron_wrapper.sh
```
(Replace YOUR_USERNAME with your actual cPanel username)

**Recommended Schedule:**
- **Every 2 hours**: `0 */2 * * *` 
- **Every 4 hours**: `0 */4 * * *`
- **Daily at 9 AM**: `0 9 * * *`

### 5. **How It Works Now**
1. 🔍 Script scrapes TikTok profile page for video IDs
2. 🆕 Finds new videos not in your database  
3. 🚀 Calls your Flask API `/api/add/<video_id>` for each new video
4. ✅ Your existing API handles getting video info and updating the JSON
5. 🎉 Website automatically shows new videos!

### 6. **Check Logs**
- After the cron runs, check `cron.log` in your website directory
- Look for backup files: `tiktok_videos_backup_YYYYMMDD_HHMMSS.json`

### 7. **Troubleshooting**
If the cron job fails:
- Check file permissions (should be 755)
- Check `cron.log` for error messages  
- Verify your Flask app is running on the server
- Make sure `.env` file has correct API key
- Ensure your server can access TikTok and make HTTP requests

## Current Status
- ✅ Uses your existing Flask API (much simpler!)
- ✅ No yt-dlp or pip installation required
- ✅ Works with basic Python + requests library
- ✅ Automatic backups before updates
- ✅ Comprehensive logging
- ✅ Production-ready for cPanel

## Next Steps
1. Upload updated `cron_wrapper.sh` to your server
2. Make sure your Flask app is running and accessible
3. Set up the cron job in cPanel
4. The cron job will find Day 180 and add it automatically!
