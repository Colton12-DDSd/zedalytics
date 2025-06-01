# zedalytics_app.py

import streamlit as st
from PIL import Image
from utils.github_data_loader import stream_filtered_race_data  # ✅ your optimized loader

# Optional: Show logo if available
# logo = Image.open("logo.png")
# st.image(logo, width=150)

st.set_page_config(page_title="Zedalytics", layout="wide")
st.title("Zedalytics")

st.markdown("""
> ⚠️ **Data Disclaimer**  
> Race data is streamed from a public GitHub source and may not reflect the full history of ZED Champions.  
> This tool is unofficial and for analytical purposes only.
""")

# --- Search UI ---
st.subheader("🔎 Search for a Horse")
user_input = st.text_input("Enter Horse Name or ID:")

if not user_input:
    st.info("Enter a horse name or ID above to begin.")
    st.stop()

# --- Stream and Filter Data ---
with st.spinner("Searching races..."):
    horse_df, all_finish_times = stream_filtered_race_data(user_input)

# --- Handle No Results ---
if horse_df.empty:
    st.warning("No races found for that horse.")
    st.stop()

# --- Show Preview ---
st.success(f"✅ Found {len(horse_df)} races for `{user_input}`.")
st.dataframe(horse_df.head(10))

# --- Optional: Show summary stats later
# st.markdown("### Performance Summary Coming Soon...")
