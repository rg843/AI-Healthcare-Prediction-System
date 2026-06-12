import requests

payload = {"age":50,"gender":"Male","bmi":28.0,"blood_pressure":140.0,"sugar":200.0,"cholesterol":250.0,"heart_rate":80.0}

r = requests.post('http://127.0.0.1:8000/api/treatment/recommend', json=payload)
print('treatment recommend', r.status_code, r.text)
