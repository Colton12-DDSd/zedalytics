# zedalytics_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use("dark_background")
# URL to the live race results data
CSV_URL = 'https://raw.githubusercontent.com/myblood-tempest/zed-champions-race-data/main/race_results.csv'

@st.cache_data(ttl=7200)
def load_data():
    df = pd.read_csv(CSV_URL)
    df['race_date'] = pd.to_datetime(df['race_date'], errors='coerce')
    return df

def show_horse_dashboard(horse_df, full_df):
    horse_df = horse_df.copy()
    name = horse_df['horse_name'].iloc[0]
    stable_name = horse_df['stable_name'].iloc[0] if 'stable_name' in horse_df.columns else "Unknown"
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

    # First row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Finish Position Distribution**")
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        horse_df['finish_position'].value_counts().sort_index().plot(kind='bar', ax=ax1, color='skyblue')
        ax1.set_xlabel("Finish Position")
        ax1.set_ylabel("Number of Races")
        st.pyplot(fig1)

    with col2:
        st.markdown("**Finish Time Distribution (All Horses) vs. This Horse's Avg & Fastest**")
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        all_finish_times = full_df['finish_time'].dropna()
        ax2.hist(all_finish_times, bins=30, color='gray', alpha=0.6, edgecolor='white', label="All Horses")
    
        horse_avg_time = horse_df['finish_time'].mean()
        horse_min_time = horse_df['finish_time'].min()
    
        ax2.axvline(horse_avg_time, color='cyan', linestyle='--', linewidth=2, label=f"{name}'s Avg")
        ax2.axvline(horse_min_time, color='yellow', linestyle='--', linewidth=2, label=f"{name}'s Fastest")
    
        ax2.set_xlabel("Finish Time")
        ax2.set_ylabel("Frequency")
        ax2.legend()
        st.pyplot(fig2)


    st.markdown("###")

    # Second row
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
    horse_id = horse_df['horse_id'].iloc[0]
    zedchampions_url = f"https://app.zedchampions.com/horse/{horse_id}"
    st.markdown(
        f"""
        <a href="{zedchampions_url}" target="_blank">
            <button style="margin-top: 10px; padding: 0.5em 1em; font-size: 16px;">🔗 View on ZED Champions</button>
        </a>
        """,
        unsafe_allow_html=True
    )

