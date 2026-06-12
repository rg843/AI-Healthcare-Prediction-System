import requests

# outcome
payload = {"age":60,"gender":"Male","bmi":30.0,"blood_pressure":150.0,"sugar":180.0,"cholesterol":240.0,"heart_rate":85.0}
r = requests.post('http://127.0.0.1:8000/api/predict/outcome', json=payload)
print('outcome', r.status_code, r.text)

# beds
r2 = requests.post('http://127.0.0.1:8000/api/beds/forecast', json={'days':5})
print('beds', r2.status_code, r2.text)

# staff schedule
r3 = requests.post('http://127.0.0.1:8000/api/staff/schedule')
print('staff', r3.status_code, r3.text)
