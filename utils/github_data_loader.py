import pandas as pd
import requests
from io import StringIO

OWNER = "myblood-tempest"
REPO = "zed-champions-race-data"
API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"

def stream_filtered_race_data(search_term):
    """
    Streams each race CSV file from GitHub, filters for the horse name or ID, 
    and returns only matching rows to keep memory use low.
    """
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        files = response.json()

        csv_files = [
            file for file in files
            if file["name"].endswith(".csv") and "race_data" in file["name"] and "chunk" in file["name"]
        ]

        if not csv_files:
            print("⚠️ No CSV files found.")
            return pd.DataFrame(), []

        matches = []
        all_finish_times = []

        for file in csv_files:
            try:
                file_response = requests.get(file["download_url"])
                file_response.raise_for_status()
                df = pd.read_csv(StringIO(file_response.text))

                # Lowercase match for name or ID
                filtered = df[
                    df["horse_name"].str.lower() == search_term.lower()
                    if "horse_name" in df.columns else False
                ] if not search_term.startswith("0x") else df[
                    df["horse_id"].str.lower() == search_term.lower()
                    if "horse_id" in df.columns else False
                ]

                if not filtered.empty:
                    matches.append(filtered)

                # Track all finish times (optional for histogram)
                if "finish_time" in df.columns:
                    all_finish_times.extend(df["finish_time"].dropna().tolist())

            except Exception as e:
                print(f"❌ Skipped {file['name']}: {e}")
                continue

        if not matches:
            return pd.DataFrame(), []

        final_df = pd.concat(matches, ignore_index=True)
        if "race_date" in final_df.columns:
            final_df["race_date"] = pd.to_datetime(final_df["race_date"], errors="coerce")

        return final_df, all_finish_times

    except Exception as e:
        print(f"❌ Search failed: {e}")
        return pd.DataFrame(), []
