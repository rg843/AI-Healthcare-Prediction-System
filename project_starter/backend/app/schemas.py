from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    role: Optional[str] = "patient"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PatientCreate(BaseModel):
    name: str
    age: int
    gender: Optional[str] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    medical_history: Optional[str] = None


class PatientOut(PatientCreate):
    id: int

    class Config:
        orm_mode = True
