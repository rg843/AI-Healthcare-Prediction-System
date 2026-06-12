import streamlit as st
import requests

st.set_page_config(layout="wide", page_title="Healthcare AI Dashboard")
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Go to", ["Dashboard", "Predict", "Appointments"])

if page == "Dashboard":
    st.title("Healthcare AI - Dashboard (Starter)")
    st.write("This is a starter Streamlit UI. Connect to the backend `/api` for live data.")

if page == "Predict":
    st.header("Disease Prediction")
    age = st.number_input("Age", min_value=0, max_value=120, value=45)
    bmi = st.number_input("BMI", min_value=0.0, max_value=100.0, value=25.0)
    sugar = st.number_input("Blood Sugar", min_value=0.0, max_value=500.0, value=100.0)
    bp = st.number_input("Blood Pressure", min_value=0.0, max_value=300.0, value=120.0)
    if st.button("Predict"):
        payload = {"age": age, "bmi": bmi, "sugar": sugar, "blood_pressure": bp}
        try:
            resp = requests.post("http://127.0.0.1:8000/api/predict", json=payload, timeout=5).json()
            st.json(resp)
        except Exception as e:
            st.error(f"Failed to reach backend: {e}")

if page == "Appointments":
    st.header("Appointments")
    st.write("Appointment management coming soon.")
