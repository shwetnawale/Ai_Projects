import ccxt
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURATION ---
SYMBOL = 'BTC/USDT'     # Binance uses USDT pairs
TIMEFRAME = '15m'       # Best for AI
START_DATE = '2020-01-01 00:00:00'
FILENAME = 'Data/btc_raw.csv'

def fetch_data():
    print(f"1. Connecting to Binance to fetch history from {START_DATE}...")
    exchange = ccxt.binance()
    since = exchange.parse8601(START_DATE)
    all_candles = []

    while since < exchange.milliseconds():
        try:
            candles = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, since=since, limit=1000)
            if not candles:
                break
            
            since = candles[-1][0] + 1 # Move time forward
            all_candles += candles
            
            # Progress update
            current_date = datetime.fromtimestamp(since/1000)
            print(f"   Fetched up to: {current_date}")
            time.sleep(0.1) # Be polite to API
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
            time.sleep(5)

    # Save
    df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    df.to_csv(FILENAME)
    print(f"✅ Success! Saved {len(df)} candles to '{FILENAME}'")

if __name__ == "__main__":
    fetch_data()