from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from .schemas import UserCreate, Token, PatientCreate, PatientOut, PredictionRequest, PredictionResponse, UserLogin, PasswordResetRequest, PasswordResetConfirm
from .schemas import UserOut, UserCreateWithRole, UserRoleUpdate
from .schemas import AppointmentCreate, AppointmentOut, AppointmentUpdate, EHRCreate, EHROut, DoctorCreate, DoctorOut
from . import db, models, auth, prediction
from . import email_utils
from . import sms_utils
from . import treatment
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()


def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()


def get_current_user(authorization: str = Header(None), db: db.SessionLocal = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        scheme, token = authorization.split()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid auth header")
    payload = auth.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    username = payload.get("sub")
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_roles(*allowed_roles: List[str]):
    def _checker(current_user: models.User = Depends(get_current_user)):
        role = getattr(current_user, "role", None)
        name = getattr(role, "name", None) if role else None
        if name not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden: insufficient role")
        return current_user
    return _checker


@router.post("/auth/register", response_model=Token)
def register(u: UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == u.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed = auth.get_password_hash(u.password)
    new = models.User(username=u.username, email=u.email, hashed_password=hashed, full_name=u.full_name)
    db.add(new)
    db.commit()
    db.refresh(new)
    token = auth.create_access_token({"sub": new.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/users", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin'))):
    users = db.query(models.User).all()
    out = []
    for u in users:
        out.append({"id": u.id, "username": u.username, "email": u.email, "full_name": u.full_name, "role": u.role.name if u.role else None})
    return out


@router.post("/users", response_model=UserOut)
def create_user(u: UserCreateWithRole, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin'))):
    if db.query(models.User).filter(models.User.username == u.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    role_obj = None
    if u.role:
        role_obj = db.query(models.Role).filter(models.Role.name == u.role).first()
    if not role_obj:
        role_obj = db.query(models.Role).filter(models.Role.name == 'patient').first()
    hashed = auth.get_password_hash(u.password)
    new = models.User(username=u.username, email=u.email, hashed_password=hashed, full_name=u.full_name, role=role_obj)
    db.add(new)
    db.commit()
    db.refresh(new)
    return {"id": new.id, "username": new.username, "email": new.email, "full_name": new.full_name, "role": new.role.name}


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin'))):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": u.id, "username": u.username, "email": u.email, "full_name": u.full_name, "role": u.role.name if u.role else None}


@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, data: UserRoleUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin'))):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    role_obj = db.query(models.Role).filter(models.Role.name == data.role).first()
    if not role_obj:
        raise HTTPException(status_code=400, detail="Role not found")
    u.role = role_obj
    db.add(u)
    db.commit()
    db.refresh(u)
    return {"detail": "Role updated"}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin'))):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(u)
    db.commit()
    return {"detail": "Deleted"}


@router.post("/auth/login", response_model=Token)
def login(u: UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == u.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not auth.verify_password(u.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/auth/forgot")
def forgot_password(req: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    reset_token = auth.create_reset_token(user.email)
    # attempt to send reset token via SMTP; fall back to returning token if SMTP not configured
    sent = email_utils.send_reset_email(user.email, reset_token)
    if sent:
        return {"detail": "Reset email sent"}
    return {"reset_token": reset_token}


@router.post("/auth/reset")
def reset_password(req: PasswordResetConfirm, db: Session = Depends(get_db)):
    payload = auth.verify_reset_token(req.token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    email = payload.get("sub")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = auth.get_password_hash(req.new_password)
    db.add(user)
    db.commit()
    return {"detail": "Password reset successful"}


@router.get("/me")
def read_profile(current_user: models.User = Depends(get_current_user)):
    return {"username": current_user.username, "email": current_user.email, "full_name": current_user.full_name}


@router.put("/me")
def update_profile(data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    for k, v in data.items():
        if hasattr(current_user, k):
            setattr(current_user, k, v)
    db.add(current_user)
    db.commit()
    return {"detail": "Profile updated"}


@router.post("/predict", response_model=PredictionResponse)
def predict(req: PredictionRequest):
    payload = req.dict()
    # build simple features order matching training
    features = [
        payload.get("age", 0),
        1 if payload.get("gender", "M").lower().startswith("m") else 0,
        payload.get("bmi", 0.0),
        payload.get("blood_pressure", 0.0),
        payload.get("sugar", 0.0),
        payload.get("cholesterol", 0.0),
        payload.get("heart_rate", 0.0),
    ]
    res = prediction.predict_disease({"disease": "diabetes", "features": features})
    return res


@router.post("/patients", response_model=PatientOut)
def create_patient(p: PatientCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin', 'doctor'))):
    new = models.Patient(**p.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.get("/patients", response_model=List[PatientOut])
def list_patients(db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin', 'doctor'))):
    items = db.query(models.Patient).all()
    return items


@router.get("/patients/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin', 'doctor'))):
    p = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p


@router.put("/patients/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin', 'doctor'))):
    p = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    for k, v in data.items():
        if hasattr(p, k):
            setattr(p, k, v)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin'))):
    p = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(p)
    db.commit()
    return {"detail": "Deleted"}


@router.post("/doctors", response_model=DoctorOut)
def create_doctor(d: DoctorCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin'))):
    new = models.Doctor(**d.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.get("/doctors", response_model=List[DoctorOut])
def list_doctors(db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin', 'doctor'))):
    return db.query(models.Doctor).all()


@router.get("/doctors/{doctor_id}", response_model=DoctorOut)
def get_doctor(doctor_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin', 'doctor'))):
    d = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return d


@router.put("/doctors/{doctor_id}", response_model=DoctorOut)
def update_doctor(doctor_id: int, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin'))):
    d = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    for k, v in data.items():
        if hasattr(d, k):
            setattr(d, k, v)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


@router.delete("/doctors/{doctor_id}")
def delete_doctor(doctor_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin'))):
    d = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Doctor not found")
    db.delete(d)
    db.commit()
    return {"detail": "Deleted"}


# Appointments
@router.post("/appointments", response_model=AppointmentOut)
def create_appointment(a: AppointmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # patients can create appointments for themselves or admin/staff can create
    if current_user.role and current_user.role.name == 'patient' and current_user.username:
        # optional: ensure patient_id corresponds to current_user
        pass
    # simple conflict detection: same doctor and scheduled_at
    conflict = db.query(models.Appointment).filter(models.Appointment.doctor_id == a.doctor_id, models.Appointment.scheduled_at == a.scheduled_at).first()
    if conflict:
        raise HTTPException(status_code=400, detail="Schedule conflict: doctor already booked for that time")
    new = models.Appointment(**a.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    # send notifications (best-effort)
    try:
        # fetch patient and doctor
        patient = db.query(models.Patient).filter(models.Patient.id == new.patient_id).first()
        doctor = db.query(models.Doctor).filter(models.Doctor.id == new.doctor_id).first()
        subject = "Appointment Confirmation"
        body = f"Appointment scheduled at {new.scheduled_at} with doctor {doctor.name if doctor else new.doctor_id}."
        if patient and hasattr(patient, 'insurance'):
            # try email if exists via linked user
            if patient.user_id:
                u = db.query(models.User).filter(models.User.id == patient.user_id).first()
                if u and u.email:
                    email_utils.send_email(u.email, subject, body)
        # SMS best-effort
        try:
            sms_utils.send_sms(None, f"Appointment at {new.scheduled_at}")
        except Exception:
            pass
    except Exception:
        pass
    return new


@router.get("/appointments", response_model=List[AppointmentOut])
def list_appointments(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role and current_user.role.name == 'doctor':
        items = db.query(models.Appointment).filter(models.Appointment.doctor_id == current_user.id).all()
    elif current_user.role and current_user.role.name == 'patient':
        # find patient's linked patient record
        patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
        items = db.query(models.Appointment).filter(models.Appointment.patient_id == (patient.id if patient else None)).all()
    else:
        items = db.query(models.Appointment).all()
    return items


@router.get("/appointments/{appointment_id}", response_model=AppointmentOut)
def get_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    a = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return a


@router.put("/appointments/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, data: AppointmentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin', 'doctor'))):
    a = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for k, v in data.dict(exclude_unset=True).items():
        if hasattr(a, k):
            setattr(a, k, v)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin', 'doctor'))):
    a = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(a)
    db.commit()
    return {"detail": "Deleted"}


# EHR
@router.post("/ehr", response_model=EHROut)
def create_ehr(e: EHRCreate, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('doctor'))):
    new = models.EHR(**e.dict())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.get("/ehr/patient/{patient_id}", response_model=List[EHROut])
def list_ehr_for_patient(patient_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    items = db.query(models.EHR).filter(models.EHR.patient_id == patient_id).all()
    return items


@router.get("/ehr/{ehr_id}", response_model=EHROut)
def get_ehr(ehr_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    e = db.query(models.EHR).filter(models.EHR.id == ehr_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="EHR not found")
    return e


@router.post("/treatment/recommend")
def recommend_treatment(payload: dict):
    # payload may contain patient_id or raw features
    features = payload.get('features') or payload
    res = treatment.recommend_by_features(features)
    return res


@router.post('/predict/outcome')
def predict_outcome(payload: dict):
    # accepts {'disease': 'diabetes', 'features': [...]} or patient features
    if 'disease' in payload:
        return prediction.predict_disease(payload)
    # try to infer using provided fields
    features = payload.get('features')
    if not features:
        # build features from common keys
        f = [payload.get('age', 0), 1 if payload.get('gender','M').lower().startswith('m') else 0, payload.get('bmi',0.0), payload.get('blood_pressure',0.0), payload.get('sugar',0.0), payload.get('cholesterol',0.0), payload.get('heart_rate',0.0)]
        return prediction.predict_disease({'disease':'diabetes','features':f})
    return prediction.predict_disease({'disease': payload.get('disease','diabetes'), 'features': features})


@router.post('/beds/forecast')
def forecast_beds(payload: dict = None):
    # payload: {'type': 'ICU', 'days': 7, 'growth_rate': 0.01}
    # read current beds
    days = (payload or {}).get('days', 7)
    growth = (payload or {}).get('growth_rate', 0.01)
    beds = []
    dbs = db.SessionLocal()
    try:
        for b in dbs.query(models.Bed).all():
            total = b.total or 0
            occupied = b.occupied or 0
            forecast = []
            for i in range(days):
                occupied = int(occupied * (1 + growth))
                if occupied > total:
                    occupied = total
                forecast.append({'day': i+1, 'occupied': occupied, 'available': total - occupied})
            beds.append({'type': b.type, 'total': total, 'forecast': forecast})
    finally:
        dbs.close()
    return {'beds': beds}


@router.get('/beds')
def list_beds(db: Session = Depends(get_db)):
    items = db.query(models.Bed).all()
    out = []
    for b in items:
        out.append({'id': b.id, 'type': b.type, 'total': b.total, 'occupied': b.occupied})
    return out


@router.post('/beds')
def create_bed(payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(require_roles('admin','staff'))):
    b = models.Bed(type=payload.get('type','General'), total=int(payload.get('total',0)), occupied=int(payload.get('occupied',0)))
    db.add(b)
    db.commit()
    db.refresh(b)
    return {'id': b.id, 'type': b.type, 'total': b.total, 'occupied': b.occupied}


@router.post('/staff/schedule')
def staff_schedule(payload: dict = None):
    # improved scheduler: prefer doctors available on the appointment day, then staff round-robin
    dbs = db.SessionLocal()
    try:
        doctors = dbs.query(models.Doctor).all()
        staff_users = [u for u in dbs.query(models.User).all() if u.role and u.role.name == 'staff']
        appts = dbs.query(models.Appointment).filter(models.Appointment.status == 'pending').all()
        schedule = []
        if not appts:
            return {'schedule': []}

        def day_name_from_str(s):
            try:
                dt = datetime.fromisoformat(s)
                return dt.strftime('%A').lower()
            except Exception:
                return None

        idx = 0
        for a in appts:
            assigned = None
            day = day_name_from_str(a.scheduled_at) if a.scheduled_at else None
            # try assign to a doctor whose availability includes the day
            for d in doctors:
                try:
                    avail = d.availability or {}
                    # availability may be dict like {'monday':'9-17'} or list
                    if isinstance(avail, dict) and day and day in {k.lower() for k in avail.keys()}:
                        # find corresponding user
                        user = dbs.query(models.User).filter(models.User.id == d.user_id).first()
                        if user:
                            assigned = user.username
                            break
                    if isinstance(avail, list) and day and day in [x.lower() for x in avail]:
                        user = dbs.query(models.User).filter(models.User.id == d.user_id).first()
                        if user:
                            assigned = user.username
                            break
                except Exception:
                    continue

            # fallback to staff round-robin
            if not assigned:
                all_staff = staff_users or [u for u in dbs.query(models.User).all() if u.role and u.role.name in ('staff','doctor')]
                if all_staff:
                    assigned = all_staff[idx % len(all_staff)].username
                    idx += 1

            schedule.append({'appointment_id': a.id, 'assigned_to': assigned})
    finally:
        dbs.close()
    return {'schedule': schedule}

