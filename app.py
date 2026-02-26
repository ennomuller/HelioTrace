"""
HelioTrace — Streamlit application entry point.

Run locally:
    streamlit run app.py

Run via Docker:
    docker-compose up
"""
import streamlit as st

st.set_page_config(
    page_title="HelioTrace",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

pg = st.navigation(
    [
        st.Page("pages/home.py", title="🏠 Home"),
        st.Page("pages/01_Propagation_Simulator.py", title="🚀 Propagation Simulator"),
    ]
)
pg.run()
