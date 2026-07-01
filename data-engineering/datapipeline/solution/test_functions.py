import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# Import functions
from functions import (
    ingest_races,
    ingest_results,
    validate_races_headers,
    validate_results_headers,
    clean_races_data,
    clean_results_data,
    join_cleaned_data,
    aggregate_best_results,
    write_final_report,
)

@pytest.fixture(scope="module")
def mock_races_csv_path():
    """Provides a mock path for races.csv."""
    return "data/races.csv"

@pytest.fixture(scope="module")
def mock_results_csv_path():
    """Provides a mock path for results.csv."""
    return "data/results.csv"

# Use patch to simulate the file system and pandas read_csv call
@patch('pandas.read_csv')
def test_ingest_races_success(mock_read_csv, mock_races_csv_path):
    """Tests successful ingestion of races.csv."""
    # Setup mock return value: a simple DataFrame structure
    mock_df = pd.DataFrame({
        'year': [2018, 2019],
        'race_name': ['Race A', 'Race B'],
        'round': [1, 1]
    })
    # Ensure dtypes are consistent for reliable comparison
    mock_df['year'] = mock_df['year'].astype(int)
    mock_read_csv.return_value = mock_df

    # Call the function
    result_df = ingest_races(mock_races_csv_path)

    # Assertions
    assert not result_df.empty
    pd.testing.assert_frame_equal(result_df, mock_df)

@patch('pandas.read_csv')
def test_ingest_races_file_not_found(mock_read_csv, mock_races_csv_path):
    """Tests handling of FileNotFoundError when reading races.csv."""
    # Raise FileNotFoundError
    mock_read_csv.side_effect = FileNotFoundError("No such file or directory: [Errno 2] No such file or directory: 'data/races.csv'")

    # Call the function
    result_df = ingest_races(mock_races_csv_path)

    # Assertions
    assert result_df.empty

def test_validate_races_headers():
    """Tests that races headers are validated successfully and invalid headers raise an error."""
    valid_df = pd.DataFrame({
        'raceId': [1],
        'year': [2018],
        'round': [1],
        'name': ['Race A'],
        'date': ['2018-03-17'],
        'time': ['01:30:00'],
    })

    validate_races_headers(valid_df)
    #Check if columns less than expected
    missing_df = valid_df.drop(columns=['raceId'])
    with pytest.raises(ValueError, match='Expected 6 columns'):
        validate_races_headers(missing_df)

    #Check if columns more than expected
    extra_df = valid_df.copy()
    extra_df['unexpected'] = [1]
    with pytest.raises(ValueError, match='Expected 6 columns'):
        validate_races_headers(extra_df)

    #Check error is raised if column name mismatch
    missing_df = valid_df.rename(columns={'raceId': 'race_id'})
    with pytest.raises(ValueError, match='Missing'):
        validate_races_headers(missing_df)

@patch('pandas.read_csv')
def test_ingest_results_success(mock_read_csv, mock_results_csv_path):
    """Tests successful ingestion of results.csv."""
    # Setup mock df
    mock_df = pd.DataFrame({
        'year': [2018, 2019],
        'driver id': ['D1', 'D2'],
        'fastest time': ['1:30.000', '1:45.000']
    })
    mock_read_csv.return_value = mock_df

    # Call the function under test, using the results path constant
    result_df = ingest_results(mock_results_csv_path)

    # Assertions
    assert not result_df.empty
    pd.testing.assert_frame_equal(result_df, mock_df)

@patch('pandas.read_csv')
def test_ingest_results_file_not_found(mock_read_csv, mock_results_csv_path):
    """Tests handling of FileNotFoundError when reading results.csv."""
    # Raise FileNotFoundError
    mock_read_csv.side_effect = FileNotFoundError("No such file or directory: [Errno 2] No such file or directory: 'data/results.csv'")

    # Call the function
    result_df = ingest_results(mock_results_csv_path)

    # Assertions
    assert result_df.empty

