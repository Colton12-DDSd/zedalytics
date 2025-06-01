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

    # Files are in the root of the repo
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

    try:
        print("🔍 Fetching file list from GitHub...")
        response = requests.get(api_url)
        response.raise_for_status()
        files = response.json()

        # Filter for chunked race_data CSVs
        csv_files = [file for file in files if file["name"].endswith(".csv") and "race_data" in file["name"] and "chunk" in file["name"]]

        print(f"📄 Found {len(csv_files)} CSV file(s) in root directory.")
        if not csv_files:
            return pd.DataFrame()

        combined_dfs = []

        for file in csv_files:
            print(f"⬇️ Downloading {file['name']}...")
            try:
                file_response = requests.get(file["download_url"])
                file_response.raise_for_status()
                df = pd.read_csv(StringIO(file_response.text))
                combined_dfs.append(df)
                print(f"✅ Loaded {len(df)} rows from {file['name']}")
            except Exception as e:
                print(f"❌ Error reading {file['name']}: {e}")

        if not combined_dfs:
            print("⚠️ No data loaded from any files.")
            return pd.DataFrame()

        final_df = pd.concat(combined_dfs, ignore_index=True)

        if "race_date" in final_df.columns:
            final_df["race_date"] = pd.to_datetime(final_df["race_date"], errors="coerce")
            print("📅 Converted 'race_date' column to datetime.")

        print(f"\n🧩 Final DataFrame has {len(final_df)} rows and {len(final_df.columns)} columns.")
        print("\n📊 Sample rows:")
        print(final_df.head(10))

        return final_df

    except Exception as e:
        print(f"❌ Failed to fetch from GitHub: {e}")
        return pd.DataFrame()
