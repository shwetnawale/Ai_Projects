import pandas as pd
import joblib
import itertools

# --- CONFIGURATION ---
LEVERAGE = 5
FEE_RATE = 0.0006  # 0.06% Exchange Fee

# SEARCH GRID (We test all combinations)
# Normal = Trust the AI. Inverted = Bet against it (just in case).
MODES = ['Normal', 'Inverted'] 
# Take Profit & Stop Loss ranges (0.5% to 3.0%)
TP_RANGES = [0.005, 0.010, 0.015, 0.020, 0.025, 0.030]
SL_RANGES = [0.005, 0.010, 0.015, 0.020, 0.025, 0.030]

print("1. Loading 5-Year Engine...")
try:
    df = pd.read_csv('btc_5yr_training.csv', index_col='timestamp', parse_dates=True)
    model = joblib.load('titan_5yr_model.pkl')
except:
    print("❌ Error: Missing data/model. Run previous steps.")
    exit()

# --- PREPARE TEST DATA ---
# We test on the last 15% (Recent 2024-2025 data)
split_point = int(len(df) * 0.85)
test_df = df.iloc[split_point:].copy()
features = ['RSI', 'MACD', 'ATR', 'SMA_50', 'Log_Ret']

print(f"2. Generating Signals for {len(test_df)} candles...")
probs = model.predict_proba(test_df[features])
test_df['Prob_Up'] = probs[:, 1]
test_df['EMA_200'] = test_df['close'].ewm(span=200, adjust=False).mean()

# --- BACKTEST FUNCTION ---
def run_backtest(mode, tp, sl):
    balance = 1000  # Start with ₹1000
    position = 0    # 0=Cash, 1=Long, -1=Short
    entry_price = 0
    
    # THRESHOLDS (Slightly relaxed to allow the Hybrid Filter to work)
    LONG_CONF = 0.51
    SHORT_CONF = 0.49
    
    for i in range(len(test_df) - 1):
        current_price = test_df['close'].iloc[i]
        prob_up = test_df['Prob_Up'].iloc[i]
        ema_200 = test_df['EMA_200'].iloc[i]
        
        # 1. DETERMINE SIGNAL
        if mode == 'Normal':
            is_buy_signal = (prob_up > LONG_CONF)
            is_sell_signal = (prob_up < SHORT_CONF)
        else: # Inverted
            is_buy_signal = (prob_up < SHORT_CONF)
            is_sell_signal = (prob_up > LONG_CONF)
            
        # 2. ENTRY LOGIC (HYBRID FILTER)
        # "Only Long above EMA 200, Only Short below EMA 200"
        if position == 0:
            # Bullish Trend -> Look for Longs
            if current_price > ema_200 and is_buy_signal:
                position = 1
                entry_price = current_price
                balance -= (balance * LEVERAGE * FEE_RATE) # Entry Fee
                
            # Bearish Trend -> Look for Shorts
            elif current_price < ema_200 and is_sell_signal:
                position = -1
                entry_price = current_price
                balance -= (balance * LEVERAGE * FEE_RATE) # Entry Fee

        # 3. EXIT LOGIC (BRACKET)
        elif position != 0:
            # Calculate PnL %
            if position == 1:
                pct = (current_price - entry_price) / entry_price
            else:
                pct = (entry_price - current_price) / entry_price
            
            # Check TP / SL
            if pct >= tp: # WIN
                balance += (balance * tp * LEVERAGE)
                balance -= (balance * LEVERAGE * FEE_RATE) # Exit Fee
                position = 0
            elif pct <= -sl: # LOSS
                balance += (balance * -sl * LEVERAGE)
                balance -= (balance * LEVERAGE * FEE_RATE) # Exit Fee
                position = 0
                
            # Bankruptcy Protection
            if balance < 100: return 0

    return balance

# --- RUN OPTIMIZATION ---
print(f"3. Testing {len(MODES)*len(TP_RANGES)*len(SL_RANGES)} strategies...")
results = []

for mode, tp, sl in itertools.product(MODES, TP_RANGES, SL_RANGES):
    final_bal = run_backtest(mode, tp, sl)
    results.append({'Mode': mode, 'TP': tp, 'SL': sl, 'Balance': final_bal})
    
    # Live update for good results
    if final_bal > 1200:
        print(f"   ✨ Found: {mode} | TP: {tp*100}% | SL: {sl*100}% -> ₹{final_bal:.2f}")

# --- REPORT ---
results_df = pd.DataFrame(results).sort_values(by='Balance', ascending=False)
print("\n" + "="*40)
print(f"🏆 TOP 3 PROFITABLE STRATEGIES")
print("="*40)
print(results_df.head(3))
print("="*40)

best = results_df.iloc[0]
if best['Balance'] > 1000:
    print(f"✅ WINNER: Use {best['Mode']} Mode")
    print(f"   Take Profit: {best['TP']*100}%")
    print(f"   Stop Loss:   {best['SL']*100}%")
    print(f"   Est. Profit: {((best['Balance']-1000)/1000)*100:.2f}%")
else:
    print("❌ Analysis: Market conditions were extremely difficult.")