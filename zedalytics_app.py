# zedalytics_app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# URL to the live race results data
CSV_URL = 'https://raw.githubusercontent.com/myblood-tempest/zed-champions-race-data/main/race_results.csv'

@st.cache_data(ttl=7200)
def load_data():
    df = pd.read_csv(CSV_URL)
    df['race_date'] = pd.to_datetime(df['race_date'], errors='coerce')
    return df

def show_horse_dashboard(horse_df):
    horse_df = horse_df.copy()
    name = horse_df['horse_name'].iloc[0]
    stable_name = horse_df['stable_name'].iloc[0] if 'stable_name' in horse_df.columns else "Unknown"
    total_races = len(horse_df)
    win_pct = (horse_df['finish_position'] == 1).mean() * 100
    top3_pct = (horse_df['finish_position'] <= 3).mean() * 100
    avg_finish = horse_df['finish_position'].mean()
    total_earnings = horse_df['earnings'].sum()
    total_profit = horse_df['profit_loss'].sum()

    st.markdown(f"### Performance Summary for `{name}`")
    st.text(f"Stable: {stable_name}")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Races", total_races)
    col2.metric("Win %", f"{win_pct:.2f}%")
    col3.metric("Top 3 %", f"{top3_pct:.2f}%")

    col4, col5 = st.columns(2)
    col4.metric("Total Earnings", f"{int(total_earnings):,} ZED")
    col5.metric("Profit / Loss", f"{int(total_profit):,} ZED")

    st.subheader("Finish Position Distribution")
    fig1, ax1 = plt.subplots()
    horse_df['finish_position'].value_counts().sort_index().plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_xlabel("Finish Position")
    ax1.set_ylabel("Number of Races")
    st.pyplot(fig1)

    st.subheader("Finish Position Over Time")
    fig2, ax2 = plt.subplots()
    ax2.plot(horse_df['race_date'], horse_df['finish_position'], marker='o')
    ax2.set_ylabel("Finish (1 = Win)")
    ax2.set_xlabel("Date")
    ax2.invert_yaxis()
    st.pyplot(fig2)

    st.subheader("Cumulative Earnings")
    horse_df.loc[:, 'cumulative_earnings'] = horse_df['earnings'].cumsum()
    fig3, ax3 = plt.subplots()
    ax3.plot(horse_df['race_date'], horse_df['cumulative_earnings'], marker='o', color='green')
    ax3.set_ylabel("ZED")
    ax3.set_xlabel("Date")
    st.pyplot(fig3)

    if 'points_change' in horse_df.columns:
        horse_df.loc[:, 'cumulative_points'] = horse_df['points_change'].cumsum()
        st.subheader("Cumulative Points Change")
        fig4, ax4 = plt.subplots()
        ax4.plot(horse_df['race_date'], horse_df['cumulative_points'], marker='o', color='purple')
        ax4.set_ylabel("MMR Points")
        ax4.set_xlabel("Date")
        st.pyplot(fig4)

    st.subheader("Top Augment Combinations")
    horse_df.loc[:, 'augment_combo'] = (
        horse_df['cpu_augment'].fillna('') + ' | ' +
        horse_df['ram_augment'].fillna('') + ' | ' +
        horse_df['hydraulic_augment'].fillna('')
    )
    augment_group = horse_df.groupby('augment_combo').agg({
        'finish_position': ['count', lambda x: (x == 1).mean() * 100]
    }).rename(columns={'count': 'Races', '<lambda_0>': 'Win %'})
    augment_group.columns = augment_group.columns.droplevel(0)
    augment_group = augment_group.sort_values('Races', ascending=False).head(5)
    st.dataframe(augment_group.style.format({'Win %': '{:.2f}'}))

def main():
    st.set_page_config(page_title="Zedalytics", layout="wide")
    st.title("Zedalytics")
    df = load_data()

    tab1, tab2, tab3 = st.tabs(["🏇 Horses", "🏠 Stables", "⚙️ Augments"])

    with tab1:
        st.subheader("🏆 Top Horses by Current Balance")
        balance_df = df.groupby(['horse_id', 'horse_name'], as_index=False)['profit_loss'].sum()
        top_balance = balance_df.sort_values('profit_loss', ascending=False).head(5)

        for _, row in top_balance.iterrows():
            with st.container():
                st.markdown(f"**{row['horse_name']}** — Balance: {int(row['profit_loss']):,} ZED")
                if st.button("View Stats", key="bal" + row['horse_id']):
                    horse_df = df[df['horse_id'] == row['horse_id']].sort_values('race_date')
                    show_horse_dashboard(horse_df)

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

            show_horse_dashboard(horse_df)

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

            col4, col5 = st.columns(2)
            col4.metric("Total Earnings", f"{int(total_earnings):,} ZED")
            col5.metric("Total Profit", f"{int(total_profit):,} ZED")

            horses = filtered[['horse_name', 'horse_id']].drop_duplicates()
            for _, row in horses.iterrows():
                horse_df = filtered[filtered['horse_id'] == row['horse_id']].copy()
                with st.container():
                    st.markdown(f"**{row['horse_name']}**")
                    st.markdown(f"Races: {len(horse_df)} | Win %: {(horse_df['finish_position'] == 1).mean() * 100:.2f}%")
                    st.markdown(f"Earnings: {int(horse_df['earnings'].sum()):,} ZED")
                    if st.button("View Stats", key=row['horse_id']):
                        show_horse_dashboard(horse_df)

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
    
        # --- Top 5 augment combos ---
        st.subheader(f"🔝 Top 5 Augment Combinations ({selected_bloodline})")
        augments = filtered_df.groupby('augment_combo').agg({
            'finish_position': ['count', lambda x: (x == 1).mean() * 100]
        }).rename(columns={'count': 'Races', '<lambda_0>': 'Win %'})
        augments.columns = augments.columns.droplevel(0)
        augments = augments.sort_values('Races', ascending=False).head(5)
        st.dataframe(augments.style.format({'Win %': '{:.2f}'}))
    
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
                st.success(f"{custom_combo} — {total} races, Win Rate in {selected_bloodline}: {win_rate:.2f}%")
            else:
                st.warning("No races found with that augment combo for this bloodline.")
    

        if custom_combo.strip(" |"):
            filtered = df[df['augment_combo'] == custom_combo]
            if not filtered.empty:
                total = len(filtered)
                win_rate = (filtered['finish_position'] == 1).mean() * 100
                st.success(f"{custom_combo} — {total} races, Win Rate: {win_rate:.2f}%")
            else:
                st.warning("No races found with that augment combo.")

if __name__ == "__main__":
    main()
