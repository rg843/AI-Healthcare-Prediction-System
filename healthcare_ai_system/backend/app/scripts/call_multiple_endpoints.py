import requests
from pprint import pprint

BASE = 'http://127.0.0.1:8000/api'

predict_payload = {
    "age": 55,
    "bmi": 30.0,
    "blood_pressure": 150.0,
    "cholesterol": 240.0,
    "sugar": 180.0,
    "symptoms": ["fatigue", "thirst"],
}

print('POST /api/predict/outcome')
r = requests.post(f'{BASE}/predict/outcome', json=predict_payload, timeout=10)
print('Status', r.status_code)
try:
    pred = r.json()
    pprint(pred)
except Exception:
    print(r.text)

# Call treatment recommendation using disease/severity from prediction
if r.status_code == 200:
    tr_payload = {
        'disease': pred.get('disease'),
        'severity': pred.get('severity'),
        'risk_score': pred.get('risk_score'),
        'symptoms': predict_payload['symptoms']
    }
    print('\nPOST /api/treatment/recommend')
    rr = requests.post(f'{BASE}/treatment/recommend', json=tr_payload, timeout=10)
    print('Status', rr.status_code)
    try:
        pprint(rr.json())
    except Exception:
        print(rr.text)

print('\nGET /api/beds/forecast')
r2 = requests.get(f'{BASE}/beds/forecast', timeout=10)
print('Status', r2.status_code)
try:
    pprint(r2.json())
except Exception:
    print(r2.text)

print('\nGET /api/staff/schedule')
r3 = requests.get(f'{BASE}/staff/schedule', timeout=10)
print('Status', r3.status_code)
try:
    pprint(r3.json())
except Exception:
    print(r3.text)
