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
    st.subheader("Horse Performance Dashboard for ZED Champions")

    df = load_data()
    mode = st.radio("Select search mode:", ["Homepage", "Horse ID/Name", "Stable Name"])

    if mode == "Homepage":
        st.subheader("🏆 Top Horses by Current Balance")
        balance_df = df.groupby(['horse_id', 'horse_name'], as_index=False)['profit_loss'].sum()
        top_balance = balance_df.sort_values('profit_loss', ascending=False).head(10)

        for _, row in top_balance.iterrows():
            with st.container():
                st.markdown(f"**{row['horse_name']}** — Balance: {int(row['profit_loss']):,} ZED")
                if st.button("View Stats", key="bal" + row['horse_id']):
                    horse_df = df[df['horse_id'] == row['horse_id']].sort_values('race_date')
                    show_horse_dashboard(horse_df)

        st.subheader("🔥 Hottest Horses (Last 5 Races)")
        recent_df = df.sort_values('race_date').groupby('horse_id').tail(5)
        recent_gain = recent_df.groupby(['horse_id', 'horse_name'], as_index=False)['profit_loss'].sum()
        top_recent = recent_gain.sort_values('profit_loss', ascending=False).head(10)

        for _, row in top_recent.iterrows():
            with st.container():
                st.markdown(f"**{row['horse_name']}** — Last 5 P/L: {int(row['profit_loss']):,} ZED")
                if st.button("View Stats", key="hot" + row['horse_id']):
                    horse_df = df[df['horse_id'] == row['horse_id']].sort_values('race_date')
                    show_horse_dashboard(horse_df)

    elif mode == "Horse ID/Name":
        user_input = st.text_input("Enter Horse ID or Name:")

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

    elif mode == "Stable Name":
        stable_input = st.text_input("Enter Stable Name:")

        if stable_input:
            filtered = df[df['stable_name'].str.lower() == stable_input.strip().lower()]
            if filtered.empty:
                st.warning("No horses found for this stable.")
                return

            sort_option = st.selectbox("Sort horses by:", ["Races", "Win %", "Earnings", "Balance", "Profit"], index=0)

            horses = filtered[['horse_name', 'horse_id']].drop_duplicates()

            sort_stats = []
            for _, row in horses.iterrows():
                horse_df = filtered[filtered['horse_id'] == row['horse_id']]
                total_races = len(horse_df)
                win_pct = (horse_df['finish_position'] == 1).mean() * 100
                earnings = horse_df['earnings'].sum()
                balance = horse_df['profit_loss'].sum()
                profit = balance - (2 * 1000)  # Assume 1000 starting balance
                sort_stats.append({
                    'horse_name': row['horse_name'],
                    'horse_id': row['horse_id'],
                    'total_races': total_races,
                    'win_pct': win_pct,
                    'earnings': earnings,
                    'balance': balance,
                    'profit': profit
                })
            sort_df = pd.DataFrame(sort_stats)

            if sort_option == "Races":
                sort_df = sort_df.sort_values("total_races", ascending=False)
            elif sort_option == "Win %":
                sort_df = sort_df.sort_values("win_pct", ascending=False)
            elif sort_option == "Earnings":
                sort_df = sort_df.sort_values("earnings", ascending=False)
            elif sort_option == "Balance":
                sort_df = sort_df.sort_values("balance", ascending=False)
            elif sort_option == "Profit":
                sort_df = sort_df.sort_values("profit", ascending=False)

            st.markdown("### Horses in Stable")
            for _, row in sort_df.iterrows():
                horse_df = filtered[filtered['horse_id'] == row['horse_id']].copy()
                with st.container():
                    cols = st.columns([2, 1])
                    with cols[0]:
                        st.markdown(f"**{row['horse_name']}**")
                        st.markdown(f"Races: {row['total_races']} | Win %: {row['win_pct']:.2f}%")
                        st.markdown(f"Earnings: {int(row['earnings']):,} ZED | Balance: {int(row['balance']):,} ZED | Profit: {int(row['profit']):,} ZED")
                    with cols[1]:
                        if st.button("View Stats", key=row['horse_id']):
                            show_horse_dashboard(horse_df)

if __name__ == "__main__":
    main()
