import os
import sys
from pprint import pprint
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, proj_root)

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# Sample payload used previously by tests
payload = {
    "age": 55,
    "bmi": 30.0,
    "blood_pressure": 150.0,
    "cholesterol": 240.0,
    "sugar": 180.0,
    "symptoms": ["fatigue", "thirst"],
}

print('Posting to /api/predict/outcome with payload:')
pprint(payload)
resp = client.post('/api/predict/outcome', json=payload)
print('\nStatus', resp.status_code)
try:
    pprint(resp.json())
except Exception:
    print(resp.text)
