import streamlit as st
import pandas as pd

# You can reuse the same CSV source
CSV_URL = 'https://raw.githubusercontent.com/myblood-tempest/zed-champions-race-data/main/race_results.csv'

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(CSV_URL)
    return df

def main():
    st.set_page_config(page_title="Stable Dashboard", layout="wide")
    st.title("📊 Stable Dashboard (Beta)")
    
    df = load_data()

    st.markdown("""
    Welcome to the **in-development Stable Dashboard**.

    This page will eventually give in-depth stats and analytics for each stable across ZED Champions data.  
    If you're seeing this — the setup works!
    """)

    st.subheader("Preview of Data (First 5 Rows)")
    st.dataframe(df.head())

if __name__ == "__main__":
    main()
