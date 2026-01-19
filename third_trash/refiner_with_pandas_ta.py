import pandas as pd
import numpy as np
import pandas_ta as ta # Ensure you have this: pip install pandas_ta

# --- CONFIGURATION ---
INPUT_FILE = 'btc_raw.csv'
OUTPUT_FILE = 'btc_ready.csv'

def calculate_price_action(df):
    # 1. Standard Indicators
    df['RSI'] = ta.rsi(df['close'], length=14)
    df['EMA_200'] = ta.ema(df['close'], length=200)
    df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    
    # MACD
    macd = ta.macd(df['close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_HIST'] = macd['MACDh_12_26_9']

    # 2. PRICE ACTION: Support & Resistance (Rolling Window)
    # We look back 50 candles to find the lowest low (Support) and highest high (Resistance)
    df['Support_50'] = df['low'].rolling(window=50).min()
    df['Resist_50'] = df['high'].rolling(window=50).max()

    # 3. PRICE ACTION: Breakouts
    # If Close > Previous Resistance => Breakout UP
    df['Breakout_Up'] = np.where(df['close'] > df['Resist_50'].shift(1), 1, 0)
    # If Close < Previous Support => Breakout DOWN
    df['Breakout_Down'] = np.where(df['close'] < df['Support_50'].shift(1), 1, 0)

    # 4. PRICE ACTION: Reversal Candles (Hammer / Shooting Star)
    # Hammer: Small body, long lower wick
    body = abs(df['close'] - df['open'])
    wick_lower = df[['open', 'close']].min(axis=1) - df['low']
    wick_upper = df['high'] - df[['open', 'close']].max(axis=1)
    
    # Logic: Lower wick is 2x larger than body, Upper wick is small
    df['Hammer'] = np.where((wick_lower > 2 * body) & (wick_upper < body), 1, 0)
    # Logic: Upper wick is 2x larger than body (Shooting Star)
    df['Shooting_Star'] = np.where((wick_upper > 2 * body) & (wick_lower < body), 1, 0)

    # 5. Trend Filter (Distance from EMA)
    df['Trend_Dist'] = (df['close'] - df['EMA_200']) / df['close']

    # 6. Target (Next candle Return) - For Training
    df['Target'] = np.where(df['close'].shift(-1) > df['close'], 1, 0) # 1 = Up, 0 = Down

    df.dropna(inplace=True)
    return df

if __name__ == "__main__":
    print("Refining data with Price Action & Indicators...")
    df = pd.read_csv(INPUT_FILE, index_col='timestamp', parse_dates=True)
    df = calculate_price_action(df)
    df.to_csv(OUTPUT_FILE)
    print(f"✅ Data Refined! Saved to '{OUTPUT_FILE}' with Price Action features.")