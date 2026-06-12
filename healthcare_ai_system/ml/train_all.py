import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
os.makedirs(MODELS_DIR, exist_ok=True)


def train_diabetes():
    from sklearn.datasets import load_diabetes
    # Use sklearn diabetes dataset as a placeholder for pipeline
    data = load_diabetes(as_frame=True)
    X = data.data
    y = (data.target > data.target.mean()).astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    xgb.fit(X_train, y_train)
    rf = RandomForestClassifier()
    rf.fit(X_train, y_train)
    joblib.dump(xgb, os.path.join(MODELS_DIR, "diabetes_xgb_model.joblib"))
    joblib.dump(rf, os.path.join(MODELS_DIR, "diabetes_rf_model.joblib"))
    print("Diabetes models saved")


def train_heart():
    # synthetic heart data pipeline
    n = 1000
    X = pd.DataFrame(np.random.randn(n, 10), columns=[f"f{i}" for i in range(10)])
    y = np.random.randint(0, 2, size=n)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    rf = RandomForestClassifier()
    rf.fit(X_train, y_train)
    joblib.dump(rf, os.path.join(MODELS_DIR, "heart_rf_model.joblib"))
    print("Heart model saved")


def train_ckd():
    n = 500
    X = pd.DataFrame(np.random.randn(n, 8), columns=[f"f{i}" for i in range(8)])
    y = np.random.randint(0, 2, size=n)
    xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    xgb.fit(X, y)
    joblib.dump(xgb, os.path.join(MODELS_DIR, "ckd_xgb_model.joblib"))
    print("CKD model saved")


def train_cancer():
    from sklearn.datasets import load_breast_cancer
    data = load_breast_cancer()
    X = pd.DataFrame(data.data, columns=data.feature_names)
    y = data.target
    xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    xgb.fit(X, y)
    joblib.dump(xgb, os.path.join(MODELS_DIR, "cancer_xgb_model.joblib"))
    print("Cancer model saved")


if __name__ == '__main__':
    train_diabetes()
    train_heart()
    train_ckd()
    train_cancer()
    print("All models trained and saved to", MODELS_DIR)