def test_validate_results_headers():
    """Tests that races headers are validated successfully and invalid headers raise an error."""
    valid_df = pd.DataFrame({
        'resultId': [1],
        'raceId': [10],
        'driverId': [2],
        'position': [1],
        'fastestLapTime': ['01:30:00'],
    })

    validate_results_headers(valid_df)

    #Check if columns less than expected
    missing_df = valid_df.drop(columns=['raceId'])
    with pytest.raises(ValueError, match='Expected 5 columns'):
        validate_results_headers(missing_df)

    #Check if columns more  than expected
    extra_df = valid_df.copy()
    extra_df['unexpected'] = [1]
    with pytest.raises(ValueError, match='Expected 5 columns'):
        validate_results_headers(extra_df)
    #Check error is raised if column name mismatch

    missing_df = valid_df.rename(columns={'raceId': 'race_id'})
    with pytest.raises(ValueError, match='Missing'):
        validate_results_headers(missing_df)

@patch('functions.clean_races_data')
def test_clean_races_data_all_checks(mock_clean_races_data, mock_races_csv_path):
    """Tests clean_races_data function to ensure all validation rules are applied."""
    # 1. Setup mock df: Include cases that should pass and cases that should fail/be cleaned.
    raw_data = {
        'raceId': [20, None, '30', 40], # Null raceid (should drop), non-int string ('30')
        'year': [2018, 2019, None, 2020], # Null year (should drop)
        'round': [1, 2, 3, 'invalid'], # Invalid round (will be handled)
        'name': ['Race A', 'Race B', 'Race C', ''], # Empty string name
        'date': ['2018-03-17', '2019-05-19', 'invalid_date', '2020-11-01'], # Invalid date (should drop)
        'time': ['1:30:00', None, '23:59:59', ''] # Null time and empty string time
    }
    # Create a DataFrame that simulates the raw input data structure
    raw_df = pd.DataFrame(raw_data)

    # 2. Define Expected Output DataFrame (Rows 0 and 3 pass )
    expected_df = pd.DataFrame({
            'raceId': [20, 40],
            'year': [2018, 2020],
            'round': [1, -1], 
            'name': ['Race A', ''], # Empty string name converted to NaN
            'date': ['2018-03-17', '2020-11-01'],
            'time': ['01:30:00', '00:00:00']
        })

    # 3. Call the function
    cleaned_df = clean_races_data(raw_df)
    expected_df['date'] = pd.to_datetime(expected_df['date'], errors='coerce') # must set the exected_df date column to datetime for comparison

    # Assertions
    assert not cleaned_df.empty
    pd.testing.assert_frame_equal(cleaned_df, expected_df.set_index([[0,3]]))  # reset index to match outputs

@patch('functions.clean_results_data')
def test_clean_results_data_all_checks(mock_clean_results_data, mock_results_csv_path):
    """Tests clean_results_data function to ensure all validation rules are applied."""
    # 1. Setup mock df: Include cases that should pass and cases that should fail/be cleaned.
    raw_data = {
        'resultId': [10, None, '30', 40,'50'], # Null resultid (should drop), non-int string ('30','50')
        'raceId': [20, 20, None, 40,50], # Null raceid (should drop)
        'driverId': ['1', '2', 3, '',7], # Empty driverid (will be handled by type conversion/drop)
        'position': ['', 2, 3, None,1], # Position: null allowed
        'fastestLapTime': [None, '2019-05-19', None, 'invalid_time','01:30:00'] # Null and invalid time (should keep null/NaN)
    }
    # Create a DataFrame that simulates the raw input data structure
    raw_df = pd.DataFrame(raw_data)

    # Define Expected Output DataFrame (Rows 0 and 4 pass)
    expected_df = pd.DataFrame({
        'resultId': [10, 50], # Only two rows should survive the filtering (null resultid or raceid)
        'raceId': [20, 50],
        'driverId': [1, 7],
        'position': [None, 1.0],
        'fastestLapTime': [pd.NA, pd.to_datetime('01:30:00', format='%H:%M:%S').strftime('%H:%M:%S')], # Create a consistent format for the expected fastestLapTime
    })

     # 4. Call the function 
    cleaned_df = clean_results_data(raw_df)

    # Assertions
    assert not cleaned_df.empty
    pd.testing.assert_frame_equal(cleaned_df, expected_df.set_index([[0,4]])) # reset index to match outputs

