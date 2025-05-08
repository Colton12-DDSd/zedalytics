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
            <img src="https://raw.githubusercontent.com/Colton12-DDSd/zedalytics/main/ZEDalytics_logo_long.png" alt="ZEDalytics Logo" style="height: 90px;">
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Load Data ---
    df = load_data()

    # --- Handle stable query param ---
    query_params = st.query_params
    if "stable" in query_params:
        stable_name = query_params["stable"]
        stable_df = df[df['stable_name'].str.lower() == stable_name.lower()]

        if stable_df.empty:
            st.warning(f"No data found for stable '{stable_name}'.")
            return

        st.markdown(
            f"""
            <h1 style='font-size: 3rem; font-weight: 700; margin-bottom: 1rem;'>{stable_name}</h1>
            """,
            unsafe_allow_html=True
        )


        # Optional: back to search
        if st.button("🔙 Back to Search"):
            st.query_params.clear()
            st.rerun()

        # Show list of horses
        horse_list = stable_df[['horse_name', 'horse_id']].drop_duplicates().sort_values('horse_name')
        st.subheader("📋 Horses in this Stable")
        
        cols = st.columns(4)
        for idx, (_, row) in enumerate(horse_list.iterrows()):
            with cols[idx % 4]:
                st.markdown(
                    f"""
                    <div style='
                        background-color: #1e1e1e;
                        padding: 1rem;
                        border-radius: 10px;
                        margin-bottom: 1rem;
                        box-shadow: 0 0 5px rgba(255,255,255,0.1);
                    '>
                        <h4 style='margin-bottom: 0.5rem;'>{row['horse_name']}</h4>
                        <p style='font-size: 0.85rem; color: gray;'>ID: {row['horse_id']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        return  # don't show the search again

    # --- Stable Search ---
    st.subheader("🔍 Search for a Stable")
    stable_input = st.text_input("Enter Stable Name (case-insensitive):")

    if stable_input:
        match = df[df['stable_name'].str.lower() == stable_input.strip().lower()]
        if match.empty:
            st.warning("No data found for that stable.")
        else:
            # Redirect using query param
            st.query_params["stable"] = stable_input.strip()
            st.rerun()

if __name__ == "__main__":
    main()
