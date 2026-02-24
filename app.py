"""
CME Explorer — Streamlit application entry point.

Run locally:
    streamlit run app.py

Run via Docker:
    docker-compose up
"""
import streamlit as st

st.set_page_config(
    page_title="CME Explorer",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("☀️ CME Explorer")
st.markdown(
    """
    Welcome to the **CME Explorer** — an interactive tool for modelling the propagation
    of Coronal Mass Ejections (CMEs) through the inner heliosphere using the
    **Drag-Based Model (DBM)** and the **Modified DBM (MODBM)**.

    ---

    ### How to use
    1. Navigate to **CME Propagation** in the sidebar.
    2. Enter your observed GCS height-time measurements in the data table.
    3. Configure the target spacecraft / planet and drag model parameters in the sidebar.
    4. Press **▶ Run Simulation** to compute the propagation and arrival prediction.

    ---

    > **Data source:** GCS parameters derived from coronagraph observations
    > (LASCO C2/C3, STEREO COR1/COR2) using the Graduated Cylindrical Shell model.
    """
)
