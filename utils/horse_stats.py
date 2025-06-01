# utils/horse_stats.py

def calculate_basic_stats(df):
    return {
        "total_races": len(df),
        "win_pct": (df['finish_position'] == 1).mean() * 100,
        "top3_pct": (df['finish_position'] <= 3).mean() * 100,
        "earnings": df['earnings'].sum(),
        "profit": df['profit_loss'].sum()
    }
