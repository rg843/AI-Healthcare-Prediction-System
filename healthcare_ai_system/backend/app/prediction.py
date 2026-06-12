import os
import joblib
from typing import Dict, Any

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "models")
MODELS_DIR = os.path.abspath(MODELS_DIR)


def load_model(name: str):
    # try exact name, then common variants
    candidates = [f"{name}.joblib", f"{name}_rf.joblib", f"{name}_xgb.joblib", f"{name.replace('_model','')}_xgb_model.joblib", f"{name.replace('_model','')}_rf_model.joblib"]
    for fn in candidates:
        path = os.path.join(MODELS_DIR, fn)
        if os.path.exists(path):
            try:
                return joblib.load(path)
            except Exception as e:
                continue
    raise FileNotFoundError(f"Model not found (tried candidates): {candidates}")


def predict_disease(payload: Dict[str, Any]):
    # Simplified: select model by disease key in payload
    disease = payload.get("disease", "diabetes")
    model_map = {
        "diabetes": "diabetes_xgb_model",
        "heart": "heart_rf_model",
        "kidney": "ckd_xgb_model",
        "cancer": "cancer_xgb_model",
    }
    model_name = model_map.get(disease, "diabetes_xgb_model")
    m = load_model(model_name)
    features = payload.get("features")
    if not features:
        raise ValueError("features required")
    # Ensure features length matches model expectation
    expected = getattr(m, "n_features_in_", None)
    if expected is not None:
        if len(features) < expected:
            features = features + [0.0] * (expected - len(features))
        elif len(features) > expected:
            features = features[:expected]

    pred = m.predict([features])[0]
    prob = None
    if hasattr(m, "predict_proba"):
        prob = float(m.predict_proba([features])[0].max())
    else:
        prob = 0.9

    # simple explainability using feature_importances_ or coefficients
    feature_names = ['age','gender_male','bmi','blood_pressure','sugar','cholesterol','heart_rate']
    explain = []
    fi = None
    if hasattr(m, 'feature_importances_'):
        fi = list(getattr(m, 'feature_importances_'))
    elif hasattr(m, 'coef_'):
        fi = list(abs(getattr(m, 'coef_').ravel()))
    if fi is not None:
        # match to available feature names
        for i, val in enumerate(fi[:len(features)]):
            fname = feature_names[i] if i < len(feature_names) else f'feat_{i}'
            explain.append({'feature': fname, 'importance': float(val), 'value': float(features[i])})
        # sort by importance desc
        explain = sorted(explain, key=lambda x: x['importance'], reverse=True)[:5]

    return {
        "disease": disease,
        "risk_score": float(pred),
        "severity": "high" if prob > 0.8 else "medium",
        "confidence": prob,
        "explainability": explain,
    }
