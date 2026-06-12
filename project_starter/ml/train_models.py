"""Starter ML training scripts: download datasets, train basic models, save with joblib"""
import joblib
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

MODEL_DIR = Path(__file__).resolve().parents[0] / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train_diabetes(path: str):
    df = pd.read_csv(path)
    # Expect PIMA columns; simple preprocessing
    X = df.drop(columns=["Outcome"]) if "Outcome" in df.columns else df.iloc[:, :-1]
    y = df["Outcome"] if "Outcome" in df.columns else df.iloc[:, -1]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    print("Diabetes accuracy:", accuracy_score(y_test, preds))
    joblib.dump(clf, MODEL_DIR / "diabetes_model.joblib")


if __name__ == '__main__':
    print("Run specific training functions with dataset paths. This is a starter.")
