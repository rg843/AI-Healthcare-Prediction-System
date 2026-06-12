from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str]
    role: Optional[str]

    class Config:
        orm_mode = True


class UserRoleUpdate(BaseModel):
    role: str


class UserCreateWithRole(UserCreate):
    role: Optional[str] = "patient"


class PatientCreate(BaseModel):
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    blood_group: Optional[str] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None
    family_history: Optional[str] = None
    allergies: Optional[str] = None
    insurance: Optional[Dict[str, Any]] = None


class PatientOut(PatientCreate):
    id: int

    class Config:
        orm_mode = True


class DoctorCreate(BaseModel):
    doctor_id: str
    name: str
    qualification: Optional[str] = None
    experience: Optional[int] = None
    department: Optional[str] = None
    availability: Optional[Dict[str, Any]] = None
    user_id: Optional[int] = None


class DoctorOut(DoctorCreate):
    id: int

    class Config:
        orm_mode = True


class PatientUpdate(BaseModel):
    name: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    weight: Optional[float]
    height: Optional[float]
    blood_group: Optional[str]
    address: Optional[str]
    medical_history: Optional[str]
    family_history: Optional[str]
    allergies: Optional[str]
    insurance: Optional[Dict[str, Any]] = None


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    scheduled_at: str
    slot: Optional[str] = None


class AppointmentOut(AppointmentCreate):
    id: int
    status: Optional[str]

    class Config:
        orm_mode = True


class AppointmentUpdate(BaseModel):
    status: Optional[str]
    notes: Optional[str]


class PredictionRequest(BaseModel):
    age: int
    gender: str
    symptoms: List[str] = []
    bmi: float
    blood_pressure: float
    sugar: float
    cholesterol: float
    heart_rate: float
    medical_history: Optional[str] = None


class PredictionResponse(BaseModel):
    disease: str
    risk_score: float
    severity: str
    confidence: float


class EHRCreate(BaseModel):
    patient_id: int
    doctor_id: int
    diagnosis: Optional[str] = None
    prescriptions: Optional[Dict[str, Any]] = None
    reports: Optional[Dict[str, Any]] = None


class EHROut(EHRCreate):
    id: int

    class Config:
        orm_mode = True