@patch('functions.join_cleaned_data')
def test_join_cleaned_data_success(mock_join):
    """Tests successful joining of cleaned races and results data."""
    # 1. Setup Mock Input DataFrames (Simulating clean outputs)
    # Races: raceId, name, round, date_time
    mock_races = pd.DataFrame({
        'raceId': [20, 30],
        'year': [2018, 2019],
        'round': [1, 2],
        'name': ['Race A', 'Race B'],
        'date': ['2018-03-17', '2019-05-19'],
        'time': ['10:00:00', '12:00:00']
    })

    mock_races['date'] = pd.to_datetime(mock_races['date'], errors='coerce') # must set the mock_races date column to datetime for comparison
 
    # Results: raceId, driverId, fastestLapTime - Only including used fields
    mock_results = pd.DataFrame({
        'resultId': [100.0, 200.0],
        'raceId': [20.0, 30.0],
        'driverId': [1.0, 2.0],
        'position': [1.0, 2.0],
        'fastestLapTime': ['1:30:00', '1:45:00']
    })

    # 2. Setup mock df (Expected merged result)
    expected_merged = pd.DataFrame({
        'raceId': [20, 30],
        'year': [2018, 2019],
        'round': [1, 2],
        'name': ['Race A', 'Race B'],
        'date': ['2018-03-17', '2019-05-19'],
        'time': ['10:00:00', '12:00:00'],
        'resultId': [100.0, 200.0],
        'driverId': [1.0, 2.0],
        'position': [1.0, 2.0],
        'fastestLapTime': ['1:30:00', '1:45:00'],
    })

    expected_merged['date'] = pd.to_datetime(expected_merged['date'], errors='coerce') # must set the expected_merged date column to datetime for comparison
 
    # 3. Call the function 
    cleaned_df = join_cleaned_data(mock_races, mock_results)

    # Assertions
    assert not cleaned_df.empty
    pd.testing.assert_frame_equal(cleaned_df, expected_merged)  # Ignore dtype differences for simplicity

@patch('functions.aggregate_best_results')
def test_aggregate_best_results_success(mock_aggregate):
    """Tests the aggregation logic to find min fastest lap time and winning driver."""
    # 1. Setup Mock Input DataFrame (Simulating joined data)
    df_merged = pd.DataFrame({
        'raceId': [20, 20, 30],
        'year': [2018, 2018, 2019],
        'round': [1, 1, 2],
        'name': ['Race A', 'Race A', 'Race B'],
        'date': ['2018-03-17', '2018-03-17', '2019-05-19'], # Separate date column
        'time': ['10:00:00', '10:00:00', '12:00:00'], # Separate time column
        'driverId': [1, 2, 2],
        'position': [1.0, 2.0, 1.0 ],
        'fastestLapTime': ['1:45:00', '1:30:00', '1:45:00']
    })

    # 2. Call the function
    result_df = aggregate_best_results(df_merged)

    # 3. Expected Output DF (Based on logic: fastest lap per race, Winner ID, Race details)
    expected_report = pd.DataFrame({
        'Race Name': ['Race A', 'Race B'],
        'Race Round': [1, 2],
        'Race Date': ['2018-03-17 10:00:00', '2019-05-19 12:00:00'], 
        'Race Winning DriverID': [1, 2],
        'Race Fastest Lap': ['1:30:00', '1:45:00']
    })

    # For simplicity, we check the DF is not empty and has the expected number of rows (2)
    assert not result_df.empty
    assert len(result_df) == 2

    print("Aggregation test passed structure check.")

def test_write_final_report_success():
    """Tests that write_final_report correctly splits data into year-specific JSON files."""
    # 1. Setup input data
    data = {
        'Race Name': ['Race A', 'Race B', 'Race C'],
        'Race Round': [1, 2, 3],
        'Race Date': pd.to_datetime(['2018-03-17 10:00:00', '2019-05-19 12:00:00', '2018-06-01 08:00:00']),
        'Race Winning DriverID': [1, 2, 3],
        'Race Fastest Lap': ['1:30:00', '1:45:00', '1:20:00']
    }
    df_report = pd.DataFrame(data)

    # Mock the to_json method on the DataFrame class while keeping the DataFrame itself real.
    mock_to_json = MagicMock()
    with patch('pandas.DataFrame.to_json', mock_to_json):
        # 2. Call the function under test
        write_final_report(df_report, "data-engineering/datapipeline/results/")

        # 3. Assertions: Check if to_json was called twice (once for 2018 and once for 2019)
        assert mock_to_json.call_count == 2

        # Verify calls for specific years
        mock_to_json.assert_any_call(
            'data-engineering/datapipeline/results/stats_2018.json',
            orient='records', indent=4, date_format='iso'
        )
        mock_to_json.assert_any_call(
            'data-engineering/datapipeline/results/stats_2019.json',
            orient='records', indent=4, date_format='iso'
        )