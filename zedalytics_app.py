# zedalytics_app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils.github_data_loader import stream_filtered_race_data
from horse_detail import render_horse_detail

plt.style.use("dark_background")

st.set_page_config(page_title="Zedalytics", layout="wide")
st.title("Zedalytics")

st.markdown("""
> ⚠️ **Data Disclaimer**  
> Race data is streamed from public GitHub and may not reflect the full ZED Champions history.
""")

# Only show search bar
st.subheader("🔎 Search Horse by ID or Name")
user_input = st.text_input("Enter Horse ID or Name:")

if not user_input:
    st.info("Please search for a horse to load race data.")
    st.stop()

with st.spinner("Searching races..."):
    horse_df, all_finish_times = stream_filtered_race_data(user_input)

if horse_df.empty:
    st.warning("No races found for that horse.")
    st.stop()

# Show the dashboard
render_horse_detail(horse_df['horse_id'].iloc[0], horse_df, lambda df, full_df: show_horse_dashboard(df, all_finish_times))


# --- Utility to Display Horse Dashboard ---
def show_horse_dashboard(horse_df, all_finish_times):
    name = horse_df['horse_name'].iloc[0]
    stable_name = horse_df.get('stable_name', ["Unknown"])[0]
    total_races = len(horse_df)
    win_pct = (horse_df['finish_position'] == 1).mean() * 100
    top3_pct = (horse_df['finish_position'] <= 3).mean() * 100
    total_earnings = horse_df['earnings'].sum()
    total_profit = horse_df['profit_loss'].sum()
    race_nums = range(1, total_races + 1)

    st.markdown(f"### Performance Summary for `{name}`")
    st.text(f"Stable: {stable_name}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Races", total_races)
    col2.metric("Win %", f"{win_pct:.2f}%")
    col3.metric("Top 3 %", f"{top3_pct:.2f}%")

    col4, col5 = st.columns(2)
    col4.metric("Total Earnings", f"{int(total_earnings):,} ZED")
    col5.metric("Profit / Loss", f"{int(total_profit):,} ZED")

    st.subheader("Performance Charts")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Finish Position Distribution**")
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        horse_df['finish_position'].value_counts().sort_index().plot(kind='bar', ax=ax1, color='skyblue')
        ax1.set_xlabel("Finish Position")
        ax1.set_ylabel("Races")
        st.pyplot(fig1)

    with col2:
        st.markdown("**Finish Time Distribution vs. This Horse**")
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        ax2.hist(all_finish_times, bins=30, color='gray', alpha=0.6, edgecolor='white', label="All Horses")
        ax2.axvline(horse_df['finish_time'].mean(), color='cyan', linestyle='--', linewidth=2, label="Avg")
        ax2.axvline(horse_df['finish_time'].min(), color='green', linestyle='--', linewidth=2, label="Fastest")
        ax2.axvline(horse_df['finish_time'].max(), color='red', linestyle=':', linewidth=2, label="Slowest")
        ax2.legend()
        st.pyplot(fig2)

    st.markdown("### Cumulative Stats")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Cumulative Earnings**")
        fig3, ax3 = plt.subplots(figsize=(5, 3))
        ax3.plot(race_nums, horse_df['earnings'].cumsum(), marker='o', color='green')
        ax3.set_ylabel("ZED")
        ax3.set_xlabel("Race Number")
        st.pyplot(fig3)

    with col4:
        if 'points_change' in horse_df.columns:
            st.markdown("**Cumulative Points**")
            fig4, ax4 = plt.subplots(figsize=(5, 3))
            ax4.plot(race_nums, horse_df['points_change'].cumsum(), marker='o', color='purple')
            ax4.set_ylabel("MMR")
            ax4.set_xlabel("Race Number")
            st.pyplot(fig4)

    st.subheader("Top Augment Combos")
    horse_df['augment_combo'] = (
        horse_df['cpu_augment'].fillna('') + ' | ' +
        horse_df['ram_augment'].fillna('') + ' | ' +
        horse_df['hydraulic_augment'].fillna('')
    )
    augment_group = horse_df.groupby('augment_combo').agg({
        'finish_position': ['count', lambda x: (x == 1).mean() * 100],
        'finish_time': 'mean'
    })
    augment_group.columns = ['Races', 'Win %', 'Avg Time']
    st.dataframe(augment_group.sort_values('Win %', ascending=False).head(5).style.format({'Win %': '{:.2f}', 'Avg Time': '{:.2f}'}))

    horse_id = horse_df['horse_id'].iloc[0]
    st.markdown(f"""<a href="https://app.zedchampions.com/horse/{horse_id}" target="_blank">
        <button style="padding:0.5em 1em;font-size:16px">🔗 View on ZED Champions</button></a>""", unsafe_allow_html=True)
