import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./healthcare_dev.db")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db():
    from . import models
    Base.metadata.create_all(bind=engine)
    # Seed default roles and an admin user for initial setup
    from sqlalchemy.orm import Session
    from . import auth
    session = Session(bind=engine)
    try:
        # create roles if missing
        role_names = ["admin", "doctor", "patient", "staff"]
        for rn in role_names:
            existing = session.query(models.Role).filter(models.Role.name == rn).first()
            if not existing:
                session.add(models.Role(name=rn))
        session.commit()

        # ensure an admin user exists
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "adminpass")
        admin = session.query(models.User).filter(models.User.username == admin_username).first()
        admin_role = session.query(models.Role).filter(models.Role.name == "admin").first()
        if not admin:
            hashed = auth.get_password_hash(admin_password)
            admin = models.User(username=admin_username, email=admin_email, hashed_password=hashed, full_name="Administrator", role=admin_role)
            session.add(admin)
            session.commit()

        # seed a sample doctor user and doctor record for testing
        doc_username = os.getenv('SAMPLE_DOCTOR', 'doc1')
        doc_email = os.getenv('SAMPLE_DOCTOR_EMAIL', 'doc1@example.com')
        doctor_user = session.query(models.User).filter(models.User.username == doc_username).first()
        doctor_role = session.query(models.Role).filter(models.Role.name == 'doctor').first()
        if not doctor_user:
            hashed = auth.get_password_hash('docpass')
            doctor_user = models.User(username=doc_username, email=doc_email, hashed_password=hashed, full_name='Dr Sample', role=doctor_role)
            session.add(doctor_user)
            session.commit()
        # create doctor record if missing
        existing_doc = session.query(models.Doctor).filter(models.Doctor.user_id == doctor_user.id).first()
        if not existing_doc:
            d = models.Doctor(user_id=doctor_user.id, doctor_id='DOC1', name='Dr Sample', qualification='MD', experience=10, department='General', availability={'monday':'9-17','tuesday':'9-17'})
            session.add(d)
            session.commit()

        # seed a sample staff user
        staff_username = os.getenv('SAMPLE_STAFF', 'staff1')
        staff_email = os.getenv('SAMPLE_STAFF_EMAIL', 'staff1@example.com')
        staff_user = session.query(models.User).filter(models.User.username == staff_username).first()
        staff_role = session.query(models.Role).filter(models.Role.name == 'staff').first()
        if not staff_user:
            hashed = auth.get_password_hash('staffpass')
            staff_user = models.User(username=staff_username, email=staff_email, hashed_password=hashed, full_name='Staff Sample', role=staff_role)
            session.add(staff_user)
            session.commit()

        # seed beds if none exist
        try:
            existing_beds = session.query(models.Bed).count()
            if existing_beds == 0:
                session.add(models.Bed(type='ICU', total=10, occupied=2))
                session.add(models.Bed(type='General', total=50, occupied=10))
                session.commit()
        except Exception:
            session.rollback()
    finally:
        session.close()
