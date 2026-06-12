from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base
import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(256), unique=True, index=True, nullable=True)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(50), default="patient")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    age = Column(Integer)
    gender = Column(String(32))
    weight = Column(Float)
    height = Column(Float)
    medical_history = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User")


class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    specialization = Column(String(128))
    availability = Column(Text)


class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    time_slot = Column(String(64))
    status = Column(String(32), default="pending")

