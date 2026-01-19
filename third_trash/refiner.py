import pandas as pd
import numpy as np

# --- CONFIGURATION ---
INPUT_FILE = 'btc_raw.csv'
OUTPUT_FILE = 'btc_ready.csv'

# --- HELPER FUNCTIONS (REPLACING PANDAS_TA) ---
def get_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False).mean()

def get_macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    hist = macd - macd.ewm(span=signal, adjust=False).mean()
    return macd, hist

# --- MAIN REFINER LOGIC ---
def calculate_price_action(df):
    # 1. Standard Indicators (Using Custom Functions)
    df['RSI'] = get_rsi(df['close'], 14)
    df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()
    df['ATR'] = get_atr(df, 14)
    
    # MACD
    df['MACD'], df['MACD_HIST'] = get_macd(df['close'])

    # 2. PRICE ACTION: Support & Resistance (Rolling Window)
    df['Support_50'] = df['low'].rolling(window=50).min()
    df['Resist_50'] = df['high'].rolling(window=50).max()

    # 3. PRICE ACTION: Breakouts
    df['Breakout_Up'] = np.where(df['close'] > df['Resist_50'].shift(1), 1, 0)
    df['Breakout_Down'] = np.where(df['close'] < df['Support_50'].shift(1), 1, 0)

    # 4. PRICE ACTION: Reversal Candles
    body = abs(df['close'] - df['open'])
    wick_lower = df[['open', 'close']].min(axis=1) - df['low']
    wick_upper = df['high'] - df[['open', 'close']].max(axis=1)
    
    # Hammer & Shooting Star Logic
    df['Hammer'] = np.where((wick_lower > 2 * body) & (wick_upper < body), 1, 0)
    df['Shooting_Star'] = np.where((wick_upper > 2 * body) & (wick_lower < body), 1, 0)

    # 5. Trend Filter
    df['Trend_Dist'] = (df['close'] - df['EMA_200']) / df['close']

    # 6. Target (Next candle Return)
    df['Target'] = np.where(df['close'].shift(-1) > df['close'], 1, 0)

    df.dropna(inplace=True)
    return df

if __name__ == "__main__":
    print("Refining data (Dependency Free Version)...")
    try:
        df = pd.read_csv(INPUT_FILE, index_col='timestamp', parse_dates=True)
        df = calculate_price_action(df)
        df.to_csv(OUTPUT_FILE)
        print(f"✅ Data Refined! Saved to '{OUTPUT_FILE}'.")
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{INPUT_FILE}'. Run miner.py first.")