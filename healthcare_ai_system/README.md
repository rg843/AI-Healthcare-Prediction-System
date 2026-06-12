# Healthcare AI System

Production-ready scaffold for an AI-powered healthcare system: backend (FastAPI), frontend (Streamlit), ML pipelines, and PostgreSQL schema.

See `requirements.txt` for Python dependencies. Use `docker-compose.yml` to run Postgres + backend + frontend.

Quick start (development):

```bash
python -m venv .venv
source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
pip install -r requirements.txt
cd healthcare_ai_system/backend
uvicorn app.main:app --reload --port 8000
```

Streamlit UI:

```bash
streamlit run healthcare_ai_system/frontend/streamlit_app.py
```

API examples:

curl example (predict outcome):

```bash
curl -X POST http://127.0.0.1:8000/api/predict/outcome \
	-H "Content-Type: application/json" \
	-d '{"age":60,"gender":"Male","bmi":30.0,"blood_pressure":150.0,"sugar":180.0,"cholesterol":240.0,"heart_rate":85.0}'
```

curl example (beds forecast):

```bash
curl -X POST http://127.0.0.1:8000/api/beds/forecast -H "Content-Type: application/json" -d '{"days":7}'
```

Run local API tests (no server required):

```bash
python healthcare_ai_system/backend/app/scripts/run_api_tests_local.py
python healthcare_ai_system/backend/app/scripts/run_scheduler_test_local.py
```

Models:
- Place trained `*.joblib` models in the `models/` folder at the project root. `prediction` will try common filename variants (e.g. `diabetes_xgb_model.joblib`, `diabetes_rf_model.joblib`).

If you want me to generate a complete `requirements.txt` or Docker compose updates, tell me and I'll add them.

Deployment (quick Docker-compose example):

```yaml
version: '3.8'
services:
	db:
		image: postgres:15
		restart: unless-stopped
		environment:
			POSTGRES_USER: postgres
			POSTGRES_PASSWORD: postgres
			POSTGRES_DB: healthcare
		ports:
			- "5432:5432"
		volumes:
			- db_data:/var/lib/postgresql/data

	backend:
		build: .
		command: uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
		volumes:
			- ./:/app
		ports:
			- "8000:8000"
		environment:
			DATABASE_URL: postgresql://postgres:postgres@db:5432/healthcare
		depends_on:
			- db

	frontend:
		image: tiangolo/uvicorn-gunicorn:python3.11
		volumes:
			- ./:/app
		command: streamlit run frontend/streamlit_app.py --server.port 8501
		ports:
			- "8501:8501"
		depends_on:
			- backend

volumes:
	db_data:
```

Notes:
- Dockerfile and production hardening not included; adapt the image and commands to your CI/CD.
- `psycopg2-binary` may require system packages on Windows; for local dev we use SQLite by default in `DATABASE_URL`.

Notifications configuration
---------------------------
- To enable SMTP email sending, set these environment variables: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL`.
- For development, enable `SHOW_EMAILS=true` to log emails instead of sending.
- To enable Twilio SMS, set `TWILIO_SID`, `TWILIO_TOKEN`, and `TWILIO_FROM` (phone number).

Example (Windows PowerShell):

```powershell
$env:SMTP_HOST = 'smtp.mailtrap.io'
$env:SMTP_PORT = '587'
$env:SMTP_USER = 'user'
$env:SMTP_PASS = 'pass'
$env:SHOW_EMAILS = 'true'
$env:TWILIO_SID = '' # optional
$env:TWILIO_TOKEN = ''
$env:TWILIO_FROM = ''
```
