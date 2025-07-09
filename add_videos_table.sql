-- Add videos table to your existing MySQL database
-- Run this in phpMyAdmin or MySQL console

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

-- Create index for better performance
CREATE INDEX idx_videos_upload_date_desc ON videos (upload_date DESC);
