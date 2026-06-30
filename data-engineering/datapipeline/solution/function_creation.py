import pandas as pd
import os
from datetime import datetime

def ingest_races(races_csv_path: str) -> pd.DataFrame:
    """ Ingests data from the races CSV file into a single Pandas DataFrame. """
    try:
        # Load the dataset from the specified path
        df = pd.read_csv(races_csv_path)
        return df
    except FileNotFoundError as e:
        print(f"Error loading races CSV: File not found at {races_csv_path}. Details: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred during data ingestion for races: {e}")
        return pd.DataFrame()

def ingest_results(results_csv_path: str) -> pd.DataFrame:
    """Ingests data from the results CSV file into a single Pandas DataFrame."""
    try:
        # Load the dataset from the specified path
        df = pd.read_csv(results_csv_path)
        return df
    except FileNotFoundError as e:
        print(f"Error loading results CSV: File not found at {results_csv_path}. Details: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred during data ingestion for results: {e}")
        return pd.DataFrame()

def clean_races_data(df_races: pd.DataFrame) -> pd.DataFrame:
    """
    Applies validation and cleaning rules to the races DataFrame.

    Checks include:
    1. raceid is an integer, non-null (rows with null/invalid raceid are dropped).
    2. year is an integer, non-null (rows with null/invalid year are dropped).
    3. round is an integer.
    4. name is a string.
    5. date is a valid date field.
    6. time is a valid time field; empty times are replaced with '00:00:00'.
    """
    print("Starting data cleaning and validation for races...")
    initial_rows = len(df_races)
    cleaned_df = df_races.copy()

    # 1. raceid checks (Integer type, non-null)
    if 'raceId' in cleaned_df.columns:
        # Attempt to convert to numeric, coercing errors to NaN
        cleaned_df['raceId'] = pd.to_numeric(cleaned_df['raceId'], errors='coerce')
        # Drop rows where raceid is NaN (null or non-convertible)
        cleaned_df.dropna(subset=['raceId'], inplace=True)
        # Convert to integer after dropping NaNs
        cleaned_df['raceId'] = cleaned_df['raceId'].astype(int)

    # 2. Year checks (Integer type, non-null)
    if 'year' in cleaned_df.columns:
        cleaned_df['year'] = pd.to_numeric(cleaned_df['year'], errors='coerce')
        cleaned_df.dropna(subset=['year'], inplace=True)
        # Convert to integer after dropping NaNs
        cleaned_df['year'] = cleaned_df['year'].astype(int)

    # 3. Round checks (Integer type)
    if 'round' in cleaned_df.columns:
        cleaned_df['round'] = pd.to_numeric(cleaned_df['round'], errors='coerce').fillna(-1).astype(int) # Use -1 for failed conversion if needed, or drop rows

    # 4. Name checks (String type)
    if 'name' in cleaned_df.columns:
        cleaned_df['name'] = cleaned_df['name'].astype(str).replace('nan', pd.NA) # Ensure string type and handle pandas NaN representation

    # 5. Date validation (Valid date field)
    date_col = 'date'
    if date_col in cleaned_df.columns:
        # Attempt to convert to datetime, coercing errors to NaT
        cleaned_df[date_col] = pd.to_datetime(cleaned_df[date_col], errors='coerce')
        # Drop rows where date is invalid (NaT)
        cleaned_df.dropna(subset=[date_col], inplace=True)

    # 6. Time validation and replacement (Empty time -> '00:00:00')
    time_col = 'time'
    if time_col in cleaned_df.columns:
          
        def format_time(row):
            if pd.isna(row['time']): # Check if original value was NaN/None
                return '00:00:00'
            try:
                # If conversion succeeded, extract time component
                dt = pd.to_datetime(row['time'], errors='coerce')
                if pd.isna(dt):
                    return '00:00:00' # Failed to parse, replace
                return dt.strftime('%H:%M:%S')
            except Exception:
                return '00:00:00'

        cleaned_df[time_col] = cleaned_df.apply(format_time, axis=1)


    final_rows = len(cleaned_df)
    print(f"Data cleaning complete. Rows dropped: {initial_rows - final_rows}. Final rows: {final_rows}")
    return cleaned_df

