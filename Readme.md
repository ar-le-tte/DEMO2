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
```text
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
```
This architecture follows 9 imortant stages:
1. TMDB API
2. tmdb_client.py  → fetch movie + credits
3. extract_bronze.py  → save one JSON per movie
4. build_silver.py  → flatten + clean + type cast
5. quality/checks.py → validate required columns
6. tmdb_movies_silver.parquet
7. build_gold.py  → add KPIs + rankings + aggregations
8. data/gold/*.csv
9. tmdb_viz.ipynb → visualization + analysis
--- 
## Project Structure

```text
DEMO2/
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
│   ├── logging_utils.py     # Logging the sucess and failures of the tasks
│   ├── tmdb_client.py
│   │
│   ├── pipeline/
│   │   ├── extract_bronze.py
│   │   ├── build_silver.py
│   │   ├── build_gold.py
│   │   └── orchestrator.py           # To orchestate the whole pipeline
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
## Pipeline Architecture
### Bronze Layer - Raw Data Extraction
This is responsible for Raw Ingestion from TMDB API and persit it without transformations: Storing the movies, credits JSON files as received.

**Key Features**
- Raw data preservation
- Parallel API extraction
- Uses `.env` secret keys for the extraction

**Key scripts**: 
1. [`TMDB Client`](src/tmdb_client.py)
   - Handles API Communication
   - Fetches movie details and movie credits

2. [`Movies Download`](src/pipeline/extract_bronze.py)
   - Downloads movies in parallel
   - Saves one `JSON` file per movie
   - Ensures idempotency (Skips already downloaded files)



### Silver Layer
This is responsible tansforming raw JSON into an analysis-ready dataset: Cleaning the data.

**Key Features**
- Flattened nested JSON
- Strong type enforcement
- Data validation
- Clean, analysis-ready table
- Parquet format for efficiency

**Key script**: 
1. [`Silver Building`](src/pipeline/build_silver.py)
   - Read all Bronze JSON files
   - Flatten nested JSON fields
   - Extract credit-based features
   - Type Casting
   - Data cleaning

2. [`Quality Checking`](src/quality/checks.py)
   - Checking the exixtense of required columns

### Gold Layer
This is responsible for computing analytical metrics, generate analytical outputs and ranked insights.
**Key scripts**: 
- [`Gold Orchestrator`]src/pipeline/build_gold.py
- src/kpis/metrics.py
- src/kpis/ranking.py
- src/kpis/search.py
- src/kpis/franchise.py
- src/kpis/directors.py

**What Happens Here**
1. KPI Feature Engineering
2. Ranking Engine: Generic ranking helper used to compute thing like:
   - Highest Revenue
   - Highest Budget
3. Advanced Search Queries: 
   - Best-rated Science Fiction + Action movies starring Bruce Willis
   - Movies starring Uma Thurman, directed by Quentin Tarantino
4. Aggregations
5. [`Visualizations`](notebooks/tmdb_viz.ipynb)
   - Reads only from Silver and Gold outputs
   - Performs no heavy transformation
   - Generates visual insights such as Revenue vs Budget trends