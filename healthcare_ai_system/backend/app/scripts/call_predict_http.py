import requests
from pprint import pprint

url = 'http://127.0.0.1:8000/api/predict/outcome'
payload = {
    "age": 55,
    "bmi": 30.0,
    "blood_pressure": 150.0,
    "cholesterol": 240.0,
    "sugar": 180.0,
    "symptoms": ["fatigue", "thirst"],
}
print('Posting to', url)
resp = requests.post(url, json=payload, timeout=10)
print('Status', resp.status_code)
try:
    pprint(resp.json())
except Exception:
    print(resp.text)
