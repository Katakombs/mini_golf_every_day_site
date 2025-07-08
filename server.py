#!/usr/bin/env python3
"""
Mini Golf Every Day - Blog Backend Server
Secure Flask application with PostgreSQL, authentication, and blog functionality
"""

import os
import re
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
import json

import bcrypt
import jwt
from flask import Flask, request, jsonify, session, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://localhost:5432/minigolf_blog')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize database
db = SQLAlchemy(app)

# Security headers middleware
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Relationships
    posts = db.relationship('BlogPost', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def is_locked(self):
        """Check if account is locked due to failed login attempts"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
    
    def lock_account(self, minutes=30):
        """Lock account for specified minutes"""
        self.locked_until = datetime.utcnow() + timedelta(minutes=minutes)
        db.session.commit()
    
    def reset_login_attempts(self):
        """Reset login attempts and unlock account"""
        self.login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def increment_login_attempts(self):
        """Increment failed login attempts"""
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.lock_account(30)  # Lock for 30 minutes
        db.session.commit()
    
    def generate_auth_token(self):
        """Generate JWT token for authentication"""
        payload = {
            'user_id': self.id,
            'username': self.username,
            'is_admin': self.is_admin,
            'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_auth_token(token):
        """Verify JWT token and return user"""
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user = User.query.get(payload['user_id'])
            if user and user.is_active:
                return user
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        return None
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email if include_sensitive else None,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        return data


class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    featured_image = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    published_at = db.Column(db.DateTime)
    
    # Foreign keys
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # SEO fields
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(500))
    
    def generate_slug(self):
        """Generate URL-friendly slug from title"""
        if not self.title:
            return ''
        
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', self.title.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        
        # Ensure uniqueness
        base_slug = slug
        counter = 1
        while BlogPost.query.filter_by(slug=slug).filter(BlogPost.id != self.id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def publish(self):
        """Publish the blog post"""
        self.is_published = True
        self.published_at = datetime.utcnow()
        if not self.slug:
            self.slug = self.generate_slug()
    
    def unpublish(self):
        """Unpublish the blog post"""
        self.is_published = False
        self.published_at = None
    
    def to_dict(self, include_content=True):
        """Convert blog post to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'featured_image': self.featured_image,
            'is_published': self.is_published,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'author': {
                'id': self.author.id,
                'username': self.author.username
            },
            'meta_title': self.meta_title,
            'meta_description': self.meta_description
        }
        
        if include_content:
            data['content'] = self.content
        
        return data


# Authentication decorators
def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        current_user = User.verify_auth_token(token)
        if not current_user:
            return jsonify({'error': 'Token is invalid or expired'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated


# Input validation
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username):
    """Validate username format"""
    if len(username) < 3 or len(username) > 20:
        return False
    pattern = r'^[a-zA-Z0-9_-]+$'
    return re.match(pattern, username) is not None


def sanitize_content(content):
    """Basic content sanitization with safe iframe support"""
    if not content:
        return ''
    
    # Allow safe iframe embeds from trusted domains
    trusted_domains = [
        'youtube.com',
        'youtube-nocookie.com',
        'vimeo.com',
        'player.vimeo.com',
        'soundcloud.com',
        'w.soundcloud.com'
    ]
    
    # Find all iframes and check if they're from trusted sources
    iframe_pattern = r'<iframe[^>]*src=["\']([^"\']+)["\'][^>]*>'
    iframes = re.findall(iframe_pattern, content, re.IGNORECASE)
    
    # Remove dangerous HTML tags except safe iframes
    dangerous_tags = ['<script', '<object', '<embed', '<link', '<meta']
    for tag in dangerous_tags:
        content = re.sub(f'{tag}[^>]*>', '', content, flags=re.IGNORECASE)
    
    # Remove iframes from untrusted domains
    def is_trusted_iframe(match):
        src = match.group(1)
        for domain in trusted_domains:
            if domain in src:
                return match.group(0)  # Keep the iframe
        return ''  # Remove untrusted iframe
    
    content = re.sub(iframe_pattern, is_trusted_iframe, content, flags=re.IGNORECASE)
    
    return content.strip()


# Database initialization
def init_db():
    """Initialize database with tables"""
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@minigolfevery.day',
                is_admin=True
            )
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'changeme123'))
            db.session.add(admin)
            db.session.commit()
            print("✅ Created admin user")


