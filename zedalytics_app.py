# zedalytics_app.py

import streamlit as st
from PIL import Image

# Optional: Add logo if you have a local file
# logo = Image.open("logo.png")
# st.image(logo, width=150)

st.set_page_config(page_title="Zedalytics", layout="wide")

st.title("Zedalytics")

st.markdown("""
> ⚠️ **Data Disclaimer**  
> Race data is streamed from a public GitHub source and may not reflect the full history of ZED Champions.  
> This tool is unofficial and for analytical purposes only.
""")

# Search Bar
st.subheader("🔎 Search for a Horse")
user_input = st.text_input("Enter Horse Name or ID:")

if not user_input:
    st.info("Enter a horse name or ID above to begin.")
    st.stop()

# Placeholder response
st.success(f"Searching for `{user_input}`... (data loading logic coming soon)")
