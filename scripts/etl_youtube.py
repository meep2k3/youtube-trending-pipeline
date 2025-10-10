"""
YouTube Trending Videos ETL Script
Extracts trending videos from YouTube API and loads into MySQL
"""

import os
import sys
from datetime import datetime, date
from googleapiclient.discovery import build
import pandas as pd
import mysql.connector
from mysql.connector import Error
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'youtube_trending')
MYSQL_USER = os.getenv('MYSQL_USER', 'youtube_user')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'youtube_pass123')

# Category mapping
CATEGORY_MAPPING = {
    '1': 'Film & Animation',
    '2': 'Autos & Vehicles',
    '10': 'Music',
    '15': 'Pets & Animals',
    '17': 'Sports',
    '19': 'Travel & Events',
    '20': 'Gaming',
    '22': 'People & Blogs',
    '23': 'Comedy',
    '24': 'Entertainment',
    '25': 'News & Politics',
    '26': 'Howto & Style',
    '27': 'Education',
    '28': 'Science & Technology',
    '29': 'Nonprofits & Activism'
}


def get_youtube_client():
    """Initialize YouTube API client"""
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        logger.info("YouTube API client initialized successfully")
        return youtube
    except Exception as e:
        logger.error(f"Failed to initialize YouTube API client: {e}")
        raise


def fetch_trending_videos(youtube, region_code='VN', max_results=50):
    """
    Fetch trending videos from YouTube API
    
    Args:
        youtube: YouTube API client
        region_code: Country code (default: VN for Vietnam)
        max_results: Maximum number of videos to fetch
    
    Returns:
        List of video data dictionaries
    """
    try:
        logger.info(f"Fetching trending videos for region: {region_code}")
        
        request = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            chart='mostPopular',
            regionCode=region_code,
            maxResults=max_results
        )
        response = request.execute()
        
        videos_data = []
        for item in response.get('items', []):
            video_id = item['id']
            snippet = item['snippet']
            statistics = item['statistics']
            content_details = item['contentDetails']
            
            video_data = {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'category_id': int(snippet.get('categoryId', 0)),
                'category_name': CATEGORY_MAPPING.get(snippet.get('categoryId', '0'), 'Unknown'),
                'duration': content_details.get('duration', ''),
                'tags': ','.join(snippet.get('tags', [])),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                'country_code': region_code,
                'trending_date': date.today()
            }
            videos_data.append(video_data)
        
        logger.info(f"Successfully fetched {len(videos_data)} trending videos")
        return videos_data
    
    except Exception as e:
        logger.error(f"Error fetching trending videos: {e}")
        raise


def get_mysql_connection():
    """Create MySQL database connection"""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            database=MYSQL_DATABASE,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        if connection.is_connected():
            logger.info("MySQL connection established")
            return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        raise


def load_to_mysql(videos_data):
    """
    Load video data into MySQL database
    
    Args:
        videos_data: List of video data dictionaries
    """
    connection = None
    try:
        connection = get_mysql_connection()
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO trending_videos 
        (video_id, title, channel_title, published_at, view_count, like_count, 
         comment_count, category_id, category_name, duration, tags, thumbnail_url, 
         country_code, trending_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        records_inserted = 0
        for video in videos_data:
            try:
                # Convert published_at to datetime
                published_at = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                
                values = (
                    video['video_id'],
                    video['title'],
                    video['channel_title'],
                    published_at,
                    video['view_count'],
                    video['like_count'],
                    video['comment_count'],
                    video['category_id'],
                    video['category_name'],
                    video['duration'],
                    video['tags'],
                    video['thumbnail_url'],
                    video['country_code'],
                    video['trending_date']
                )
                
                cursor.execute(insert_query, values)
                records_inserted += 1
                
            except Exception as e:
                logger.warning(f"Error inserting video {video['video_id']}: {e}")
                continue
        
        connection.commit()
        logger.info(f"Successfully inserted {records_inserted} records into database")
        
        # Update daily statistics
        update_daily_statistics(cursor, connection)
        
    except Error as e:
        logger.error(f"Error loading data to MySQL: {e}")
        if connection:
            connection.rollback()
        raise
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            logger.info("MySQL connection closed")


def update_daily_statistics(cursor, connection):
    """Update daily statistics table"""
    try:
        stats_query = """
        INSERT INTO daily_statistics 
        (stat_date, total_videos, total_views, total_likes, total_comments, 
         avg_views_per_video, most_popular_category)
        SELECT 
            trending_date,
            COUNT(*) as total_videos,
            SUM(view_count) as total_views,
            SUM(like_count) as total_likes,
            SUM(comment_count) as total_comments,
            AVG(view_count) as avg_views_per_video,
            (SELECT category_name FROM trending_videos t2 
             WHERE t2.trending_date = t1.trending_date 
             GROUP BY category_name 
             ORDER BY COUNT(*) DESC LIMIT 1) as most_popular_category
        FROM trending_videos t1
        WHERE trending_date = CURDATE()
        GROUP BY trending_date
        ON DUPLICATE KEY UPDATE
            total_videos = VALUES(total_videos),
            total_views = VALUES(total_views),
            total_likes = VALUES(total_likes),
            total_comments = VALUES(total_comments),
            avg_views_per_video = VALUES(avg_views_per_video),
            most_popular_category = VALUES(most_popular_category)
        """
        
        cursor.execute(stats_query)
        connection.commit()
        logger.info("Daily statistics updated successfully")
        
    except Exception as e:
        logger.error(f"Error updating daily statistics: {e}")


def run_etl(region_code='VN', max_results=50):
    """
    Run the complete ETL process
    
    Args:
        region_code: Country code for trending videos
        max_results: Maximum number of videos to fetch
    """
    try:
        logger.info("Starting YouTube Trending ETL process")
        
        # Extract
        youtube = get_youtube_client()
        videos_data = fetch_trending_videos(youtube, region_code, max_results)
        
        if not videos_data:
            logger.warning("No videos fetched. Exiting.")
            return
        
        # Transform (already done in fetch_trending_videos)
        logger.info(f"Transforming {len(videos_data)} videos data")
        
        # Load
        load_to_mysql(videos_data)
        
        logger.info("ETL process completed successfully")
        
    except Exception as e:
        logger.error(f"ETL process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Can be run standalone for testing
    run_etl(region_code='VN', max_results=50)