def main():
    st.set_page_config(page_title="Zedalytics", layout="wide")
    st.title("Zedalytics")
    df = load_data()
    df['augment_combo'] = (
    df['cpu_augment'].fillna('') + ' | ' +
    df['ram_augment'].fillna('') + ' | ' +
    df['hydraulic_augment'].fillna('')
)


    tab1, tab2, tab3, tab4 = st.tabs(["🏇 Horses", "🏠 Stables", "⚙️ Augments", "🥇 Leaderboard"])

    with tab1:
        st.subheader("🏆 Top Horses by Current Balance")
        balance_df = df.groupby(['horse_id', 'horse_name'], as_index=False)['profit_loss'].sum()
        top_balance = balance_df.sort_values('profit_loss', ascending=False).head(5)
    
        # Initialize accordion tracker
        if "active_horse_id" not in st.session_state:
            st.session_state["active_horse_id"] = None
    
        for _, row in top_balance.iterrows():
            with st.container():
                horse_id = row['horse_id']
                is_active = st.session_state["active_horse_id"] == horse_id
    
                st.markdown(f"**{row['horse_name']}** — Balance: {int(row['profit_loss']):,} ZED")
    
                clicked = st.button("Hide Stats" if is_active else "View Stats", key="btn_" + horse_id)
    
                if clicked:
                    # If already open, close it; otherwise, open the new one
                    st.session_state["active_horse_id"] = None if is_active else horse_id
    
                # Show dashboard if active horse is selected (after state update)
                if st.session_state["active_horse_id"] == horse_id:
                    horse_df = df[df['horse_id'] == horse_id].sort_values('race_date')
                    show_horse_dashboard(horse_df, df)
    
        st.subheader("🔎 Search Horse by ID or Name")
        user_input = st.text_input("Enter Horse ID or Name:", key="horse_search")
        if user_input:
            user_input = user_input.strip()
            if len(user_input) == 36:
                horse_df = df[df['horse_id'] == user_input].sort_values('race_date')
            else:
                matches = df[df['horse_name'].str.contains(user_input, case=False, na=False)]
                if matches.empty:
                    st.warning("No horses found matching that name.")
                    return
                selected_name = matches['horse_name'].unique()[0]
                horse_df = matches[matches['horse_name'] == selected_name].sort_values('race_date')
    
            if horse_df.empty:
                st.warning("No race data found for this horse.")
                return
    
            show_horse_dashboard(horse_df, df)



    with tab2:
        st.subheader("🏠 Top Earning Stables")
        stable_df = df.groupby('stable_name', as_index=False)['earnings'].sum()
        top_stables = stable_df.sort_values('earnings', ascending=False).head(5)
        st.dataframe(top_stables)

        stable_input = st.text_input("Enter Stable Name:", key="stable_search")
        if stable_input:
            filtered = df[df['stable_name'].str.lower() == stable_input.strip().lower()]
            if filtered.empty:
                st.warning("No horses found for this stable.")
                return

            total_races = len(filtered)
            total_earnings = filtered['earnings'].sum()
            total_profit = filtered['profit_loss'].sum()
            total_wins = (filtered['finish_position'] == 1).sum()
            win_pct = (filtered['finish_position'] == 1).mean() * 100

            st.markdown(f"### Stats for `{stable_input}`")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Races", total_races)
            col2.metric("Total Wins", total_wins)
            col3.metric("Win %", f"{win_pct:.2f}%")

            col4, col5, col6 = st.columns(3)
            col4.metric("Total Earnings", f"{int(total_earnings):,} ZED")
            col5.metric("Total Profit", f"{int(total_profit):,} ZED")
            col6.metric("Win %", f"{win_pct:.2f}%")


            horses = filtered[['horse_name', 'horse_id']].drop_duplicates()
            for _, row in horses.iterrows():
                horse_df = filtered[filtered['horse_id'] == row['horse_id']].copy()
                with st.container():
                    total_races = len(horse_df)
                    win_pct = (horse_df['finish_position'] == 1).mean() * 100
                    total_earnings = int(horse_df['earnings'].sum())
                    total_profit = int(horse_df['profit_loss'].sum())
            
                    st.markdown(f"**{row['horse_name']}**")
                    st.markdown(f"Races: {total_races} | Win %: {win_pct:.2f}%")
                    st.markdown(f"Earnings: {total_earnings:,} ZED | Profit: {total_profit:,} ZED")
            
                    if st.button("View Stats", key=row['horse_id']):
                        show_horse_dashboard(horse_df, df)


    with tab3:
        st.subheader("⚙️ Augment Analytics")
    
        # --- Select bloodline ---
        bloodlines = ["All"] + sorted(df['bloodline'].dropna().unique())
        selected_bloodline = st.selectbox("Select Bloodline:", options=bloodlines)
    
        # --- Filter by bloodline ---
        if selected_bloodline != "All":
            filtered_df = df[df['bloodline'] == selected_bloodline].copy()
        else:
            filtered_df = df.copy()
    
        # --- Prepare augment combo column ---
        filtered_df['augment_combo'] = (
            filtered_df['cpu_augment'].fillna('') + ' | ' +
            filtered_df['ram_augment'].fillna('') + ' | ' +
            filtered_df['hydraulic_augment'].fillna('')
        )
    
        # --- Sorting toggle ---
        st.subheader("Top Augment Combinations (Min. 100 Races)")
        sort_option = st.radio("Sort by:", options=["Win %", "Avg Finish Time"], horizontal=True)
    
        # --- Group and sort ---
        augment_group = filtered_df.groupby('augment_combo').agg({
            'finish_position': ['count', lambda x: (x == 1).mean() * 100],
            'finish_time': 'mean'
        })
    
        augment_group.columns = ['Races', 'Win %', 'Avg Finish Time']
        augment_group = augment_group[augment_group['Races'] >= 100]
    
        if sort_option == "Win %":
            augment_group = augment_group.sort_values('Win %', ascending=False)
        else:
            augment_group = augment_group.sort_values('Avg Finish Time')
    
        st.dataframe(augment_group.head(5).style.format({
            'Win %': '{:.2f}',
            'Avg Finish Time': '{:.2f}'
        }))
    
        # --- Custom augment combo testing ---
        st.subheader("🔧 Test a Custom Augment Combo")
    
        cpu_options = sorted(df['cpu_augment'].dropna().unique())
        ram_options = sorted(df['ram_augment'].dropna().unique())
        hyd_options = sorted(df['hydraulic_augment'].dropna().unique())
    
        cpu = st.selectbox("CPU Augment:", options=[""] + cpu_options, key="cpu")
        ram = st.selectbox("RAM Augment:", options=[""] + ram_options, key="ram")
        hyd = st.selectbox("Hydraulic Augment:", options=[""] + hyd_options, key="hyd")
    
        custom_combo = f"{cpu} | {ram} | {hyd}"
        if custom_combo.strip(" |"):
            match = filtered_df[filtered_df['augment_combo'] == custom_combo]
            if not match.empty:
                total = len(match)
                win_rate = (match['finish_position'] == 1).mean() * 100
                avg_time = match['finish_time'].mean()
                st.success(f"{custom_combo} — {total} races, Win Rate: {win_rate:.2f}%, Avg Finish Time: {avg_time:.2f}")
            else:
                st.warning("No races found with that augment combo for this bloodline.")

    with tab4:
        st.subheader("🥇 Leaderboards")
    
        # Preprocess base data
        horse_stats = df.groupby(['horse_id', 'horse_name'], as_index=False).agg(
            races=('finish_position', 'count'),
            wins=('finish_position', lambda x: (x == 1).sum()),
            win_pct=('finish_position', lambda x: (x == 1).mean() * 100),
            avg_time=('finish_time', 'mean'),
            total_profit=('profit_loss', 'sum')
        )
    
        # 💸 Top by Profit
        st.markdown("### 💰 Top 10 Horses by Profit")
        top_profit = horse_stats.sort_values('total_profit', ascending=False).head(10)
        st.dataframe(top_profit[['horse_name', 'races', 'total_profit']].style.format({'total_profit': '{:,.0f} ZED'}))
    
        # 🏆 Top by Win %
        st.markdown("### 🏆 Top 10 Horses by Win % (min 20 races)")
        top_win_pct = horse_stats[horse_stats['races'] >= 20].sort_values('win_pct', ascending=False).head(10)
        st.dataframe(top_win_pct[['horse_name', 'races', 'win_pct']].style.format({'win_pct': '{:.2f}%'}))
    
        # ⚡️ Top by Avg Finish Time
        st.markdown("### ⏱️ Top 10 Horses by Avg Finish Time (min 20 races)")
        top_time = horse_stats[horse_stats['races'] >= 20].sort_values('avg_time').head(10)
        st.dataframe(top_time[['horse_name', 'races', 'avg_time']].style.format({'avg_time': '{:.2f}'}))
    
        # 🏁 Fastest Individual Finish Times
        st.markdown("### 🏁 Fastest Individual Finish Times")
        fastest_df = df.dropna(subset=["finish_time"]).sort_values("finish_time").head(10)
        fastest_df["Augments"] = (
            fastest_df['cpu_augment'].fillna('') + " | " +
            fastest_df['ram_augment'].fillna('') + " | " +
            fastest_df['hydraulic_augment'].fillna('')
        )
        st.dataframe(fastest_df[['horse_name', 'finish_time', 'Augments']].rename(columns={'finish_time': 'Fastest Time'}).style.format({'Fastest Time': '{:.2f}'}))
    
        # 💥 Biggest Single-Race ZED Win
        st.markdown("### 💥 Biggest Single-Race ZED Win")
        biggest_win = df.sort_values("profit_loss", ascending=False).head(10)
        biggest_win["Augments"] = (
            biggest_win['cpu_augment'].fillna('') + " | " +
            biggest_win['ram_augment'].fillna('') + " | " +
            biggest_win['hydraulic_augment'].fillna('')
        )
        st.dataframe(biggest_win[['horse_name', 'profit_loss', 'Augments']].rename(columns={'profit_loss': 'ZED Won'}).style.format({'ZED Won': '{:,.0f} ZED'}))
    
        # ⚙️ Fastest Avg Horses + Most Common Augs
        st.markdown("### ⚙️ Top 10 Fastest Avg Horses + Common Augments")
        avg_times = df.dropna(subset=["finish_time"]).groupby(['horse_id', 'horse_name']).agg(
            avg_time=('finish_time', 'mean'),
            races=('finish_time', 'count')
        ).query("races >= 5").sort_values("avg_time").head(10)
    
        top_fastest_ids = avg_times.index.get_level_values('horse_id')
        popular_augs = df[df['horse_id'].isin(top_fastest_ids)].groupby('horse_id').agg(
            most_common_cpu=('cpu_augment', lambda x: x.mode().iloc[0] if not x.mode().empty else ""),
            most_common_ram=('ram_augment', lambda x: x.mode().iloc[0] if not x.mode().empty else ""),
            most_common_hyd=('hydraulic_augment', lambda x: x.mode().iloc[0] if not x.mode().empty else "")
        )
    
        leaderboard_avg = avg_times.reset_index().merge(popular_augs.reset_index(), on="horse_id")
        leaderboard_avg["Augments"] = (
            leaderboard_avg['most_common_cpu'] + " | " +
            leaderboard_avg['most_common_ram'] + " | " +
            leaderboard_avg['most_common_hyd']
        )
        st.dataframe(leaderboard_avg[['horse_name', 'avg_time', 'races', 'Augments']].style.format({'avg_time': '{:.2f}'}))


if __name__ == "__main__":
    main()
