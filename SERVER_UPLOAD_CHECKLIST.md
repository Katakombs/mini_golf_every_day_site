# 🚀 Server Upload Checklist - Mini Golf Every Day

## 📋 Files to Upload

### ✅ Core Website Files
- `index.html` (now dynamic version with Instagram link)
- `watch.html` (now dynamic version with Instagram link) 
- `about.html` (updated with dynamic stats and Instagram link)
- `blog.html`
- `contact.html`
- `favicon.ico`

### ✅ Static Assets
- `css/` folder (all CSS files)
- `images/` folder (all images)
- `js/` folder (all JavaScript files)

### ✅ Python Backend Files
- `flask_app.py`
- `passenger_wsgi.py`
- `tiktok_automation.py`
- `add_video.py`
- `cron_update.py`
- `cron_wrapper.sh`
- `requirements.txt`
- `.htaccess`

### ✅ Database File
- `tiktok_videos.json` (178 videos - 46KB file)

### ✅ Automation Scripts
- `fetch_all_videos.py` (for future use)
- `debug.py` (for troubleshooting)

## 🔧 Server Setup Steps

### 1. Upload Files
Upload all the files listed above to your shared hosting directory.

### 2. Install Python Dependencies
SSH into your server and run:
```bash
pip install -r requirements.txt
```

### 3. Set File Permissions
```bash
chmod +x cron_wrapper.sh
chmod +x cron_update.py
chmod 644 *.html
chmod 644 *.json
chmod 644 *.py
```

### 4. Test Flask API
Visit these URLs to verify:
- `https://minigolfevery.day/api/status`
- `https://minigolfevery.day/api/videos`

### 5. Set Up Cron Job
Add to your crontab:
```bash
# Update TikTok videos every 6 hours
0 */6 * * * /path/to/your/site/cron_wrapper.sh
```

### 6. Test Website
- Homepage: `https://minigolfevery.day/`
- Watch page: `https://minigolfevery.day/watch.html`

## 🎯 Expected Results

After upload, your website will:
- ✨ Show live count of 178 videos
- 🔍 Allow users to search all videos
- 📱 Work perfectly on mobile
- ⚡ Auto-update every 6 hours
- 🎬 Display all TikTok videos dynamically

## 🆘 Troubleshooting

If something doesn't work:
1. Check Flask API endpoints first
2. Verify `tiktok_videos.json` uploaded correctly
3. Check browser console for JavaScript errors
4. Review server error logs

## 📞 Support Files

Keep these locally for reference:
- `index_static.html` (backup)
- `watch_static.html` (backup)
- `tiktok_videos_backup_*.json` (backup)
- All `*_backup_*.html` files

---
**Upload Date**: July 3, 2025
**Total Videos**: 178
**Database Size**: 46KB
