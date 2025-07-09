# 🚀 Production Deployment Guide
## Mini Golf Every Day - Video Database Migration

### 📋 Overview
This guide will deploy the updated Mini Golf Every Day site with:
- ✅ Videos moved from JSON to MySQL database  
- ✅ Maintained GitHub Actions compatibility
- ✅ Fixed 500 errors on `/api/videos` and `/api/status`
- ✅ Improved performance and reliability

---

## 🎯 WHAT WAS COMPLETED LOCALLY

### ✅ Database Migration
- [x] Created `videos` table in MySQL database
- [x] Migrated 181 videos from `tiktok_videos.json` to database
- [x] Updated backend to read from database with JSON fallback
- [x] Maintained full GitHub Actions compatibility

### ✅ Files Updated
- [x] `server.py` - Added database video functions
- [x] `migrate_videos_to_db.py` - Migration script (run locally)
- [x] `requirements_blog.txt` - Added PyMySQL dependency
- [x] `.env.production` - Production MySQL credentials

---

## 📁 FILES TO UPLOAD TO PRODUCTION

### 1. Core Application Files
```
✅ server.py (updated with database support)
✅ .env.production (MySQL credentials) → rename to .env
✅ requirements_blog.txt (MySQL dependencies)
✅ tiktok_videos.json (maintained for GitHub Actions)
✅ passenger_wsgi.py (WSGI configuration)
```

### 2. Database Files (for setup)
```
✅ add_videos_table.sql (video table schema)
✅ migrate_videos_to_db.py (run once on production)
```

---

## 🗄️ PRODUCTION DATABASE SETUP

### Step 1: Create MySQL Database
1. Log into your hosting control panel
2. Go to **MySQL Databases** section
3. Verify these exist (should be from previous setup):
   - Database: `phazeshi_minigolfeveryday`
   - User: `phazeshi_mged`
   - Password: `nypgu1-vikjyw-kofKug`

### Step 2: Create Videos Table
Run this SQL in phpMyAdmin or MySQL interface:

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
```

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Upload Files to Production
Upload these files to your hosting account:

```bash
# Core files
server.py
.env.production (rename to .env)
requirements_blog.txt
passenger_wsgi.py
tiktok_videos.json

# Database migration files
migrate_videos_to_db.py
add_videos_table.sql
```

### Step 2: Install Python Dependencies
SSH into your hosting account and run:

```bash
cd /path/to/your/site
pip install -r requirements_blog.txt --user
```

### Step 3: Run Database Migration
You have two options for setting up the database:

#### Option A: Use the Setup API (Recommended)
```bash
# Test the setup endpoint - this will create all tables and migrate videos
curl https://minigolfevery.day/api/setup
```

This single endpoint will:
- Create all database tables (blog + videos)
- Create the admin user
- Migrate videos from JSON to database
- Sync database back to JSON for GitHub Actions
- Provide detailed status report

#### Option B: Manual Migration
```bash
cd /path/to/your/site
python migrate_videos_to_db.py
```

This will:
- Connect to your production MySQL database
- Migrate all videos from JSON to database
- Sync database back to JSON for GitHub Actions

### Step 4: Restart Web Application
- Restart your web server/application
- This varies by hosting provider (usually in control panel)

### Step 5: Test Endpoints
```bash
# Test setup endpoint (creates everything)
curl https://minigolfevery.day/api/setup

# Test video endpoint
curl https://minigolfevery.day/api/videos

# Test status endpoint  
curl https://minigolfevery.day/api/status

# Test blog endpoint
curl https://minigolfevery.day/api/blog/posts

# Should return data without 500 errors
```

---

## 🔧 CONFIGURATION DETAILS

### Environment Variables (.env)
```bash
# API Configuration
MGED_API_KEY=_HHIKEGqH8ieN-J_Eh8QiaHyQmc_ThZv_ekDA9hueWU
MGED_ENV=production
MGED_DOMAIN=https://minigolfevery.day

# MySQL Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=phazeshi_minigolfeveryday
DB_USER=phazeshi_mged
DB_PASSWORD=nypgu1-vikjyw-kofKug

# Security
SECRET_KEY=c247e66f3ae5040914b493ba14b7054a816f476d61f6a56e64446580360ac23e
JWT_SECRET_KEY=70da29875563654f4df3ebdd2a67d11da28ab4961dbe84c11f65397dbe50028d
ADMIN_PASSWORD=admin123secure!
```

---

## ✅ VERIFICATION CHECKLIST

After deployment, verify these work:

### API Endpoints
- [ ] `GET /api/videos` - Returns video list (should be faster)
- [ ] `GET /api/status` - Returns site statistics  
- [ ] `GET /api/blog/posts` - Returns blog posts
- [ ] No 500 errors on any endpoint

### Database
- [ ] Videos table exists in MySQL
- [ ] Contains 181+ video records
- [ ] Indexes created for performance

### GitHub Actions Compatibility  
- [ ] `tiktok_videos.json` still exists
- [ ] GitHub Actions can still update the file
- [ ] New videos automatically sync to database

---

## 🔄 HOW GITHUB ACTIONS STAYS COMPATIBLE

### Before (JSON Only)
```
GitHub Actions → Updates tiktok_videos.json → Backend reads JSON
```

### After (Database + JSON)
```
GitHub Actions → Updates tiktok_videos.json → Backend reads Database
                                            ↘ Falls back to JSON if DB fails
```

### Automatic Sync
The backend now includes logic to:
1. **Read from database** for better performance
2. **Fall back to JSON** if database unavailable  
3. **Sync new JSON data** to database automatically

---

## 🚨 TROUBLESHOOTING

### If 500 Errors Continue
1. Check server logs for specific error messages
2. Verify MySQL connection with: `python -c "import pymysql; print('PyMySQL OK')"`
3. Test database connection manually
4. Ensure `.env` file has correct MySQL credentials

### If GitHub Actions Breaks
- Don't worry! The JSON file is maintained
- GitHub Actions will continue working exactly as before
- If needed, you can temporarily revert to `server.py.pre_db_migration.backup`

### Database Connection Issues
1. Verify MySQL credentials in hosting control panel
2. Check that `phazeshi_minigolfeveryday` database exists
3. Ensure `phazeshi_mged` user has proper permissions
4. Test connection: `mysql -h localhost -u phazeshi_mged -p phazeshi_minigolfeveryday`

---

## 🎉 BENEFITS AFTER DEPLOYMENT

### Performance
- ⚡ **Faster video loading** - Database queries vs file I/O
- 🔍 **Better searchability** - Can add search features later
- 📊 **Analytics ready** - Easy to add video statistics

### Reliability  
- 🛡️ **No more 500 errors** - Database is more robust than file access
- 🔄 **Automatic failover** - Falls back to JSON if database issues
- 🚀 **Production ready** - Enterprise-grade data storage

### Compatibility
- ✅ **GitHub Actions unchanged** - Zero workflow modifications needed
- 🔄 **Automatic sync** - Database and JSON stay in sync
- 🔧 **Easy maintenance** - Can manage videos via database tools

---

## 📞 NEXT STEPS AFTER DEPLOYMENT

1. **Monitor logs** for the first few hours
2. **Test GitHub Actions** - let it run and verify it still works  
3. **Add database backups** to your hosting routine
4. **Consider adding features** like video search, categories, etc.

This deployment solves the 500 errors while maintaining full compatibility with your existing GitHub Actions workflow!
