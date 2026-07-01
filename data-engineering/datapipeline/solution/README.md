# Data Pipeline Solution: F1 Race Performance Analysis

## 🚀 Overview
This project implements an end-to-end data pipeline to process raw Formula 1 race and results datasets. The goal is to ingest, clean, join, and aggregate the data to determine the best performance (fastest lap time) and winning driver for every recorded race, outputting structured JSON reports per year.

## ⚙️ Function Purposes
The core logic resides in `functions.py` and is orchestrated by `main.py`.

### Data Ingestion & Cleaning (`functions.py`)
*   **`ingest_races(races_csv_path)`**: Reads the raw race data from `races.csv` into a Pandas DataFrame .
*   **`validate_races_headers(df_races)`**: Checks to ensure the number of columns and names is as expected for the races dataset
*   **`ingest_results(results_csv_path)`**: Reads the raw results data from `results.csv`, into a Pandas DataFrame.
*   **`validate_results_headers(df_results)`**: Checks to ensure the number of columns and names is as expected for the results dataset
*   **`clean_races_data(df_races)`**: Performs  validation and cleaning on race data.
*   **`clean_results_data(df_results)`**: Performs  validation and cleaning on results data.

### Data Processing & Aggregation
*   **`join_cleaned_data(df_races, df_results)`**: Merges the cleaned race data and results data using an outer join on `raceId`, ensuring all records are retained.
*   **`aggregate_best_results(df_merged)`**: This is the core business logic. It groups the merged data by race ID to:
    1.  Calculate the fastest lap time across all entries for that race.
    2.  Identify the winning driver (where `position == 1`).
    3.  Compile a final report containing the Race Name, Round, Date, Winning Driver ID, and the overall Fastest Lap Time.

### Output Generation
*   **`write_final_report(df_report, OUTPUT_JSON)`**: Takes the aggregated DataFrame and writes it to multiple JSON files in the specified output directory (`results/`). It creates a separate file for each year found (e.g., `stats_2018.json`, `stats_2019.json`).

## Assumptions
1. Where data is missing for the fields Date, Year, Result ID, or Race ID, the affected records are removed during cleaning.
2. Fastest Lap is calculated at the race level, so the fastest lap reported for a race may come from a driver who did not win that race.
3. In practice, additional requirements gathering should be executed to ensure full understanding of data lineage, this will be to ensure treatment/removal of data is done appropriately and to ensure alignment with business expectations.

## 🏃 How to Run
The easiest way to run this pipeline is to clone the repository, open a terminal in the project directory, and point Python at that directory.

Example:

```bash
git clone <repo-url>
cd path/to/your/clone/data-engineering/datapipeline
python solution/main.py
```

This is the simplest approach because it keeps the relative file paths consistent, allowing the pipeline to find the CSV files in the `source-data/` folder and write the output JSON files into the `results/` folder.

**Prerequisites:**
1.  Ensure all necessary dependencies are installed in your environment.
2.  The raw data files (`races.csv` and `results.csv`) must be present in the `source-data/` directory relative to the project root.

**Required Python packages:**
- `pandas`
- `pytest` (only required to run the unit tests)



## ☁️ Cloud Deployment & Scaling
The provided code is only built to run locally and for relatively low volumes of data. If the desired end goal for this was to deploy in a fully automated cloud service, the following requirements and considerations should be invesigated.

### Objective

The final solution to look to address the following issues:
- Scale to account for both data volume and complexity of manipulation
- Automation - Allow the process to run without human interaction
- Security - Ensure data is stored,processed and accessed in a compliant manner

### Considerations

- **Process Lineage** - We would need to understand how the data would be ingested in to the environment i.e manual upload, API driven. This would help determine the required tool sets in order to fully automate the solution, it would also impact the required Python packages utilised.
- **Data Scope** - Would data remain consistent over time or would additional variables be introduced. Furthermore, would data be sent in incremental fashion or full reloads of information. 
- **Destination** - Where would the output data be landing, is it to feed in to existing dashboards or be pushed directly back to the client?
- **Data utilisation** - How would the data be used, will their be a requirement to allow the client to query it, will this be utilised in additionl analytics down the line?

### Suggested Cloud Components 
The following denotes a high level component requiremment for a cloud based solutions

- **Storage** - To accomodate increased volumes of data, it would be recommended to utilise a scalable storage component such as **AWS S3**, **Azure Datalake**.**Delta Lake** or similar. This would allow ingestion of all formats in their raw forms. Depending on the client requirement, it may also be considered to store the outputs in a database (SQL Server, Postgres...)

- **Compute** -  To automate code runs and account for increased data velocity and complexity utilising a scalable and flexible compute solution such as **Databricks** would be required. This could be deployed in cloud provider of choice such as Amazon or Azure. Furthermore, utilisation of a tool such as Databricks would allow for orchestation of workflows ensuring full automated solution. For Azure specifically, a reasonable alternative would also to be consider Microsoft Fabric which would meet the same requirements. Please note, costs would need to be investigated to ensure reasonable operating costs.

- **Access** - Service level accounts and key stores should be utilised to ensure only relevant access and secrecy of keys

- **Environments** - To ensure consistent of code updates, reduce package conflicts and simplify reproduction, invesigtating container solutions such as **Docker** will allow for simplistic promotion of udpates from local, staging and production.


