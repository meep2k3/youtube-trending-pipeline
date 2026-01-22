from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

# Import ETL function
from etl_youtube import extract_to_datalake, load_from_datalake_to_warehouse

# Default arguments for the DAG
default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 1, 1),
}

# Define the DAG
with DAG(
    'youtube_trending_pipeline',
    default_args=default_args,
    description='ETL pipeline for YouTube trending videos',
    schedule_interval='0 9 * * *',  # Run daily at 9 AM
    catchup=False,
    tags=['youtube', 'scd_type_2', 'datalake']
) as dag:
    
    def task_extract_wrapper(**context):
        file_path = extract_to_datalake(region_code='VN', max_results=50)
        context['ti'].xcom_push(key='raw_json_path', value=file_path)
    
    extract_task = PythonOperator(
        task_id = 'extract_to_datalake',
        python_callable = task_extract_wrapper,
        provide_context = True
    )

    def task_load_wrapper(**context):
        file_path = context['ti'].xcom_pull(key='raw_json_path', task_ids='extract_to_datalake')
        if not file_path:
            raise ValueError("No file path received from extract task")
        
        load_from_datalake_to_warehouse(file_path)
    
    load_task = PythonOperator (
        task_id = 'load_to_warehouse',
        python_callable = task_load_wrapper,
        provide_context = True 
    )

    extract_task >> load_task
