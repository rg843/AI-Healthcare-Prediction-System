import sys, os
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, proj_root)

from backend.app import db, models, auth
from backend.app.main import app
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# ensure DB initialized
db.init_db()

# create a sample patient
session = db.SessionLocal()
try:
    # create patient user
    pu = session.query(models.User).filter(models.User.username == 'patient1').first()
    if not pu:
        pu = models.User(username='patient1', email='patient1@example.com', hashed_password=auth.get_password_hash('patientpass'), full_name='Patient One')
        session.add(pu)
        session.commit()
    patient = session.query(models.Patient).filter(models.Patient.user_id == pu.id).first()
    if not patient:
        patient = models.Patient(user_id=pu.id, name='Patient One', age=45)
        session.add(patient)
        session.commit()
    # create a pending appointment for tomorrow
    tomorrow = (datetime.utcnow() + timedelta(days=1)).replace(microsecond=0).isoformat()
    appt = models.Appointment(patient_id=patient.id, doctor_id=None, scheduled_at=tomorrow, slot='morning', status='pending')
    session.add(appt)
    session.commit()
    appt_id = appt.id
finally:
    session.close()

client = TestClient(app)
resp = client.post('/api/staff/schedule')
print('status', resp.status_code)
print(resp.json())

# cleanup test appointment
session = db.SessionLocal()
try:
    a = session.query(models.Appointment).filter(models.Appointment.id == appt_id).first()
    if a:
        session.delete(a)
        session.commit()
finally:
    session.close()
