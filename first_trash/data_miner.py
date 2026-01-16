import ccxt
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURATION ---
# ⚠️ SECURITY WARNING: Never share your Secret Key online. 
# I have kept your keys here so the code runs, but regenerate them later!
exchange = ccxt.delta({
    'apiKey': 'DscZ8vmfSmjMISIvFHj2naxP7YrC2r',
    'secret': 'JbXwOP6TQUm5jPxi8fxzK8SNU1NUyPa7CU8LUYMfqHkAcyN7ErSWHRR5wuBT',
    'options': {'defaultType': 'future'},
    'urls': {
        'api': {
            'public': 'https://api.india.delta.exchange',
            'private': 'https://api.india.delta.exchange',
        }
    }
})

symbol = 'BTC/USD:USD'
timeframe = '15m'
START_DATE = '2024-01-01 00:00:00' # Fetch data starting from here

def fetch_deep_history():
    print(f"⛏️ STARTING MINING ON DELTA EXCHANGE ({symbol})...")
    
    # 1. Setup Timestamps
    # Convert '2024-01-01' to milliseconds (Unix Timestamp)
    since = exchange.parse8601(pd.Timestamp(START_DATE).isoformat())
    now = exchange.milliseconds()
    
    all_candles = []
    
    # 2. The Pagination Loop
    while since < now:
        try:
            print(f"   Fetching from {exchange.iso8601(since)}...")
            
            # Fetch batch of candles
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            
            if not ohlcv:
                print("   ⚠️ No data returned. Mining complete or gap found.")
                break
            
            # Add to our list
            all_candles.extend(ohlcv)
            
            # UPDATE 'since': Set it to the time of the LAST candle + 1ms
            # This tells Delta: "Give me data starting immediately after the last one"
            last_candle_time = ohlcv[-1][0]
            since = last_candle_time + 1
            
            # Sleep to respect Rate Limits (Delta is strict!)
            time.sleep(1) 
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print("   Retrying in 5 seconds...")
            time.sleep(5)
            continue

    # 3. Save to CSV
    print(f"🔨 Refining {len(all_candles)} candles...")
    
    df = pd.DataFrame(all_candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Convert Timestamp to Readable Date (IST)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')
    
    # Set Index
    df.set_index('timestamp', inplace=True)
    
    # Remove duplicates (Just in case)
    df = df[~df.index.duplicated(keep='first')]
    
    # Save
    filename = 'deep_market_data.csv'
    df.to_csv(filename)
    
    print("\n" + "="*40)
    print(f"✅ SUCCESS! Data saved to '{filename}'")
    print(f"📊 Total Candles: {len(df)}")
    print(f"📅 Start Date:    {df.index[0]}")
    print(f"📅 End Date:      {df.index[-1]}")
    print("="*40)

if __name__ == "__main__":
    fetch_deep_history()