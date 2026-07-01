import pandas as pd
from env_vars import OUTPUT_JSON, RACES_CSV, RESULTS_CSV

from functions import (
    ingest_races,
    validate_races_headers,
    ingest_results,
    validate_results_headers,
    clean_races_data,
    clean_results_data,
    join_cleaned_data,
    aggregate_best_results,
    write_final_report,
)


df = pd.DataFrame({
        'raceId': [1],
        'year': [2018],
        'round': [1],
        'name': ['Race A'],
        'date': ['2018-03-17'],
        'time': ['01:30:00'],
        'asasa': ['01:30:00'],
    })





#print(len(df.columns) )
validate_races_headers(df)

#print(df.columns.tolist())

valid_df = pd.DataFrame({
        'resultId': [1],
        'raceId': [10],
        'driverId': [2],
        'position': [1],
        'fastestLapTime': ['01:30:00'],
        'asasa': ['01:30:00'],
    })

df2 = pd.DataFrame(valid_df)
#validate_results_headers(df2)