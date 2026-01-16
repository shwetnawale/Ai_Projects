import pandas as pd
import numpy as np

# --- 1. CONFIGURATION ---
INPUT_FILE = 'deep_market_data.csv'  # <--- NEW FILE
OUTPUT_FILE = 'training_data.csv'

print(f"1. Loading massive dataset ({INPUT_FILE})...")
try:
    df = pd.read_csv(INPUT_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
except FileNotFoundError:
    print(f"❌ Error: '{INPUT_FILE}' not found.")
    exit()

# --- 2. MANUAL MATH INDICATORS (No Libraries) ---
print("2. Computing Indicators on 70,000+ rows...")

# Function: RSI
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Function: MACD
def calculate_macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

# Function: ATR
def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(window=period).mean()

# APPLYING THE MATH
df['RSI'] = calculate_rsi(df['close'])
df['MACD'], df['MACD_SIGNAL'] = calculate_macd(df['close'])
df['ATR'] = calculate_atr(df)
df['SMA_50'] = df['close'].rolling(window=50).mean()

# LOG RETURNS (Crucial for deep learning)
df['Log_Ret'] = np.log(df['close'] / df['close'].shift(1))

# --- 3. CREATE TARGET ---
print("3. Creating Targets...")
# Target: 1 if NEXT candle is higher, 0 if lower
df['Target'] = (df['close'].shift(-1) > df['close']).astype(int)

# --- 4. CLEAN & SAVE ---
print("4. Cleaning...")
df.dropna(inplace=True)

df.to_csv(OUTPUT_FILE)
print(f"✅ SUCCESS! Processed data saved to '{OUTPUT_FILE}'")
print(f"   Rows ready for AI: {len(df)}")