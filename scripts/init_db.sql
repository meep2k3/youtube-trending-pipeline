-- Create database if not exists
CREATE DATABASE IF NOT EXISTS youtube_trending;

USE youtube_trending;

-- Table for trending videos
CREATE TABLE IF NOT EXISTS trending_videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    video_id VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    channel_title VARCHAR(255),
    published_at DATETIME,
    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    category_id INT,
    category_name VARCHAR(100),
    duration VARCHAR(50),
    tags TEXT,
    thumbnail_url VARCHAR(500),
    country_code VARCHAR(5),
    trending_date DATE,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_video_id (video_id),
    INDEX idx_trending_date (trending_date),
    INDEX idx_category (category_id),
    INDEX idx_country (country_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table for video categories
CREATE TABLE IF NOT EXISTS video_categories (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert common YouTube categories
INSERT INTO video_categories (category_id, category_name) VALUES
(1, 'Film & Animation'),
(2, 'Autos & Vehicles'),
(10, 'Music'),
(15, 'Pets & Animals'),
(17, 'Sports'),
(19, 'Travel & Events'),
(20, 'Gaming'),
(22, 'People & Blogs'),
(23, 'Comedy'),
(24, 'Entertainment'),
(25, 'News & Politics'),
(26, 'Howto & Style'),
(27, 'Education'),
(28, 'Science & Technology'),
(29, 'Nonprofits & Activism')
ON DUPLICATE KEY UPDATE category_name = VALUES(category_name);

-- Table for daily statistics
CREATE TABLE IF NOT EXISTS daily_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stat_date DATE NOT NULL,
    total_videos INT,
    total_views BIGINT,
    total_likes BIGINT,
    total_comments BIGINT,
    avg_views_per_video DECIMAL(15,2),
    most_popular_category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_date (stat_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- View for quick analytics
CREATE OR REPLACE VIEW v_trending_analytics AS
SELECT 
    trending_date,
    category_name,
    COUNT(*) as video_count,
    SUM(view_count) as total_views,
    AVG(view_count) as avg_views,
    SUM(like_count) as total_likes,
    SUM(comment_count) as total_comments,
    MAX(view_count) as max_views
FROM trending_videos
GROUP BY trending_date, category_name
ORDER BY trending_date DESC, total_views DESC;