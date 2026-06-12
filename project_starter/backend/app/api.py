from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, auth
from .db import get_db
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

router = APIRouter()


@router.post('/auth/register', response_model=dict)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail='Username already registered')
    hashed = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"username": db_user.username, "id": db_user.id}


@router.post('/auth/token', response_model=schemas.Token)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    access_token = auth.create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/patients', response_model=dict)
def create_patient(p: schemas.PatientCreate, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    patient = models.Patient(name=p.name, age=p.age, gender=p.gender, weight=p.weight, height=p.height, medical_history=p.medical_history, user_id=current_user.id)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return {"patient_id": patient.id}


@router.get('/patients/{patient_id}', response_model=schemas.PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db), current_user=Depends(auth.get_current_user)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail='Patient not found')
    return patient


@router.post('/predict')
def predict(payload: dict):
    # Placeholder: integrate ML models in `project_starter/ml` and call them here
    return {"disease": "healthy", "risk_score": 0.12, "severity": "low"}
