import ccxt
import pandas as pd
import numpy as np
import joblib
import time
import os
import requests
import hashlib
import hmac
from datetime import datetime

# --- 1. CONFIG IMPORT (SIMPLIFIED) ---
# Now that User_data.py is in the same folder, we just import it directly.
try:
    import User_data
    print("✅ Loaded API Keys from User_data.py")
except ImportError:
    print("❌ ERROR: Could not find 'User_data.py'.")
    print("   👉 Please MOVE 'User_data.py' out of the config folder and put it next to live.py.")
    exit()

# --- 2. ASSIGN KEYS ---
API_KEY = User_data.API_KEY
SECRET_KEY = User_data.SECRET_KEY

SYMBOL = 'BTC/USD:USD'  
TIMEFRAME = '15m'
RISK_PER_TRADE = 0.01  # 1% Risk
MAX_LEVERAGE = 10      # Start low

# FILE PATHS
MODEL_FILE = 'brain.pkl'
LOG_FILE = 'live_logs.csv'

# --- HELPER FUNCTIONS ---
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
    return macd

# --- 3. TIME SYNC ---
def get_time_offset():
    try:
        resp = requests.get('https://api.india.delta.exchange/v2/server_time')
        if resp.status_code == 200:
            server_time = int(resp.json()['result']) 
            local_time = int(time.time())
            diff = (server_time - local_time) * 1000
            return diff + 1000 
    except Exception as e:
        print(f"⚠️ Time Sync Failed: {e}")
    return 0 

offset = get_time_offset()
print(f"⏳ Time Offset applied: {offset}ms")

# --- 4. CONNECT TO LIVE INDIA EXCHANGE ---
print(f"2. Connecting to Delta India (Live)...")
exchange = ccxt.delta({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'options': {
        'defaultType': 'future',
        'adjustForTimeDifference': False,
        'timeDifference': offset
    },
    'urls': {
        'api': {
            'public': 'https://api.india.delta.exchange',
            'private': 'https://api.india.delta.exchange',
        }
    }
})

# --- 5. LOAD BRAIN ---
try:
    model = joblib.load(MODEL_FILE)
except:
    print(f"❌ Error: {MODEL_FILE} not found.")
    exit()

# --- 6. DEPTH & FLOW ---
def analyze_market_depth():
    try:
        ob = exchange.fetch_order_book(SYMBOL, limit=50)
        bids_vol = sum([x[1] for x in ob['bids']])
        asks_vol = sum([x[1] for x in ob['asks']])
        ob_imbalance = (bids_vol - asks_vol) / (bids_vol + asks_vol)

        trades = exchange.fetch_trades(SYMBOL, limit=100)
        buy_vol = sum([t['amount'] for t in trades if t['side'] == 'buy'])
        sell_vol = sum([t['amount'] for t in trades if t['side'] == 'sell'])
        
        if (buy_vol + sell_vol) > 0:
            flow_imbalance = (buy_vol - sell_vol) / (buy_vol + sell_vol)
        else:
            flow_imbalance = 0
            
        final_score = (ob_imbalance * 0.4) + (flow_imbalance * 0.6)
        return final_score, bids_vol, asks_vol
    except:
        return 0, 0, 0

# --- 7. LEVERAGE ---
def calculate_dynamic_leverage(entry, sl):
    sl_dist_pct = abs(entry - sl) / entry
    if sl_dist_pct == 0: return 1
    safe_leverage = 1 / (sl_dist_pct + 0.005) 
    final_lev = min(int(safe_leverage), MAX_LEVERAGE)
    return max(1, final_lev)

# --- 8. PROCESS DATA ---
def process_data(df):
    df['RSI'] = get_rsi(df['close'])
    df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()
    df['ATR'] = get_atr(df)
    df['MACD'] = get_macd(df['close'])
    
    df['Support_50'] = df['low'].rolling(window=50).min()
    df['Resist_50'] = df['high'].rolling(window=50).max()
    df['Breakout_Up'] = np.where(df['close'] > df['Resist_50'].shift(1), 1, 0)
    df['Breakout_Down'] = np.where(df['close'] < df['Support_50'].shift(1), 1, 0)
    
    body = abs(df['close'] - df['open'])
    wick_lower = df[['open', 'close']].min(axis=1) - df['low']
    wick_upper = df['high'] - df[['open', 'close']].max(axis=1)
    df['Hammer'] = np.where((wick_lower > 2 * body) & (wick_upper < body), 1, 0)
    df['Shooting_Star'] = np.where((wick_upper > 2 * body) & (wick_lower < body), 1, 0)
    
    df['Trend_Dist'] = (df['close'] - df['EMA_200']) / df['close']
    return df.iloc[-1] 

