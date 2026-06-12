# Healthcare AI - Starter Scaffold

This starter scaffold provides a Postgres-ready FastAPI backend, a Streamlit frontend stub, and a starter ML training script. It's meant as a safe sandbox to begin implementing the full system.

Quick start (dev, sqlite):

1. Create and activate a Python venv.

2. Install backend deps:

```bash
pip install -r project_starter/backend/requirements.txt
```

3. Run backend:

```bash
cd project_starter/backend
uvicorn app.main:app --reload --port 8000
```

4. Run Streamlit frontend (in separate terminal):

```bash
streamlit run project_starter/frontend/streamlit_app.py
```

Production notes:
- Set `DATABASE_URL` to a Postgres connection string (e.g. `postgresql://user:pass@host:5432/db`).
- Add Alembic migrations and secure secret management.
- Replace ML placeholders in `project_starter/ml` with full pipelines and dataset downloads.
