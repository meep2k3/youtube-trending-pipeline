DROP DATABASE IF EXISTS youtube_trending;
CREATE DATABASE youtube_trending CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE youtube_trending;

-- 1. Dimension Video 
CREATE TABLE dim_video_scd (
    video_surrogate_key INT AUTO_INCREMENT PRIMARY KEY,
    video_id VARCHAR(50) NOT NULL,
    title VARCHAR(500),
    channel_title VARCHAR(255),
    tags TEXT,
    thumbnail_url VARCHAR(500),
    category_id INT,
    duration VARCHAR(20),
    effective_start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_end_date TIMESTAMP NULL,
    is_current BOOLEAN DEFAULT TRUE,

    INDEX idx_video_lookup (video_id, is_current)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. Fact Table: Trending Metrics
CREATE TABLE fact_trending_daily (
    fact_id INT AUTO_INCREMENT PRIMARY KEY,
    video_surrogate_key INT,
    date_id INT,

    view_count BIGINT,
    like_count BIGINT,
    comment_count BIGINT,
    rank_in_trending INT,

    trending_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (video_surrogate_key) REFERENCES dim_video_scd(video_surrogate_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 3. View hỗ trợ phân tích nhanh
CREATE OR REPLACE VIEW v_content_strategy AS 
SELECT 
    d.title,
    d.channel_title,

    f.trending_date,
    f.view_count,
    f.rank_in_trending,

    f.view_count - LAG(f.view_count, 1) OVER (PARTITION BY d.video_id ORDER BY f.trending_date) AS view_growth_24h
FROM fact_trending_daily f 
JOIN dim_video_scd d ON f.video_surrogate_key = d.video_surrogate_key;
