import pandas as pd
import os
from datetime import datetime

def ingest_races(races_csv_path: str) -> pd.DataFrame:
    """ Ingests data from the races CSV file into a Pandas DataFrame. """
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
    
def validate_races_headers(df_races: pd.DataFrame) -> None:
    """Validate that the ingested races data contains the expected columns."""
    required_headers = ['raceId', 'year', 'round', 'name', 'date', 'time']
    missing_headers = [header for header in required_headers if header not in df_races.columns]
    if missing_headers:
        raise ValueError(f"Missing required races headers: {missing_headers}")
    

def ingest_results(results_csv_path: str) -> pd.DataFrame:
    """Ingests data from the results CSV file into a Pandas DataFrame."""
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

def validate_results_headers(df_results: pd.DataFrame) -> None:
    """Validate that the ingested results data contains the expected columns."""
    required_headers = ['resultId', 'raceId', 'driverId', 'position', 'fastestLapTime']
    missing_headers = [header for header in required_headers if header not in df_results.columns]
    if missing_headers:
        raise ValueError(f"Missing required results headers: {missing_headers}")

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
    print("Running data cleaning and validation for races...")
    initial_rows = len(df_races)
    cleaned_df = df_races.copy()

    # 1. raceid checks (Integer type, non-null)
    if 'raceId' in cleaned_df.columns:
        # Attempt to convert to numeric replacing errors with null
        cleaned_df['raceId'] = pd.to_numeric(cleaned_df['raceId'], errors='coerce')
        # Drop rows where raceid is null
        cleaned_df= cleaned_df.dropna(subset=['raceId'])
        # Convert to integer after dropping nulls
        cleaned_df['raceId'] = cleaned_df['raceId'].astype(int)

    # 2. Year checks (Integer type, non-null)
    if 'year' in cleaned_df.columns:
        # Attempt to convert to numeric replacing errors with null
        cleaned_df['year'] = pd.to_numeric(cleaned_df['year'], errors='coerce')
        # Drop rows where year is null
        cleaned_df.dropna(subset=['year'], inplace=True)
        # Convert to integer after dropping nulls
        cleaned_df['year'] = cleaned_df['year'].astype(int)

    # 3. Round checks (Integer type)
    if 'round' in cleaned_df.columns:
        cleaned_df['round'] = pd.to_numeric(cleaned_df['round'], errors='coerce').fillna(-1).astype(int) # Use -1 for failed conversion if needed, or drop rows

    # 4. Name checks (String type)
    if 'name' in cleaned_df.columns:
        cleaned_df['name'] = cleaned_df['name'].astype(str).replace('nan', pd.NA) # Pandas NA

    # 5. Date validation (Valid date field)
    date_col = 'date'
    if date_col in cleaned_df.columns:
        # Attempt to convert to datetime
        cleaned_df[date_col] = pd.to_datetime(cleaned_df[date_col], errors='coerce')
        # Drop rows where date is invalid 
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
    print("Running data cleaning and validation for results...")
    initial_rows = len(df_results)
    cleaned_df = df_results.copy()

    # 1. resultid checks (Integer type, non-null)
    if 'resultId' in cleaned_df.columns:
        # Attempt to convert to numeric replacing errors with null
        cleaned_df['resultId'] = pd.to_numeric(cleaned_df['resultId'], errors='coerce')
        # Drop rows where resultid is null
        cleaned_df.dropna(subset=['resultId'], inplace=True)
        # Convert to integer after dropping nulls
        cleaned_df['resultId'] = cleaned_df['resultId'].astype(int)

    # 2. raceid checks (Integer type, non-null)
    if 'raceId' in cleaned_df.columns:
        # Attempt to convert to numeric replacing errors with null
        cleaned_df['raceId'] = pd.to_numeric(cleaned_df['raceId'], errors='coerce')
        # Drop rows where resultid is null
        cleaned_df.dropna(subset=['raceId'], inplace=True)
        # Convert to integer after dropping nulls
        cleaned_df['raceId'] = cleaned_df['raceId'].astype(int)

    # 3. driverid checks (Integer type, non-null)
    if 'driverId' in cleaned_df.columns:
        # Attempt to convert to numeric replacing errors with null
        cleaned_df['driverId'] = pd.to_numeric(cleaned_df['driverId'], errors='coerce')
        # Drop rows where driverid is null
        cleaned_df.dropna(subset=['driverId'], inplace=True)
        # Convert to integer after dropping nulls
        cleaned_df['driverId'] = cleaned_df['driverId'].astype(int)

    # 4. Position checks (Integer type, null allowed)
    if 'position' in cleaned_df.columns:
        # Coerce to numeric, keeping  nulls
        cleaned_df['position'] = pd.to_numeric(cleaned_df['position'], errors='coerce')

    # 5. Fastestlap validation and replacement (Null kept as null)
    time_col = 'fastestLapTime'
    if time_col in cleaned_df.columns:
        # Attempt to convert to datetime 
       # cleaned_df[f'{time_col}_dt'] = pd.to_datetime(cleaned_df[time_col], errors='coerce')
        
        def format_time(row):
            if pd.isna(row['fastestLapTime']): # Check if original value was NaN/None
                return None # Keep Nulls
            try:
                # Extract time component
                dt = pd.to_datetime(row['fastestLapTime'], errors='coerce')
                if pd.isna(dt):
                    return None # Keep Nulls
                return dt.strftime('%H:%M:%S')

            except Exception:
                return None # Keep null on error

        cleaned_df[time_col] = cleaned_df.apply(format_time, axis=1)


    final_rows = len(cleaned_df)
    print(f"Data cleaning complete. Rows dropped: {initial_rows - final_rows}. Final rows: {final_rows}")
    return cleaned_df

