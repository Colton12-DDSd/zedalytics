import streamlit as st
import matplotlib.pyplot as plt

def render_horse_detail(horse_id, df, show_horse_dashboard):
    horse_df = df[df['horse_id'] == horse_id].sort_values('race_date')

    if horse_df.empty:
        st.error("No data found for this horse.")
        return

    name = horse_df['horse_name'].iloc[0]
    stable_name = horse_df['stable_name'].iloc[0] if 'stable_name' in horse_df.columns else "Unknown"
    total_races = len(horse_df)
    win_pct = (horse_df['finish_position'] == 1).mean() * 100
    top3_pct = (horse_df['finish_position'] <= 3).mean() * 100
    total_earnings = horse_df['earnings'].sum()
    total_profit = horse_df['profit_loss'].sum()
    race_nums = range(1, total_races + 1)

    st.title(f"📊 Detailed Stats for {name}")
    st.button("🔙 Back to Horses", on_click=lambda: st.experimental_set_query_params())

    st.text(f"Stable: {stable_name}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Races", total_races)
    col2.metric("Win %", f"{win_pct:.2f}%")
    col3.metric("Top 3 %", f"{top3_pct:.2f}%")

    col4, col5 = st.columns(2)
    col4.metric("Total Earnings", f"{int(total_earnings):,} ZED")
    col5.metric("Profit / Loss", f"{int(total_profit):,} ZED")

    st.subheader("Performance Charts")

    # First row: Finish Position and Time Distributions
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Finish Position Distribution**")
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        horse_df['finish_position'].value_counts().sort_index().plot(kind='bar', ax=ax1, color='skyblue')
        ax1.set_xlabel("Finish Position")
        ax1.set_ylabel("Number of Races")
        st.pyplot(fig1)

    with col2:
        st.markdown("**Finish Time Distribution (All Horses) vs. This Horse**")
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        all_finish_times = df['finish_time'].dropna()
        ax2.hist(all_finish_times, bins=30, color='gray', alpha=0.6, edgecolor='white', label="All Horses")
        horse_avg_time = horse_df['finish_time'].mean()
        horse_min_time = horse_df['finish_time'].min()
        horse_max_time = horse_df['finish_time'].max()

        ax2.axvline(horse_avg_time, color='cyan', linestyle='--', linewidth=2, label=f"{name}'s Avg")
        ax2.axvline(horse_min_time, color='green', linestyle='--', linewidth=2, label=f"{name}'s Fastest")
        ax2.axvline(horse_max_time, color='red', linestyle=':', linewidth=2, label=f"{name}'s Slowest")
        ax2.set_xlabel("Finish Time")
        ax2.set_ylabel("Frequency")
        ax2.legend(fontsize='small')
        st.pyplot(fig2)

    st.markdown("###")

    # Second row: Cumulative charts
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**Cumulative Earnings**")
        horse_df['cumulative_earnings'] = horse_df['earnings'].cumsum()
        fig3, ax3 = plt.subplots(figsize=(5, 3))
        ax3.plot(race_nums, horse_df['cumulative_earnings'], marker='o', color='green')
        ax3.set_ylabel("ZED")
        ax3.set_xlabel("Race Number")
        st.pyplot(fig3)

    with col4:
        if 'points_change' in horse_df.columns:
            st.markdown("**Cumulative Points Change**")
            horse_df['cumulative_points'] = horse_df['points_change'].cumsum()
            fig4, ax4 = plt.subplots(figsize=(5, 3))
            ax4.plot(race_nums, horse_df['cumulative_points'], marker='o', color='purple')
            ax4.set_ylabel("MMR Points")
            ax4.set_xlabel("Race Number")
            st.pyplot(fig4)

    # Augment breakdown
    st.subheader("Top Augment Combinations")
    horse_df['augment_combo'] = (
        horse_df['cpu_augment'].fillna('') + ' | ' +
        horse_df['ram_augment'].fillna('') + ' | ' +
        horse_df['hydraulic_augment'].fillna('')
    )

    augment_group = horse_df.groupby('augment_combo').agg({
        'finish_position': ['count', lambda x: (x == 1).mean() * 100],
        'finish_time': 'mean'
    })
    augment_group.columns = ['Races', 'Win %', 'Avg Finish Time']
    augment_group = augment_group.sort_values('Win %', ascending=False).head(5)

    st.dataframe(augment_group.style.format({
        'Win %': '{:.2f}',
        'Avg Finish Time': '{:.2f}'
    }))

    st.markdown("---")
    zedchampions_url = f"https://app.zedchampions.com/horse/{horse_id}"
    st.markdown(
        f"""
        <a href="{zedchampions_url}" target="_blank">
            <button style="margin-top: 10px; padding: 0.5em 1em; font-size: 16px;">🔗 View on ZED Champions</button>
        </a>
        """,
        unsafe_allow_html=True
    )
