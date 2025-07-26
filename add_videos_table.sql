-- Add engagement fields to existing videos table
-- Run this on production database to add the new columns

-- Add new columns if they don't exist
ALTER TABLE videos 
ADD COLUMN IF NOT EXISTS view_count INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS like_count INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS comment_count INT DEFAULT 0;

-- Add indexes for better performance on sorting
CREATE INDEX IF NOT EXISTS idx_view_count ON videos (view_count);
CREATE INDEX IF NOT EXISTS idx_like_count ON videos (like_count);
CREATE INDEX IF NOT EXISTS idx_comment_count ON videos (comment_count);

-- Verify the changes
DESCRIBE videos;
