import sys, os
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, proj_root)
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

print('Testing /api/predict/outcome')
payload = {"age":60,"gender":"Male","bmi":30.0,"blood_pressure":150.0,"sugar":180.0,"cholesterol":240.0,"heart_rate":85.0}
resp = client.post('/api/predict/outcome', json=payload)
print(resp.status_code, resp.json())

print('\nTesting /api/beds/forecast')
resp = client.post('/api/beds/forecast', json={'days':5})
print(resp.status_code, resp.json())

print('\nTesting /api/staff/schedule')
resp = client.post('/api/staff/schedule', json={})
print(resp.status_code, resp.json())
