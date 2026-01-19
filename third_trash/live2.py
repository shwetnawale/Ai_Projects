import pandas as pd
import joblib
import ccxt
import os
import csv
from datetime import datetime, timedelta

# --- 1. CONFIGURATION ---
SYMBOL = 'BTCUSD'
TIMEFRAME = '15m'
MODEL_FILE = 'brain.pkl'
DAYS_TO_TEST = 7
DETAILED_LOG = "backtest_analysis_detailed.csv"

# Public connection (Fast & No Keys Required for Backtesting)
exchange = ccxt.delta()

def get_indicators(df):
    """Calculates the exact 8 features your brain.pkl expects."""
    close = df['close']
    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    df['RSI'] = 100 - (100 / (1 + (gain/loss)))
    # MACD
    df['MACD'] = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    # ATR
    tr = pd.concat([df['high']-df['low'], abs(df['high']-close.shift()), abs(df['low']-close.shift())], axis=1).max(axis=1)
    df['ATR'] = tr.ewm(alpha=1/14, adjust=False).mean()
    # Trend_Dist (EMA 200)
    df['Trend_Dist'] = close - close.ewm(span=200, adjust=False).mean()
    # Breakouts
    df['Breakout_Up'] = (close > df['high'].rolling(50).max().shift(1)).astype(int)
    df['Breakout_Down'] = (close < df['low'].rolling(50).min().shift(1)).astype(int)
    # Patterns
    body = abs(df['close'] - df['open'])
    lower_wick = df[['open', 'close']].min(axis=1) - df['low']
    upper_wick = df['high'] - df[['open', 'close']].max(axis=1)
    df['Hammer'] = ((lower_wick > 2 * body) & (upper_wick < body)).astype(int)
    df['Shooting_Star'] = ((upper_wick > 2 * body) & (lower_wick < body)).astype(int)
    return df.dropna()

def log_detailed_trade(data):
    header = ["IST_Date", "IST_Time", "Entry", "High", "Low", "AI_Score", "SL", "TP", "Result"]
    file_exists = os.path.isfile(DETAILED_LOG)
    with open(DETAILED_LOG, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists: writer.writeheader()
        writer.writerow(data)

def run_simulation():
    if os.path.exists(DETAILED_LOG): os.remove(DETAILED_LOG)
    print(f"📡 Extracting {DAYS_TO_TEST} days of data...")
    since = exchange.parse8601((datetime.utcnow() - timedelta(days=DAYS_TO_TEST)).isoformat())
    ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, since=since, limit=1000)
    df = get_indicators(pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'vol']))

    print(f"🧠 Running AI Simulation (Syncing to IST)...")
    model = joblib.load(MODEL_FILE)
    features = ['RSI', 'MACD', 'ATR', 'Trend_Dist', 'Breakout_Up', 'Breakout_Down', 'Hammer', 'Shooting_Star']
    probs = model.predict_proba(df[features])[:, 1]
    
    trades_sensed = 0
    wins, losses = 0, 0
    
    for i in range(len(df)):
        if probs[i] > 0.65: 
            trades_sensed += 1
            row = df.iloc[i]
            entry, atr = row['close'], row['ATR']
            sl, tp = entry - (atr * 2), entry + (atr * 3)
            
            outcome = "PENDING"
            # Increased look-ahead to 100 candles (25 hours) to reduce "PENDING"
            future = df.iloc[i+1 : i+100] 
            for _, f_row in future.iterrows():
                if f_row['low'] <= sl: outcome = "LOSS"; break
                if f_row['high'] >= tp: outcome = "WIN"; break
            
            if outcome == "WIN": wins += 1
            elif outcome == "LOSS": losses += 1
            
            # --- SYNC TO DELTA INDIA IST ---
            ist_dt = datetime.fromtimestamp(row['ts']/1000) + timedelta(hours=5, minutes=30)
            
            log_detailed_trade({
                "IST_Date": ist_dt.strftime('%Y-%m-%d'), 
                "IST_Time": ist_dt.strftime('%H:%M:%S'),
                "Entry": f"{entry:.2f}", 
                "High": f"{row['high']:.2f}", 
                "Low": f"{row['low']:.2f}",
                "AI_Score": f"{probs[i]:.2f}", 
                "SL": f"{sl:.2f}", 
                "TP": f"{tp:.2f}", 
                "Result": outcome
            })

    print(f"\n✅ ANALYSIS COMPLETE")
    print(f"--------------------------")
    print(f"Trades Sensed: {trades_sensed} | Wins: {wins} | Losses: {losses}")
    if (wins + losses) > 0: print(f"Win Rate: {(wins/(wins+losses)*100):.1f}%")
    print(f"--------------------------")
    print(f"📁 Detailed report saved to: {DETAILED_LOG}")

if __name__ == "__main__":
    run_simulation()