# TMDB Movies Analytics Lab

## Overview
This lab implements an **end-to-end data analytics pipeline** using data from **The Movie Database (TMDB) API**.  
The pipeline follows a **Bronze → Silver → Gold** architecture and combines **Python, Pandas**.

It separates:

- Data extraction logic
- Transformation and cleaning
- KPI computation
- Search queries and aggregations
- Visualization (in a jupyter notebook)

---
## System Architecture
TMDB API
   ↓
Extraction Layer
(src/tmdb_client.py)
   ↓
Bronze Storage
(src/pipeline/extract_bronze.py)
   ↓
Raw JSON Files
(data/bronze/*.json)
   ↓
Silver Transformation Layer
(src/pipeline/build_silver.py)
   ↓
Quality Validation
(src/quality/checks.py)
   ↓
Silver Dataset (Parquet)
(data/silver/tmdb_movies_silver.parquet)
   ↓
KPI & Analytics Layer
(src/kpis/*)
   ↓
Gold Builder
(src/pipeline/build_gold.py)
   ↓
Gold KPI Outputs (CSV)
(data/gold/*.csv)
   ↓
Visualization Layer
(notebooks/tmdb_viz.ipynb)
   ↓
Plots, Insights, Final Report
--- 
## Project Structure

```text
.
├── data/
│   ├── bronze/        # Raw JSON bundles from TMDB API
│   ├── silver/        # Cleaned analysis-ready dataset (parquet)
│   ├── gold/          # KPI outputs (CSV files)
│
├── notebooks/
│   └── tmdb_viz.ipynb  # Visualizations and insights
│
├── src/
│   ├── config.py
│   ├── logging_utils.py
│   ├── tmdb_client.py
│   │
│   ├── pipeline/
│   │   ├── extract_bronze.py
│   │   ├── build_silver.py
│   │   ├── build_gold.py
│   │   └── orchestrator.py
│   │
│   ├── kpis/
│   │   ├── metrics.py
│   │   ├── ranking.py
│   │   ├── search.py
│   │   ├── franchise.py
│   │   └── directors.py
│   │
│   └── quality/
│       └── checks.py
│
├── .gitignore
└── README.md
```

