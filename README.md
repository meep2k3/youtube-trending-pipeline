# 🚀 YouTube Trending Content Strategy Pipeline

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![Airflow](https://img.shields.io/badge/Apache%20Airflow-2.7-orange.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg)
![Superset](https://img.shields.io/badge/Superset-Visualization-success.svg)

> **From Data to Viral:** An end-to-end data engineering project that helps Content Creators optimize their strategy by analyzing YouTube Trending metrics.

---

## 🎯 1. Business Problem & Solution

### The Challenge
For YouTubers and Marketing Agencies, getting into the "Trending" tab is a goldmine. However, the YouTube algorithm is a "black box." Creators often struggle with:
* **Timing:** Not knowing which video topics are rising *right now*.
* **Clickbait vs. Quality:** High views don't always mean high engagement.
* **Trend Volatility:** Hard to track real-time changes in rank and metadata (titles/thumbnails).

### The Solution
This project builds an automated pipeline to scrape, store, and analyze trending data daily. It transforms raw metrics into actionable **Content Strategies**.

### 📊 Key Insights (Current MVP)
Currently, the system provides 3 core metrics to aid decision-making:

1.  **🚀 Top Viral Velocity (Growth Rate):**
    * *Question:* Which videos are gaining views the fastest in the last 24h?
    * *Value:* Helps identify "rising stars" to react to, rather than just looking at cumulative views.
2.  **🔥 Trending Categories:**
    * *Question:* Which content categories (Music, Gaming, News) dominate the top charts?
    * *Value:* Helps creators choose the right niche for their next video.
3.  **❤️ Engagement Rate High-Score:**
    * *Question:* Which videos have the highest (Like + Comment) / View ratio?
    * *Value:* Identifies high-quality content that truly resonates with audiences, filtering out empty "clickbait."

---

## 🛠️ 2. Tech Stack

| Component | Technology | Role & Responsibility |
|-----------|-----------|-----------------------|
| **Ingestion** | **Python (Google API Client)** | Fetches data from YouTube Data API v3. |
| **Orchestration** | **Apache Airflow** | Schedules daily workflows, manages retries and dependencies. |
| **Storage (Raw)** | **Data Lake (Local/Mounted)** | Stores raw JSON files for audit trails and reprocessing capabilities. |
| **Storage (Curated)** | **MySQL (Star Schema)** | Stores structured data with **SCD Type 2** logic. |
| **Visualization** | **Apache Superset** | Interactive dashboards for business insights. |
| **Infrastructure** | **Docker Compose** | Containerizes the entire stack for reproducible deployment. |

---

## 🔄 3. Data Architecture & Flow

The pipeline follows a modern **ELT (Extract - Load - Transform)** pattern with a Data Lake layer.

```mermaid
graph LR
    A[YouTube API] -->|Extract JSON| B(Data Lake / Local Storage)
    B -->|Parse & SCD Logic| C[(MySQL Data Warehouse)]
    C -->|SQL View| D[Superset Dashboard]
```

### 🔹 Step 1: Data Lake (Raw Layer)
* Instead of loading directly into the DB, raw data is fetched from the API and saved as **JSON files** in a mounted volume (`/datalake`).
* **Benefit:** Allows re-processing of historical data if logic changes, without calling the API again (saving quota).

### 🔹 Step 2: Data Warehouse (Serving Layer)
* Data is parsed from JSON and loaded into **MySQL**.
* **Modeling:** Implemented **Star Schema**.
    * **Fact Table:** `fact_trending_daily` (Transactional metrics: views, rank, growth).
    * **Dimension Table:** `dim_video_scd` (Video metadata).
* **⭐ Highlight: SCD Type 2 (Slowly Changing Dimension):**
    * The system tracks changes in **Video Titles** and **Thumbnails**.
    * If a YouTuber changes a title to optimize clicks, the system keeps *both* the old and new versions, allowing us to analyze the effectiveness of the change.

---

## ⚡ 4. Airflow DAG Workflow

The pipeline is orchestrated by the DAG `youtube_content_strategy_pipeline`, consisting of two main tasks connected via **XCom**:

![Airflow Pipeline](images/airflow_pipeline.png)

1.  **`extract_to_datalake`**:
    * Calls YouTube API.
    * Saves `raw_VN_YYYYMMDD.json` to the Data Lake.
    * Pushes the file path to XCom.
2.  **`load_to_warehouse`**:
    * Pulls the file path from XCom.
    * Checks for SCD Type 2 changes (Insert vs Update).
    * Loads metrics into Fact tables.

---

## 📈 5. Dashboards & Results

### A. Viral Velocity & Engagement
*Captures the fastest-growing videos and highest-quality audience interaction.*

![Viral Velocity](images/viral_velocity.png)
![Dashboard Growth](images/dashboard_growth_engagement.png)

### B. Category Dominance
*Breakdown of top trending categories by total view share.*

![Dashboard Category](images/dashboard_category.png)
