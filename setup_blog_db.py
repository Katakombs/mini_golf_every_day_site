#!/usr/bin/env python3
"""
Database setup script for Mini Golf Every Day Blog
Creates PostgreSQL database and initializes tables
"""

import os
import sys
import secrets
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

def create_database():
    """Create PostgreSQL database if it doesn't exist"""
    
    # Database connection parameters
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_user = os.environ.get('DB_USER', 'dz')  # Default to current user
    db_password = os.environ.get('DB_PASSWORD', '')
    db_name = os.environ.get('DB_NAME', 'minigolf_blog')
    
    print(f"🔍 Connecting to PostgreSQL at {db_host}:{db_port}")
    print(f"📊 Database name: {db_name}")
    
    try:
        # Connect to PostgreSQL server (without specific database)
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database='postgres'  # Connect to default postgres database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if exists:
            print(f"✅ Database '{db_name}' already exists")
        else:
            # Create database
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Created database '{db_name}'")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def generate_env_file():
    """Generate .env.blog file if it doesn't exist"""
    
    env_file = '.env.blog'
    
    if os.path.exists(env_file):
        print(f"✅ {env_file} already exists")
        return True
    
    print(f"📝 Creating {env_file}...")
    
    # Generate secure keys
    secret_key = secrets.token_hex(32)
    jwt_secret_key = secrets.token_hex(32)
    admin_password = secrets.token_urlsafe(16)
    
    # Default database URL
    db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres@localhost:5432/minigolf_blog')
    
    env_content = f"""# Mini Golf Every Day - Blog Environment Configuration
# Generated on {datetime.now().isoformat()}

# Security Keys (automatically generated)
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret_key}

# Database Configuration
DATABASE_URL={db_url}

# Admin Account (change this password!)
ADMIN_PASSWORD={admin_password}

# Optional: Email configuration for future features
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-app-password

# Production settings
FLASK_ENV=development
DEBUG=True
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Created {env_file}")
        print(f"🔑 Admin password: {admin_password}")
        print(f"⚠️  Please change the admin password after first login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating {env_file}: {e}")
        return False

def setup_database():
    """Initialize database tables"""
    
    print("🔧 Setting up database tables...")
    
    try:
        # Load environment variables
        if os.path.exists('.env.blog'):
            with open('.env.blog', 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#') and '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        
        # Import and initialize the Flask app
        from server import app, init_db
        
        with app.app_context():
            init_db()
            print("✅ Database tables created successfully")
            
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Mini Golf Every Day - Blog Database Setup")
    print("=" * 50)
    
    # Step 1: Generate environment file
    if not generate_env_file():
        sys.exit(1)
    
    # Step 2: Create PostgreSQL database
    if not create_database():
        print("❌ Failed to create database. Please check your PostgreSQL connection.")
        print("💡 Make sure PostgreSQL is running and you have the correct credentials.")
        sys.exit(1)
    
    # Step 3: Setup database tables
    if not setup_database():
        sys.exit(1)
    
    print("\n🎉 Database setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review and update .env.blog with your settings")
    print("2. Change the admin password after first login")
    print("3. Install requirements: pip install -r requirements_blog.txt")
    print("4. Start the server: python server.py")
    
if __name__ == "__main__":
    main()
