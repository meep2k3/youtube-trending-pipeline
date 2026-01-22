import os
import sys
import json
import logging
from datetime import datetime
from googleapiclient.discovery import build
import mysql.connector
from mysql.connector import Error

# logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Config
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
MYSQL_CONFIG = {
    'host' : os.getenv('MYSQL_HOST', 'mysql'),
    'database' : os.getenv('MYSQL_DATABASE', 'youtube_trending'),
    'user' : os.getenv('MYSQL_USER', 'youtube_user'),
    'password' : os.getenv('MYSQL_PASSWORD', 'youtube_pass123')
}

DATALAKE_PATH = "/opt/airflow/datalake"

def get_youtube_client():
    if not YOUTUBE_API_KEY:
        raise ValueError("Youtube API key is missing")
    return build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def extract_to_datalake(region_code='VN', max_results=50):
    # Etract API -> JSON file
    try:
        youtube = get_youtube_client()
        logger.info(f"Fetching {max_results} videos for {region_code} ...")

        request = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            chart='mostPopular',
            regionCode=region_code,
            maxResults=max_results
        )

        response = request.execute()

        # Tạo đường dẫn lưu file json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"raw_{region_code}_{timestamp}.json"
        full_path = os.path.join(DATALAKE_PATH, file_name)

        # Dam bao file ton tai
        os.makedirs(DATALAKE_PATH, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=4)
        logger.info(f"Data extracted to data lake: {full_path}")
        return full_path
    
    except Exception as e:
        logger.error(f"Extract failed: {e}")
        raise

def process_scd_type_2(cursor, video_item):
    """Xu ly logic SCD type 2 cho Dimension Video"""
    video_id = video_item['id']
    snippet = video_item['snippet']
    new_title = snippet.get('title', '')
    channel_title = snippet.get('channelTitle', '')
    tags = ','.join(snippet.get('tags', []))
    thumbnail = snippet.get('thumbnails', {}).get('high', {}).get('url', '')
    cat_id = snippet.get('categoryId', 0)
    duration = video_item['contentDetails'].get('duration', '')

    # Kiem tra phien ban hien tai
    cursor.execute("""
        SELECT video_surrogate_key, title 
        FROM dim_video_scd 
        WHERE video_id = %s AND is_current = TRUE
""", (video_id,))
    
    current_record = cursor.fetchone()

    if not current_record:
        # Case 1: Video moi -> Insert
        sql = """
            INSERT INTO dim_video_scd 
            (video_id, title, channel_title, tags, thumbnail_url, category_id, duration, is_current, effective_start_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, NOW())
        """
        cursor.execute(sql, (video_id, new_title, channel_title, tags, thumbnail, cat_id, duration))
        return cursor.lastrowid
    
    else:
        surrogate_key, current_title = current_record
        # Case 2: Video cu doi title -> SCD Update
        if current_title != new_title:
            logger.info(f"SCD Change Detected for video {video_id}: Title changed")
            
            # Đóng record cũ
            cursor.execute("""
                UPDATE dim_video_scd 
                SET is_current = FALSE, effective_end_date = NOW() 
                WHERE video_surrogate_key = %s
            """, (surrogate_key,))
            
            # Insert record mới
            sql = """
                INSERT INTO dim_video_scd 
                (video_id, title, channel_title, tags, thumbnail_url, category_id, duration, is_current, effective_start_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, NOW())
            """
            cursor.execute(sql, (video_id, new_title, channel_title, tags, thumbnail, cat_id, duration))
            return cursor.lastrowid
        
        # Case 3: Không đổi gì -> Return key cũ
        return surrogate_key
    
def load_from_datalake_to_warehouse(file_path):
    """Transform, load JSON -> MySQL"""
    logger.info(f"Processing file: {file_path}")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = None
    try: 
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()

        rank = 0
        date_id = int(datetime.now().strftime("%Y%m%d"))
        trending_date = datetime.now().strftime("%Y-%m-%d")

        for item in data.get('items', []):
            rank += 1
            # Handle dimension
            video_key = process_scd_type_2(cursor, item)

            # Handle fact
            stats = item['statistics']
            sql_fact = """
                INSERT INTO fact_trending_daily 
                (video_surrogate_key, date_id, view_count, like_count, comment_count, rank_in_trending, trending_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(sql_fact, (
                video_key,
                date_id,
                int(stats.get('viewCount', 0)),
                int(stats.get('likeCount', 0)),
                int(stats.get('commentCount', 0)),
                rank,
                trending_date
            ))
        
        conn.commit()
        logger.info(f"Successfully processed {rank} videos")

    except Exception as e:
        logger.error(f"Database error: {e}")
        if conn: conn.rollback()
        raise
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    try:
        path = extract_to_datalake()
        load_from_datalake_to_warehouse(path)
    except Exception as e:
        logger.error(f"Pipeline Failed: {e}")