def clean_results_data(df_results: pd.DataFrame) -> pd.DataFrame:
    """
    Applies validation and cleaning rules to the results DataFrame, 
    allowing nulls for position and fastestlap if they are not critical keys.

    Checks include:
    1. resultid is an integer, non-null (rows with null/invalid resultid are dropped).
    2. raceid is an integer, non-null (rows with null/invalid raceid are dropped).
    3. driverid is an integer, non-null (rows with null/invalid driverid are dropped).
    4. position: Kept as is if null, otherwise cast to integer.
    5. fastestlap: Kept as is if null, otherwise standardized time format.
    """
    print("Starting data cleaning and validation for results...")
    initial_rows = len(df_results)
    cleaned_df = df_results.copy()

    # 1. resultid checks (Integer type, non-null)
    if 'resultid' in cleaned_df.columns:
        # Attempt to convert to numeric, coercing errors to NaN
        cleaned_df['resultid'] = pd.to_numeric(cleaned_df['resultid'], errors='coerce')
        # Drop rows where resultid is NaN (null or non-convertible)
        cleaned_df.dropna(subset=['resultid'], inplace=True)
        # Convert to integer after dropping NaNs
        cleaned_df['resultid'] = cleaned_df['resultid'].astype(int)

    # 2. raceid checks (Integer type, non-null)
    if 'raceid' in cleaned_df.columns:
        # Attempt to convert to numeric, coercing errors to NaN
        cleaned_df['raceid'] = pd.to_numeric(cleaned_df['raceid'], errors='coerce')
        # Drop rows where raceid is NaN (null or non-convertible)
        cleaned_df.dropna(subset=['raceid'], inplace=True)
        # Convert to integer after dropping NaNs
        cleaned_df['raceid'] = cleaned_df['raceid'].astype(int)

    # 3. driverid checks (Integer type, non-null)
    if 'driverid' in cleaned_df.columns:
        # Attempt to convert to numeric, coercing errors to NaN
        cleaned_df['driverid'] = pd.to_numeric(cleaned_df['driverid'], errors='coerce')
        # Drop rows where driverid is NaN (null or non-convertible)
        cleaned_df.dropna(subset=['driverid'], inplace=True)
        # Convert to integer after dropping NaNs
        cleaned_df['driverid'] = cleaned_df['driverid'].astype(int)

    # 4. Position checks (Integer type, null allowed)
    if 'position' in cleaned_df.columns:
        # Coerce to numeric, keeping NaN for nulls
        cleaned_df['position'] = pd.to_numeric(cleaned_df['position'], errors='coerce')

    # 5. Fastestlap validation and replacement (Null kept as null)
    time_col = 'fastestlap'
    if time_col in cleaned_df.columns:
        # Attempt to convert to datetime objects first, then extract time component
        cleaned_df[f'{time_col}_dt'] = pd.to_datetime(cleaned_df[time_col], errors='coerce')
        
        def format_time(row):
            if pd.isna(row['fastestlap']): # Check if original value was NaN/None
                return None # Keep nulls as None 
            try:
                # If conversion succeeded, extract time component
                dt = pd.to_datetime(row['fastestlap'], errors='coerce')
                if pd.isna(dt):
                    return None # Failed to parse, keep null
                return dt.strftime('%H:%M:%S')

            except Exception:
                return None # Keep null on error

        cleaned_df[time_col] = cleaned_df.apply(format_time, axis=1)


    final_rows = len(cleaned_df)
    print(f"Data cleaning complete. Rows dropped: {initial_rows - final_rows}. Final rows: {final_rows}")
    return cleaned_df

