import requests

print('forgot:')
r = requests.post('http://127.0.0.1:8000/api/auth/forgot', json={'email':'admin@example.com'})
print(r.status_code, r.text)

print('login:')
r2 = requests.post('http://127.0.0.1:8000/api/auth/login', json={'username':'admin','password':'adminpass'})
print(r2.status_code, r2.text)
if r2.status_code==200:
    tok = 'Bearer ' + r2.json().get('access_token')
    print('create doctor:')
    rd = requests.post('http://127.0.0.1:8000/api/doctors', json={'doctor_id':'D100','name':'Dr. Alice','qualification':'MD','department':'General'}, headers={'Authorization':tok})
    print(rd.status_code, rd.text)
    rl = requests.get('http://127.0.0.1:8000/api/doctors', headers={'Authorization':tok})
    print('list doctors', rl.status_code, rl.text)
else:
    print('login failed')
