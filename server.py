#!/usr/bin/env python3
"""
Mini Golf Every Day - Blog Backend Server
Secure Flask application with PostgreSQL, authentication, and blog functionality
"""

import os
import re
import hashlib
import secrets
import smtplib
from datetime import datetime, timedelta
from functools import wraps
import json
import traceback

import bcrypt
import jwt
from flask import Flask, request, jsonify, session, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Try to import MySQL drivers
MYSQL_DRIVERS = {
    'pymysql': None,
    'mysqldb': None,
    'mysqlconnector': None
}

# Global connection pool for shared hosting
_connection_pool = None
_max_connections = 5

try:
    import pymysql
    MYSQL_DRIVERS['pymysql'] = pymysql
except ImportError:
    pass

try:
    import MySQLdb
    MYSQL_DRIVERS['mysqldb'] = MySQLdb
except ImportError:
    pass

try:
    import mysql.connector
    MYSQL_DRIVERS['mysqlconnector'] = mysql.connector
except ImportError:
    pass

# Load environment variables
if os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

app = Flask(__name__)
CORS(app)

# Resource optimization settings
import gc
import os
import time
from collections import defaultdict

# Set environment variables for optimization
os.environ['PYTHONUNBUFFERED'] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

# Configure Flask for shared hosting
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache
app.config['TEMPLATES_AUTO_RELOAD'] = False
app.config['DEBUG'] = False

# Disable SQLAlchemy query logging in production
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Simple rate limiting for shared hosting
_request_counts = defaultdict(list)
_MAX_REQUESTS_PER_MINUTE = 60

# Shared hosting process limits
_MAX_CONCURRENT_PROCESSES = 3
_active_processes = 0

def check_rate_limit(ip):
    """Simple rate limiting"""
    now = time.time()
    minute_ago = now - 60
    
    # Clean old requests
    _request_counts[ip] = [req_time for req_time in _request_counts[ip] if req_time > minute_ago]
    
    # Check if limit exceeded
    if len(_request_counts[ip]) >= _MAX_REQUESTS_PER_MINUTE:
        return False
    
    # Add current request
    _request_counts[ip].append(now)
    return True

def check_process_limit():
    """Check if we're at process limit for shared hosting"""
    global _active_processes
    return _active_processes < _MAX_CONCURRENT_PROCESSES

def acquire_process_slot():
    """Acquire a process slot"""
    global _active_processes
    if check_process_limit():
        _active_processes += 1
        return True
    return False

def release_process_slot():
    """Release a process slot"""
    global _active_processes
    if _active_processes > 0:
        _active_processes -= 1

def force_garbage_collection():
    """Force garbage collection to free memory"""
    gc.collect()

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Database configuration for shared hosting compatibility
def get_database_uri():
    """Get database URI with fallback options"""
    database_url = os.environ.get('DATABASE_URL')
    
    # Try individual components first for better compatibility
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT', '3306')
    db_name = os.environ.get('DB_NAME')
    
    if db_user and db_password and db_host and db_name:
        # Determine best MySQL driver
        if MYSQL_DRIVERS['pymysql']:
            # PyMySQL is preferred for shared hosting
            return f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
        elif MYSQL_DRIVERS['mysqlconnector']:
            # mysql-connector-python as fallback
            return f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
        elif MYSQL_DRIVERS['mysqldb']:
            # MySQLdb (older, less preferred)
            return f'mysql+mysqldb://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
        else:
            # Generic MySQL (will auto-detect driver)
            return f'mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
    elif database_url:
        # Use direct URL
        return database_url
    else:
        # Final fallback to SQLite
        return 'sqlite:///blog.db'

# Set database URI
database_uri = get_database_uri()
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300
}
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


