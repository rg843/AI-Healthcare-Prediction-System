from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import router as api_router
from .db import init_db

app = FastAPI(title="Healthcare AI Backend - Starter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok", "service": "Healthcare AI Backend - Starter"}
