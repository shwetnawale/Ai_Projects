import time

# --- ⚠️ GOD MODE TIME FIX ⚠️ ---
# We overwrite the system time logic BEFORE loading anything else.
# Your PC is ~12s slow. We add 15s to be safe (+3s ahead of server).
original_time = time.time
def patched_time():
    return original_time() + 15.0 # Force +15 seconds
time.time = patched_time
print(f"   ⏱️ SYSTEM TIME HACKED: Added +15 seconds.")

# ---------------------------------------------------------
import ccxt
import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime

# --- CONFIGURATION ---
API_KEY = '6vsMK1JvvJn1v5FewdmPpvyg0HVPIK'
SECRET_KEY = 'ZbX7FTKKQnuJUOwJ0hHRZllloaawo1Aw5KWQFK5ji2c2Iha3nJo1E0IwzoWi'
SYMBOL = 'BTC/USD:USD' 
TIMEFRAME = '15m'
QTY = 10 

# STRATEGY SETTINGS
TAKE_PROFIT_PCT = 0.030  
STOP_LOSS_PCT = 0.025    
LONG_CONF = 0.51
SHORT_CONF = 0.51 # Relaxed to ensure immediate trade

LOG_FILE = 'titan_paper_trades.csv'

# --- CONNECT ---
print("1. Connecting to Delta Exchange (India Testnet)...")
exchange = ccxt.delta({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'options': {'defaultType': 'future'}, # No special time options needed, we hacked time.time()
    'urls': {
        'api': {
            'public': 'https://cdn-ind.testnet.deltaex.org',
            'private': 'https://cdn-ind.testnet.deltaex.org',
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

# --- LOGGING ---
def log_trade(action, price, reason, pnl=0):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_row = pd.DataFrame([{
        'Time': timestamp, 'Action': action, 'Price': price, 'Reason': reason, 'PnL_Pct': pnl
    }])
    if not os.path.exists(LOG_FILE):
        new_row.to_csv(LOG_FILE, index=False)
    else:
        new_row.to_csv(LOG_FILE, mode='a', header=False, index=False)
    print(f"   📝 Logged: {action} @ {price}")

# --- DATA HELPERS ---
def fetch_live_data():
    try:
        bars = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=300)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df['timestamp'] = df['timestamp'].dt.tz_convert('Asia/Kolkata')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"   ⚠️ Data Fetch Error: {e}")
        return pd.DataFrame()

def calculate_features(df):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    
    df['tr'] = pd.concat([
        df['high'] - df['low'], (df['high'] - df['close'].shift()).abs(), (df['low'] - df['close'].shift()).abs()
    ], axis=1).max(axis=1)
    df['ATR'] = df['tr'].rolling(14).mean()
    
    df['SMA_50'] = df['close'].rolling(50).mean()
    df['EMA_200'] = df['close'].ewm(span=200).mean()
    df['Log_Ret'] = np.log(df['close'] / df['close'].shift(1))
    return df

# --- MAIN LOOP ---
print(f"3. Starting Titan Bot (DEMO MODE)...")
print(f"   Symbol: {SYMBOL}")

position = 0 
entry_price = 0

while True:
    try:
        print(f"\n⏳ {datetime.now().strftime('%H:%M:%S')} - Fetching market data...")
        df = fetch_live_data()
        
        if df.empty:
            time.sleep(5)
            continue

        df = calculate_features(df)
        current = df.iloc[-1]
        
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
                exchange.create_market_order(SYMBOL, 'buy', QTY)
                position = 1
                entry_price = price
                log_trade('BUY_LONG', price, f"Conf: {prob_up:.2f}")
                print("   ✅ ORDER FILLED ON DEMO!")
                
            elif price < ema_200 and prob_up < SHORT_CONF:
                print("   🔻 SIGNAL: GO SHORT!")
                exchange.create_market_order(SYMBOL, 'sell', QTY)
                position = -1
                entry_price = price
                log_trade('SELL_SHORT', price, f"Conf: {prob_up:.2f}")
                print("   ✅ ORDER FILLED ON DEMO!")
            else:
                print("   😴 No Trade. Waiting...")

        # --- EXIT ---
        elif position != 0:
            pct = (price - entry_price) / entry_price
            if position == -1: pct = -pct
            print(f"   PnL: {pct*100:.4f}%")
            
            if pct >= TAKE_PROFIT_PCT:
                print("   💰 TAKE PROFIT!")
                side = 'sell' if position == 1 else 'buy'
                exchange.create_market_order(SYMBOL, side, QTY)
                position = 0
                log_trade('EXIT_WIN', price, "Target Hit", pct)
            elif pct <= -STOP_LOSS_PCT:
                print("   🛑 STOP LOSS!")
                side = 'sell' if position == 1 else 'buy'
                exchange.create_market_order(SYMBOL, side, QTY)
                position = 0
                log_trade('EXIT_LOSS', price, "Stop Hit", pct)

        time.sleep(15) 

    except Exception as e:
        print(f"   ❌ Error: {e}")
        time.sleep(15)