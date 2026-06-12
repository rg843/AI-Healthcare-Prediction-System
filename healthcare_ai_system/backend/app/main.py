from fastapi import FastAPI
from . import db, models
from .api import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Healthcare AI System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    db.init_db()


app.include_router(api_router, prefix="/api")
