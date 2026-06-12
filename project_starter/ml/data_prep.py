"""Data preparation utilities: download or load datasets for diabetes, heart, kidney, cancer.
Provides fallback synthetic data if downloads fail.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import requests

DATA_DIR = Path(__file__).resolve().parents[0] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _download(url: str, dest: Path):
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
        return True
    except Exception:
        return False


def load_pima(dest: Path = None):
    """Load or download Pima Indians Diabetes dataset.
    Returns DataFrame with last column named 'Outcome' as target.
    """
    dest = Path(dest) if dest else DATA_DIR / "pima.csv"
    if not dest.exists():
        url = "https://raw.githubusercontent.com/selva86/datasets/master/PimaIndiansDiabetes.csv"
        ok = _download(url, dest)
        if not ok:
            # synthetic fallback
            cols = ["Pregnancies","Glucose","BloodPressure","SkinThickness","Insulin","BMI","DiabetesPedigreeFunction","Age","Outcome"]
            df = pd.DataFrame(np.random.randint(0,100,size=(100,9)), columns=cols)
            df.to_csv(dest, index=False)
    return pd.read_csv(dest)


def load_heart(dest: Path = None):
    dest = Path(dest) if dest else DATA_DIR / "heart.csv"
    if not dest.exists():
        url = "https://raw.githubusercontent.com/ansh941/Machine-Learning-Datasets/master/heart.csv"
        ok = _download(url, dest)
        if not ok:
            # synthetic fallback
            cols = [f"f{i}" for i in range(13)] + ["target"]
            df = pd.DataFrame(np.random.randint(0,2,size=(200,14)), columns=cols)
            df.to_csv(dest, index=False)
    return pd.read_csv(dest)


def load_ckd(dest: Path = None):
    dest = Path(dest) if dest else DATA_DIR / "ckd.csv"
    if not dest.exists():
        url = "https://raw.githubusercontent.com/plotly/datasets/master/ChronicKidneyDisease.csv"
        ok = _download(url, dest)
        if not ok:
            # synthetic fallback
            cols = [f"c{i}" for i in range(15)] + ["target"]
            df = pd.DataFrame(np.random.randint(0,2,size=(200,16)), columns=cols)
            df.to_csv(dest, index=False)
    return pd.read_csv(dest)


def load_cancer(dest: Path = None):
    dest = Path(dest) if dest else DATA_DIR / "cancer.csv"
    if not dest.exists():
        url = "https://raw.githubusercontent.com/plotly/datasets/master/data.csv"
        ok = _download(url, dest)
        if not ok:
            # synthetic fallback
            cols = [f"m{i}" for i in range(20)] + ["target"]
            df = pd.DataFrame(np.random.rand(300,21), columns=cols)
            df["target"] = (df["m0"] > 0.5).astype(int)
            df.to_csv(dest, index=False)
    return pd.read_csv(dest)


if __name__ == '__main__':
    print("Preparing datasets...")
    print("Pima:", load_pima().shape)
    print("Heart:", load_heart().shape)
    print("CKD:", load_ckd().shape)
    print("Cancer:", load_cancer().shape)
