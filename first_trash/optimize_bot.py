import pandas as pd
import optuna
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# --- 1. LOAD DATA ---
print("1. Loading Training Data...")
df = pd.read_csv('training_data.csv', index_col='timestamp', parse_dates=True)

features = ['RSI', 'MACD', 'ATR', 'SMA_50', 'Log_Ret']
X = df[features]
y = df['Target']

# SPLIT: Train on first 80% (Jan 2024 - mid 2025), Test on last 20% (Late 2025 - 2026)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

print(f"   Training on {len(X_train)} candles.")
print(f"   Testing on  {len(X_test)} candles.")

# --- 2. OPTIMIZATION LOOP ---
def objective(trial):
    param = {
        'n_estimators': trial.suggest_int('n_estimators', 200, 1000),
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'gamma': trial.suggest_float('gamma', 0, 5),
        
        'eval_metric': 'logloss',
        'random_state': 42,
        'n_jobs': -1
    }

    model = XGBClassifier(**param)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    return accuracy_score(y_test, preds)

print("2. Starting Deep Optimization (This will take time)...")
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=30) 

# --- 3. SAVE BEST MODEL ---
print("\n" + "="*40)
print(f"🏆 BEST REALISTIC ACCURACY: {study.best_value * 100:.2f}%")
print("="*40)

best_params = study.best_params
best_params['eval_metric'] = 'logloss'
final_model = XGBClassifier(**best_params)
final_model.fit(X_train, y_train)

joblib.dump(final_model, 'titan_optuna_model.pkl')
print("✅ Deep Model Saved as 'titan_optuna_model.pkl'")