from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from .db import Base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from .db import Base


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))
    full_name = Column(String(255))
    role = relationship("Role")


class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255), nullable=False)
    age = Column(Integer)
    gender = Column(String(20))
    weight = Column(Float)
    height = Column(Float)
    blood_group = Column(String(10))
    address = Column(Text)
    medical_history = Column(Text)
    family_history = Column(Text)
    allergies = Column(Text)
    insurance = Column(JSON)


class Doctor(Base):
    __tablename__ = "doctors"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    doctor_id = Column(String(50), unique=True)
    name = Column(String(255))
    qualification = Column(String(255))
    experience = Column(Integer)
    department = Column(String(255))
    availability = Column(JSON)


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    scheduled_at = Column(String)
    slot = Column(String(50))
    status = Column(String(50), default="pending")
    notes = Column(Text)


class EHR(Base):
    __tablename__ = "ehr"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    diagnosis = Column(Text)
    prescriptions = Column(JSON)
    reports = Column(JSON)


class Bed(Base):
    __tablename__ = "beds"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    total = Column(Integer, default=0)
    occupied = Column(Integer, default=0)


class Resource(Base):
    __tablename__ = "resources"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    total = Column(Integer, default=0)
    available = Column(Integer, default=0)


class ModelMetadata(Base):
    __tablename__ = "model_metadata"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    version = Column(String(50))
    path = Column(String(1024))
    metrics = Column(JSON)