def join_cleaned_data(df_races: pd.DataFrame, df_results: pd.DataFrame) -> pd.DataFrame:
    """
    Joins the cleaned races and results DataFrames on the common 'raceid' key.

    Uses an outer merge to ensure records present in either dataset are retained.
    """
    print("Starting join ")
    # Use an outer merge to keep all records present in either dataframe
    merged_df = pd.merge(
        df_races, 
        df_results, 
        on='raceId', 
        how='outer',
        suffixes=('_race', '_result') # Suffixes help distinguish columns with the same name
    )
    print("Join operation complete.")
    return merged_df

def aggregate_best_results(df_merged: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates the merged DataFrame to find the best race performance for each race, 
    calculating minimum fastest lap time across all entries for a given race ID.
    """
    print("Starting aggregations")
    
    # 1. Group by the unique race identifier (raceId) to find min time per race.
    # We use 'raceId' as the grouping key since it is the primary link between datasets.
    grouped = df_merged.groupby('raceId')


    # 2. Calculate the minimum fastest lap time for each group
    min_fastest_lap = grouped['fastestLapTime'].min().reset_index()
    min_fastest_lap.rename(columns={'fastestLapTime': 'Race Fastest Lap'}, inplace=True)

    # 3. Determine the winning driver and race details for the minimum time record
    # We filter the original merged DF to find the row that corresponds to this minimum lap time,
    # AND where position was 1 (as per previous logic).
    winner_df  = df_merged[df_merged['position'] == 1]

   #4. Create base fo Race ID 
    df_merged['date_time'] =  pd.to_datetime(df_merged["date"].astype(str) + " " + df_merged["time"].astype(str))
    base_df = df_merged[['raceId', 'name', 'round', 'date_time']].drop_duplicates().reset_index(drop=True) 

    
    pre_report = pd.merge(
        base_df,
        winner_df[['raceId', 'driverId']],
        on='raceId',
        how='left'
    )

    final_report = pd.merge(
        pre_report[['raceId', 'name', 'round', 'date_time', 'driverId']],
        min_fastest_lap,
        on='raceId',
        how='left'
    )

    # 4. Final cleanup and renaming to match requested output schema
    final_report = final_report.rename(columns={
        'name': 'Race Name',
        'round': 'Race Round',
        'date_time': 'Race Date',
        'driverId': 'Race Winning DriverID'
    })

    # 5. Final selection of columns and ensuring correct types (optional, but good practice)
   
    final_report['Race Date'] = pd.to_datetime(final_report['Race Date']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')# Ensure date is in ISO format for JSON output
    final_report['Race Winning DriverID'] = final_report['Race Winning DriverID'].astype('Int64') # Ensure integer type
    final_report = final_report[['Race Name', 'Race Round', 'Race Date', 'Race Winning DriverID', 'Race Fastest Lap']]
    
    print("Aggregation complete.")
    return final_report

def write_final_report(df_report: pd.DataFrame, OUTPUT_JSON: str) -> None:
    """ Writes the final aggregated report DataFrame into separate JSON files, 
    one file per year, following the 'stats_{year}.json' naming convention.

    """
    if df_report.empty:
        print("Cannot write report: Input DataFrame is empty.")
        return
    # Ensure 'Race Date' column is in datetime format to extract the year reliably
    try:
        df_report['Race Date'] = pd.to_datetime(df_report['Race Date'])
    except Exception as e:
        print(f"Error converting 'Race Date' for file writing: {e}. Skipping file write.")
        return
    # Get all unique years present in the report
    unique_years = sorted(df_report['Race Date'].dt.year.unique())
    print("\n--- Starting Final Report Writing ---")
    for year in unique_years:
        # Filter the DataFrame for the current year
        yearly_data = df_report[df_report['Race Date'].dt.year == year].copy()
        # Create the filename following the convention stats_{year}.json
        filename = f"stats_{year}.json"
        output_path = os.path.join(OUTPUT_JSON, filename) 
        try:
            # Write the filtered data to a JSON file
            yearly_data.to_json(output_path, orient='records', indent=4,date_format='iso')
            print(f"Successfully wrote report for year {year} to {output_path}")
        except Exception as e:
            print(f"Failed to write report for year {year} to {output_path}. Error: {e}")
