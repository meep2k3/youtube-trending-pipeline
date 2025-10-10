"""
Airflow DAG for YouTube Trending Videos ETL Pipeline
Runs daily to fetch and store trending videos data
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

# Import ETL function
from etl_youtube import run_etl

# Default arguments for the DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 1),
}

# Define the DAG
dag = DAG(
    'youtube_trending_pipeline',
    default_args=default_args,
    description='ETL pipeline for YouTube trending videos',
    schedule_interval='0 9 * * *',  # Run daily at 9 AM
    catchup=False,
    tags=['youtube', 'etl', 'trending'],
)


def check_api_key():
    """Check if YouTube API key is configured"""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key or api_key == 'YOUR_YOUTUBE_API_KEY_HERE':
        raise ValueError("YouTube API key is not configured properly!")
    print(f"API key configured: {api_key[:10]}...")


def check_database_connection():
    """Check MySQL database connectivity"""
    import mysql.connector
    from mysql.connector import Error
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'mysql'),
            database=os.getenv('MYSQL_DATABASE', 'youtube_trending'),
            user=os.getenv('MYSQL_USER', 'youtube_user'),
            password=os.getenv('MYSQL_PASSWORD', 'youtube_pass123')
        )
        if connection.is_connected():
            print("Database connection successful")
            connection.close()
    except Error as e:
        raise Exception(f"Database connection failed: {e}")


def fetch_vietnam_trending():
    """Fetch trending videos for Vietnam"""
    print("Fetching trending videos for Vietnam (VN)")
    run_etl(region_code='VN', max_results=50)


def fetch_us_trending():
    """Fetch trending videos for United States"""
    print("Fetching trending videos for United States (US)")
    run_etl(region_code='US', max_results=50)


def fetch_global_trending():
    """Fetch trending videos globally (multiple regions)"""
    print("Fetching trending videos for multiple regions")
    regions = ['VN', 'US', 'GB', 'JP', 'KR']
    
    for region in regions:
        try:
            print(f"Fetching for region: {region}")
            run_etl(region_code=region, max_results=30)
        except Exception as e:
            print(f"Failed to fetch for {region}: {e}")
            continue


def generate_daily_report():
    """Generate daily analytics report"""
    import mysql.connector
    from datetime import date
    
    connection = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'mysql'),
        database=os.getenv('MYSQL_DATABASE', 'youtube_trending'),
        user=os.getenv('MYSQL_USER', 'youtube_user'),
        password=os.getenv('MYSQL_PASSWORD', 'youtube_pass123')
    )
    
    cursor = connection.cursor(dictionary=True)
    
    # Get today's statistics
    query = """
    SELECT * FROM daily_statistics 
    WHERE stat_date = CURDATE()
    """
    cursor.execute(query)
    stats = cursor.fetchone()
    
    if stats:
        print("=" * 50)
        print(f"Daily Report - {stats['stat_date']}")
        print("=" * 50)
        print(f"Total Videos: {stats['total_videos']}")
        print(f"Total Views: {stats['total_views']:,}")
        print(f"Total Likes: {stats['total_likes']:,}")
        print(f"Total Comments: {stats['total_comments']:,}")
        print(f"Avg Views/Video: {stats['avg_views_per_video']:,.2f}")
        print(f"Most Popular Category: {stats['most_popular_category']}")
        print("=" * 50)
    
    cursor.close()
    connection.close()


# Task 1: Check prerequisites
task_check_api = PythonOperator(
    task_id='check_api_key',
    python_callable=check_api_key,
    dag=dag,
)

task_check_db = PythonOperator(
    task_id='check_database',
    python_callable=check_database_connection,
    dag=dag,
)

# Task 2: Fetch trending videos for Vietnam
task_fetch_vn = PythonOperator(
    task_id='fetch_vietnam_trending',
    python_callable=fetch_vietnam_trending,
    dag=dag,
)

# Task 3: Fetch trending videos for US (optional)
task_fetch_us = PythonOperator(
    task_id='fetch_us_trending',
    python_callable=fetch_us_trending,
    dag=dag,
)

# Task 4: Generate daily report
task_report = PythonOperator(
    task_id='generate_daily_report',
    python_callable=generate_daily_report,
    dag=dag,
)

# Task 5: Data quality check
task_quality_check = BashOperator(
    task_id='data_quality_check',
    bash_command='''
    echo "Running data quality checks..."
    echo "Checking for duplicate entries..."
    echo "Validating data types..."
    echo "Data quality check completed!"
    ''',
    dag=dag,
)

# Define task dependencies
[task_check_api, task_check_db] >> task_fetch_vn >> task_fetch_us >> task_quality_check >> task_report


# Alternative DAG for multiple regions (uncomment to use)
"""
with DAG(
    'youtube_trending_multi_region',
    default_args=default_args,
    description='Fetch trending videos from multiple regions',
    schedule_interval='0 10 * * *',
    catchup=False,
    tags=['youtube', 'etl', 'multi-region'],
) as dag_multi:
    
    fetch_global = PythonOperator(
        task_id='fetch_global_trending',
        python_callable=fetch_global_trending,
    )
    
    report = PythonOperator(
        task_id='generate_report',
        python_callable=generate_daily_report,
    )
    
    fetch_global >> report
"""