import ccxt
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURATION ---
# We use Binance because it has the cleanest 5-year history (No API keys needed for public data)
exchange = ccxt.binance({'enableRateLimit': True})
symbol = 'BTC/USDT'
timeframe = '15m'
START_DATE = '2020-01-01 00:00:00'

def fetch_5_years():
    print(f"⛏️ STARTING 5-YEAR MINE: {symbol} since {START_DATE}...")
    
    # Convert Start Date to Milliseconds
    since = exchange.parse8601(pd.Timestamp(START_DATE).isoformat())
    now = exchange.milliseconds()
    
    all_candles = []
    batch_count = 0
    
    while since < now:
        try:
            # Fetch 1000 candles
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            
            if not ohlcv:
                print("   ⚠️ No more data received.")
                break
            
            all_candles.extend(ohlcv)
            
            # Update 'since' pointer to the end of this batch
            since = ohlcv[-1][0] + 1
            batch_count += 1
            
            # Show progress every 10 batches
            if batch_count % 10 == 0:
                current_date = pd.to_datetime(ohlcv[-1][0], unit='ms')
                print(f"   Now at: {current_date} | Total: {len(all_candles)} candles")
            
            # Sleep to be polite to Binance API
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ Network Error: {e}. Retrying in 5s...")
            time.sleep(5)

    # --- SAVE ---
    print(f"💾 Saving {len(all_candles)} candles to CSV...")
    df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Formatting
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata') # Adjust to your timezone
    df.set_index('timestamp', inplace=True)
    
    # Save Raw Data
    filename = 'btc_5yr_raw.csv'
    df.to_csv(filename)
    
    print("\n" + "="*40)
    print(f"✅ MISSION COMPLETE")
    print(f"Filesize: ~15-20 MB")
    print(f"Rows:     {len(df)}")
    print(f"From:     {df.index[0]}")
    print(f"To:       {df.index[-1]}")
    print("="*40)

if __name__ == "__main__":
    fetch_5_years()