"""
HelioTrace — Heliospheric Propagation Simulator
Streamlit application entry point.

Run locally:
    streamlit run app.py

Run via Docker:
    docker-compose up
"""
import streamlit as st

st.set_page_config(
    page_title="HelioTrace",
    page_icon="🌞",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.title("🌞 HelioTrace: Heliospheric Propagation Simulator")
st.caption(
    "An interactive research tool for 3-D CME reconstruction "
    "and inner-heliosphere propagation modelling."
)
st.divider()

# ── Feature cards ─────────────────────────────────────────────────────────────
left, right = st.columns(2, gap="large")

with left:
    st.subheader("What it does")
    st.markdown(
        """
        **HelioTrace** combines two complementary modelling steps into a
        single interactive workflow:

        - **GCS Fitting** — reconstruct the 3-D CME morphology from
          multi-viewpoint coronagraph images using the *Graduated Cylindrical
          Shell* model.  The Height-Time (H-T) profile and initial apex
          velocity are extracted via a weighted linear least-squares fit.

        - **DBM / MODBM Propagation** — propagate the fitted CME to any
          target spacecraft or planet using the *Drag-Based Model* (constant
          drag; Vršnak et al. 2013) or the *Modified DBM* (position-dependent
          drag with a sunspot-number-driven ambient density profile; Venzmer
          & Bothmer 2018).

        Results include predicted **transit time**, **arrival speed**, and
        **arrival epoch**, displayed alongside interactive Plotly charts.
        """
    )

with right:
    st.subheader("How to use")
    st.markdown(
        """
        1. Navigate to **Event Geometry** in the sidebar.
        2. Enter your observed GCS height-time measurements in the data table.
        3. Inspect the live **3-D GCS mesh** and the **H-T fit** in the two
           side-by-side tabs.
        4. Configure the target body, drag model, and solar-wind parameters
           in the sidebar panel, then press **▶ Run Simulation**.
        5. Read off the propagation forecast and KPI summary cards in the
           results section.
        """
    )

st.divider()

# ── Data sources & known limitations ─────────────────────────────────────────
st.subheader("Data Sources & Current Limitations")
st.info(
    """
    **Height-time measurements** are entered manually by the user, derived
    from coronagraph imagery (LASCO C2/C3, STEREO COR1/COR2) processed with
    standard GCS fitting software.

    **Target / spacecraft positions** (e.g., Earth, STEREO-A/B) are currently
    provided as **placeholder / dummy coordinates** for demonstration purposes.
    Live ephemeris retrieval (via `astropy` + `sunpy` HEEQ frames) is planned
    for a future release and will make arrival-time predictions fully
    event-specific.
    """,
    icon="ℹ️",
)

st.divider()

# ── Attribution & License ─────────────────────────────────────────────────────
st.subheader("Attribution & License")

col_attr, col_cite = st.columns(2, gap="large")

with col_attr:
    st.markdown("**Third-party code**")
    st.markdown(
        """
        The GCS geometry core (`src/heliotrace/physics/geometry.py`) is
        adapted from [**gcs_python**](https://github.com/johan12345/gcs_python)
        by **Johan von Forstner**, used under the
        [MIT License](https://github.com/johan12345/gcs_python/blob/master/LICENSE).
        """
    )
    st.markdown("**Project License**")
    st.markdown(
        "HelioTrace is released under the **MIT License** — "
        "see `LICENSE` in the repository root."
    )

with col_cite:
    st.markdown("**Citing HelioTrace**")
    st.markdown("If you use HelioTrace in your research, please cite:")
    st.code(
        """\
Müller, E. (2026). HelioTrace: Solar Propagation Suite [Software].
GitHub. https://github.com/ennomuller/HelioTrace

[Link to Master's Thesis for accurate scientific explanation]\
""",
        language="text",
    )
