# GitHub Actions + cPanel Setup Guide

This is a **much better solution** than trying to run yt-dlp on your cPanel server!

## 🎯 **How It Works:**

1. **GitHub Actions** runs yt-dlp in the cloud every 4 hours
2. **Fetches real TikTok titles** and video information  
3. **Commits updated JSON** back to your repository
4. **Your cPanel server** simply downloads the updated JSON file
5. **Your website** always shows the latest videos with real titles

## 📋 **Setup Steps:**

### **1. Push Your Code to GitHub**

```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit"

# Add your GitHub repository
git remote add origin https://github.com/yourusername/mini_golf_every_day_site.git
git push -u origin main
```

### **2. GitHub Repository Settings**

- Go to your repository on GitHub
- Navigate to **Settings → Actions → General**
- Under **Workflow permissions**, select **"Read and write permissions"**
- Check **"Allow GitHub Actions to create and approve pull requests"**

### **3. Update GitHub Sync Script**

Edit `github_sync.sh` and replace `yourusername` with your actual GitHub username:

```bash
GITHUB_RAW_URL="https://raw.githubusercontent.com/YOURUSERNAME/mini_golf_every_day_site/main/tiktok_videos.json"
```

### **4. Upload to cPanel Server**

Upload these files to your cPanel server:
- `github_sync.sh` (the new sync script)
- `tiktok_videos.json` (current database)
- `flask_app.py` (for manual API access if needed)
- `.env` (environment variables)

Set permissions:
```bash
chmod 755 github_sync.sh
chmod 664 tiktok_videos.json
```

### **5. Set Up cPanel Cron Job**

In cPanel Cron Jobs, add:
- **Command**: `/home/yourusername/public_html/github_sync.sh`
- **Schedule**: `*/30 * * * *` (every 30 minutes)

### **6. Test the Workflow**

1. **Manual GitHub Action**: Go to Actions tab → "Update TikTok Videos" → "Run workflow"
2. **Check results**: Wait a few minutes, then check if `tiktok_videos.json` was updated
3. **Test cPanel sync**: Run `./github_sync.sh` manually on your server

## 🎉 **Benefits of This Approach:**

- ✅ **Real TikTok titles** from yt-dlp
- ✅ **No server dependencies** (no need to install yt-dlp on cPanel)
- ✅ **Runs in the cloud** with GitHub's infrastructure
- ✅ **Automatic backups** in git history
- ✅ **Reliable scheduling** with GitHub Actions
- ✅ **Easy monitoring** through GitHub Actions logs
- ✅ **Fast server sync** (just downloads a JSON file)

## 🔍 **Monitoring:**

- **GitHub Actions**: Check the "Actions" tab in your repository
- **Server logs**: Check `github_sync.log` on your cPanel server
- **Website**: Verify new videos appear automatically

## 🚀 **Result:**

Your website will now automatically update with real TikTok video titles every few hours, and your cPanel server only needs to download a small JSON file - no complex dependencies required!
