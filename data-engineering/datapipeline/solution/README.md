# Data Pipeline Solution: F1 Race Performance Analysis

## 🚀 Overview
This project implements an end-to-end data pipeline to process raw Formula 1 race and results datasets. The goal is to ingest, clean, join, and aggregate the data to determine the best performance (fastest lap time) and winning driver for every recorded race, outputting structured JSON reports per year.

## ⚙️ Function Purposes
The core logic resides in `function_creation.py` and is orchestrated by `main.py`.

### Data Ingestion & Cleaning (`function_creation.py`)
*   **`ingest_races(races_csv_path)`**: Reads the raw race metadata from `races.csv` into a Pandas DataFrame, handling file loading errors.
*   **`ingest_results(results_csv_path)`**: Reads the raw results data from `results.csv`, handling file loading errors.
*   **`clean_races_data(df_races)`**: Performs rigorous validation and cleaning on race metadata, ensuring fields like `raceId`, `year`, `date`, and `time` are correctly typed and non-null.
*   **`clean_results_data(df_results)`**: Cleans the results data, validating critical identifiers (`resultid`, `raceid`, `driverid`) and standardizing time formats for `fastestlap`.

### Data Processing & Aggregation
*   **`join_cleaned_data(df_races, df_results)`**: Merges the cleaned race metadata and results data using an outer join on `raceId`, ensuring all records are retained.
*   **`aggregate_best_results(df_merged)`**: This is the core business logic. It groups the merged data by race ID to:
    1.  Calculate the minimum fastest lap time across all entries for that race.
    2.  Identify the winning driver (where `position == 1`).
    3.  Compile a final report containing the Race Name, Round, Date, Winning Driver ID, and the overall Fastest Lap Time.

### Output Generation
*   **`write_final_report(df_report, OUTPUT_JSON)`**: Takes the aggregated DataFrame and writes it to multiple JSON files in the specified output directory (`results/`). It creates a separate file for each year found (e.g., `stats_2018.json`, `stats_2019.json`).

## 🏃 How to Run
To execute the entire pipeline, run the following command from your terminal:

```bash
python solution/main.py
```

**Prerequisites:**
1.  Ensure all necessary dependencies (like `pandas`) are installed in your environment.
2.  The raw data files (`races.csv` and `results.csv`) must be present in the `source-data/` directory relative to the project root.

## ☁️ Cloud Deployment & Scaling
For production use or scaling, this pipeline should be containerized and orchestrated using cloud services.

**Recommended Architecture:**
1.  **Containerization**: Package the application using **Docker**. This ensures consistent execution across environments (local, staging, production).
2.  **Orchestration**: Use **Kubernetes (K8s)** or a managed service like AWS ECS/Google Cloud Run to manage deployment and scaling of the processing job.
3.  **Workflow Management**: Implement the pipeline using an orchestrator such as **Apache Airflow**, **Prefect**, or **Dagster**. This allows scheduling, dependency management, monitoring, and retries for the entire workflow (Ingest -> Clean -> Aggregate -> Write).

**Required Cloud Resources:**
*   **Compute**: A container service (e.g., AWS Fargate, Google Cloud Run) capable of running Python/Pandas jobs.
*   **Storage**: Cloud Object Storage (e.g., **AWS S3**, **Google Cloud Storage**) for storing raw input data (`source-data`) and final output reports (`results`). This provides durability and scalability far beyond local file systems.
*   **Compute Resources**: Depending on the volume of historical data, sufficient CPU/Memory allocated to the container job runner is required. For large datasets, consider using **Dask** or **Spark** within the processing step if Pandas memory limits are hit.