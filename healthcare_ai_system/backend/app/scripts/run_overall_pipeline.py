import csv
import os
import requests
from pprint import pprint

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data'))
INPUT_CSV = os.path.join(DATA_DIR, 'sample_dataset.csv')
OUT_CSV = os.path.join(DATA_DIR, 'overall_results.csv')
PRED_URL = 'http://127.0.0.1:8000/api/predict/outcome'
TREAT_URL = 'http://127.0.0.1:8000/api/treatment/recommend'

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
        row_result = {'id': r['id']}
        try:
            pr = requests.post(PRED_URL, json=payload, timeout=10)
            if pr.status_code == 200:
                pred = pr.json()
                row_result.update({
                    'disease': pred.get('disease'),
                    'severity': pred.get('severity'),
                    'risk_score': pred.get('risk_score'),
                    'confidence': pred.get('confidence')
                })
                # call treatment
                tr_payload = {
                    'disease': pred.get('disease'),
                    'severity': pred.get('severity'),
                    'risk_score': pred.get('risk_score'),
                    'symptoms': payload['symptoms']
                }
                tr = requests.post(TREAT_URL, json=tr_payload, timeout=10)
                if tr.status_code == 200:
                    tret = tr.json()
                    # flatten recommendations
                    recs = []
                    for rec in tret.get('recommendations', []):
                        recs.extend(rec.get('recommendations', []))
                    row_result['recommendations'] = ';'.join(recs)
                else:
                    row_result['treatment_error'] = f'status {tr.status_code}'
            else:
                row_result['error'] = f'predict status {pr.status_code}'
        except Exception as e:
            row_result['error'] = str(e)
        results.append(row_result)

# write out
fieldnames = ['id','disease','severity','risk_score','confidence','recommendations','error','treatment_error']
with open(OUT_CSV, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
        writer.writerow({k: row.get(k, '') for k in fieldnames})

print('Wrote overall results to', OUT_CSV)
for r in results[:5]:
    pprint(r)
