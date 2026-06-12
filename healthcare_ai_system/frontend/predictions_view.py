import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title='Batch Predictions', layout='wide')
st.title('Batch Prediction Results')

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'prediction_results.csv')
if not os.path.exists(DATA_PATH):
    st.error(f'Prediction results not found at {DATA_PATH}')
else:
    df = pd.read_csv(DATA_PATH)
    st.subheader('Summary')
    st.write('Rows:', len(df))
    st.write('Disease counts:')
    st.write(df['disease'].value_counts())
    st.write('Severity distribution:')
    st.write(df['severity'].value_counts())
    st.write('Average confidence:', df['confidence'].astype(float).mean())

    st.subheader('Table')
    st.dataframe(df)

    st.subheader('Confidence Distribution')
    fig = px.histogram(df, x='confidence', nbins=20, title='Confidence Distribution')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader('Risk Score vs Confidence')
    fig2 = px.scatter(df, x='risk_score', y='confidence', color='severity', title='Risk vs Confidence')
    st.plotly_chart(fig2, use_container_width=True)
