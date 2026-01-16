import pandas as pd
import joblib
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION ---
INITIAL_BALANCE = 1000  # ₹1000 Starting Capital
LEVERAGE = 5            # 5x Leverage (Safe for beginners)
FEE_RATE = 0.0005       # 0.05% per trade (Standard Exchange Fee)
STOP_LOSS_PCT = 0.02    # 2% Stop Loss (Risk Management)

# --- 2. LOAD RESOURCES ---
print("1. Loading the Titan Engine...")
try:
    df = pd.read_csv('training_data.csv', index_col='timestamp', parse_dates=True)
    model = joblib.load('titan_optuna_model.pkl')
except FileNotFoundError:
    print("❌ Error: Missing data or model. Run previous steps.")
    exit()

# --- 3. PREPARE TEST DATA ---
# We only backtest on the last 20% of data (The "Test Set")
# We strictly cannot test on data the model was trained on!
split_point = int(len(df) * 0.8)
test_df = df.iloc[split_point:].copy()

# Select the features exactly as we trained them
features = ['RSI', 'MACD', 'ATR', 'SMA_50', 'Log_Ret']
X_test = test_df[features]

print(f"2. Simulating trading on {len(test_df)} candles...")

# --- 4. RUN THE SIMULATION (The Loop) ---
# Generate all predictions at once (Vectorized is faster, but loop is clearer for logic)
test_df['Signal'] = model.predict(X_test)

balance = INITIAL_BALANCE
position = 0  # 0 = No Position, 1 = Long (Bought)
entry_price = 0
balance_history = [balance]
trades = []

print("3. Trading in progress...")

for i in range(len(test_df) - 1):
    current_price = test_df['close'].iloc[i]
    next_price = test_df['close'].iloc[i+1] # We exit at the next candle close for simulation
    signal = test_df['Signal'].iloc[i]
    
    # LOGIC:
    # If Signal is 1 (Buy) and we have no position -> BUY
    if signal == 1 and position == 0:
        position = 1
        entry_price = current_price
        # Pay Fee (Entry)
        cost = balance * LEVERAGE
        fee = cost * FEE_RATE
        balance -= fee
        
    # If Signal is 0 (Sell) and we have a position -> SELL
    elif signal == 0 and position == 1:
        position = 0
        exit_price = current_price
        
        # Calculate Profit/Loss
        # (Exit - Entry) / Entry * Leverage * Balance
        raw_return = (exit_price - entry_price) / entry_price
        pnl = (balance * raw_return * LEVERAGE)
        
        # Pay Fee (Exit)
        fee = (balance * LEVERAGE) * FEE_RATE
        
        # Update Balance
        balance += pnl - fee
        trades.append(pnl - fee)
        
    # STOP LOSS CHECK (Safety Mechanism)
    # If price drops 2% below entry, force sell immediately
    elif position == 1:
        current_drawdown = (current_price - entry_price) / entry_price
        if current_drawdown < -STOP_LOSS_PCT:
            position = 0 # Force Sell
            pnl = (balance * -STOP_LOSS_PCT * LEVERAGE)
            fee = (balance * LEVERAGE) * FEE_RATE
            balance += pnl - fee
            trades.append(pnl - fee)
            
    # Record balance for the graph
    balance_history.append(balance)

# --- 5. REPORT CARD ---
final_balance = balance
profit = final_balance - INITIAL_BALANCE
roi = (profit / INITIAL_BALANCE) * 100
win_rate = len([t for t in trades if t > 0]) / len(trades) * 100 if len(trades) > 0 else 0

print("\n" + "="*40)
print(f"💰 FINAL RESULTS (Simulated)")
print("="*40)
print(f"Start Balance:   ₹{INITIAL_BALANCE:.2f}")
print(f"Final Balance:   ₹{final_balance:.2f}")
print(f"Total Profit:    ₹{profit:.2f} ({roi:.2f}%)")
print(f"Total Trades:    {len(trades)}")
print(f"Win Rate:        {win_rate:.2f}%")
print("="*40)

# --- 6. VISUALIZE ---
plt.figure(figsize=(10, 6))
plt.plot(balance_history, label='Wallet Balance (₹)', color='green')
plt.title(f"Titan Bot Performance (Accuracy: 57%)")
plt.xlabel("Time (Candles)")
plt.ylabel("Balance in Rupees")
plt.axhline(y=INITIAL_BALANCE, color='r', linestyle='--', label='Start Capital')
plt.legend()
plt.grid(True)
plt.show()