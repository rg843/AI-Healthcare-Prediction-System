import pandas as pd
import json
from pathlib import Path
base = Path.cwd()
print('CWD:', base)
paths = [base / 'prediction_results.csv', base / 'healthcare_ai_system' / 'data' / 'overall_detailed.jsonl']
for p in paths:
    print('Checking', p)
    if not p.exists():
        print(' MISSING')
        continue
    try:
        if p.suffix == '.csv':
            df = pd.read_csv(p)
            print(df.head(3).to_dict())
        else:
            with open(p,'r',encoding='utf-8') as fh:
                for i,line in enumerate(fh):
                    if i>2: break
                    print(json.loads(line))
    except Exception as e:
        print(' ERROR', e)
