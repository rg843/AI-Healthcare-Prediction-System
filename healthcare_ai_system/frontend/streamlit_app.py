import streamlit as st
import requests
import plotly.express as px
import os
from pathlib import Path
import pandas as pd
import json
import io
import zipfile

try:
    API_URL = st.secrets.get("API_URL")
except Exception:
    API_URL = None

if not API_URL:
    API_URL = os.environ.get("API_URL", "http://localhost:8000/api")


def main():
    st.set_page_config(page_title="Healthcare AI", layout="wide")
    st.sidebar.title("Healthcare AI")
    page = st.sidebar.selectbox("Navigation", ["Dashboard", "Predict", "Outcome", "Treatment", "Appointments", "EHR", "Beds", "Staff", "Patients", "Manage Patients", "Manage Doctors", "Admin Users", "Batch Results"])

    # simple auth selector
    if 'admin_page' not in st.session_state:
        st.session_state['admin_page'] = None
    auth_page = st.sidebar.selectbox("Account", ["Anonymous", "Login", "Register"]) if 'auth_page' not in st.session_state else st.session_state.get('auth_page')
    st.session_state['auth_page'] = auth_page

    if auth_page == "Login":
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login Now"):
            r = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
            if r.status_code == 200:
                tok = r.json().get('access_token')
                st.session_state['token'] = tok
                st.success("Logged in")
                st.experimental_rerun()
            else:
                st.error(r.text)

    if auth_page == "Register":
        st.header("Register")
        username = st.text_input("Username", key="reg_user")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Create Account"):
            r = requests.post(f"{API_URL}/auth/register", json={"username": username, "email": email, "password": password})
            if r.status_code == 200:
                st.success("Account created and logged in")
                st.session_state['token'] = r.json().get('access_token')
                st.experimental_rerun()
            else:
                st.error(r.text)

    token = st.session_state.get("token")
    headers = {}
    if token:
        headers = {"Authorization": f"Bearer {token}"}

    # Pages
    if page == "Dashboard":
        st.header("Admin Dashboard")
        st.write("KPIs and charts will show here")
        fig = px.bar(x=["ICU", "General"], y=[10, 50], title="Beds Occupancy")
        st.plotly_chart(fig)

    if page == "Predict":
        st.header("Disease Prediction")
        age = st.number_input("Age", 0, 120, 30)
        gender = st.selectbox("Gender", ["Male", "Female"])
        bmi = st.number_input("BMI", 0.0, 100.0, 24.0)
        bp = st.number_input("Blood Pressure", 0.0, 300.0, 120.0)
        sugar = st.number_input("Sugar", 0.0, 1000.0, 90.0)
        chol = st.number_input("Cholesterol", 0.0, 1000.0, 180.0)
        hr = st.number_input("Heart Rate", 0.0, 250.0, 70.0)
        if st.button("Predict"):
            payload = {"age": age, "gender": gender, "symptoms": [], "bmi": bmi, "blood_pressure": bp, "sugar": sugar, "cholesterol": chol, "heart_rate": hr}
            r = requests.post(f"{API_URL}/predict", json=payload)
            if r.status_code == 200:
                st.json(r.json())
            else:
                st.error(r.text)

    if page == "Appointments":
        st.header("Book Appointment")
        pid = st.number_input("Patient ID", 0, 100000, 1)
        did = st.number_input("Doctor ID", 0, 100000, 1)
        sched = st.text_input("Scheduled At (ISO)")
        if st.button("Book"):
            if not token:
                st.info("You must be logged in to book an appointment.")
            else:
                payload = {"patient_id": pid, "doctor_id": did, "scheduled_at": sched}
                r = requests.post(f"{API_URL}/appointments", json=payload, headers=headers)
                if r.status_code == 200:
                    st.success("Appointment booked")
                else:
                    st.error(r.text)

        st.markdown("---")
        st.subheader("My Appointments")
        if not token:
            st.info("You must be logged in to view your appointments.")
            if st.button("Go to Login"):
                st.session_state['auth_page'] = "Login"
                st.experimental_rerun()
        else:
            r = requests.get(f"{API_URL}/appointments", headers=headers)
            if r.status_code == 200:
                for a in r.json():
                    st.write(a)
            else:
                st.error(r.text)

    if page == "EHR":
        st.header("EHR Records")
        with st.form('create_ehr'):
            pid = st.number_input('Patient ID', 0, 100000, 1)
            did = st.number_input('Doctor ID', 0, 100000, 1)
            diag = st.text_area('Diagnosis')
            pres = st.text_area('Prescriptions (JSON)')
            submitted = st.form_submit_button('Create EHR')
            if submitted:
                try:
                    pres_json = {} if not pres else eval(pres)
                except Exception:
                    pres_json = {}
                payload = {'patient_id': pid, 'doctor_id': did, 'diagnosis': diag, 'prescriptions': pres_json}
                r = requests.post(f"{API_URL}/ehr", json=payload, headers=headers)
                if r.status_code == 200:
                    st.success('EHR created')
                else:
                    st.error(r.text)

        st.markdown('---')
        st.subheader('View EHR by Patient')
        pidq = st.number_input('Patient ID (view)', 0, 100000, 1, key='view_pid')
        if st.button('Refresh EHR'):
            r = requests.get(f"{API_URL}/ehr/patient/{pidq}", headers=headers)
            if r.status_code == 200:
                st.write(r.json())
            else:
                st.error(r.text)

    if page == "Treatment":
        st.header("Treatment Recommendation")
        age = st.number_input("Age", 0, 120, 30, key='t_age')
        gender = st.selectbox("Gender", ["Male", "Female"], key='t_gender')
        bmi = st.number_input("BMI", 0.0, 100.0, 24.0, key='t_bmi')
        bp = st.number_input("Blood Pressure", 0.0, 300.0, 120.0, key='t_bp')
        sugar = st.number_input("Sugar", 0.0, 1000.0, 90.0, key='t_sugar')
        chol = st.number_input("Cholesterol", 0.0, 1000.0, 180.0, key='t_chol')
        hr = st.number_input("Heart Rate", 0.0, 250.0, 70.0, key='t_hr')
        if st.button("Get Recommendation"):
            payload = {"age": age, "gender": gender, "bmi": bmi, "blood_pressure": bp, "sugar": sugar, "cholesterol": chol, "heart_rate": hr}
            r = requests.post(f"{API_URL}/treatment/recommend", json=payload, headers=headers)
            if r.status_code == 200:
                st.json(r.json())
            else:
                st.error(r.text)

    if page == "Outcome":
        st.header("Outcome Prediction")
        age = st.number_input("Age", 0, 120, 30, key='o_age')
        gender = st.selectbox("Gender", ["Male", "Female"], key='o_gender')
        bmi = st.number_input("BMI", 0.0, 100.0, 24.0, key='o_bmi')
        bp = st.number_input("Blood Pressure", 0.0, 300.0, 120.0, key='o_bp')
        sugar = st.number_input("Sugar", 0.0, 1000.0, 90.0, key='o_sugar')
        chol = st.number_input("Cholesterol", 0.0, 1000.0, 180.0, key='o_chol')
        hr = st.number_input("Heart Rate", 0.0, 250.0, 70.0, key='o_hr')
        if st.button("Predict Outcome"):
            payload = {"age": age, "gender": gender, "bmi": bmi, "blood_pressure": bp, "sugar": sugar, "cholesterol": chol, "heart_rate": hr}
            r = requests.post(f"{API_URL}/predict/outcome", json=payload)
            if r.status_code == 200:
                st.json(r.json())
            else:
                st.error(r.text)

    if page == "Beds":
        st.header("Beds Forecast")
        days = st.number_input("Forecast days", 1, 30, 7)
        if st.button("Forecast"):
            r = requests.post(f"{API_URL}/beds/forecast", json={"days": days})
            if r.status_code == 200:
                data = r.json().get('beds', [])
                # build plotly chart
                for bed in data:
                    df_x = [d['day'] for d in bed.get('forecast', [])]
                    df_y_occ = [d['occupied'] for d in bed.get('forecast', [])]
                    df_y_av = [d['available'] for d in bed.get('forecast', [])]
                    fig = px.line(x=df_x, y=[df_y_occ, df_y_av], labels={'x': 'Day', 'value': 'Count'}, title=f"{bed.get('type')} Bed Forecast")
                    fig.update_layout(legend=dict(title='Series'), xaxis=dict(dtick=1))
                    st.plotly_chart(fig)
            else:
                st.error(r.text)

    if page == "Staff":
        st.header("Staff Scheduler")
        if st.button("Generate Schedule"):
            r = requests.post(f"{API_URL}/staff/schedule")
            if r.status_code == 200:
                st.json(r.json())
            else:
                st.error(r.text)

    if page == "Manage Patients":
        st.header("Manage Patients")
        if not token:
            st.info("You must be logged in to manage patients.")
            if st.button("Go to Login"):
                st.session_state['auth_page'] = "Login"
                st.experimental_rerun()
        else:
            if st.button("Refresh Patients"):
                pass
            r = requests.get(f"{API_URL}/patients", headers=headers)
            if r.status_code == 200:
                patients = r.json()
                for p in patients:
                    st.write(p)
                    cols = st.columns(3)
                    if cols[0].button(f"Delete {p['id']}"):
                        rd = requests.delete(f"{API_URL}/patients/{p['id']}", headers=headers)
                        if rd.status_code == 200:
                            st.success("Deleted")
                        else:
                            st.error(rd.text)
            else:
                st.error(r.text)

    if page == "Batch Results":
        st.header("Batch Prediction Results")
        base = Path.cwd()
        preds1 = base / "prediction_results.csv"
        preds2 = base / "healthcare_ai_system" / "data" / "prediction_results.csv"
        overall_csv = base / "healthcare_ai_system" / "data" / "overall_results.csv"
        detailed_jsonl = base / "healthcare_ai_system" / "data" / "overall_detailed.jsonl"

        if preds1.exists():
            try:
                dfp = pd.read_csv(preds1)
                st.subheader("prediction_results.csv")
                st.dataframe(dfp)
            except Exception as e:
                st.error(f"Failed to read {preds1}: {e}")

        if overall_csv.exists():
            try:
                dfo = pd.read_csv(overall_csv)
                st.subheader("overall_results.csv")
                st.dataframe(dfo)
            except Exception as e:
                st.error(f"Failed to read {overall_csv}: {e}")

        if detailed_jsonl.exists():
            try:
                st.subheader("overall_detailed.jsonl (summary)")
                items = []
                with open(detailed_jsonl, 'r', encoding='utf-8') as fh:
                    for i, line in enumerate(fh):
                        if i >= 100:
                            break
                        items.append(json.loads(line))
                summary = []
                for it in items:
                    pred = it.get('prediction', {})
                    summary.append({'id': it.get('id'), 'disease': pred.get('disease'), 'severity': pred.get('severity'), 'confidence': pred.get('confidence')})
                st.dataframe(pd.DataFrame(summary))
            except Exception as e:
                st.error(f"Failed to read {detailed_jsonl}: {e}")

        if any(p.exists() for p in [preds1, overall_csv, detailed_jsonl, preds2]):
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, 'w') as zf:
                for p in [preds1, preds2, overall_csv, detailed_jsonl]:
                    if p.exists():
                        zf.write(p, arcname=p.name)
            buf.seek(0)
            st.download_button(label="Download all results (zip)", data=buf, file_name="batch_results.zip", mime="application/zip")

    if page == "Manage Doctors":
        st.header("Manage Doctors")
        if not token:
            st.info("You must be logged in to manage doctors.")
            if st.button("Go to Login"):
                st.session_state['auth_page'] = "Login"
                st.experimental_rerun()
        else:
            with st.form("create_doc"):
                doc_id = st.text_input("Doctor ID")
                name = st.text_input("Name", key="doc_name")
                qualification = st.text_input("Qualification")
                dept = st.text_input("Department")
                submitted = st.form_submit_button("Create Doctor")
                if submitted:
                    payload = {"doctor_id": doc_id, "name": name, "qualification": qualification, "department": dept}
                    r = requests.post(f"{API_URL}/doctors", json=payload, headers=headers)
                    if r.status_code == 200:
                        st.success("Doctor created")
                    else:
                        st.error(r.text)
            r = requests.get(f"{API_URL}/doctors", headers=headers)
            if r.status_code == 200:
                for d in r.json():
                    st.write(d)
                    cols = st.columns(3)
                    if cols[0].button(f"Delete doc {d['id']}"):
                        rd = requests.delete(f"{API_URL}/doctors/{d['id']}", headers=headers)
                        if rd.status_code == 200:
                            st.success("Deleted")
                        else:
                            st.error(rd.text)
            else:
                st.error(r.text)

    if page == "Admin Users":
        st.header("Admin - Users")
        if not token:
            st.info("You must be logged in as an admin to access this page.")
            if st.button("Go to Login"):
                st.session_state['auth_page'] = "Login"
                st.experimental_rerun()
        else:
            # create user
            with st.form("create_user"):
                uname = st.text_input("Username")
                email = st.text_input("Email")
                pwd = st.text_input("Password", type="password")
                role = st.selectbox("Role", ["admin", "doctor", "patient", "staff"])
                submitted = st.form_submit_button("Create User")
                if submitted:
                    payload = {"username": uname, "email": email, "password": pwd, "role": role}
                    r = requests.post(f"{API_URL}/users", json=payload, headers=headers)
                    if r.status_code == 200:
                        st.success("User created")
                        st.experimental_rerun()
                    elif r.status_code in (401, 403):
                        st.error(r.text)
                        if st.button("Go to Login"):
                            st.session_state['auth_page'] = "Login"
                            st.experimental_rerun()
                    else:
                        st.error(r.text)

            # list users
            r = requests.get(f"{API_URL}/users", headers=headers)
            if r.status_code == 200:
                for u in r.json():
                    st.write(u)
                    cols = st.columns(4)
                    if cols[0].button(f"Make admin {u['id']}"):
                        rd = requests.put(f"{API_URL}/users/{u['id']}/role", json={"role": "admin"}, headers=headers)
                        if rd.status_code == 200:
                            st.success("Role updated")
                            st.experimental_rerun()
                        else:
                            st.error(rd.text)
                    if cols[1].button(f"Delete {u['id']}"):
                        rd = requests.delete(f"{API_URL}/users/{u['id']}", headers=headers)
                        if rd.status_code == 200:
                            st.success("Deleted")
                            st.experimental_rerun()
                        else:
                            st.error(rd.text)
            elif r.status_code == 403:
                st.error("Forbidden: you need admin privileges to view users.")
            elif r.status_code == 401:
                st.info("Not authenticated. Please login as admin.")
                if st.button("Go to Login"):
                    st.session_state['auth_page'] = "Login"
                    st.experimental_rerun()
            else:
                st.error(r.text)


if __name__ == '__main__':
    main()
