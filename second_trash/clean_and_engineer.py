import pandas as pd
import numpy as np

# --- CONFIG ---
INPUT_FILE = 'btc_5yr_raw.csv'
OUTPUT_FILE = 'btc_5yr_training.csv'

print(f"1. Loading Raw Data: {INPUT_FILE}...")
try:
    df = pd.read_csv(INPUT_FILE, index_col='timestamp', parse_dates=True)
except FileNotFoundError:
    print("❌ Error: Run Step 1 first.")
    exit()

original_rows = len(df)

# --- A. CLEANING (THE SURGERY) ---
print("2. Scrubbing Data...")

# 1. Remove Duplicate Times (If Binance sent overlaps)
df = df[~df.index.duplicated(keep='first')]

# 2. Sort Index (Crucial for time series)
df.sort_index(inplace=True)

# 3. Check for Flatlines (Zero volume or No price movement)
# We allow some low volume, but purely 0 volume often means exchange downtime
df = df[df['volume'] > 0] 

# --- B. FEATURE ENGINEERING (THE MATH) ---
print("3. Calculating Advanced Indicators...")

# RSI (Relative Strength Index)
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# MACD
def calculate_macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    return macd

# ATR (Volatility)
df['tr1'] = df['high'] - df['low']
df['tr2'] = (df['high'] - df['close'].shift()).abs()
df['tr3'] = (df['low'] - df['close'].shift()).abs()
df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
df['ATR'] = df['tr'].rolling(14).mean()

# Indicators
df['RSI'] = calculate_rsi(df['close'])
df['MACD'] = calculate_macd(df['close'])
df['SMA_50'] = df['close'].rolling(50).mean()
df['EMA_200'] = df['close'].ewm(span=200).mean() # The "God Line" for Hybrid Logic

# Log Returns (Normalized price movement)
df['Log_Ret'] = np.log(df['close'] / df['close'].shift(1))

# --- C. CREATE TARGET (The Answer Key) ---
# Target = 1 if NEXT candle is higher, 0 if lower
df['Target'] = (df['close'].shift(-1) > df['close']).astype(int)

# Drop NaN values created by indicators (first 200 rows)
df.dropna(inplace=True)

# Save
df.to_csv(OUTPUT_FILE)

print("\n" + "="*40)
print(f"✅ DATA READY FOR AI")
print(f"Original: {original_rows} candles")
print(f"Cleaned:  {len(df)} candles")
print(f"Saved to: {OUTPUT_FILE}")
print("="*40)