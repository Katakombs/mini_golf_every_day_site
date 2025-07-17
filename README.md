# 🏌️‍♂️ Mini Golf Every Day

A dynamic website showcasing the daily mini golf adventures with an integrated blog and video gallery. Features automated video updates via GitHub Actions and a secure admin interface.

## 🎯 Features

- **🎬 Video Gallery** - 181+ TikTok videos with database storage
- **📝 Blog System** - Secure admin interface with post management  
- **🔄 Auto-Updates** - GitHub Actions automatically fetch new videos
- **📊 Statistics** - Real-time video counts and progress tracking
- **📱 Responsive Design** - Perfect viewing on all devices
- **🔐 Admin Panel** - Secure blog management with authentication
- **🚀 Production Ready** - MySQL database with fallback systems

## 🚀 Live Site

Visit: [https://minigolfevery.day](https://minigolfevery.day)

## 📱 Social Media

- **TikTok**: [@minigolfeveryday](https://www.tiktok.com/@minigolfeveryday)
- **Instagram**: [@mini.golf.every.day](https://www.instagram.com/mini.golf.every.day/)

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **Backend**: Python Flask with SQLAlchemy
- **Database**: MySQL with JSON fallback for GitHub Actions compatibility
- **Authentication**: JWT-based secure admin system
- **Automation**: GitHub Actions with yt-dlp for video fetching
- **Hosting**: Shared hosting with WSGI support
- **Dependencies**: PyMySQL, Flask-SQLAlchemy, bcrypt

## 📊 Project Stats

- **Days Running**: 181+ days (as of July 2025)
- **Videos**: 181+ TikTok videos in database
- **Blog Posts**: Admin-managed content system
- **Database**: MySQL with 181+ video records
- **Started**: January 1, 2025
- **GitHub Actions**: Automated every 4 hours

## 🔧 Development

### Prerequisites
- Python 3.8+ 
- MySQL (MAMP for local development)
- pip package manager

### Local Setup
```bash
# Clone repository
git clone https://github.com/yourusername/mini_golf_every_day_site.git
cd mini_golf_every_day_site

# Install dependencies
pip install -r requirements_blog.txt

# Set up local environment
cp .env.example .env
# Edit .env with your local MySQL credentials

# Run migration to set up video database
python migrate_videos_to_db.py

# Start development server
python server.py
```

```

## 🚀 Production Deployment

### Quick Deploy
```bash
# Upload files to hosting
# See DEPLOYMENT_CHECKLIST.md for detailed steps

# One-command setup
curl https://minigolfevery.day/api/setup
```

### Manual Deployment
See the comprehensive deployment guides:
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Step-by-step checklist
- **[PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md)** - Detailed instructions
- **[MYSQL_DEPLOYMENT_GUIDE.md](MYSQL_DEPLOYMENT_GUIDE.md)** - Database setup

## 📁 Project Structure
```
├── 🌐 Frontend
│   ├── index.html              # Dynamic homepage
│   ├── watch.html              # Video gallery  
│   ├── blog.html               # Blog page
│   ├── blog-admin.html         # Admin interface
│   ├── about.html              # About page
│   ├── contact.html            # Contact page
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   └── images/                 # Assets
│
├── 🐍 Backend
│   ├── server.py               # Main Flask application
│   ├── passenger_wsgi.py       # WSGI configuration
│   └── requirements_blog.txt   # Python dependencies
│
├── 🗄️ Database
│   ├── add_videos_table.sql    # Video table schema
│   ├── migrate_videos_to_db.py # Migration script
│   └── tiktok_videos.json      # Video data (GitHub Actions)
│
├── 🚀 Deployment
│   ├── .env.production         # Production environment
│   ├── deploy_video_database.sh # Deployment script
│   └── DEPLOYMENT_*.md         # Deployment guides
│
├── 🤖 Automation
│   ├── .github/workflows/      # GitHub Actions
│   │   ├── update_tiktok_videos.yml
│   │   └── update_videos.py
│   └── cron_update.py          # Legacy cron script
│
└── 📚 Documentation
    ├── README.md               # This file
    ├── AUTOMATION_README.md    # Automation docs
    ├── GITHUB_SETUP.md         # GitHub Actions setup
    └── *.md                    # Various guides
```

## 🤖 Automation System

### GitHub Actions (Primary)
- **Runs every 4 hours** automatically
- **Fetches new videos** using yt-dlp
- **Updates tiktok_videos.json** 
- **Commits changes** back to repository
- **Zero maintenance** required

### Backend Integration  
- **Reads from MySQL database** for performance
- **Falls back to JSON** if database unavailable
- **Auto-syncs new videos** from JSON to database
- **Maintains GitHub Actions compatibility**

## 🔐 Admin Features

### Blog Management
- **Secure login** with JWT authentication
- **Create/Edit/Delete** blog posts
- **Rich text editor** with markdown support
- **Image uploads** and media management
- **SEO optimization** with meta tags

### Video Management
- **Database storage** for better performance
- **Automatic sync** with GitHub Actions
- **Search and filtering** capabilities
- **Statistics and analytics**

## 🎯 API Endpoints

### Public APIs
- `GET /api/videos` - Video gallery data
- `GET /api/status` - Site statistics  
- `GET /api/blog/posts` - Published blog posts
- `GET /api/setup` - One-command database setup

### Admin APIs (Authenticated)
- `POST /api/auth/login` - Admin login
- `GET /api/blog/admin/posts` - All posts (admin)
- `POST /api/blog/admin/posts` - Create post
- `PUT /api/blog/admin/posts/:id` - Update post
- `DELETE /api/blog/admin/posts/:id` - Delete post

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration  
MGED_API_KEY=your_api_key
MGED_ENV=production
MGED_DOMAIN=https://minigolfevery.day

# Database (MySQL)
DB_HOST=localhost
DB_PORT=3306
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password

# Security
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
ADMIN_PASSWORD=your_admin_password
```

## 🎉 Recent Updates

### Video Database Migration (July 2025)
- ✅ **Migrated 181 videos** from JSON to MySQL database
- ✅ **Improved performance** with database queries vs file I/O
- ✅ **Maintained GitHub Actions compatibility** with automatic JSON sync
- ✅ **Added setup API** for one-command deployment
- ✅ **Fixed 500 errors** on video endpoints
- ✅ **Added fallback systems** for reliability

## 🎨 Design

- **Brand Colors**: Green (#059669) and Yellow (#FDE047)
- **Typography**: Fredoka (headings), Inter (body)
- **Layout**: Mobile-first responsive design
- **Icons**: Custom SVG logo and social media icons

## 📝 License

This project is personal/educational. TikTok content belongs to [@minigolfeveryday](https://www.tiktok.com/@minigolfeveryday).

## 🎉 About

Started as a New Year's resolution to play mini golf every single day in 2025. What began as a simple daily challenge has grown into a celebration of family, fun, and consistency - one putt at a time.

**Created with ❤️ for MJ**
