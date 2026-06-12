from typing import Dict, Any
from .prediction import predict_disease


def recommend_by_features(features: Dict[str, Any]):
    # features expected to include age, gender, bmi, blood_pressure, sugar, cholesterol, heart_rate
    # run two quick disease predictions
    diab = predict_disease({"disease": "diabetes", "features": [
        features.get("age", 0),
        1 if features.get("gender", "M").lower().startswith("m") else 0,
        features.get("bmi", 0.0),
        features.get("blood_pressure", 0.0),
        features.get("sugar", 0.0),
        features.get("cholesterol", 0.0),
        features.get("heart_rate", 0.0),
    ]})
    heart = predict_disease({"disease": "heart", "features": [
        features.get("age", 0),
        1 if features.get("gender", "M").lower().startswith("m") else 0,
        features.get("bmi", 0.0),
        features.get("blood_pressure", 0.0),
        features.get("sugar", 0.0),
        features.get("cholesterol", 0.0),
        features.get("heart_rate", 0.0),
    ]})

    recommendations = []
    if diab.get("risk_score", 0) > 0.5:
        recommendations.append({"disease": "diabetes", "recommendations": ["Metformin 500mg once daily", "Dietary changes", "Exercise 30min daily"]})
    if heart.get("risk_score", 0) > 0.5:
        recommendations.append({"disease": "heart_disease", "recommendations": ["Start statin therapy", "Control blood pressure", "Refer to cardiology"]})
    if not recommendations:
        recommendations.append({"disease": "general", "recommendations": ["Healthy diet", "Regular exercise", "Routine follow-up"]})
    return {"predictions": [diab, heart], "recommendations": recommendations}
