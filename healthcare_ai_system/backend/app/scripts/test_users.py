import requests

# login as admin
r = requests.post('http://127.0.0.1:8000/api/auth/login', json={'username':'admin','password':'adminpass'})
print('login', r.status_code)
if r.status_code!=200:
    print('cannot login')
    raise SystemExit(1)

tok = 'Bearer ' + r.json().get('access_token')
headers = {'Authorization': tok}

# create user
ru = requests.post('http://127.0.0.1:8000/api/users', json={'username':'u1','email':'u1@example.com','password':'pass123','role':'patient'}, headers=headers)
print('create user', ru.status_code, ru.text)

# list users
rl = requests.get('http://127.0.0.1:8000/api/users', headers=headers)
print('list users', rl.status_code, rl.text)

# change role
if ru.status_code==200:
    uid = ru.json().get('id')
    rp = requests.put(f'http://127.0.0.1:8000/api/users/{uid}/role', json={'role':'doctor'}, headers=headers)
    print('update role', rp.status_code, rp.text)

# delete user
if ru.status_code==200:
    uid = ru.json().get('id')
    rd = requests.delete(f'http://127.0.0.1:8000/api/users/{uid}', headers=headers)
    print('delete', rd.status_code, rd.text)
