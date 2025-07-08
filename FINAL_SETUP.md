# 🚀 GitHub Actions Setup - COMPLETE GUIDE

## ✅ **What You Have Now:**

1. **GitHub Actions Workflow** (`.github/workflows/update_tiktok_videos.yml`)
2. **Smart Update Script** (`.github/workflows/update_videos.py`) 
3. **cPanel Sync Script** (`github_sync.sh`)
4. **Public Repository** (no authentication needed)

## 📋 **Final Setup Steps:**

### **1. Push All Files to GitHub**

```bash
git add .
git commit -m "Add GitHub Actions automation for TikTok videos"
git push origin main
```

### **2. Make Repository Public** ✅ DONE
- Your repository is already public at: `Katakombs/mini_golf_every_day_site`

### **3. Enable GitHub Actions**
- Go to: https://github.com/Katakombs/mini_golf_every_day_site/settings/actions
- Under "Actions permissions", select **"Allow all actions and reusable workflows"**
- Under "Workflow permissions", select **"Read and write permissions"**

### **4. Test GitHub Actions Manually**
- Go to: https://github.com/Katakombs/mini_golf_every_day_site/actions
- Click "Update TikTok Videos" workflow
- Click "Run workflow" button
- Wait 2-3 minutes and check if `tiktok_videos.json` gets updated

### **5. Upload to cPanel Server**

Upload these files to your server:
```
github_sync.sh          # Main sync script
tiktok_videos.json      # Current video database  
.env                    # Environment variables (optional)
flask_app.py           # API server (optional)
```

Set permissions:
```bash
chmod 755 github_sync.sh
chmod 644 tiktok_videos.json
```

### **6. Set Up cPanel Cron Job**

In cPanel → Cron Jobs, add:
- **Command**: `/home/yourusername/public_html/github_sync.sh`
- **Schedule**: `*/30 * * * *` (every 30 minutes)

### **7. Test Complete System**

```bash
# Test GitHub sync manually on your server
./github_sync.sh

# Check the log
cat github_sync.log
```

## 🎯 **How It Works:**

1. **Every 4 hours**: GitHub Actions runs yt-dlp in the cloud
2. **Gets real titles**: Like "Day 181. Balance. #minigolfeveryday..."
3. **Commits to repo**: Updates `tiktok_videos.json` automatically
4. **Every 30 minutes**: Your server downloads the latest JSON
5. **Website updates**: Shows new videos with real titles instantly

## 🎉 **Benefits:**

- ✅ **Real TikTok video titles** (not generic ones)
- ✅ **No server dependencies** (no yt-dlp installation needed)
- ✅ **Reliable cloud execution** (GitHub's infrastructure)
- ✅ **Automatic backups** (git history)
- ✅ **Easy monitoring** (GitHub Actions logs)
- ✅ **Fast server sync** (just downloads a JSON file)

## 📊 **Monitoring:**

- **GitHub Actions**: https://github.com/Katakombs/mini_golf_every_day_site/actions
- **Server logs**: `github_sync.log` on your cPanel server
- **Latest JSON**: https://raw.githubusercontent.com/Katakombs/mini_golf_every_day_site/refs/heads/main/tiktok_videos.json

## 🚨 **Troubleshooting:**

If GitHub Actions fails:
- Check the Actions tab for error logs
- TikTok might be blocking yt-dlp temporarily
- The workflow will retry on the next schedule

If server sync fails:
- Check `github_sync.log` for curl errors
- Verify the GitHub URL is accessible
- Check file permissions

Your automation is now bulletproof! 🎬✨
