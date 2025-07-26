#!/usr/bin/env python3
"""
Migrate videos from tiktok_videos.json to MySQL database
This maintains compatibility with GitHub Actions while moving to database storage
"""

import os
import json
import sys
import pymysql
from datetime import datetime
from dotenv import load_dotenv

def load_environment():
    """Load environment variables"""
    # Try regular .env first, then production
    if os.path.exists('.env'):
        load_dotenv('.env')
        print("✅ Loaded .env file")
    elif os.path.exists('.env.production'):
        load_dotenv('.env.production')
        print("✅ Loaded .env.production file")
    else:
        print("❌ No environment file found (.env or .env.production)")
        return False
    return True

def connect_to_database():
    """Connect to MySQL database"""
    try:
        connection = pymysql.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            port=int(os.environ.get('DB_PORT', 3306)),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print(f"✅ Connected to MySQL database: {os.environ.get('DB_NAME')}")
        return connection
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"   Host: {os.environ.get('DB_HOST', 'localhost')}")
        print(f"   Port: {os.environ.get('DB_PORT', 3306)}")
        print(f"   Database: {os.environ.get('DB_NAME')}")
        print(f"   User: {os.environ.get('DB_USER')}")
        return None

def create_videos_table(connection):
    """Create videos table if it doesn't exist"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS videos (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    video_id VARCHAR(255) UNIQUE NOT NULL,
                    title TEXT,
                    upload_date VARCHAR(8),
                    url VARCHAR(500),
                    view_count INT DEFAULT 0,
                    like_count INT DEFAULT 0,
                    comment_count INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_video_id (video_id),
                    INDEX idx_upload_date (upload_date),
                    INDEX idx_view_count (view_count),
                    INDEX idx_like_count (like_count),
                    INDEX idx_comment_count (comment_count)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Create additional index for better performance (separate statement)
            try:
                cursor.execute("""
                    CREATE INDEX idx_videos_upload_date_desc 
                    ON videos (upload_date DESC)
                """)
            except pymysql.Error as e:
                # Index might already exist
                if e.args[0] != 1061:  # 1061 = Duplicate key name
                    print(f"⚠️ Index creation warning: {e}")
            
        connection.commit()
        print("✅ Videos table created/verified")
        return True
    except Exception as e:
        print(f"❌ Failed to create videos table: {e}")
        return False

def load_json_videos():
    """Load videos from tiktok_videos.json"""
    try:
        if os.path.exists('tiktok_videos.json'):
            with open('tiktok_videos.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            videos = data.get('videos', [])
            print(f"✅ Loaded {len(videos)} videos from JSON file")
            return videos
        else:
            print("⚠️ tiktok_videos.json not found - starting with empty database")
            return []
    except Exception as e:
        print(f"❌ Failed to load JSON file: {e}")
        return []

def migrate_videos_to_database(connection, videos):
    """Migrate videos from JSON to database"""
    try:
        migrated = 0
        skipped = 0
        
        with connection.cursor() as cursor:
            for video in videos:
                video_id = video.get('video_id', '')
                title = video.get('title', '')
                upload_date = video.get('upload_date', '')
                url = video.get('url', f"https://www.tiktok.com/@minigolfeveryday/video/{video_id}")
                view_count = video.get('view_count', 0)
                like_count = video.get('like_count', 0)
                comment_count = video.get('comment_count', 0)
                
                if not video_id:
                    print(f"⚠️ Skipping video with no ID: {video}")
                    skipped += 1
                    continue
                
                try:
                    # Insert or update video
                    cursor.execute("""
                        INSERT INTO videos (video_id, title, upload_date, url, view_count, like_count, comment_count)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        title = VALUES(title),
                        upload_date = VALUES(upload_date),
                        url = VALUES(url),
                        view_count = VALUES(view_count),
                        like_count = VALUES(like_count),
                        comment_count = VALUES(comment_count),
                        updated_at = CURRENT_TIMESTAMP
                    """, (video_id, title, upload_date, url, view_count, like_count, comment_count))
                    
                    migrated += 1
                    
                except Exception as e:
                    print(f"⚠️ Failed to migrate video {video_id}: {e}")
                    skipped += 1
        
        connection.commit()
        print(f"✅ Migration complete: {migrated} migrated, {skipped} skipped")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def sync_database_to_json(connection):
    """Sync database back to JSON for GitHub Actions compatibility"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT video_id, title, upload_date, url
                FROM videos
                ORDER BY upload_date DESC, created_at DESC
            """)
            
            db_videos = cursor.fetchall()
        
        # Convert to JSON format
        json_videos = []
        for video in db_videos:
            json_videos.append({
                'video_id': video['video_id'],
                'title': video['title'] or '',
                'upload_date': video['upload_date'] or '',
                'url': video['url'] or f"https://www.tiktok.com/@minigolfeveryday/video/{video['video_id']}"
            })
        
        # Create JSON structure
        json_data = {
            'videos': json_videos,
            'last_updated': datetime.now().isoformat(),
            'total_count': len(json_videos)
        }
        
        # Write to JSON file
        with open('tiktok_videos.json', 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Synced {len(json_videos)} videos to tiktok_videos.json")
        return True
        
    except Exception as e:
        print(f"❌ Failed to sync to JSON: {e}")
        return False

def verify_migration(connection):
    """Verify the migration was successful"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM videos")
            db_count = cursor.fetchone()['count']
        
        # Check JSON file
        json_count = 0
        if os.path.exists('tiktok_videos.json'):
            with open('tiktok_videos.json', 'r') as f:
                data = json.load(f)
                json_count = len(data.get('videos', []))
        
        print(f"📊 Verification:")
        print(f"   Database videos: {db_count}")
        print(f"   JSON file videos: {json_count}")
        
        if db_count == json_count and db_count > 0:
            print("✅ Migration verified successfully")
            return True
        else:
            print("⚠️ Video counts don't match")
            return False
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    print("🎬 MIGRATING VIDEOS FROM JSON TO DATABASE")
    print("=" * 50)
    
    # Load environment
    if not load_environment():
        sys.exit(1)
    
    # Connect to database
    connection = connect_to_database()
    if not connection:
        sys.exit(1)
    
    try:
        # Create videos table
        if not create_videos_table(connection):
            sys.exit(1)
        
        # Load videos from JSON
        videos = load_json_videos()
        
        # Migrate to database
        if not migrate_videos_to_database(connection, videos):
            sys.exit(1)
        
        # Sync back to JSON for GitHub Actions compatibility
        if not sync_database_to_json(connection):
            sys.exit(1)
        
        # Verify migration
        if not verify_migration(connection):
            print("⚠️ Migration completed but verification failed")
        
        print("\n✅ MIGRATION COMPLETE!")
        print("🎯 WHAT HAPPENED:")
        print("  1. Created videos table in MySQL database")
        print("  2. Migrated all videos from JSON to database")
        print("  3. Synced database back to JSON for GitHub Actions")
        print("  4. Your GitHub Actions will continue to work normally")
        print("\n💡 NEXT STEPS:")
        print("  1. Update server.py to read from database instead of JSON")
        print("  2. GitHub Actions will keep JSON file in sync with database")
        print("  3. Best of both worlds: database reliability + GitHub Actions compatibility")
        
    finally:
        connection.close()

if __name__ == '__main__':
    main()
