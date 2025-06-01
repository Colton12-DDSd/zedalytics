import streamlit as st
from PIL import Image
from utils.github_data_loader import stream_filtered_race_data
from utils.horse_stats import calculate_basic_stats

# --- Page Setup ---
st.set_page_config(page_title="Zedalytics", layout="wide")

# --- Logo (scaled to ~25% width) ---
logo = Image.open("ZEDalytics_logo_long.png")
st.image(logo, width=300)  # Adjust pixel width to fit ~25% of a typical desktop width

# --- Title & Disclaimer ---
st.markdown("""
> ⚠️ **Data Disclaimer**  
> Race data is streamed from a public GitHub source and may not reflect the full history of ZED Champions.  
> This tool is unofficial and for analytical purposes only.
""")

# --- Search Bar ---
st.subheader("🔎 Search for a Horse")
user_input = st.text_input("Enter Horse Name or ID:")

if not user_input:
    st.info("Enter a horse name or ID above to begin.")
    st.stop()

# --- Search & Load ---
with st.spinner("Searching races..."):
    horse_df, all_finish_times = stream_filtered_race_data(user_input)

if horse_df.empty:
    st.warning("No races found for that horse.")
    st.stop()

# --- Stats ---
st.subheader("📊 Performance Summary")
stats = calculate_basic_stats(horse_df)

col1, col2, col3 = st.columns(3)
col1.metric("Total Races", stats["total_races"])
col2.metric("Win %", f"{stats['win_pct']:.2f}%")
col3.metric("Top 3 %", f"{stats['top3_pct']:.2f}%")

col4, col5 = st.columns(2)
col4.metric("Total Earnings", f"{int(stats['earnings']):,} ZED")
col5.metric("Profit / Loss", f"{int(stats['profit']):,} ZED")
