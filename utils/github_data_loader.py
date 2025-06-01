import pandas as pd
import requests
from io import StringIO

OWNER = "myblood-tempest"
REPO = "zed-champions-race-data"
API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"


def stream_filtered_race_data(horse_query):
    """
    Efficiently searches and filters race data from large GitHub CSVs
    for a specific horse name or ID using chunked loading.

    Args:
        horse_query (str): Horse name or ID (case-insensitive)

    Returns:
        pd.DataFrame: Filtered race data
        list: List of all finish times (for plotting if needed)
    """
    try:
        # Get list of all CSV files in the GitHub repo
        response = requests.get(API_URL)
        response.raise_for_status()
        files = response.json()

        # Filter race data files
        csv_files = [
            file for file in files
            if file["name"].endswith(".csv")
            and "race_data" in file["name"]
            and "chunk" in file["name"]
        ]

        if not csv_files:
            return pd.DataFrame(), []

        horse_query = horse_query.lower()
        filtered_rows = []
        all_finish_times = []

        for file in csv_files:
            file_url = file["download_url"]
            file_response = requests.get(file_url)
            file_response.raise_for_status()

            # Use chunks to avoid memory blowups
            for chunk in pd.read_csv(StringIO(file_response.text), chunksize=10000):
                if 'horse_name' in chunk.columns and 'horse_id' in chunk.columns:
                    match = chunk[
                        (chunk['horse_name'].str.lower() == horse_query) |
                        (chunk['horse_id'].str.lower() == horse_query)
                    ]
                    if not match.empty:
                        filtered_rows.append(match)
                if 'finish_time' in chunk.columns:
                    all_finish_times.extend(chunk['finish_time'].dropna().tolist())

        if not filtered_rows:
            return pd.DataFrame(), all_finish_times

        result_df = pd.concat(filtered_rows, ignore_index=True)

        if "race_date" in result_df.columns:
            result_df["race_date"] = pd.to_datetime(result_df["race_date"], errors="coerce")

        return result_df, all_finish_times

    except Exception as e:
        print(f"❌ stream_filtered_race_data() failed: {e}")
        return pd.DataFrame(), []
        
def load_recent_finish_times(limit=500):
    import requests
    from io import StringIO
    import pandas as pd

    owner = "myblood-tempest"
    repo = "zed-champions-race-data"
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        files = response.json()

        csv_files = sorted(
            [file for file in files if file["name"].endswith(".csv") and "race_data" in file["name"]],
            key=lambda x: x["name"],
            reverse=True  # recent first
        )

        finish_times = []

        for file in csv_files:
            file_response = requests.get(file["download_url"])
            file_response.raise_for_status()

            # Efficient column load with chunking
            for chunk in pd.read_csv(StringIO(file_response.text), usecols=["finish_time"], chunksize=5000):
                finish_times.extend(chunk["finish_time"].dropna().tolist())
                if len(finish_times) >= limit:
                    return finish_times[:limit]

        return finish_times[:limit]

    except Exception as e:
        print(f"❌ Failed to load recent finish times: {e}")
        return []

