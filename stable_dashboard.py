import streamlit as st
import pandas as pd

# URL to race data
CSV_URL = 'https://raw.githubusercontent.com/myblood-tempest/zed-champions-race-data/main/race_results.csv'

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(CSV_URL)
    df['race_date'] = pd.to_datetime(df['race_date'], errors='coerce')
    return df

def main():
    st.set_page_config(page_title="Stable Dashboard", layout="wide")

    # --- Top-Aligned Logo ---
    st.markdown(
        """
        <div style="text-align: left; margin-top: -1rem; margin-bottom: 1rem;">
            <img src="https://raw.githubusercontent.com/Colton12-DDSd/zedalytics/main/ZEDalytics_logo_long.png" alt="ZEDalytics Logo" style="height: 100px;">
        </div>
        """,
        unsafe_allow_html=True
    )



    # --- Load Data ---
    df = load_data()

    # --- Stable Search ---
    st.subheader("🔍 Search for a Stable")
    stable_input = st.text_input("Enter Stable Name (case-insensitive):")

    if not stable_input:
        st.info("Please enter a stable name to begin.")
        return

    stable_df = df[df['stable_name'].str.lower() == stable_input.strip().lower()]

    if stable_df.empty:
        st.warning("No data found for that stable.")
        return

    # --- Stable Summary Metrics ---
    st.subheader(f"📊 Overview for Stable: `{stable_input}`")

    total_races = len(stable_df)
    total_earnings = stable_df['earnings'].sum()
    total_profit = stable_df['profit_loss'].sum()
    total_wins = (stable_df['finish_position'] == 1).sum()
    win_pct = (stable_df['finish_position'] == 1).mean() * 100

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Races", total_races)
    col2.metric("Total Wins", total_wins)
    col3.metric("Win %", f"{win_pct:.2f}%")

    col4, col5 = st.columns(2)
    col4.metric("Total Earnings", f"{int(total_earnings):,} ZED")
    col5.metric("Total Profit", f"{int(total_profit):,} ZED")

    st.divider()

    # --- Coming Next ---
    st.info("✅ Coming next: Horse roster, augment effectiveness, race history, and performance charts.")

if __name__ == "__main__":
    main()
