import requests

try:
    r = requests.post('http://127.0.0.1:8000/api/auth/login', json={'username':'admin','password':'adminpass'}, timeout=5)
    print('login', r.status_code, r.text)
    if r.status_code == 200:
        tok = 'Bearer ' + r.json().get('access_token')
        patient = {'name': 'John Doe', 'age': 45, 'gender': 'M'}
        r2 = requests.post('http://127.0.0.1:8000/api/patients', json=patient, headers={'Authorization': tok}, timeout=5)
        print('create_patient', r2.status_code, r2.text)
except Exception as e:
    print('error', e)
