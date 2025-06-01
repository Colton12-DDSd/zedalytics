import pandas as pd
import requests
from io import StringIO

def load_all_race_data():
    """
    Loads and concatenates all race data CSV files from the 'data_chunks' folder
    of the 'zed-champions-race-data' GitHub repository.
    
    Returns:
        pd.DataFrame: Combined DataFrame of all race data.
    """
    # GitHub repository info
    owner = "myblood-tempest"
    repo = "zed-champions-race-data"
    folder = "data_chunks"

    # GitHub API endpoint to list files in the folder
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder}"

    try:
        # Get list of files in the folder
        response = requests.get(api_url)
        response.raise_for_status()
        files = response.json()

        # Filter for .csv files
        csv_files = [file for file in files if file['name'].endswith('.csv')]

        if not csv_files:
            print("⚠️ No CSV files found in the repository folder.")
            return pd.DataFrame()

        combined_dfs = []

        # Download and load each CSV file
        for file in csv_files:
            try:
                file_response = requests.get(file["download_url"])
                file_response.raise_for_status()
                df = pd.read_csv(StringIO(file_response.text))
                combined_dfs.append(df)
            except Exception as e:
                print(f"❌ Error reading {file['name']}: {e}")

        if not combined_dfs:
            print("⚠️ No data could be loaded from any files.")
            return pd.DataFrame()

        # Combine all into one DataFrame
        final_df = pd.concat(combined_dfs, ignore_index=True)

        # Convert race_date column to datetime if present
        if "race_date" in final_df.columns:
            final_df["race_date"] = pd.to_datetime(final_df["race_date"], errors="coerce")

        return final_df

    except Exception as e:
        print(f"❌ Failed to fetch file list from GitHub: {e}")
        return pd.DataFrame()
