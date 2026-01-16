import pandas as pd
import numpy as np

# --- CONFIGURATION ---
INPUT_FILE = 'training_data.csv'
OUTPUT_FILE = 'clean_training_data.csv'

print(f"1. Loading damaged dataset: {INPUT_FILE}...")
try:
    df = pd.read_csv(INPUT_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
except FileNotFoundError:
    print("❌ Error: File not found.")
    exit()

original_count = len(df)
print(f"   Original Rows: {original_count}")

# --- SURGERY STEP 1: REMOVE FLATLINES ---
# If High == Low, the price didn't move. This is often an API error for Bitcoin.
# We also check if Volume is 0 or 1.
print("2. Removing 'Zombie' candles (Flatlines)...")
df = df[df['high'] != df['low']]  # Drop rows where price didn't move AT ALL
df = df[df['volume'] > 10]        # Drop rows with near-zero volume

# --- SURGERY STEP 2: REMOVE GAPS ---
# We calculate the time difference between candles.
# If a gap is > 1 hour, we can't trust the indicators (RSI/MACD) around it.
# Strategy: Instead of complex filling, we will just DROP the older data
# and keep the most recent continuous chunk.

print("3. Checking for Time Gaps...")
df = df.sort_index()
df['time_diff'] = df.index.to_series().diff()

# Find the last major gap (e.g., > 1 hour)
gap_threshold = pd.Timedelta(hours=1)
gaps = df[df['time_diff'] > gap_threshold]

if len(gaps) > 0:
    last_gap_time = gaps.index[-1]
    print(f"   ⚠️ Found massive gap at {last_gap_time}")
    print("   ✂️ CUTTING all data before this gap to ensure integrity.")
    
    # Keep only data AFTER the last gap
    df = df[df.index > last_gap_time]
else:
    print("   ✅ No major time gaps found.")

# --- SURGERY STEP 3: RE-CALCULATE INDICATORS ---
# Since we cut rows, the old RSI/MACD values at the start might be wrong.
# We must re-run the math.
print("4. Re-calculating Indicators on clean data...")

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['RSI'] = calculate_rsi(df['close'])
df['SMA_50'] = df['close'].rolling(window=50).mean()
df['Log_Ret'] = np.log(df['close'] / df['close'].shift(1))

# Clean up any NaNs from the new calculations
df.dropna(inplace=True)

# --- SAVE ---
count_after = len(df)
removed = original_count - count_after

print("\n" + "="*40)
print(f"✅ SURGERY COMPLETE")
print(f"Removed: {removed} bad rows")
print(f"Remaining: {count_after} clean rows")
print(f"New Start Date: {df.index[0]}")
print(f"New End Date:   {df.index[-1]}")
print(f"Saved to: '{OUTPUT_FILE}'")
print("="*40)

df.to_csv(OUTPUT_FILE)