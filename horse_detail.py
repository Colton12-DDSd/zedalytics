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
    st.button("🔙 Back to Horses", on_click=lambda: st.query_params.clear())

    st.text(f"Stable: {stable_name}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Races", total_races)
    col2.metric("Win %", f"{win_pct:.2f}%")
    col3.metric("Top 3 %", f"{top3_pct:.2f}%")

    col4, col5 = st.columns(2)
    col4.metric("Total Earnings", f"{int(total_earnings):,} ZED")
    col5.metric("Profit / Loss", f"{int(total_profit):,} ZED")

    st.subheader("Performance Charts")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**Finish Position**")
        fig1, ax1 = plt.subplots(figsize=(4, 2.5))
        horse_df['finish_position'].value_counts().sort_index().plot(kind='bar', ax=ax1, color='skyblue')
        ax1.set_xlabel("Position")
        ax1.set_ylabel("Count")
        st.pyplot(fig1)

    with col2:
        st.markdown("**Finish Time Histogram**")
        fig2, ax2 = plt.subplots(figsize=(4, 2.5))
        all_times = df['finish_time'].dropna()
        ax2.hist(all_times, bins=30, color='gray', alpha=0.6, edgecolor='white')
        avg = horse_df['finish_time'].mean()
        min_time = horse_df['finish_time'].min()
        max_time = horse_df['finish_time'].max()
        ax2.axvline(avg, color='cyan', linestyle='--', linewidth=2, label="Avg")
        ax2.axvline(min_time, color='green', linestyle='--', linewidth=2, label="Fastest")
        ax2.axvline(max_time, color='red', linestyle=':', linewidth=2, label="Slowest")
        ax2.set_xlabel("Time")
        ax2.set_ylabel("Frequency")
        ax2.legend(fontsize='x-small')
        st.pyplot(fig2)

    with col3:
        st.markdown("**Earnings Over Time**")
        horse_df['cumulative_earnings'] = horse_df['earnings'].cumsum()
        fig3, ax3 = plt.subplots(figsize=(4, 2.5))
        ax3.plot(horse_df['cumulative_earnings'], marker='o', color='green')
        ax3.set_xlabel("Race #")
        ax3.set_ylabel("ZED")
        st.pyplot(fig3)

    with col4:
        st.markdown("**MMR Points Over Time**")
        if 'points_change' in horse_df.columns:
            horse_df['cumulative_points'] = horse_df['points_change'].cumsum()
            fig4, ax4 = plt.subplots(figsize=(4, 2.5))
            ax4.plot(horse_df['cumulative_points'], marker='o', color='purple')
            ax4.set_xlabel("Race #")
            ax4.set_ylabel("Points")
            st.pyplot(fig4)
        else:
            st.info("No points data.")

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