# API Routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validation
        if not validate_username(username):
            return jsonify({'error': 'Username must be 3-20 characters, alphanumeric only'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.is_active:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if account is locked
        if user.is_locked():
            return jsonify({'error': 'Account temporarily locked due to failed login attempts'}), 423
        
        # Verify password
        if not user.check_password(password):
            user.increment_login_attempts()
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Successful login
        user.reset_login_attempts()
        token = user.generate_auth_token()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user info"""
    return jsonify({'user': current_user.to_dict(include_sensitive=True)}), 200


@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Logout user (client should delete token)"""
    return jsonify({'message': 'Logged out successfully'}), 200


# Blog API Routes
@app.route('/api/blog/posts', methods=['GET'])
def get_blog_posts():
    """Get blog posts with pagination and filtering"""
    try:
        # Query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 50)  # Max 50 per page
        limit = request.args.get('limit', type=int)  # For simple limit queries
        published_only = request.args.get('published', 'true').lower() == 'true'
        featured_only = request.args.get('featured', 'false').lower() == 'true'
        author_id = request.args.get('author_id', type=int)
        
        # If limit is specified, use it instead of pagination
        if limit:
            per_page = min(limit, 50)
            page = 1
        
        # Build query
        query = BlogPost.query
        
        if published_only:
            query = query.filter(BlogPost.is_published == True)
        
        if featured_only:
            query = query.filter(BlogPost.is_featured == True)
        
        if author_id:
            query = query.filter(BlogPost.author_id == author_id)
        
        # Order by published date (or created date for unpublished)
        query = query.order_by(
            BlogPost.published_at.desc().nullslast(),
            BlogPost.created_at.desc()
        )
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        posts = [post.to_dict(include_content=False) for post in pagination.items]
        
        return jsonify({
            'posts': posts,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch blog posts'}), 500


@app.route('/api/blog/posts/<slug>', methods=['GET'])
def get_blog_post(slug):
    """Get single blog post by slug"""
    try:
        post = BlogPost.query.filter_by(slug=slug).first()
        
        if not post:
            return jsonify({'error': 'Blog post not found'}), 404
        
        # Only allow published posts for non-authenticated users
        auth_header = request.headers.get('Authorization')
        current_user = None
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                current_user = User.verify_auth_token(token)
            except:
                pass
        
        # Check if user can view unpublished posts
        if not post.is_published:
            if not current_user or (not current_user.is_admin and current_user.id != post.author_id):
                return jsonify({'error': 'Blog post not found'}), 404
        
        return jsonify({'post': post.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch blog post'}), 500


@app.route('/api/blog/posts/<int:post_id>', methods=['GET'])
@token_required
def get_blog_post_by_id(current_user, post_id):
    """Get single blog post by ID for editing"""
    try:
        post = BlogPost.query.get(post_id)
        
        if not post:
            return jsonify({'error': 'Blog post not found'}), 404
        
        # Check if user can view this post (admin or author)
        if not current_user.is_admin and post.author_id != current_user.id:
            return jsonify({'error': 'Permission denied'}), 403
        
        return jsonify({'post': post.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch blog post'}), 500


@app.route('/api/blog/posts', methods=['POST'])
@token_required
def create_blog_post(current_user):
    """Create new blog post"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        excerpt = data.get('excerpt', '').strip()
        featured_image = data.get('featured_image', '').strip()
        is_published = data.get('is_published', False)
        is_featured = data.get('is_featured', False)
        meta_title = data.get('meta_title', '').strip()
        meta_description = data.get('meta_description', '').strip()
        
        # Validation
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        if not content:
            return jsonify({'error': 'Content is required'}), 400
        
        if len(title) > 200:
            return jsonify({'error': 'Title too long (max 200 characters)'}), 400
        
        # Sanitize content
        content = sanitize_content(content)
        excerpt = sanitize_content(excerpt)
        
        # Create post
        post = BlogPost(
            title=title,
            content=content,
            excerpt=excerpt,
            featured_image=featured_image,
            is_featured=is_featured and current_user.is_admin,  # Only admins can feature posts
            author_id=current_user.id,
            meta_title=meta_title,
            meta_description=meta_description
        )
        
        # Generate slug
        post.slug = post.generate_slug()
        
        # Handle publishing
        if is_published:
            post.publish()
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'message': 'Blog post created successfully',
            'post': post.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create blog post'}), 500


@app.route('/api/blog/posts/<int:post_id>', methods=['PUT'])
@token_required
def update_blog_post(current_user, post_id):
    """Update blog post"""
    try:
        post = BlogPost.query.get(post_id)
        
        if not post:
            return jsonify({'error': 'Blog post not found'}), 404
        
        # Check permissions
        if not current_user.is_admin and current_user.id != post.author_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return jsonify({'error': 'Title is required'}), 400
            if len(title) > 200:
                return jsonify({'error': 'Title too long (max 200 characters)'}), 400
            
            # Update slug if title changed
            if post.title != title:
                post.title = title
                post.slug = post.generate_slug()
        
        if 'content' in data:
            content = data['content'].strip()
            if not content:
                return jsonify({'error': 'Content is required'}), 400
            post.content = sanitize_content(content)
        
        if 'excerpt' in data:
            post.excerpt = sanitize_content(data['excerpt'].strip())
        
        if 'featured_image' in data:
            post.featured_image = data['featured_image'].strip()
        
        if 'meta_title' in data:
            post.meta_title = data['meta_title'].strip()
        
        if 'meta_description' in data:
            post.meta_description = data['meta_description'].strip()
        
        # Handle publishing state
        if 'is_published' in data:
            is_published = data['is_published']
            if is_published and not post.is_published:
                post.publish()
            elif not is_published and post.is_published:
                post.unpublish()
        
        # Handle featured state (admin only)
        if 'is_featured' in data and current_user.is_admin:
            post.is_featured = data['is_featured']
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Blog post updated successfully',
            'post': post.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update blog post'}), 500


@app.route('/api/blog/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_blog_post(current_user, post_id):
    """Delete blog post"""
    try:
        post = BlogPost.query.get(post_id)
        
        if not post:
            return jsonify({'error': 'Blog post not found'}), 404
        
        # Check permissions
        if not current_user.is_admin and current_user.id != post.author_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Blog post deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete blog post'}), 500


@app.route('/api/blog/posts/<int:post_id>/public', methods=['GET'])
def get_public_blog_post(post_id):
    """Get single published blog post for public viewing"""
    try:
        post = BlogPost.query.filter_by(id=post_id, is_published=True).first()
        
        if not post:
            return jsonify({'error': 'Blog post not found'}), 404
        
        return jsonify({'post': post.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch blog post'}), 500


# TikTok Video API Routes
@app.route('/api/videos', methods=['GET'])
def get_videos():
    """Get TikTok videos from JSON file"""
    try:
        with open('tiktok_videos.json', 'r') as f:
            data = json.load(f)
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({'videos': []}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to load videos'}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status and statistics"""
    try:
        # Load video data
        try:
            with open('tiktok_videos.json', 'r') as f:
                data = json.load(f)
            videos = data.get('videos', [])
        except FileNotFoundError:
            videos = []
        
        # Calculate statistics
        total_videos = len(videos)
        
        # Calculate days running (from first video date if available)
        days_running = 0
        if videos:
            # Get the first video's upload date
            first_video = min(videos, key=lambda x: x.get('upload_date', '99999999'))
            if 'upload_date' in first_video:
                try:
                    # Parse upload_date (format: YYYYMMDD)
                    first_date = datetime.strptime(first_video['upload_date'], '%Y%m%d')
                    days_running = (datetime.now() - first_date).days + 1
                except ValueError:
                    days_running = total_videos  # Fallback to video count
            else:
                days_running = total_videos
        
        # Get latest video info
        latest_video = None
        if videos:
            latest_video = max(videos, key=lambda x: x.get('upload_date', '00000000'))
        
        return jsonify({
            'video_count': total_videos,  # Using video_count for compatibility with existing frontend
            'total_videos': total_videos,
            'days_running': days_running,
            'latest_video': latest_video,
            'last_updated': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get status',
            'video_count': 0,  # Using video_count for compatibility
            'total_videos': 0,
            'days_running': 0,
            'latest_video': None,
            'last_updated': datetime.now().isoformat()
        }), 500


# Admin routes
@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
def get_all_users(current_user):
    """Get all users (admin only)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        pagination = User.query.order_by(User.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        users = [user.to_dict(include_sensitive=True) for user in pagination.items]
        
        return jsonify({
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch users'}), 500


@app.route('/api/admin/users/<int:user_id>/toggle-active', methods=['POST'])
@token_required
@admin_required
def toggle_user_active(current_user, user_id):
    """Toggle user active status (admin only)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot modify your own account'}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'user': user.to_dict(include_sensitive=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user'}), 500


# Static file serving (for existing functionality)
@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('.', filename)


if __name__ == '__main__':
    # Initialize database if running directly
    with app.app_context():
        db.create_all()
    
    # Run the application
    app.run(host='0.0.0.0', port=5002, debug=True)
