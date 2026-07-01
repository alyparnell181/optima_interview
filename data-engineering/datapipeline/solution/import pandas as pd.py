import pandas as pd

from function_creation import (
    ingest_races,
    validate_races_headers, 
    validate_results_headers,   
    ingest_results,
    clean_races_data,
    clean_results_data,
    join_cleaned_data,
    aggregate_best_results,
    write_final_report
)

raw_data = {
        'asasa': [20, None, '30', 40], # Null raceid (should drop), non-int string ('30')
        'year': [2018, 2019, None, 2020], # Null year (should drop)
        'round': [1, 2, 3, 'invalid'], # Invalid round (will be handled)
        'name': ['Race A', 'Race B', 'Race C', ''], # Empty string name
        'date': ['2018-03-17', '2019-05-19', 'invalid_date', '2020-11-01'], # Invalid date (should drop)
        'time': ['1:30:00', None, '23:59:59', ''] # Null time and empty string time
    }

rw=pd.DataFrame(raw_data)


validate_races_headers(rw)
clean_races_data(rw)