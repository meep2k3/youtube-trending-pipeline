# 🎬 YouTube Trending Data Pipeline

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> A fully automated data engineering pipeline that extracts YouTube trending videos, processes the data, and provides actionable insights through interactive dashboards.

## 📊 Project Overview

This project demonstrates an end-to-end data pipeline using modern data engineering tools:

- **Automated Data Collection**: Fetches trending videos daily from YouTube Data API
- **ETL Pipeline**: Transforms and loads data into MySQL with data quality checks
- **Workflow Orchestration**: Scheduled and monitored with Apache Airflow
- **Data Visualization**: Interactive dashboards built with Apache Superset
- **Containerized Deployment**: Fully dockerized for easy deployment

## 🏗️ Architecture

```
┌─────────────┐
│ YouTube API │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────┐     ┌──────────────┐
│   Airflow   │────▶│  MySQL  │────▶│   Superset   │
│ (Scheduler) │     │ (Store) │     │ (Visualize)  │
└─────────────┘     └─────────┘     └──────────────┘
       │
       ▼
    Docker Compose
```

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Data Source** | YouTube Data API v3 | Extract trending videos data |
| **Orchestration** | Apache Airflow 2.7.3 | Schedule and monitor ETL jobs |
| **ETL** | Python (pandas, requests) | Data transformation and loading |
| **Database** | MySQL 8.0 | Store structured data |
| **Visualization** | Apache Superset 3.0 | Interactive dashboards |
| **Deployment** | Docker Compose | Container orchestration |

## ✨ Features

- ✅ **Automated Daily Pipeline**: Runs every day at 9 AM
- ✅ **Multi-Region Support**: Fetch data from multiple countries
- ✅ **Error Handling**: Retry mechanism with exponential backoff
- ✅ **Data Quality**: Validation, deduplication, and statistics tracking
- ✅ **Real-time Monitoring**: Airflow UI for pipeline monitoring
- ✅ **Interactive Dashboards**: 7+ visualizations for insights
- ✅ **Scalable Architecture**: Easy to extend and modify

## 📸 Screenshots

### Airflow DAG
![Airflow DAG](screenshots/airflow-dag.png)

### Superset Dashboard
![Dashboard](screenshots/superset-dashboard.png)

## 🚀 Quick Start

### Prerequisites

- Docker Desktop
- Python 3.10+
- YouTube Data API Key ([Get it here](https://console.cloud.google.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/meep2k3/youtube-trending-pipeline.git
   cd youtube-trending-pipeline
   ```

2. **Set up environment variables**
   ```bash
   # Copy example and fill in your values
   copy .env.example .env
   
   # Generate keys (Windows)
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Start the pipeline**
   ```bash
   docker-compose up -d
   ```

4. **Access the applications**
   - **Airflow**: http://localhost:8080 (admin/admin)
   - **Superset**: http://localhost:8088 (admin/admin)
   - **MySQL**: localhost:3307

### Verify Installation

```bash
# Check all containers are running
docker-compose ps

# Run test script
python test_system.py

# Trigger DAG manually in Airflow UI
```

## 📊 Data Schema

### trending_videos Table

| Column | Type | Description |
|--------|------|-------------|
| video_id | VARCHAR(255) | Unique video identifier |
| title | VARCHAR(500) | Video title |
| channel_title | VARCHAR(255) | Channel name |
| view_count | BIGINT | Number of views |
| like_count | BIGINT | Number of likes |
| category_name | VARCHAR(100) | Video category |
| trending_date | DATE | Date when trending |

See [init_db.sql](scripts/init_db.sql) for complete schema.

## 📈 Pipeline Workflow

1. **Extract**: Fetch trending videos from YouTube API
2. **Transform**: Clean, validate, and enrich data
3. **Load**: Insert into MySQL with deduplication
4. **Aggregate**: Calculate daily statistics
5. **Monitor**: Track success/failure in Airflow

## 🎯 Key Insights Generated

- 📊 Most popular video categories
- 🕐 Best time to publish for trending
- 📈 View count trends over time
- ⭐ Top performing channels
- 💬 Engagement rate analysis

## 🧪 Testing

```bash
# Run system tests
python test_system.py

# Test individual components
docker exec -it airflow_standalone python /opt/airflow/scripts/etl_youtube.py

# Check data quality
docker exec -it youtube_mysql mysql -u youtube_user -p
```

## 📝 Project Structure

```
youtube-trending-pipeline/
├── dags/
│   └── youtube_trending_dag.py    # Airflow DAG definition
├── scripts/
│   ├── etl_youtube.py             # ETL logic
│   └── init_db.sql                # Database schema
├── dashboards/                    # Project screenshots
├── docker-compose.yml             # Container orchestration
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🔧 Configuration

### Change Data Collection Frequency

Edit `dags/youtube_trending_dag.py`:
```python
schedule_interval='0 9 * * *'  # Daily at 9 AM
# Change to: '0 */6 * * *' for every 6 hours
```

### Add More Regions

Edit `dags/youtube_trending_dag.py`:
```python
regions = ['VN', 'US', 'GB', 'JP', 'KR']
```

## 🐛 Troubleshooting

### Containers won't start
```bash
docker-compose down -v
docker-compose up -d --build
```

### API quota exceeded
- Reduce `max_results` in DAG
- Decrease collection frequency
- Quota resets daily at 12:00 AM PST

### More issues?
Check [STEP_BY_STEP_GUIDE.md](STEP_BY_STEP_GUIDE.md) for detailed troubleshooting.

## 🚀 Future Enhancements

- [ ] Real-time streaming with Kafka
- [ ] Sentiment analysis on video titles
- [ ] ML model for trend prediction
- [ ] Multi-cloud deployment (AWS/GCP/Azure)
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Data quality monitoring with Great Expectations

## 📚 Documentation

- [Step-by-Step Setup Guide](STEP_BY_STEP_GUIDE.md)
- [API Documentation](https://developers.google.com/youtube/v3)
- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Superset Documentation](https://superset.apache.org/docs/intro)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/meep2k3)
- Email: vinhquyen0401@gmail.com

## 🙏 Acknowledgments

- YouTube Data API for providing trending data
- Apache Software Foundation for Airflow and Superset
- Docker community for containerization tools

## 📞 Contact

For questions or feedback, please open an issue or contact me directly.

