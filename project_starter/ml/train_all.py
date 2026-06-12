"""Train models for Diabetes, Heart, Kidney, Cancer and save to `ml/models/` using joblib."""
from pathlib import Path
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import xgboost as xgb

from .data_prep import load_pima, load_heart, load_ckd, load_cancer

MODEL_DIR = Path(__file__).resolve().parents[0] / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def _train_and_save(clf, X, y, name: str):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"{name} accuracy: {acc:.4f}")
    print(classification_report(y_test, preds, zero_division=0))
    joblib.dump(clf, MODEL_DIR / f"{name}_model.joblib")


def train_diabetes():
    df = load_pima()
    if 'Outcome' in df.columns:
        X = df.drop(columns=['Outcome'])
        y = df['Outcome']
    else:
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
    clf = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    _train_and_save(clf, X, y, 'diabetes_xgb')
    # also save a RandomForest
    _train_and_save(RandomForestClassifier(n_estimators=100, random_state=42), X, y, 'diabetes_rf')


def train_heart():
    df = load_heart()
    if 'target' in df.columns:
        X = df.drop(columns=['target'])
        y = df['target']
    else:
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
    _train_and_save(RandomForestClassifier(n_estimators=100, random_state=42), X, y, 'heart_rf')


def train_ckd():
    df = load_ckd()
    if 'target' in df.columns:
        X = df.drop(columns=['target'])
        y = df['target']
    else:
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
    clf = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    _train_and_save(clf, X, y, 'ckd_xgb')


def train_cancer():
    df = load_cancer()
    # Attempt to coerce target to binary label (malignant vs benign)
    if 'target' in df.columns:
        y = df['target']
        X = df.drop(columns=['target'])
    else:
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]

    # Clean target: drop NA, convert to numeric if possible
    try:
        y = pd.to_numeric(y, errors='coerce')
    except Exception:
        pass
    mask = ~y.isna()
    X = X.loc[mask].reset_index(drop=True)
    y = y.loc[mask].reset_index(drop=True)

    # If multiclass, convert to binary by (value > 0)
    if y.nunique() > 2:
        y = (y > 0).astype(int)

    # XGBoost
    _train_and_save(xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss'), X, y, 'cancer_xgb')
    # Simple neural network if tensorflow available
    try:
        import tensorflow as tf
        from tensorflow.keras import Sequential
        from tensorflow.keras.layers import Dense
        model = Sequential([Dense(64, activation='relu', input_shape=(X.shape[1],)), Dense(32, activation='relu'), Dense(1, activation='sigmoid')])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        model.fit(X, y, epochs=10, batch_size=32, validation_split=0.1, verbose=0)
        # save keras model
        model.save(MODEL_DIR / 'cancer_keras')
        print('Saved Keras cancer model')
    except Exception as e:
        print('TensorFlow not available or training failed:', e)


if __name__ == '__main__':
    print('Training diabetes...')
    train_diabetes()
    print('Training heart...')
    train_heart()
    print('Training ckd...')
    train_ckd()
    print('Training cancer...')
    train_cancer()
    print('All training complete. Models saved in', MODEL_DIR)
