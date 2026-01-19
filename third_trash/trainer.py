import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# --- CONFIGURATION ---
INPUT_FILE = 'btc_ready.csv'
MODEL_FILE = 'brain.pkl'

def train_brain():
    print("Loading data...")
    df = pd.read_csv(INPUT_FILE)
    
    # Features (Inputs for the Brain)
    features = [
        'RSI', 'MACD', 'ATR', 'Trend_Dist', 
        'Breakout_Up', 'Breakout_Down', 
        'Hammer', 'Shooting_Star'
    ]
    X = df[features]
    y = df['Target']

    # Split Data (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # Train XGBoost
    print("Training AI Model (XGBoost)...")
    model = XGBClassifier(n_estimators=200, learning_rate=0.05, max_depth=5, eval_metric='logloss')
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"✅ Model Trained! Accuracy: {acc*100:.2f}%")
    
    # Save
    joblib.dump(model, MODEL_FILE)
    print(f"💾 Saved brain to '{MODEL_FILE}'")

if __name__ == "__main__":
    train_brain()