"""
HelioTrace — Home page.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.title("☀️ HelioTrace")
st.subheader("Interactive CME Propagation Explorer")
st.markdown(
    """
    **HelioTrace** is an interactive application for **space weather analysis**.
    It streamlines the **workflow** from coronagraph observations to impact
    forecasts of **Coronal Mass Ejections (CMEs)**, by integrating 3D GCS
    geometric reconstruction with drag-based physics modelling.
    """
)

st.divider()

# ---------------------------------------------------------------------------
# Quick Start
# ---------------------------------------------------------------------------
st.subheader("🚀 Quick Start")
st.markdown(
    "📈 **Enter GCS and Height-Time Data** ➢ "
    "📐 **Inspect 3D Shape and Speed Fit** ➢ "
    "🎯 **Set Target & Drag Parameters** ➢ "
    "▶️ **Run Simulation** ➢ "
    "📊 **Get Arrival Forecast** "
)
st.info("Hit **⚡ Fill with example** to explore the full workflow with real CME data instantly!")

st.divider()

# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------
st.subheader("✨ Features")
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        """
        - 🌐 **Interactive 3D Reconstructions** — Turn reconstruction data into interactive 3D flux-rope visualizations.
        - 🎯 **Geometric Hit vs. Miss Check** — Quickly distinguish between target-impacting events and off-target misses.
        - 📐 **Kinematic Fitting** — Extract initial CME apex velocities from height-time profiles.
        - 🏹 **Target-Directed Kinematics** — Auto-extract the Earthward/target-directed velocity.
        """
    )
with col2:
    st.markdown(
        """
        - 🌊 **Drag-Based Model (DBM)** — Simulate ICME propagation with the field-standard, highly cited benchmark.
        - 🔬 **Physics-Enhanced MoDBM** — Solve ICME propagation numerically, featuring variable solar wind conditions.
        - 📊 **Trajectory Analytics** — Visually track and compare ICME kinematics side-by-side for both models.
        - 🕐 **Space Weather Forecasting** — Forecast ToA, transit time, and impact speed to help assess risks.
        """
    )

st.divider()

# ---------------------------------------------------------------------------
# Science Background
# ---------------------------------------------------------------------------
st.subheader("🔬 Science Background")
st.markdown(
    """
    Coronal Mass Ejections (CMEs) are explosive eruptions of magnetised plasma from
    the Sun's corona. When directed at Earth, ICMEs (their interplanetary counterpart)
    can trigger severe geomagnetic storms. To forecast these impacts for Earth and
    other targets in the inner heliosphere, HelioTrace simulates the ICME's journey
    using a four-step physics workflow:

    1. **📷 3D Reconstruction**: A true 3D model of the CME, optimally obtained from
       multi-viewpoint satellite data, is used to eliminate 2D projection errors common
       in traditional forecasting methods.
    2. **📈 Kinematic Tracking**: By tracking the CME's front (or "apex") height across
       sequential images, its initial expansion speed radially outward from the Sun's
       corona can be approximated.
    3. **🎯 Target-Directed Velocity**: Assuming the CME expands self-similarly, the
       precise velocity component directed at the chosen target (e.g. Earth) can be
       extracted using a 3D geometric ratio.
    4. **🌊 Interplanetary Propagation**: In interplanetary space, the ambient solar wind
       acts as a drag force. Thus, fast ICMEs brake, while slow ones accelerate. This drag
       is modelled to forecast accurate arrival times and speeds.
    """
)

st.markdown("#### Core Physics Frameworks")
st.markdown("HelioTrace is built on heliophysics research, utilizing the following frameworks:")
st.markdown(
    "| Component | Scientific Model | What it enables |\n"
    "| :--- | :--- | :--- |\n"
    "| **3D CME Shape** "
    "| Graduated Cylindrical Shell (GCS) – "
    "[Thernisien et al. (2006)](https://doi.org/10.1086/508254) "
    "| 3D flux-rope modelling to extract physical dimensions and kinematics. |\n"
    "| **Constant-Drag Force** "
    "| Drag-Based Model (DBM) – "
    "[Vršnak et al. (2013)](https://doi.org/10.1007/s11207-012-0035-4) "
    "| Analytical equation of motion featuring a constant solar wind speed estimate. |\n"
    "| **Variable-Drag Force** "
    "| Modified DBM (MoDBM) – "
    "[Müller (2025)](https://doi.org/10.5281/zenodo.18788366), "
    "solar wind profiles from "
    "[Venzmer & Bothmer (2018)](https://doi.org/10.1051/0004-6361/201731831) "
    "| Numerically integrated solution with distance- and SSN-dependent solar wind models. |"
)

st.divider()

# ---------------------------------------------------------------------------
# Acknowledgments
# ---------------------------------------------------------------------------
with st.expander("📚 Acknowledgments & Credits", expanded=False):
    st.markdown(
        """
        #### GCS Geometry Code
        Significant portions of the GCS mesh geometry in this project
        (`src/heliotrace/physics/geometry.py`) are adapted from the
        **[gcs_python](https://github.com/johan12345/gcs_python)** library
        by **Johan von Forstner**, which is itself a Python port of IDL routines
        from the original GCS model implementation. I gratefully acknowledge
        this foundational work.

        #### Scientific Models & Citations
        - **GCS Model**: Thernisien, A. F. R., Howard, R. A., & Vourlidas, A. (2006).
        ApJ, 652, 763. [doi:10.1086/508254](https://doi.org/10.1086/508254)
        - **DBM**: Vršnak, B. et al. (2013). Solar Phys, 285, 295–315.
        [doi:10.1007/s11207-012-0035-4](https://doi.org/10.1007/s11207-012-0035-4)
        - **MoDBM solar wind speed/density profiles**: Venzmer, M. S. & Bothmer, V. (2018).
          A&A, 611, A36. [doi:10.1051/0004-6361/201731831](https://doi.org/10.1051/0004-6361/201731831)

        #### Software
        | Package | Role |
        |---|---|
        | [Streamlit](https://streamlit.io) | Interactive web framework |
        | [Plotly](https://plotly.com/python/) | Interactive visualisation |
        | [SciPy](https://scipy.org) | ODE integration, triangulation, linear algebra |
        | [NumPy](https://numpy.org) | Numerical arrays |
        | [Astropy](https://www.astropy.org) | Units and physical constants |
        | [SunPy](https://sunpy.org) | Solar coordinate frames (optional) |
        | [Pandas](https://pandas.pydata.org) | Tabular data handling |
        """
    )

st.divider()

# ---------------------------------------------------------------------------
# Data source notice
# ---------------------------------------------------------------------------
st.caption(
    "📡 Data source: GCS parameters derived from multi-viewpoint coronagraph observations "
    "(LASCO C2/C3, STEREO COR1/COR2) using the Graduated Cylindrical Shell model."
)

# ---------------------------------------------------------------------------
# SEO injection (hidden)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="display:none">
        <h2>Keywords</h2>
        <p>HelioTrace, Solar physics simulation, Heliospheric modeling, Coronal Mass Ejection,
        Space weather forecasting Python, ICME arrival time, Drag-Based Model, GCS model,
        Solar eruption, CME propagation, Streamlit space weather app.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