# --- 9. LOGGING ---
def log_analysis(row, conf, ob_score, action):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {'Time': ts, 'Price': row['close'], 'AI_Conf': round(conf, 2), 'OB_Score': round(ob_score, 2), 'Action': action}
    df_log = pd.DataFrame([data])
    if not os.path.exists(LOG_FILE):
        df_log.to_csv(LOG_FILE, index=False)
    else:
        df_log.to_csv(LOG_FILE, mode='a', header=False, index=False)
    
    emoji = "😐"
    if ob_score > 0.2: emoji = "🟢 Bullish"
    if ob_score < -0.2: emoji = "🔴 Bearish"
    print(f"📊 {ts} | P: {row['close']} | AI: {conf:.2f} | Depth: {ob_score:.2f} {emoji} | Act: {action}")

# --- 10. RESTART CHECK ---
print("♻️  Checking for existing positions...")
position = 0
try:
    positions = exchange.fetch_positions()
    open_pos = [p for p in positions if p['symbol'] == SYMBOL and float(p['size']) > 0]
    
    if open_pos:
        existing = open_pos[0]
        side = existing['side']
        print(f"⚠️ FOUND OPEN POSITION: {side.upper()} {existing['size']} contracts")
        if side == 'long': position = 1
        else: position = -1
    else:
        print("✅ No open positions. Starting fresh.")
except Exception as e:
    print(f"❌ AUTH ERROR: {e}")
    print("👉 Double check your keys in User_data.py!")
    exit()

# --- 11. MAIN LOOP ---
print("🤖 Starting LIVE TRADING BOT (REAL MONEY)...")
while True:
    try:
        candles = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=100)
        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        current = process_data(df)
        
        features = [[
            current['RSI'], current['MACD'], current['ATR'], current['Trend_Dist'],
            current['Breakout_Up'], current['Breakout_Down'], 
            current['Hammer'], current['Shooting_Star']
        ]]
        prob_up = model.predict_proba(features)[0][1]
        
        ob_score, bids, asks = analyze_market_depth()
        
        price = current['close']
        atr = current['ATR']
        action = "WAIT"
        
        # DECISION LOGIC
        if position == 0 and prob_up > 0.60 and ob_score > -0.1:
            if bids * 3 > asks: 
                action = "BUY"
                sl_price = price - (2 * atr)
                lev = calculate_dynamic_leverage(price, sl_price)
                
                print(f"🚀 ENTER LONG | Lev: {lev}x | SL: {sl_price:.2f}")
                exchange.set_leverage(lev, SYMBOL)
                exchange.create_order(SYMBOL, 'market', 'buy', 1) 
                exchange.create_order(SYMBOL, 'stop_market', 'sell', 1, {'stopPrice': sl_price})
                position = 1

        elif position == 0 and prob_up < 0.40 and ob_score < 0.1:
            if asks * 3 > bids: 
                action = "SELL"
                sl_price = price + (2 * atr)
                lev = calculate_dynamic_leverage(price, sl_price)
                
                print(f"🔻 ENTER SHORT | Lev: {lev}x | SL: {sl_price:.2f}")
                exchange.set_leverage(lev, SYMBOL)
                exchange.create_order(SYMBOL, 'market', 'sell', 1) 
                exchange.create_order(SYMBOL, 'stop_market', 'buy', 1, {'stopPrice': sl_price})
                position = -1
        
        if position != 0:
            pos_check = [p for p in exchange.fetch_positions() if p['symbol'] == SYMBOL and float(p['size']) > 0]
            if not pos_check:
                print("💰 Position Closed. Resetting.")
                position = 0

        log_analysis(current, prob_up, ob_score, action)
        time.sleep(15)

    except Exception as e:
        print(f"⚠️ Loop Error: {e}")
        time.sleep(15)