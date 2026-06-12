import requests

def main():
    base='http://localhost:8000'
    out_lines = []
    try:
        login = requests.post(base+'/api/auth/login', json={'username':'admin','password':'adminpass'}, timeout=5)
        out_lines.append(f'login {login.status_code}')
        if login.status_code!=200:
            out_lines.append('login response: ' + login.text)
        else:
            tok = login.json().get('access_token')
            headers = {'Authorization': f'Bearer {tok}'}
            endpoints = ['/api/patients','/api/doctors','/api/appointments']
            for ep in endpoints:
                r = requests.get(base+ep, headers=headers, timeout=5)
                out_lines.append(f'{ep} {r.status_code}')
                out_lines.append(r.text[:400])
    except Exception as e:
        out_lines.append('error ' + str(e))
    # write results to file for reliable retrieval
    fn = 'healthcare_ai_system/backend/app/scripts/test_protected_endpoints_output.txt'
    with open(fn, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))
    print('WROTE', fn)

if __name__ == '__main__':
    main()
