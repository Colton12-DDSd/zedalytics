def calculate_basic_stats(df):
    total_races = len(df)
    win_pct = (df['finish_position'] == 1).mean() * 100
    top3_pct = (df['finish_position'] <= 3).mean() * 100
    earnings = df['earnings'].sum() if 'earnings' in df.columns else 0
    profit = df['profit_loss'].sum() if 'profit_loss' in df.columns else 0

    return {
        "total_races": total_races,
        "win_pct": win_pct,
        "top3_pct": top3_pct,
        "earnings": earnings,
        "profit": profit
    }
