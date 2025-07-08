#!/usr/bin/env python3
"""
Simple database initialization for Mini Golf Every Day Blog
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path so we can import server
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from server import app, db, User
    
    def init_database():
        """Initialize the database tables and admin user"""
        with app.app_context():
            print("🔧 Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Create admin user if it doesn't exist
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123secure!')
                admin = User(
                    username='admin',
                    email='admin@minigolfevery.day',
                    is_admin=True
                )
                admin.set_password(admin_password)
                db.session.add(admin)
                db.session.commit()
                print("✅ Created admin user")
                print(f"🔑 Admin username: admin")
                print(f"🔑 Admin password: {admin_password}")
            else:
                print("✅ Admin user already exists")
            
            print("\n🎉 Database setup completed successfully!")
            print("🚀 You can now start the blog server with: python server.py")
    
    if __name__ == '__main__':
        init_database()
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure PostgreSQL is running")
    print("2. Check your database credentials in .env")
    print("3. Make sure the database 'minigolf_blog' exists")
    sys.exit(1)
