# Mini Golf Every Day - Blog System Documentation

## 🎉 Blog System Successfully Set Up!

Your secure blog functionality is now fully operational with PostgreSQL database, user authentication, and a complete API.

### 🚀 Quick Start

**Server is currently running on:** http://localhost:5002

### 🔐 Admin Access
- **Username:** `admin`
- **Password:** `admin123secure!`
- **Email:** admin@minigolfevery.day

### 📋 Available Features

#### ✅ Backend Features (Complete)
- ✅ Secure user registration and login
- ✅ JWT-based authentication
- ✅ Password hashing with bcrypt
- ✅ Account lockout after failed attempts
- ✅ Blog post CRUD operations
- ✅ Admin user management
- ✅ Input validation and sanitization
- ✅ Security headers
- ✅ PostgreSQL database integration
- ✅ Auto-generated slugs for SEO
- ✅ Pagination support

#### ✅ Frontend Features (Complete)
- ✅ Responsive blog interface
- ✅ Login/Register modals
- ✅ Blog post listing with pagination
- ✅ User authentication state management
- ✅ Admin controls for authenticated users

### 🌐 API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

#### Blog Posts
- `GET /api/blog/posts` - Get published posts (public)
- `GET /api/blog/posts/<id>` - Get specific post (public)
- `POST /api/blog/posts` - Create new post (auth required)
- `PUT /api/blog/posts/<id>` - Update post (author/admin)
- `DELETE /api/blog/posts/<id>` - Delete post (author/admin)

#### Admin Only
- `GET /api/admin/users` - List all users
- `POST /api/admin/users/<id>/toggle-active` - Enable/disable user
- `GET /api/admin/posts` - Get all posts (including drafts)

### 🛠 How to Use

#### For Administrators:
1. **Login:** Use the login button in the header with admin credentials
2. **Create Posts:** Click "Write Post" in the user menu (coming soon in UI)
3. **Manage Users:** Access admin endpoints via API
4. **Publish/Unpublish:** Control post visibility

#### For Regular Users:
1. **Register:** Click login button, then "Sign Up"
2. **Write Posts:** Create draft posts (admin approval required)
3. **View Posts:** Browse published content

#### For Developers:
- **API Testing:** Use the curl examples below
- **Database:** PostgreSQL on localhost:5432
- **Environment:** Configure via `.env` file

### 📖 Example API Usage

#### Register a new user:
\`\`\`bash
curl -X POST http://localhost:5002/api/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
  }'
\`\`\`

#### Login:
\`\`\`bash
curl -X POST http://localhost:5002/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "admin",
    "password": "admin123secure!"
  }'
\`\`\`

#### Create a blog post:
\`\`\`bash
curl -X POST http://localhost:5002/api/blog/posts \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -d '{
    "title": "My First Post",
    "content": "This is my first blog post content...",
    "excerpt": "A brief summary of the post",
    "is_published": true
  }'
\`\`\`

### 🔧 Configuration Files

- **`.env`** - Environment variables (secrets, database URL)
- **`server.py`** - Main Flask application
- **`requirements_blog.txt`** - Python dependencies
- **`init_db.py`** - Database initialization script

### 🛡 Security Features

- **Password Hashing:** bcrypt with salt
- **JWT Authentication:** Secure token-based auth
- **Input Validation:** Email, username, and content validation
- **Rate Limiting:** Account lockout after failed login attempts
- **SQL Injection Protection:** SQLAlchemy ORM
- **XSS Protection:** Content sanitization
- **Security Headers:** CSRF, XSS, and clickjacking protection

### 📝 Database Schema

#### Users Table
- id, username, email, password_hash
- is_admin, is_active, created_at, last_login
- login_attempts, locked_until

#### Blog Posts Table
- id, title, slug, content, excerpt
- featured_image, is_published, is_featured
- created_at, updated_at, published_at
- author_id, meta_title, meta_description

### 🚀 Production Deployment

For production deployment:

1. **Update Environment:**
   - Set strong SECRET_KEY and JWT_SECRET_KEY
   - Configure production DATABASE_URL
   - Set FLASK_ENV=production and DEBUG=False

2. **Use Production WSGI Server:**
   \`\`\`bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 server:app
   \`\`\`

3. **Set up HTTPS and reverse proxy (nginx/Apache)**

4. **Database Backup and Monitoring**

### 🐛 Troubleshooting

#### Common Issues:
- **Port 5000 in use:** Server runs on port 5002 instead
- **Database connection:** Ensure PostgreSQL is running
- **Python 3.13 compatibility:** Uses latest SQLAlchemy 2.0.36

#### Logs:
- Check terminal output for Flask debug information
- Database errors will show in console

### 🎯 Next Steps

#### Frontend Enhancements:
- Complete post editor UI
- Image upload functionality
- Comment system
- Search functionality

#### Backend Enhancements:
- Email verification
- Password reset
- File upload API
- Content moderation

---

**🎉 Your blog is ready to use! Visit http://localhost:5002/blog.html to get started.**
