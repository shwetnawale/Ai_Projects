import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

# --- 1. LOAD THE REFINED FUEL ---
print("1. Loading training data...")
try:
    df = pd.read_csv('training_data.csv', index_col='timestamp', parse_dates=True)
except FileNotFoundError:
    print("❌ Error: 'training_data.csv' not found.")
    exit()

# --- 2. SEPARATE FEATURES (X) AND TARGET (y) ---
# We use the indicators we created manually
features = ['RSI', 'MACD', 'ATR', 'SMA_50', 'Log_Ret']
X = df[features]
y = df['Target']

# --- 3. SPLIT DATA (NO SHUFFLING!) ---
# Vital: Keep the order intact for time-series data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

print(f"2. Training XGBoost on {len(X_train)} candles...")
print(f"   Testing on {len(X_test)} candles...")

# --- 4. TRAIN THE "FERRARI" (XGBoost) ---
# n_estimators: Number of boosting rounds
# learning_rate: How fast it learns (lower is slower but more precise)
# max_depth: How complex each tree is
model = XGBClassifier(
    n_estimators=200, 
    learning_rate=0.05, 
    max_depth=5, 
    eval_metric='logloss',
    use_label_encoder=False,
    random_state=42
)

model.fit(X_train, y_train)

# --- 5. EVALUATE ---
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print("\n" + "="*30)
print(f"🔥 XGBOOST ACCURACY: {accuracy * 100:.2f}%")
print("="*30)

# Feature Importance (What actually matters?)
importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
print("\n🔍 FEATURE IMPORTANCE:")
print(importances)

# Save if good
if accuracy > 0.50:
    joblib.dump(model, 'titan_xgb_model.pkl')
    print("\n✅ Model saved as 'titan_xgb_model.pkl'")
else:
    print("\n⚠️ Accuracy too low. Needs better features.")