def join_cleaned_data(df_races: pd.DataFrame, df_results: pd.DataFrame) -> pd.DataFrame:
    """
    Joins the cleaned races and results DataFrames on the join key 'raceid' key.
    Uses an outer merge to ensure records present in either dataset are retained.
    """
    print("Running join operation...")
    # Use an outer merge to keep all records present in either dataframe
    merged_df = pd.merge(
        df_races, 
        df_results, 
        on='raceId', 
        how='outer',
        suffixes=('_race', '_result') 
    )
    print("Join operation complete.")
    return merged_df

def aggregate_best_results(df_merged: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates data to find the race winner for each race 
    Also finds the fastest lap time for each race, regardless of who won
    """
    print("Running aggregations")
    
    # 1. Group by raceId to find min time per race.
    grouped = df_merged.groupby('raceId')

    # 2. Identify the  fastest lap time for each race
    fastest_lap = grouped['fastestLapTime'].min().reset_index()
    fastest_lap.rename(columns={'fastestLapTime': 'Race Fastest Lap'}, inplace=True)

    # 3. Determine the winning driver and race details using position == 1
    winner_df  = df_merged[df_merged['position'] == 1]

   #4. Create base fo Race ID  to ensure all records are kept
    df_merged['date_time'] =  pd.to_datetime(df_merged["date"].astype(str) + " " + df_merged["time"].astype(str))
    base_df = df_merged[['raceId', 'name', 'round', 'date_time']].drop_duplicates().reset_index(drop=True) 

    # Join on the winners information
    pre_report = pd.merge(
        base_df,
        winner_df[['raceId', 'driverId']], # Only keep the raceId and driverId for the winner
        on='raceId',
        how='left'
    )
    # Join on the fastest lap information
    final_report = pd.merge(
        pre_report[['raceId', 'name', 'round', 'date_time', 'driverId']],
        fastest_lap,
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

    # 5. Final check to ensure data types are correct and columns are in the desired order
    final_report['Race Winning DriverID'] = final_report['Race Winning DriverID'].astype('Int64') # Ensure integer type
    final_report['Race Round'] = final_report['Race Round'].astype('Int64') # Ensure integer type
    final_report = final_report[['Race Name', 'Race Round', 'Race Date', 'Race Winning DriverID', 'Race Fastest Lap']]
    
    print("Aggregation complete.")
    return final_report

def write_final_report(df_report: pd.DataFrame, OUTPUT_JSON: str) -> None:
    """ Writes the final aggregated report into separate JSON files, 
    one file per year, following the 'stats_{year}.json' naming convention.
    """
    if df_report.empty:
        print("Cannot write report: Input DataFrame is empty.")
        return
    #Determine unique years in the report for file creation
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
            yearly_data.to_json(output_path, orient='records', indent=4,date_format='iso') # ensure date is output in isoformat
            print(f"Successfully wrote report for year {year} to {output_path}")
        except Exception as e:
            print(f"Failed to write report for year {year} to {output_path}. Error: {e}")
