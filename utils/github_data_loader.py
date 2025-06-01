import pandas as pd
import requests
from io import StringIO

def load_combined_race_data():
    """
    Loads and concatenates all race data CSV files from the root of the 
    'zed-champions-race-data' GitHub repository.

    Returns:
        pd.DataFrame: Combined DataFrame of all race data.
    """
    owner = "myblood-tempest"
    repo = "zed-champions-race-data"
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        files = response.json()

        # Match CSVs with "race_data" and "chunk" in filename
        csv_files = [file for file in files if file["name"].endswith(".csv") and "race_data" in file["name"] and "chunk" in file["name"]]

        if not csv_files:
            return pd.DataFrame()

        combined_dfs = []

        for file in csv_files:
            try:
                file_response = requests.get(file["download_url"])
                file_response.raise_for_status()
                df = pd.read_csv(StringIO(file_response.text))
                combined_dfs.append(df)
            except:
                continue  # Silently skip bad files

        if not combined_dfs:
            return pd.DataFrame()

        final_df = pd.concat(combined_dfs, ignore_index=True)

        if "race_date" in final_df.columns:
            final_df["race_date"] = pd.to_datetime(final_df["race_date"], errors="coerce")

        return final_df

    except:
        return pd.DataFrame()
