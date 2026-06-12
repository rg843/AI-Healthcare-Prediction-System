import requests

# login as admin
r = requests.post('http://127.0.0.1:8000/api/auth/login', json={'username':'admin','password':'adminpass'})
print('login', r.status_code)
if r.status_code!=200:
    print('cannot login')
    raise SystemExit(1)

tok = 'Bearer ' + r.json().get('access_token')
headers = {'Authorization': tok}

# create appointment
ra = requests.post('http://127.0.0.1:8000/api/appointments', json={'patient_id':1,'doctor_id':1,'scheduled_at':'2026-06-13T10:00:00'}, headers=headers)
print('create appointment', ra.status_code, ra.text)

# list appointments
rl = requests.get('http://127.0.0.1:8000/api/appointments', headers=headers)
print('list appointments', rl.status_code, rl.text)

# create ehr
# create a doctor user and doctor record, then create ehr as doctor
ru = requests.post('http://127.0.0.1:8000/api/users', json={'username':'doc1','email':'doc1@example.com','password':'docpass','role':'doctor'}, headers=headers)
print('create doctor user', ru.status_code, ru.text)
doc_id = None
if ru.status_code==200:
    doc_id = ru.json().get('id')
else:
    # try to find existing user
    rl = requests.get('http://127.0.0.1:8000/api/users', headers=headers)
    if rl.status_code==200:
        for u in rl.json():
            if u.get('username')=='doc1':
                doc_id = u.get('id')
                break
if doc_id:
    rd = requests.post('http://127.0.0.1:8000/api/doctors', json={'doctor_id':'D200','name':'Dr. Bob','user_id':doc_id}, headers=headers)
    print('create doctor record', rd.status_code, rd.text)
    doc_record_id = None
    if rd.status_code==200:
        try:
            doc_record_id = rd.json().get('id')
        except:
            doc_record_id = None
    else:
        # try to find existing doctor linked to this user
        rlistd = requests.get('http://127.0.0.1:8000/api/doctors', headers=headers)
        if rlistd.status_code==200:
            for dd in rlistd.json():
                if dd.get('user_id')==doc_id or dd.get('doctor_id')=='D200':
                    doc_record_id = dd.get('id')
                    break

    # login as doctor
    rdoc = requests.post('http://127.0.0.1:8000/api/auth/login', json={'username':'doc1','password':'docpass'})
    print('doctor login', rdoc.status_code, rdoc.text)
    if rdoc.status_code==200:
        doctok = 'Bearer '+rdoc.json().get('access_token')
        if doc_record_id:
            rhe = requests.post('http://127.0.0.1:8000/api/ehr', json={'patient_id':1,'doctor_id':doc_record_id,'diagnosis':'Test','prescriptions':{'med':'x'}}, headers={'Authorization':doctok})
            print('create ehr as doctor', rhe.status_code, rhe.text)

            # list ehr for patient
            rl = requests.get('http://127.0.0.1:8000/api/ehr/patient/1', headers={'Authorization':doctok})
            print('list ehr', rl.status_code, rl.text)
        else:
            print('no doctor record id found')
