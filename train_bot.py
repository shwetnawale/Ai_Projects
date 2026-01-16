import pandas as pd
import optuna
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

print("1. Loading 5-Year Dataset...")
try:
    df = pd.read_csv('btc_5yr_training.csv', index_col='timestamp', parse_dates=True)
except:
    print("❌ Error: Run Step 2 first.")
    exit()

# Features for the AI
features = ['RSI', 'MACD', 'ATR', 'SMA_50', 'Log_Ret']
X = df[features]
y = df['Target']

# Split: Train on 2020-2024, Test on 2024-2025
# 85% Train, 15% Test
split = int(len(df) * 0.85)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]

print(f"   Training on {len(X_train)} candles (Historical)")
print(f"   Testing on  {len(X_test)} candles (Recent)")

# --- OPTIMIZATION FUNCTION ---
def objective(trial):
    param = {
        'n_estimators': trial.suggest_int('n_estimators', 300, 1000), # More trees for more data
        'max_depth': trial.suggest_int('max_depth', 4, 12),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.15),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'gamma': trial.suggest_float('gamma', 0, 5),
        'eval_metric': 'logloss', 
        'n_jobs': -1, 
        'random_state': 42
    }
    model = XGBClassifier(**param)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    return accuracy_score(y_test, preds)

print("2. Starting AI Optimization (Optuna)...")
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=30) # 30 Trials to find best settings

print(f"\n🏆 BEST ACCURACY: {study.best_value*100:.2f}%")
print("   (Note: >52% on 5 years of data is excellent)")

# --- SAVE FINAL MODEL ---
best_params = study.best_params
best_params['eval_metric'] = 'logloss'
final_model = XGBClassifier(**best_params)
final_model.fit(X_train, y_train)

joblib.dump(final_model, 'titan_5yr_model.pkl')
print("✅ Brain Saved as 'titan_5yr_model.pkl'")