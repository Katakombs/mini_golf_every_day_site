# 🚀 PRODUCTION DEPLOYMENT CHECKLIST
## Video Database Migration - Step by Step

### ✅ READY TO DEPLOY
All files have been prepared and tested locally. GitHub Actions compatibility is maintained.

---

## 📁 STEP 1: UPLOAD FILES

Upload these files to your hosting account:

```
✅ server.py (updated with database support)
✅ .env.production (MySQL credentials) 
✅ requirements_blog.txt (MySQL dependencies)
✅ passenger_wsgi.py (WSGI configuration)  
✅ tiktok_videos.json (GitHub Actions compatibility)
✅ migrate_videos_to_db.py (migration script)
✅ add_videos_table.sql (database schema)
```

**Upload Method:** Use your preferred method (FTP, SFTP, FileZilla, etc.)

---

## 🗄️ STEP 2: DATABASE SETUP

### A. Create Videos Table
1. Log into your hosting control panel
2. Open **phpMyAdmin** or **MySQL** interface  
3. Select database: `phazeshi_minigolfeveryday`
4. Copy and run this SQL:

```sql
CREATE TABLE IF NOT EXISTS videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    video_id VARCHAR(255) UNIQUE NOT NULL,
    title TEXT,
    upload_date VARCHAR(8), 
    url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_video_id (video_id),
    INDEX idx_upload_date (upload_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX idx_videos_upload_date_desc ON videos (upload_date DESC);
```

---

## 💻 STEP 3: DATABASE SETUP

You have two options:

### Option A: One-Command Setup (Recommended)
```bash
# Navigate to your site directory  
cd /home/yourusername/public_html

# Rename environment file
mv .env.production .env

# Install Python dependencies
pip install -r requirements_blog.txt --user

# Run complete setup (creates tables + migrates videos)
curl https://yourdomain.com/api/setup
```

### Option B: Manual Setup
```bash
# Navigate to your site directory
cd /home/yourusername/public_html

# Rename environment file
mv .env.production .env

# Install Python dependencies
pip install -r requirements_blog.txt --user

# Run database migration manually
python migrate_videos_to_db.py
```

---

## 🔄 STEP 4: RESTART APPLICATION

Restart your web server/application:
- **cPanel:** Go to "Python Apps" → Restart
- **Other hosting:** Check your control panel for restart option
- **SSH:** May need to restart passenger/uwsgi service

---

## 🧪 STEP 5: TEST DEPLOYMENT

Test these endpoints to verify everything works:

```bash
# Test complete setup endpoint
curl https://minigolfevery.day/api/setup

# Test video endpoint (should be faster now)
curl https://minigolfevery.day/api/videos

# Test status endpoint
curl https://minigolfevery.day/api/status

# Test blog endpoint
curl https://minigolfevery.day/api/blog/posts
```

**Expected Results:**
- ✅ No 500 errors
- ✅ Fast response times
- ✅ All endpoints return proper JSON data
- ✅ Setup endpoint shows video migration success

---

## ✅ VERIFICATION CHECKLIST

After deployment, confirm these are working:

### API Endpoints
- [ ] `/api/videos` - Returns 181+ videos (database source)
- [ ] `/api/status` - Returns site statistics 
- [ ] `/api/blog/posts` - Returns blog posts
- [ ] No 500 errors on any endpoint

### Database  
- [ ] Videos table exists in MySQL
- [ ] Contains 181+ video records
- [ ] Migration script completed successfully

### GitHub Actions Compatibility
- [ ] `tiktok_videos.json` file still exists
- [ ] GitHub Actions workflow unchanged
- [ ] Next video update will sync to database automatically

---

## 🚨 IF SOMETHING GOES WRONG

### Quick Rollback
```bash
# Restore original server.py
cp server.py.pre_db_migration.backup server.py

# Restart application
# Your hosting restart method here
```

### Debug Steps
1. Check server error logs
2. Verify MySQL credentials in `.env`
3. Test database connection manually
4. Ensure all files uploaded correctly

---

## 🎉 SUCCESS! 

After deployment you'll have:
- ⚡ **Faster video loading** (database vs file I/O)
- 🛡️ **No more 500 errors** (robust database storage)  
- ✅ **GitHub Actions compatibility** (automatic JSON sync)
- 🚀 **Production ready** (enterprise-grade data storage)

Your GitHub Actions will continue working exactly as before, but now the backend reads from a database for better performance and reliability!
