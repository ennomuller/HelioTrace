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

# app.py
st.markdown(
    """
    <style>
    :root {
        --top-gutter: 0.75rem; /* The master "tightness" control */
    }
    [data-testid="stMainBlockContainer"] {
        padding-top: var(--top-gutter);
    }
    @media (max-width: 768px) {
        :root { --top-gutter: 0.5rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

pg = st.navigation(
    [
        st.Page("pages/home.py", title="🏠 Home"),
        st.Page("pages/01_Propagation_Simulator.py", title="🚀 Propagation Simulator"),
    ]
)
pg.run()
