import pandas as pd
import joblib

# Load Data & Model
df = pd.read_csv('training_data.csv', index_col='timestamp', parse_dates=True)
model = joblib.load('titan_optuna_model.pkl')

# Select Test Data (Last 20%)
split_point = int(len(df) * 0.8)
test_df = df.iloc[split_point:].copy()
features = ['RSI', 'MACD', 'ATR', 'SMA_50', 'Log_Ret']

# Get Probabilities
probs = model.predict_proba(test_df[features])
test_df['Prob_Buy'] = probs[:, 1]  # Chance of "UP"

# REPORT
max_conf = test_df['Prob_Buy'].max()
avg_conf = test_df['Prob_Buy'].mean()

print("\n" + "="*40)
print(f"🕵️ DETECTIVE REPORT")
print("="*40)
print(f"Max Confidence Found: {max_conf * 100:.2f}%")
print(f"Avg Confidence:       {avg_conf * 100:.2f}%")
print("-" * 40)

if max_conf > 0.50:
    rec_threshold = max_conf - 0.01  # Set it 1% below the max
    print(f"✅ RECOMMENDATION: Set Threshold to {rec_threshold:.2f}")
else:
    print("❌ SYSTEM FAILURE: Model has zero confidence.")
print("="*40)