import requests

urls = [
    ('Streamlit', 'http://127.0.0.1:8501'),
    ('Streamlit localhost', 'http://localhost:8501'),
    ('API docs', 'http://127.0.0.1:8000/docs'),
    ('API root', 'http://127.0.0.1:8000'),
]

for name, url in urls:
    try:
        r = requests.get(url, timeout=5)
        print(f"{name} {url} -> {r.status_code}")
    except Exception as e:
        print(f"{name} {url} -> ERROR: {e}")
