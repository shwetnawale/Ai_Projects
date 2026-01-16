import ccxt
import pandas as pd
import numpy as np
import joblib
import time
from datetime import datetime

# --- CONFIGURATION ---
API_KEY = 'DscZ8vmfSmjMISIvFHj2naxP7YrC2r'
SECRET_KEY = 'JbXwOP6TQUm5jPxi8fxzK8SNU1NUyPa7CU8LUYMfqHkAcyN7ErSWHRR5wuBT'

# The symbol we found in your list
SYMBOL = 'BTC/USD:USD' 
TIMEFRAME = '15m'
LEVERAGE = 5
QTY = 10 

# STRATEGY SETTINGS 
TAKE_PROFIT_PCT = 0.030  
STOP_LOSS_PCT = 0.025    
LONG_CONF = 0.51
SHORT_CONF = 0.49

# SAFETY SWITCH (Set to False to trade with REAL money)
PAPER_MODE = True  

# --- CONNECT TO DELTA INDIA ---
print("1. Connecting to Delta India...")
exchange = ccxt.delta({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'options': {'defaultType': 'future'},
    'urls': {
        'api': {
            'public': 'https://api.india.delta.exchange',
            'private': 'https://api.india.delta.exchange',
        }
    }
})

# --- LOAD BRAIN ---
print("2. Loading AI Brain...")
try:
    model = joblib.load('titan_5yr_model.pkl')
except:
    print("❌ Error: 'titan_5yr_model.pkl' not found.")
    exit()

# --- HELPER FUNCTIONS ---
def fetch_live_data():
    # Fetch 300 candles to allow 200 EMA calculation
    bars = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=300)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')
    df.set_index('timestamp', inplace=True)
    return df

def calculate_features(df):
    # 1. RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 2. MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    
    # 3. ATR
    df['tr'] = pd.concat([
        df['high'] - df['low'],
        (df['high'] - df['close'].shift()).abs(),
        (df['low'] - df['close'].shift()).abs()
    ], axis=1).max(axis=1)
    df['ATR'] = df['tr'].rolling(14).mean()
    
    # 4. Moving Averages
    df['SMA_50'] = df['close'].rolling(50).mean()
    df['EMA_200'] = df['close'].ewm(span=200).mean()
    
    # 5. Log Return
    df['Log_Ret'] = np.log(df['close'] / df['close'].shift(1))
    
    return df

# --- MAIN LOOP ---
print(f"3. Starting Titan Bot ({'PAPER' if PAPER_MODE else 'REAL'} MODE)...")
print(f"   Symbol: {SYMBOL}")

position = 0 
entry_price = 0

while True:
    try:
        print(f"\n⏳ {datetime.now().strftime('%H:%M:%S')} - Fetching market data...")
        df = fetch_live_data()
        df = calculate_features(df)
        
        current = df.iloc[-1]
        
        # Prepare data for AI
        features = current[['RSI', 'MACD', 'ATR', 'SMA_50', 'Log_Ret']].values.reshape(1, -1)
        prob_up = model.predict_proba(features)[0][1]
        
        price = current['close']
        ema_200 = current['EMA_200']
        
        print(f"   Price: ${price:.2f} | EMA 200: ${ema_200:.2f}")
        print(f"   AI Confidence: {prob_up*100:.2f}% UP")
        
        # --- ENTRY ---
        if position == 0:
            if price > ema_200 and prob_up > LONG_CONF:
                print("   🚀 SIGNAL: GO LONG!")
                if not PAPER_MODE:
                    exchange.create_market_order(SYMBOL, 'buy', QTY)
                position = 1
                entry_price = price
                
            elif price < ema_200 and prob_up < SHORT_CONF:
                print("   🔻 SIGNAL: GO SHORT!")
                if not PAPER_MODE:
                    exchange.create_market_order(SYMBOL, 'sell', QTY)
                position = -1
                entry_price = price
            else:
                print("   😴 No Trade. Waiting...")

        # --- EXIT ---
        elif position != 0:
            pct = (price - entry_price) / entry_price
            if position == -1: pct = -pct
            
            print(f"   PnL: {pct*100:.4f}%")
            
            if pct >= TAKE_PROFIT_PCT:
                print("   💰 TAKE PROFIT!")
                if not PAPER_MODE:
                    side = 'sell' if position == 1 else 'buy'
                    exchange.create_market_order(SYMBOL, side, QTY)
                position = 0
                
            elif pct <= -STOP_LOSS_PCT:
                print("   🛑 STOP LOSS!")
                if not PAPER_MODE:
                    side = 'sell' if position == 1 else 'buy'
                    exchange.create_market_order(SYMBOL, side, QTY)
                position = 0

        time.sleep(15) 

    except Exception as e:
        print(f"   ❌ Error: {e}")
        time.sleep(5)