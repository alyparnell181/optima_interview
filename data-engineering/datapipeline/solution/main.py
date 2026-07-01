
from env_vars import OUTPUT_JSON, RACES_CSV, RESULTS_CSV
from function_creation import (
    ingest_races,
    validate_races_headers,   
    ingest_results,
    validate_results_headers, 
    clean_races_data,
    clean_results_data,
    join_cleaned_data,
    aggregate_best_results,
    write_final_report
)
#Execute all functions in sequence to produce the final report
def main() -> None:
    races = ingest_races(RACES_CSV)
    validate_races_headers(races)
    results = ingest_results(RESULTS_CSV)
    validate_results_headers(results)
    cleaned_races = clean_races_data(races)
    cleaned_results = clean_results_data(results)
    merged_df = join_cleaned_data(cleaned_races, cleaned_results)
    final_df =aggregate_best_results(merged_df)
    write_final_report(final_df, OUTPUT_JSON)
  
if __name__ == "__main__":
    main()
