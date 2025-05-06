# horse_detail.py

import streamlit as st

def render_horse_detail(horse_id, df, show_horse_dashboard):
    horse_df = df[df['horse_id'] == horse_id].sort_values('race_date')

    if horse_df.empty:
        st.error("No data found for this horse.")
        return

    st.title(f"📊 Detailed Stats for {horse_df['horse_name'].iloc[0]}")
    st.button("🔙 Back to Horses", on_click=lambda: st.experimental_set_query_params())
    show_horse_dashboard(horse_df, df)
