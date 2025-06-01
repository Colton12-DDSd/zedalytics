import pandas as pd
import requests
from io import StringIO

OWNER = "myblood-tempest"
REPO = "zed-champions-race-data"
API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"


def load_combined_race_data():
    """
    Loads and concatenates all race data CSV files from the GitHub repo.

    Returns:
        pd.DataFrame: Combined DataFrame of all race data.
    """
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        files = response.json()

        csv_files = [file for file in files
                     if file["name"].endswith(".csv")
                     and "race_data" in file["name"]
                     and "chunk" in file["name"]]

        if not csv_files:
            print("⚠️ No CSV files found.")
            return pd.DataFrame()

        combined_dfs = []

        for file in csv_files:
            try:
                file_response = requests.get(file["download_url"])
                file_response.raise_for_status()
                df = pd.read_csv(StringIO(file_response.text))
                combined_dfs.append(df)
            except Exception as e:
                print(f"❌ Error reading {file['name']}: {e}")
                continue

        if not combined_dfs:
            print("⚠️ No data loaded.")
            return pd.DataFrame()

        final_df = pd.concat(combined_dfs, ignore_index=True)

        if "race_date" in final_df.columns:
            final_df["race_date"] = pd.to_datetime(final_df["race_date"], errors="coerce")

        return final_df

    except Exception as e:
        print(f"❌ Failed to load data from GitHub: {e}")
        return pd.DataFrame()


def search_horse_all_files(horse_name):
    """
    Searches for a specific horse name across all race data files.

    Args:
        horse_name (str): The exact name to search for.

    Returns:
        pd.DataFrame: Filtered DataFrame with matching horse_name rows.
    """
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        files = response.json()

        csv_files = [file for file in files
                     if file["name"].endswith(".csv")
                     and "race_data" in file["name"]
                     and "chunk" in file["name"]]

        if not csv_files:
            print("⚠️ No CSV files found.")
            return pd.DataFrame()

        result_df = []

        for file in csv_files:
            try:
                file_response = requests.get(file["download_url"])
                file_response.raise_for_status()
                df = pd.read_csv(StringIO(file_response.text))

                if "horse_name" in df.columns:
                    filtered = df[df["horse_name"].str.lower() == horse_name.lower()]
                    if not filtered.empty:
                        result_df.append(filtered)

            except Exception as e:
                print(f"❌ Error reading {file['name']}: {e}")
                continue

        if not result_df:
            print("⚠️ No matching horses found.")
            return pd.DataFrame()

        final_df = pd.concat(result_df, ignore_index=True)

        if "race_date" in final_df.columns:
            final_df["race_date"] = pd.to_datetime(final_df["race_date"], errors="coerce")

        return final_df

    except Exception as e:
        print(f"❌ Search failed: {e}")
        return pd.DataFrame()
