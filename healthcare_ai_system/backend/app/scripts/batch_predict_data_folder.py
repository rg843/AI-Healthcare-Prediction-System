import csv
import os
import requests
from pprint import pprint

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data'))
INPUT_CSV = os.path.join(DATA_DIR, 'sample_dataset.csv')
OUT_CSV = os.path.join(DATA_DIR, 'prediction_results.csv')
API_URL = 'http://127.0.0.1:8000/api/predict/outcome'

if not os.path.exists(INPUT_CSV):
    print('Input CSV not found at', INPUT_CSV)
    raise SystemExit(1)

results = []
with open(INPUT_CSV, newline='') as f:
    reader = csv.DictReader(f)
    for r in reader:
        payload = {
            'age': float(r['age']),
            'bmi': float(r['bmi']),
            'blood_pressure': float(r['blood_pressure']),
            'cholesterol': float(r['cholesterol']),
            'sugar': float(r['sugar']),
            'symptoms': r['symptoms'].split(';') if r['symptoms'] else []
        }
        try:
            resp = requests.post(API_URL, json=payload, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                results.append({
                    'id': r['id'],
                    'disease': data.get('disease'),
                    'severity': data.get('severity'),
                    'risk_score': data.get('risk_score'),
                    'confidence': data.get('confidence')
                })
            else:
                results.append({'id': r['id'], 'error': f'status {resp.status_code}'})
        except Exception as e:
            results.append({'id': r['id'], 'error': str(e)})

with open(OUT_CSV, 'w', newline='') as f:
    fieldnames = ['id', 'disease', 'severity', 'risk_score', 'confidence', 'error']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
        writer.writerow({k: row.get(k, '') for k in fieldnames})

print('Wrote predictions to', OUT_CSV)
print('First 5 results:')
for r in results[:5]:
    pprint(r)
