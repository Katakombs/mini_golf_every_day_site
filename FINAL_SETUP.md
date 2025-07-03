# 📁 Essential Files for Your Server

## Upload Only These Files:

### ✅ Core Web App (Required):
```
passenger_wsgi.py    - WSGI entry point
flask_app.py         - Your web application  
requirements.txt     - Dependencies
```

### ✅ TikTok Automation:
```
tiktok_automation.py - Main automation logic
add_video.py         - Add individual videos
tiktok_server.sh     - Command line tool
test_detection.py    - Test if automation works
```

### ✅ Your Website:
```
index.html           - Homepage
watch.html           - Watch page  
about.html           - About page
css/                 - Stylesheets
js/                  - JavaScript
images/              - Images
favicon.ico          - Site icon
```

## 🚀 Quick Commands:

### Add a video:
```bash
./tiktok_server.sh add VIDEO_ID
```

### Check status:
```bash
./tiktok_server.sh status
```

### Test automation:
```bash
./tiktok_server.sh test
```

### Via web API:
```
https://yourdomain.com/api/add/VIDEO_ID
https://yourdomain.com/api/status
https://yourdomain.com/api/update
```

## 🗑️ Files Removed (Not Needed):
- Multiple documentation files
- Alternative server implementations  
- Development/testing scripts
- Backup automation methods

Your setup is now clean and minimal! 🎉
