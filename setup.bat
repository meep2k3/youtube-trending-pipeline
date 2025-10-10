@echo off
echo ====================================
echo YouTube Trending Pipeline Setup
echo ====================================
echo.

REM Check if Docker is running
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop for Windows
    pause
    exit /b 1
)

echo [1/6] Creating project directories...
if not exist "dags" mkdir dags
if not exist "scripts" mkdir scripts
if not exist "logs" mkdir logs
if not exist "plugins" mkdir plugins
echo Done!
echo.

echo [2/6] Generating security keys...
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" > temp_fernet.txt
python -c "import secrets; print(secrets.token_urlsafe(32))" > temp_secret1.txt
python -c "import secrets; print(secrets.token_urlsafe(32))" > temp_secret2.txt

set /p FERNET_KEY=<temp_fernet.txt
set /p SECRET_KEY1=<temp_secret1.txt
set /p SECRET_KEY2=<temp_secret2.txt

del temp_fernet.txt temp_secret1.txt temp_secret2.txt
echo Done!
echo.

echo [3/6] Please enter your YouTube API Key:
set /p YOUTUBE_KEY="API Key: "
echo.

echo [4/6] Creating .env file...
(
echo # MySQL Configuration
echo MYSQL_ROOT_PASSWORD=rootpassword123
echo MYSQL_DATABASE=youtube_trending
echo MYSQL_USER=youtube_user
echo MYSQL_PASSWORD=youtube_pass123
echo.
echo # YouTube API
echo YOUTUBE_API_KEY=%YOUTUBE_KEY%
echo.
echo # Airflow Configuration
echo AIRFLOW_FERNET_KEY=%FERNET_KEY%
echo AIRFLOW_SECRET_KEY=%SECRET_KEY1%
echo.
echo # Superset Configuration
echo SUPERSET_SECRET_KEY=%SECRET_KEY2%
) > .env
echo Done!
echo.

echo [5/6] Creating docker volumes...
docker volume create youtube-pipeline_mysql_data
docker volume create youtube-pipeline_postgres_data
docker volume create youtube-pipeline_superset_data
echo Done!
echo.

echo [6/6] Starting Docker containers...
echo This may take several minutes on first run...
docker-compose up -d
echo.

echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo Services are starting up...
echo Please wait 2-3 minutes for all services to be ready.
echo.
echo Access URLs:
echo   - Airflow: http://localhost:8080 (admin/admin)
echo   - Superset: http://localhost:8088 (admin/admin)
echo   - MySQL: localhost:3306
echo.
echo To check status: docker-compose ps
echo To view logs: docker-compose logs -f
echo.
pause