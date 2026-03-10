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
    **HelioTrace** is an interactive research tool for modelling the propagation of
    **Interplanetary Coronal Mass Ejections (ICMEs)** through the inner heliosphere.
    Built with Python & Streamlit, it combines 3D geometric fitting of coronagraph
    observations with physics-based drag models to predict ICME arrival times and
    impact speeds at any heliospheric target.
    """
)

st.divider()

# ---------------------------------------------------------------------------
# Quick Start
# ---------------------------------------------------------------------------
st.subheader("🚀 Quick Start")
st.markdown(
    """
    1. **📡 GCS Observations** — Enter your observed GCS height-time measurements
       in the interactive data table. Inspect the Height-Time fit and the live 3D
       GCS geometry visualisation.
    2. **🌌 ICME Propagation** — Configure the target body and drag model parameters
       in the sidebar, then press **▶ Run Simulation** to compute DBM and MoDBM
       trajectories and arrival predictions.
    """
)

st.divider()

# ---------------------------------------------------------------------------
# Capabilities
# ---------------------------------------------------------------------------
st.subheader("✨ Capabilities")
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        """
        - 📋 **Interactive GCS data table** — enter multi-epoch coronagraph measurements
        - 📐 **Linear Height-Time fit** — weighted least-squares with velocity & error annotation
        - 🌐 **Live 3D GCS geometry** — Plotly Mesh3d visualisation of the flux-rope shell
        - 🎯 **Geometric hit/miss check** — projection ratio toward any heliospheric target
        """
    )
with col2:
    st.markdown(
        """
        - 🌬️ **DBM** — analytic Drag-Based Model with configurable solar wind speed
        - 🔬 **MoDBM** — Modified DBM with distance/SSN-dependent density profile (solved numerically)
        - 📊 **Comparison plots** — side-by-side Distance-vs-Time and Velocity-vs-Time
        - 🕐 **Arrival prediction** — transit time, impact speed, and ΔToA vs observation
        """
    )

st.divider()

# ---------------------------------------------------------------------------
# Science Background
# ---------------------------------------------------------------------------
st.subheader("🔬 Science Background")
st.markdown(
    """
    **CMEs** are large-scale eruptions of magnetised plasma from the Sun's corona.
    When directed toward Earth or other targets in the inner heliosphere, their arrival
    can trigger geomagnetic storms and disrupt critical infrastructure — making accurate
    transit-time forecasting an active area of space weather research.

    HelioTrace chains three physics components:

    | Component | Model | What it enables in the app |
    |---|---|---|
    | **3D CME geometry** | GCS — Graduated Cylindrical Shell ([Thernisien et al. 2006](https://doi.org/10.1086/508254)) | Live 3D mesh, projection ratio, initial velocity from multi-epoch observations |
    | **Constant-drag propagation** | DBM ([Vršnak et al. 2013](https://doi.org/10.1007/s11207-012-0035-4)) | Fast analytic transit-time estimate with a single solar wind speed parameter |
    | **Physics-enhanced propagation** | MoDBM (density profile from [Venzmer & Bothmer 2018](https://doi.org/10.1051/0004-6361/201731831)) | Numerically integrated solution with distance- and SSN-dependent solar wind |

    The **target-directed velocity** ($v_\\text{target}$) is derived from the apex velocity
    by self-similar expansion scaling: $v_\\text{target} = v_\\text{apex} \\cdot (h_\\text{target}/h_\\text{apex})$,
    where the height ratio is extracted from the GCS geometry.
    """
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
          *Modeling of Flux Rope Coronal Mass Ejections.* ApJ, 652, 763.
          [doi:10.1086/508254](https://doi.org/10.1086/508254)
        - **DBM**: Vršnak, B. et al. (2013). *Propagation of Interplanetary CMEs.*
          Solar Phys, 285, 295–315. [doi:10.1007/s11207-012-0035-4](https://doi.org/10.1007/s11207-012-0035-4)
        - **MoDBM solar wind profile**: Venzmer, M. S. & Bothmer, V. (2018).
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
