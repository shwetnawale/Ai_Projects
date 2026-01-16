import pandas as pd
import joblib
import itertools

# --- 1. CONFIGURATION ---
INITIAL_BALANCE = 1000
LEVERAGE = 5
FEE_RATE = 0.0006

# PARAMETERS TO TEST
# We will test ALL combinations of these (Brute Force)
MODES = ['Normal', 'Inverted'] # Normal = Follow AI, Inverted = Do Opposite
TP_RANGES = [0.005, 0.010, 0.015, 0.020, 0.025] # 0.5% to 2.5%
SL_RANGES = [0.005, 0.010, 0.015, 0.020, 0.025] # 0.5% to 2.5%

# --- 2. LOAD DATA ---
print("1. Loading Data for Strategy Optimization...")
try:
    df = pd.read_csv('training_data.csv', index_col='timestamp', parse_dates=True)
    model = joblib.load('titan_optuna_model.pkl')
except:
    print("❌ Error: Missing data/model.")
    exit()

# USE TEST DATA ONLY (Last 20%)
split_point = int(len(df) * 0.8)
test_df = df.iloc[split_point:].copy()
features = ['RSI', 'MACD', 'ATR', 'SMA_50', 'Log_Ret']

# Generate Signal Probabilities
probs = model.predict_proba(test_df[features])
test_df['Prob_Up'] = probs[:, 1]
test_df['EMA_200'] = test_df['close'].ewm(span=200, adjust=False).mean()

print(f"2. Testing {len(MODES) * len(TP_RANGES) * len(SL_RANGES)} different strategies...")
print("   This determines if we should FOLLOW or FADE the bot.")

# --- 3. THE BACKTEST ENGINE FUNCTION ---
def run_backtest(mode, tp, sl):
    balance = INITIAL_BALANCE
    position = 0
    entry_price = 0
    
    # Thresholds
    LONG_CONF = 0.51
    SHORT_CONF = 0.49
    
    for i in range(len(test_df) - 1):
        current_price = test_df['close'].iloc[i]
        prob_up = test_df['Prob_Up'].iloc[i]
        ema_200 = test_df['EMA_200'].iloc[i]
        
        # LOGIC SWITCHER
        # If 'Inverted', we swap the logic (Buy becomes Sell)
        if mode == 'Inverted':
            signal_long = (prob_up < SHORT_CONF) # AI says Down -> We Buy
            signal_short = (prob_up > LONG_CONF) # AI says Up -> We Sell
        else:
            signal_long = (prob_up > LONG_CONF)
            signal_short = (prob_up < SHORT_CONF)

        # ENTRY
        if position == 0:
            # Trend Filter (Always respected)
            if current_price > ema_200 and signal_long:
                position = 1
                entry_price = current_price
                balance -= (balance * LEVERAGE * FEE_RATE)
            elif current_price < ema_200 and signal_short:
                position = -1
                entry_price = current_price
                balance -= (balance * LEVERAGE * FEE_RATE)

        # EXIT
        elif position != 0:
            if position == 1:
                pct = (current_price - entry_price) / entry_price
            else:
                pct = (entry_price - current_price) / entry_price
                
            if pct >= tp: # Win
                balance += (balance * tp * LEVERAGE)
                balance -= (balance * LEVERAGE * FEE_RATE)
                position = 0
            elif pct <= -sl: # Loss
                balance += (balance * -sl * LEVERAGE)
                balance -= (balance * LEVERAGE * FEE_RATE)
                position = 0
                
            # BANKRUPTCY CHECK
            if balance < 50: return 0

    return balance

# --- 4. BRUTE FORCE LOOP ---
results = []

for mode, tp, sl in itertools.product(MODES, TP_RANGES, SL_RANGES):
    final_bal = run_backtest(mode, tp, sl)
    results.append({
        'Mode': mode,
        'TP': tp,
        'SL': sl,
        'Balance': final_bal
    })
    # Print progress for good results
    if final_bal > 1000:
        print(f"   found: {mode} | TP: {tp*100}% | SL: {sl*100}% -> ₹{final_bal:.2f}")

# --- 5. REPORT ---
results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by='Balance', ascending=False)

print("\n" + "="*40)
print(f"🏆 TOP 3 STRATEGIES FOUND")
print("="*40)
print(results_df.head(3))
print("="*40)

best_strat = results_df.iloc[0]
if best_strat['Balance'] > 1000:
    print(f"✅ SOLUTION FOUND: Use {best_strat['Mode']} Mode.")
    print(f"   Take Profit: {best_strat['TP']*100}%")
    print(f"   Stop Loss:   {best_strat['SL']*100}%")
else:
    print("❌ SYSTEM FAILURE: Even inversion didn't work. Market is too choppy.")