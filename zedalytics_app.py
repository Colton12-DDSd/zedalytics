# zedalytics_app.py
from horse_detail import render_horse_detail
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use("dark_background")
# URL to the live race results data
CSV_URL = 'https://raw.githubusercontent.com/myblood-tempest/zed-champions-race-data/main/race_results.csv'

@st.cache_data(ttl=600)
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
        horse_slowest_time = horse_df['finish_time'].max()
    
        ax2.axvline(horse_avg_time, color='cyan', linestyle='--', linewidth=2, label=f"{name}'s Avg")
        ax2.axvline(horse_min_time, color='green', linestyle='--', linewidth=2, label=f"{name}'s Fastest")
        ax2.axvline(horse_slowest_time, color='red', linestyle=':', linewidth=2, label=f"{name}'s Slowest")

    
        ax2.set_xlabel("Finish Time")
        ax2.set_ylabel("Frequency")
        ax2.legend(fontsize="small")
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
    st.markdown("""
    > ⚠️ **Data Disclaimer**  
    > The race data displayed is sourced from a public GitHub file and may not reflect the full race history available on ZED Champions.  
    > Some races may be missing until a complete and official API is available.
    """)

    df = load_data()
    df['augment_combo'] = (
        df['cpu_augment'].fillna('') + ' | ' +
        df['ram_augment'].fillna('') + ' | ' +
        df['hydraulic_augment'].fillna('')
    )

    # ✅ Now that df is defined, we can safely check query params
    query_params = st.query_params
    if "horse_id" in query_params:
        horse_id = query_params["horse_id"]  # <- ✅ no [0] needed
        render_horse_detail(horse_id, df, show_horse_dashboard)
        st.stop()



    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🐎 Horses", 
        "🏠 Stables", 
        "⚙️ Augments", 
        "🥇 Leaderboard", 
        "🏇 Active Racers"
    ])


    with tab1:
        st.subheader("🏆 Top Horses by Current Balance")
        balance_df = df.groupby(['horse_id', 'horse_name'], as_index=False)['profit_loss'].sum()
        top_balance = balance_df.sort_values('profit_loss', ascending=False).head(10)
    
        for _, row in top_balance.iterrows():
            with st.container():
                horse_id = row['horse_id']
                horse_name = row['horse_name']
                profit = int(row['profit_loss'])
    
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{horse_name}** — Balance: {profit:,} ZED")
                with col2:
                    detail_url = f"?horse_id={horse_id}"
                    st.markdown(
                        f"""
                        <a href="{detail_url}" target="_blank">
                            <button style="margin-top: 0.25em; padding: 0.4em 0.8em; font-size: 14px;">📊 More Stats</button>
                        </a>
                        """,
                        unsafe_allow_html=True
                    )
    
        st.divider()
    
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
    
        df = df.dropna(subset=["finish_time"])  # Ensure finish_time exists
        df['augment_combo'] = (
            df['cpu_augment'].fillna('') + ' | ' +
            df['ram_augment'].fillna('') + ' | ' +
            df['hydraulic_augment'].fillna('')
        )
    
        # 🕒 Fastest Single Race Times
        st.markdown("### ⚡ Fastest Single Race Times")
        fastest_races = df[['horse_name', 'stable_name', 'augment_combo', 'finish_time', 'race_date']].sort_values('finish_time').head(10)
        st.dataframe(
            fastest_races.style.format({
                'finish_time': '{:.2f}',
                'race_date': lambda d: d.strftime('%Y-%m-%d')
            })
        )

    
        # 🏁 Fastest Average Horses (Min 3 races)
        st.markdown("### 🚀 Fastest Average Horses (Min. 3 Races)")
        avg_times = (
            df.groupby(['horse_id', 'horse_name', 'stable_name', 'augment_combo'])
            .agg(races=('finish_time', 'count'), avg_time=('finish_time', 'mean'))
            .reset_index()
        )
        fastest_avg = avg_times[avg_times['races'] >= 3].sort_values('avg_time').head(10)
        st.dataframe(fastest_avg[['horse_name', 'stable_name', 'augment_combo', 'races', 'avg_time']].style.format({'avg_time': '{:.2f}'}))
    
        # 💰 Top Earners (Min 3 races)
        st.markdown("### 💰 Top Earners (Min. 3 Races)")
        earners = (
            df.groupby(['horse_id', 'horse_name', 'stable_name', 'augment_combo'])
            .agg(races=('earnings', 'count'), total_earnings=('earnings', 'sum'))
            .reset_index()
        )
        top_earners = earners[earners['races'] >= 3].sort_values('total_earnings', ascending=False).head(10)
        st.dataframe(top_earners[['horse_name', 'stable_name', 'augment_combo', 'races', 'total_earnings']].style.format({'total_earnings': '{:,.0f} ZED'}))

    with tab5:
        st.subheader("Recently Active Horses (Last 24 Hours)")
    
        now = pd.Timestamp.now(tz='UTC')
        recent_df = df[df['race_date'] >= now - pd.Timedelta(hours=24)].copy()
    
        if recent_df.empty:
            st.info("No races found in the last 24 hours.")
        else:
            # Rename for clarity
            recent_df.rename(columns={
                "rating": "stars",
                "speed_rating": "speed_stars",
                "sprint_rating": "sprint_stars",
                "endurance_rating": "endurance_stars"
            }, inplace=True)
    
            # Dropdown filters
            bloodlines = ["All"] + sorted(recent_df['bloodline'].dropna().unique())
            selected_bloodline = st.selectbox("Filter by Bloodline:", bloodlines)
    
            stars = ["All"] + sorted(recent_df['stars'].dropna().unique())
            selected_stars = st.selectbox("Filter by Overall Stars:", stars)
    
            speed_stars = ["All"] + sorted(recent_df['speed_stars'].dropna().unique())
            selected_speed = st.selectbox("Filter by Speed Stars:", speed_stars)
    
            sprint_stars = ["All"] + sorted(recent_df['sprint_stars'].dropna().unique())
            selected_sprint = st.selectbox("Filter by Sprint Stars:", sprint_stars)
    
            endurance_stars = ["All"] + sorted(recent_df['endurance_stars'].dropna().unique())
            selected_endurance = st.selectbox("Filter by Endurance Stars:", endurance_stars)
    
            # Apply filters
            if selected_bloodline != "All":
                recent_df = recent_df[recent_df['bloodline'] == selected_bloodline]
            if selected_stars != "All":
                recent_df = recent_df[recent_df['stars'] == selected_stars]
            if selected_speed != "All":
                recent_df = recent_df[recent_df['speed_stars'] == selected_speed]
            if selected_sprint != "All":
                recent_df = recent_df[recent_df['sprint_stars'] == selected_sprint]
            if selected_endurance != "All":
                recent_df = recent_df[recent_df['endurance_stars'] == selected_endurance]
    
            # Aggregate latest race per horse
            latest_races = (
                recent_df.sort_values("race_date", ascending=False)
                .groupby(["horse_id", "horse_name", "stable_name", "bloodline", "stars", "speed_stars", "sprint_stars", "endurance_stars"], as_index=False)
                .agg(last_race_date=('race_date', 'max'), total_races=('race_id', 'count'))
            )
    
            st.markdown(f"**Total Horses Matching Filter:** {len(latest_races)}")
            st.dataframe(latest_races.sort_values("last_race_date", ascending=False).style.format({
                "last_race_date": lambda d: d.strftime("%Y-%m-%d %H:%M"),
                "total_races": "{:,}"
            }))
    



if __name__ == "__main__":
    main()