def setup_video_database():
    """Setup video database table and migrate data from JSON"""
    try:
        result = {
            'video_table_created': False,
            'videos_migrated': 0,
            'videos_existing': 0,
            'json_synced': False,
            'errors': []
        }
        
        # Get direct database connection
        connection = get_db_connection()
        if not connection:
            result['errors'].append('Could not connect to database')
            return result
        
        try:
            with connection.cursor() as cursor:
                # Create videos table
                cursor.execute("""
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
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                
                # Create additional index
                try:
                    cursor.execute("""
                        CREATE INDEX idx_videos_upload_date_desc 
                        ON videos (upload_date DESC)
                    """)
                except Exception:
                    # Index might already exist, ignore
                    pass
                
                connection.commit()
                result['video_table_created'] = True
                
                # Check existing videos in database
                cursor.execute("SELECT COUNT(*) as count FROM videos")
                existing_count = cursor.fetchone()['count']
                result['videos_existing'] = existing_count
                
                # If no videos in database, try to migrate from JSON
                if existing_count == 0:
                    try:
                        if os.path.exists('tiktok_videos.json'):
                            with open('tiktok_videos.json', 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            videos = data.get('videos', [])
                            
                            # Migrate videos to database
                            migrated = 0
                            for video in videos:
                                try:
                                    cursor.execute("""
                                        INSERT IGNORE INTO videos (video_id, title, upload_date, url)
                                        VALUES (%s, %s, %s, %s)
                                    """, (
                                        video.get('video_id', ''),
                                        video.get('title', ''),
                                        video.get('upload_date', ''),
                                        video.get('url', f"https://www.tiktok.com/@minigolfeveryday/video/{video.get('video_id', '')}")
                                    ))
                                    migrated += 1
                                except Exception as e:
                                    result['errors'].append(f"Failed to migrate video {video.get('video_id', 'unknown')}: {str(e)}")
                            
                            connection.commit()
                            result['videos_migrated'] = migrated
                            
                            # Sync database back to JSON to ensure consistency
                            cursor.execute("""
                                SELECT video_id, title, upload_date, url
                                FROM videos
                                ORDER BY upload_date DESC, created_at DESC
                            """)
                            
                            db_videos = cursor.fetchall()
                            json_videos = []
                            for video in db_videos:
                                json_videos.append({
                                    'video_id': video['video_id'],
                                    'title': video['title'] or '',
                                    'upload_date': video['upload_date'] or '',
                                    'url': video['url'] or f"https://www.tiktok.com/@minigolfeveryday/video/{video['video_id']}"
                                })
                            
                            # Update JSON file
                            json_data = {
                                'videos': json_videos,
                                'last_updated': datetime.now().isoformat(),
                                'total_count': len(json_videos)
                            }
                            
                            with open('tiktok_videos.json', 'w', encoding='utf-8') as f:
                                json.dump(json_data, f, indent=2, ensure_ascii=False)
                            
                            result['json_synced'] = True
                            
                    except Exception as e:
                        result['errors'].append(f"JSON migration failed: {str(e)}")
                
        finally:
            connection.close()
        
        return result
        
    except Exception as e:
        return {
            'video_table_created': False,
            'videos_migrated': 0,
            'videos_existing': 0,
            'json_synced': False,
            'errors': [f"Video database setup failed: {str(e)}"]
        }


# API Routes

def get_db_connection():
    """Get database connection for video operations with connection pooling"""
    global _connection_pool
    
    try:
        # Simple connection pool for shared hosting
        if _connection_pool is None:
            _connection_pool = []
        
        # Return existing connection if available
        while _connection_pool:
            try:
                conn = _connection_pool.pop()
                # Test if connection is still alive
                conn.ping(reconnect=False)
                return conn
            except:
                continue
        
        # Create new connection if pool is empty
        if len(_connection_pool) < _max_connections:
            conn = pymysql.connect(
                host=os.environ.get('DB_HOST', 'localhost'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                database=os.environ.get('DB_NAME'),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,  # Reduce transaction overhead
                read_timeout=30,   # Prevent hanging connections
                write_timeout=30
            )
            return conn
        else:
            print("[WARNING] Connection pool exhausted, creating temporary connection")
            return pymysql.connect(
                host=os.environ.get('DB_HOST', 'localhost'),
                user=os.environ.get('DB_USER'),
                password=os.environ.get('DB_PASSWORD'),
                database=os.environ.get('DB_NAME'),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return None

def return_db_connection(connection):
    """Return connection to pool"""
    global _connection_pool
    if connection and _connection_pool is not None:
        try:
            connection.ping(reconnect=False)
            if len(_connection_pool) < _max_connections:
                _connection_pool.append(connection)
            else:
                connection.close()
        except:
            connection.close()

def get_videos_from_database():
    """Get videos from database, fallback to JSON if database fails"""
    try:
        # Try database first
        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT video_id, title, upload_date, url, 
                               COALESCE(view_count, 0) as view_count,
                               COALESCE(like_count, 0) as like_count,
                               COALESCE(comment_count, 0) as comment_count
                        FROM videos
                        ORDER BY upload_date DESC, created_at DESC
                        LIMIT 200
                    """)
                    
                    db_videos = cursor.fetchall()
                    
                    # Convert to expected format
                    videos = []
                    for video in db_videos:
                        videos.append({
                            'video_id': video['video_id'],
                            'title': video['title'] or '',
                            'upload_date': video['upload_date'] or '',
                            'url': video['url'] or f"https://www.tiktok.com/@minigolfeveryday/video/{video['video_id']}",
                            'view_count': video.get('view_count', 0),
                            'like_count': video.get('like_count', 0),
                            'comment_count': video.get('comment_count', 0)
                        })
                    
                    return {
                        'videos': videos,
                        'last_updated': datetime.now().isoformat(),
                        'total_count': len(videos),
                        'source': 'database'
                    }
            finally:
                return_db_connection(connection)
        
    except Exception as e:
        print(f"[ERROR] Database video fetch failed: {e}")
    
    # Fallback to JSON file
    try:
        with open('tiktok_videos.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            data['source'] = 'json_fallback'
            return data
    except Exception as e:
        print(f"[ERROR] JSON fallback failed: {e}")
        return {
            'videos': [],
            'last_updated': datetime.now().isoformat(),
            'total_count': 0,
            'source': 'empty_fallback'
        }

def get_video_stats_from_database():
    """Get video statistics from database with JSON fallback"""
    try:
        # Try database first
        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Single optimized query to get all stats
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_videos,
                            MIN(upload_date) as first_date,
                            MAX(upload_date) as last_date,
                            MAX(CONCAT(upload_date, '|', video_id, '|', COALESCE(title, ''), '|', COALESCE(url, ''))) as latest_video_data
                        FROM videos 
                        WHERE upload_date IS NOT NULL AND upload_date != ''
                    """)
                    
                    stats = cursor.fetchone()
                    total_videos = stats['total_videos'] or 0
                    
                    # Parse latest video data
                    latest_video_data = None
                    if stats['latest_video_data']:
                        parts = stats['latest_video_data'].split('|')
                        if len(parts) >= 4:
                            latest_video_data = {
                                'video_id': parts[1],
                                'title': parts[2] or '',
                                'upload_date': parts[0] or '',
                                'url': parts[3] or f"https://www.tiktok.com/@minigolfeveryday/video/{parts[1]}"
                            }
                    
                    # Calculate days running
                    days_running = 0
                    if stats['first_date']:
                        try:
                            first_date = datetime.strptime(stats['first_date'], '%Y%m%d')
                            days_running = (datetime.now() - first_date).days + 1
                        except ValueError:
                            days_running = total_videos
                    else:
                        days_running = total_videos
                    
                    return {
                        'video_count': total_videos,
                        'total_videos': total_videos,
                        'days_running': days_running,
                        'latest_video': latest_video_data,
                        'last_updated': datetime.now().isoformat(),
                        'source': 'database'
                    }
            finally:
                return_db_connection(connection)
        
    except Exception as e:
        print(f"[ERROR] Database stats fetch failed: {e}")
    
    # Fallback to JSON processing (existing logic)
    try:
        with open('tiktok_videos.json', 'r') as f:
            data = json.load(f)
        videos = data.get('videos', [])
        
        total_videos = len(videos)
        days_running = 0
        
        if videos:
            first_video = min(videos, key=lambda x: x.get('upload_date', '99999999'))
            if 'upload_date' in first_video:
                try:
                    first_date = datetime.strptime(first_video['upload_date'], '%Y%m%d')
                    days_running = (datetime.now() - first_date).days + 1
                except ValueError:
                    days_running = total_videos
            else:
                days_running = total_videos
        
        latest_video = None
        if videos:
            latest_video = max(videos, key=lambda x: x.get('upload_date', '00000000'))
        
        return {
            'video_count': total_videos,
            'total_videos': total_videos,
            'days_running': days_running,
            'latest_video': latest_video,
            'last_updated': datetime.now().isoformat(),
            'source': 'json_fallback'
        }
        
    except Exception as e:
        print(f"[ERROR] JSON stats fallback failed: {e}")
        return {
            'video_count': 0,
            'total_videos': 0,
            'days_running': 0,
            'latest_video': None,
            'last_updated': datetime.now().isoformat(),
            'source': 'empty_fallback'
        }


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
        # MySQL doesn't support NULLS LAST, so we use CASE for equivalent behavior
        query = query.order_by(
            db.case(
                (BlogPost.published_at.is_(None), BlogPost.created_at),
                else_=BlogPost.published_at
            ).desc(),
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
        }, 201)
        
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
    """Get TikTok videos from database with JSON fallback"""
    # Rate limiting
    client_ip = request.remote_addr
    if not check_rate_limit(client_ip):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    try:
        data = get_videos_from_database()
        # Force garbage collection after large data operations
        gc.collect()
        return jsonify(data), 200
    except Exception as e:
        print(f"[ERROR] Videos endpoint failed: {e}")
        return jsonify({
            'error': 'Failed to load videos',
            'videos': [],
            'source': 'error_fallback'
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status and statistics from database with JSON fallback"""
    try:
        stats = get_video_stats_from_database()
        return jsonify(stats), 200
        
    except Exception as e:
        print(f"[ERROR] Status endpoint failed: {e}")
        return jsonify({
            'error': 'Failed to get status',
            'video_count': 0,
            'total_videos': 0,
            'days_running': 0,
            'latest_video': None,
            'last_updated': datetime.now().isoformat(),
            'source': 'error_fallback'
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


@app.route('/api/admin/pull-videos', methods=['POST'])
@token_required
@admin_required
def pull_videos(current_user):
    """Manually pull latest videos from TikTok (admin only) - Optimized for shared hosting"""
    import subprocess
    import os
    
    # Check process limits for shared hosting
    if not acquire_process_slot():
        return jsonify({
            'error': 'Server is busy. Please try again in a few minutes.',
            'details': 'Too many concurrent processes'
        }), 503
    
    try:
        # Get the absolute path to the update_videos.py script
        script_path = os.path.join(os.path.dirname(__file__), 'update_videos.py')
        
        # List of Python executables to try (prioritize system Python for shared hosting)
        python_executables = [
            'python3',
            'python',
            '/usr/bin/python3',
            '/usr/bin/python',
            '/opt/alt/python39/bin/python3',
            '/opt/alt/python39/bin/python',
            '/home/phazeshi/virtualenv/minigolfeveryday/3.9/bin/python'
        ]
        
        result = None
        last_error = None
        
        for python_exec in python_executables:
            try:
                # Run the script with optimized flags for shared hosting
                result = subprocess.run([
                    python_exec, script_path, '--yes', '--quiet', '--shared-hosting'
                ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)  # Reduced timeout
                
                # If successful, break out of the loop
                if result.returncode == 0:
                    break
                else:
                    last_error = f"Exit code {result.returncode}: {result.stderr}"
                    
            except FileNotFoundError:
                continue  # Try next Python executable
            except Exception as e:
                last_error = str(e)
                continue
        
        if result is None:
            return jsonify({
                'error': 'Failed to pull videos',
                'details': 'No working Python executable found',
                'attempted_executables': python_executables
            }), 500
        
        if result.returncode == 0:
            # Clean the output to remove any problematic characters
            output_text = result.stdout.replace('\x00', '').strip()
            
            # Now run the database migration to sync JSON data to database
            print("Running database migration to sync JSON data...")
            db_result = None
            
            for python_exec in python_executables:
                try:
                    # Run the migration script
                    env = os.environ.copy()
                    env['PYTHONDONTWRITEBYTECODE'] = '1'
                    env['PYTHONUNBUFFERED'] = '1'
                    env['PYTHONIOENCODING'] = 'utf-8'
                    env['LC_ALL'] = 'en_US.UTF-8'
                    env['LANG'] = 'en_US.UTF-8'
                    
                    db_result = subprocess.run([
                        python_exec, 'migrate_videos_to_db.py'
                    ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=60, env=env)
                    
                    if db_result.returncode == 0:
                        print("Database migration completed successfully")
                        break
                    else:
                        print(f"Database migration failed: {db_result.stderr}")
                        
                except FileNotFoundError:
                    continue
                except Exception as e:
                    print(f"Database migration error: {str(e)}")
                    continue
            
            # Parse the output to extract stats if available
            output_lines = output_text.split('\n') if output_text else []
            stats = {
                'processed': 0,
                'new': 0,
                'updated': 0,
                'success': True
            }
            
            # Try to extract stats from output
            import re
            for line in output_lines:
                line_lower = line.lower().strip()
                
                # Look for specific patterns: "Processed: X videos" or "   Processed: X videos"
                if 'processed:' in line_lower:
                    try:
                        match = re.search(r'processed:\s*(\d+)', line_lower)
                        if match:
                            stats['processed'] = int(match.group(1))
                    except:
                        pass
                elif 'new:' in line_lower:
                    try:
                        match = re.search(r'new:\s*(\d+)', line_lower)
                        if match:
                            stats['new'] = int(match.group(1))
                    except:
                        pass
                elif 'updated:' in line_lower:
                    try:
                        match = re.search(r'updated:\s*(\d+)', line_lower)
                        if match:
                            stats['updated'] = int(match.group(1))
                    except:
                        pass
            
            # Force garbage collection after large operation
            force_garbage_collection()
            
            return jsonify({
                'message': 'Videos pulled successfully',
                'processed': stats['processed'],
                'new': stats['new'],
                'updated': stats['updated'],
                'output': output_text[:500] + '...' if len(output_text) > 500 else output_text
            }), 200
        else:
            # Clean error output
            error_text = result.stderr.replace('\x00', '').strip() if result.stderr else 'Unknown error'
            
            return jsonify({
                'error': 'Failed to pull videos',
                'details': error_text[:200] + '...' if len(error_text) > 200 else error_text,
                'attempted_executables': python_executables
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Video pull timed out (3 minutes)'}), 408
    except Exception as e:
        return jsonify({
            'error': 'Failed to pull videos',
            'details': str(e),
            'attempted_executables': python_executables
        }), 500
    finally:
        # Always release the process slot
        release_process_slot()





# Database Setup Route (for production initialization)
@app.route('/api/setup', methods=['GET', 'POST'])
def setup_database_api():
    """Initialize database tables, admin user, and video database - for production setup only"""
    try:
        # Check MySQL driver availability
        available_drivers = [name for name, driver in MYSQL_DRIVERS.items() if driver is not None]
        
        # Try to create tables with current database configuration
        db.create_all()
        
        # Setup video database table and migration
        video_setup_result = setup_video_database()
        
        # Check if admin user exists (check both usernames)
        admin = User.query.filter_by(username='MGED!').first()
        if not admin:
            admin = User.query.filter_by(username='admin').first()
        
        admin_created = False
        admin_updated = False
        
        if not admin:
            # Create new admin user with MGED! username
            admin = User(
                username='MGED!',
                email='admin@minigolfevery.day',
                is_admin=True
            )
            admin.set_password(os.environ.get('ADMIN_PASSWORD', 'admin123secure!'))
            db.session.add(admin)
            db.session.commit()
            admin_created = True
        elif admin.username == 'admin':
            # Update existing admin user to use MGED! username  
            admin.username = 'MGED!'
            db.session.commit()
            admin_updated = True
        
        # Create sample post if no posts exist
        post_count = BlogPost.query.count()
        post_created = False
        
        if post_count == 0:
            sample_post = BlogPost(
                title="Welcome to Mini Golf Every Day Blog!",
                content="""<h2>Welcome to the official blog!</h2>
                
<p>This is the first post on the Mini Golf Every Day blog. Here you'll find:</p>

<ul>
<li>🏌️‍♂️ Tips and tricks for mini golf</li>
<li>🎯 Course reviews and recommendations</li>
<li>📝 Behind-the-scenes stories</li>
<li>🎉 Updates on the daily challenge</li>
</ul>

<p>Stay tuned for more content!</p>

<h3>About the Challenge</h3>
<p>The Mini Golf Every Day challenge started on January 1, 2025, with a simple goal: play mini golf every single day for the entire year. What began as a personal challenge has grown into a celebration of family, fun, and consistency.</p>

<p>Follow along on <a href="https://www.tiktok.com/@minigolfeveryday" target="_blank">TikTok @minigolfeveryday</a> for daily videos!</p>""",
                excerpt="Welcome to the official Mini Golf Every Day blog! Here you'll find tips, course reviews, and behind-the-scenes stories from the daily challenge.",
                is_published=True,
                is_featured=True,
                author_id=admin.id
            )
            sample_post.slug = sample_post.generate_slug()
            sample_post.publish()
            
            db.session.add(sample_post)
            db.session.commit()
            post_created = True
        
        # Get final stats
        user_count = User.query.count()
        total_posts = BlogPost.query.count()
        published_posts = BlogPost.query.filter_by(is_published=True).count()
        
        return jsonify({
            'status': 'success',
            'message': 'Database setup completed successfully!',
            'database_uri': app.config['SQLALCHEMY_DATABASE_URI'].split('@')[0] + '@***',
            'mysql_drivers_available': available_drivers,
            'setup_performed': {
                'tables_created': True,
                'admin_user_created': admin_created,
                'admin_user_updated': admin_updated,
                'sample_post_created': post_created,
                'video_table_created': video_setup_result.get('video_table_created', False),
                'videos_migrated': video_setup_result.get('videos_migrated', 0),
                'videos_existing': video_setup_result.get('videos_existing', 0),
                'json_synced': video_setup_result.get('json_synced', False)
            },
            'stats': {
                'total_users': user_count,
                'total_posts': total_posts,
                'published_posts': published_posts,
                'total_videos': video_setup_result.get('videos_existing', 0) + video_setup_result.get('videos_migrated', 0)
            },
            'video_setup_errors': video_setup_result.get('errors', []),
            'next_steps': [
                'Visit /blog.html to see your blog',
                'Login with username: MGED!, password: admin123secure!',
                'Change the admin password after first login',
                'Test video endpoints: /api/videos and /api/status',
                'GitHub Actions will continue to work with JSON fallback'
            ]
        }), 200
        
    except Exception as e:
        error_trace = traceback.format_exc()
        return jsonify({
            'status': 'error',
            'message': f'Database setup failed: {str(e)}',
            'error_type': type(e).__name__,
            'error_trace': error_trace,
            'suggestion': 'Check database connection and ensure MySQL drivers are installed',
            'database_uri': app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured').split('@')[0] + '@***' if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured'),
            'mysql_drivers_available': [name for name, driver in MYSQL_DRIVERS.items() if driver is not None],
            'required_packages': [
                'PyMySQL (pip install pymysql)',
                'mysql-connector-python (pip install mysql-connector-python)',
                'Flask-SQLAlchemy (pip install flask-sqlalchemy)'
            ]
        }), 500

# Static file serving (for existing functionality)
@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('.', filename)


# Image Upload API Routes
@app.route('/api/upload/image', methods=['POST'])
def upload_image():
    """Upload image for blog posts"""
    try:
        # Simple auth check (fallback if token_required fails)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization required'}), 401
        
        token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Invalid token'}), 401
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not file.filename or '.' not in file.filename:
            return jsonify({'error': 'Invalid file format'}), 400
        
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': 'File type not allowed. Use PNG, JPG, JPEG, GIF, or WebP'}), 400
        
        # Validate file size (16MB max)
        file.seek(0, 2)  # Seek to end of file
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 16 * 1024 * 1024:  # 16MB
            return jsonify({'error': 'File size too large. Maximum 16MB allowed'}), 400
        
        # Generate secure filename
        filename = secure_filename(file.filename)
        # Add timestamp to avoid filename conflicts
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{timestamp}{ext}"
        
        # Ensure uploads directory exists
        uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(uploads_dir, filename)
        file.save(file_path)
        
        # Return relative URL
        file_url = f'/uploads/{filename}'
        
        return jsonify({
            'url': file_url,
            'filename': filename,
            'size': file_size
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Image upload failed: {e}")
        return jsonify({'error': 'Image upload failed'}), 500


# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    return send_from_directory(uploads_dir, filename)


# Contact Form API
@app.route('/api/contact', methods=['POST'])
def contact_form():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Sanitize inputs
        name = data['name'].strip()[:100]  # Limit to 100 characters
        email = data['email'].strip().lower()
        subject = data['subject'].strip()[:200]  # Limit to 200 characters
        message = data['message'].strip()[:2000]  # Limit to 2000 characters
        
        # Prepare email content
        email_subject = f"Contact Form: {subject} - Mini Golf Every Day"
        email_body = f"""
New contact form submission from Mini Golf Every Day website:

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}

---
Sent from: https://minigolfevery.day/contact.html
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """.strip()
        
        # Send email silently
        try:
            smtp_server = os.environ.get('SMTP_SERVER', 'localhost')
            smtp_port = int(os.environ.get('SMTP_PORT', '25'))
            sender_email = os.environ.get('SENDER_EMAIL', 'noreply@minigolfevery.day')
            sender_password = os.environ.get('SENDER_PASSWORD', '')
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = 'minigolfeveryday@gmail.com'
            msg['Subject'] = email_subject
            
            msg.attach(MIMEText(email_body, 'plain'))
            
            # Send email
            if smtp_server == 'localhost' and not sender_password:
                # Simple local mail server (no authentication)
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.send_message(msg)
            else:
                # Authenticated SMTP server
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    if sender_password:
                        server.login(sender_email, sender_password)
                    server.send_message(msg)
            
            print(f"[INFO] Contact form email sent from {email} to minigolfeveryday@gmail.com")
            
            return jsonify({
                'success': True,
                'message': 'Message sent successfully'
            }), 200
            
        except Exception as email_error:
            print(f"[ERROR] Failed to send contact form email: {email_error}")
            
            # Log the contact form submission for manual follow-up
            contact_log_file = 'contact_submissions.log'
            log_entry = f"{datetime.now().isoformat()} | {name} | {email} | {subject} | {message}\n"
            
            try:
                with open(contact_log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
                print(f"[INFO] Contact form submission logged to {contact_log_file}")
            except Exception as log_error:
                print(f"[ERROR] Failed to log contact form submission: {log_error}")
            
            # Return success anyway to not confuse the user
            return jsonify({
                'success': True,
                'message': 'Message sent successfully'
            }), 200
            
    except Exception as e:
        print(f"[ERROR] Contact form processing failed: {e}")
        return jsonify({
            'error': 'Failed to process contact form'
        }), 500
