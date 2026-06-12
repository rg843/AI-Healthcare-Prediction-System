import os
import csv
import json
import requests
from pprint import pprint

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data'))
INPUT_CSV = os.path.join(DATA_DIR, 'sample_dataset.csv')
OUT_JSONL = os.path.join(DATA_DIR, 'overall_detailed.jsonl')
PRED_URL = 'http://127.0.0.1:8000/api/predict/outcome'
TREAT_URL = 'http://127.0.0.1:8000/api/treatment/recommend'

if not os.path.exists(INPUT_CSV):
    print('Input CSV not found at', INPUT_CSV)
    raise SystemExit(1)

with open(OUT_JSONL, 'w', encoding='utf-8') as out:
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
            entry = {'id': r['id'], 'input': payload}
            try:
                pr = requests.post(PRED_URL, json=payload, timeout=10)
                pr.raise_for_status()
                pred = pr.json()
                entry['prediction'] = pred
            except Exception as e:
                entry['prediction_error'] = str(e)
                out.write(json.dumps(entry) + '\n')
                continue
            # treatment
            try:
                tr_payload = {
                    'disease': pred.get('disease'),
                    'severity': pred.get('severity'),
                    'risk_score': pred.get('risk_score'),
                    'symptoms': payload['symptoms']
                }
                tr = requests.post(TREAT_URL, json=tr_payload, timeout=10)
                tr.raise_for_status()
                entry['treatment'] = tr.json()
            except Exception as e:
                entry['treatment_error'] = str(e)
            out.write(json.dumps(entry) + '\n')

print('Wrote detailed results to', OUT_JSONL)
# print first 3 entries
with open(OUT_JSONL, 'r', encoding='utf-8') as f:
    for i in range(3):
        line = f.readline()
        if not line:
            break
        pprint(json.loads(line))
