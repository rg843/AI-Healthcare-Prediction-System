import csv
import os
import requests
from pprint import pprint

OUT_CSV = 'prediction_results.csv'
SAMPLE_CSV = 'sample_dataset.csv'
API_URL = 'http://127.0.0.1:8000/api/predict/outcome'

# Create a sample dataset if not exists
if not os.path.exists(SAMPLE_CSV):
    rows = []
    for i in range(1, 21):
        rows.append({
            'id': i,
            'age': 20 + i,
            'bmi': 18 + i * 0.8,
            'blood_pressure': 100 + i,
            'cholesterol': 150 + i * 2,
            'sugar': 90 + i * 3,
            'symptoms': 'fatigue;thirst' if i % 3 == 0 else ''
        })
    with open(SAMPLE_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print('Wrote sample dataset to', SAMPLE_CSV)

# Read dataset and call API for each row
results = []
with open(SAMPLE_CSV, newline='') as f:
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

# Write results
with open(OUT_CSV, 'w', newline='') as f:
    fieldnames = ['id', 'disease', 'severity', 'risk_score', 'confidence', 'error']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
        writer.writerow({k: row.get(k, '') for k in fieldnames})

print('Wrote predictions to', OUT_CSV)
pprint(results[:5])
