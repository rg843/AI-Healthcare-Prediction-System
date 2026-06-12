"""Prediction loader: loads joblib models from `../ml/models` and exposes `predict_disease`."""
from pathlib import Path
import joblib
import numpy as np

MODEL_DIR = Path(__file__).resolve().parents[2].joinpath('ml','models')
_models = {}

for fname in MODEL_DIR.glob('*_model.joblib'):
    try:
        name = fname.stem.replace('_model','')
        _models[name] = joblib.load(fname)
    except Exception:
        pass


def _make_vector(features, expected_len):
    vals = [
        float(features.get('age',0) or 0),
        float(features.get('bmi',0) or 0),
        float(features.get('sugar',0) or 0),
        float(features.get('blood_pressure',0) or 0),
        float(features.get('cholesterol',0) or 0),
    ]
    if expected_len <= len(vals):
        return np.array([vals[:expected_len]], dtype=float)
    return np.array([vals + [0.0] * (expected_len - len(vals))], dtype=float)


def predict_disease(payload: dict):
    model_key = (payload.get('model') or 'diabetes').lower()
    model = _models.get(model_key)
    if model is not None:
        try:
            n_in = getattr(model, 'n_features_in_', None) or 4
            X = _make_vector(payload, int(n_in))
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X)[0]
                risk = float(proba[1]) if len(proba)>1 else float(proba[0])
            else:
                pred = model.predict(X)[0]
                risk = float(pred)
            severity = 'low' if risk < 0.4 else 'medium' if risk < 0.7 else 'high'
            label = model_key if risk>=0.5 else 'healthy'
            return {'disease': label, 'risk_score': round(risk,3), 'severity': severity}
        except Exception:
            pass
    # fallback heuristic
    age = payload.get('age',0)
    bmi = payload.get('bmi',0)
    sugar = payload.get('sugar',0)
    bp = payload.get('blood_pressure',0)
    score = min(float(age)/100.0,1.0)*0.3 + min(float(bmi)/40.0,1.0)*0.3 + min(float(sugar)/200.0,1.0)*0.2 + min(float(bp)/200.0,1.0)*0.2
    if score < 0.25:
        pred = 'healthy'
    else:
        pred = 'diabetes'
    severity = 'low' if score < 0.4 else 'medium' if score < 0.7 else 'high'
    return {'disease': pred, 'risk_score': round(score,3), 'severity': severity}
