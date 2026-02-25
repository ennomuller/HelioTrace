"""
GCS Observations — HelioTrace page 1.

Provides the geometrical and observation data interface:
  - GCS height-time data entry (interactive table)
  - Weighted linear H-T fit with velocity annotation
  - 3D GCS mesh visualisation and target hit/miss check

Derived parameters and the cleaned DataFrame are persisted to
``st.session_state`` (keys ``KEY_DERIVED_PARAMS`` and ``KEY_CLEAN_DF``)
so that the ICME Propagation page can consume them without re-running
the geometry.
"""
from __future__ import annotations

import astropy.units as u
import pandas as pd
import streamlit as st

from heliotrace.config import DEFAULT_GCS_ROWS, KEY_DERIVED_PARAMS, KEY_CLEAN_DF
from heliotrace.models.schemas import DerivedGCSParams
from heliotrace.physics.apex_ratio import get_target_apex_ratio
from heliotrace.simulation.runner import derive_gcs_params
from heliotrace.ui.components.gcs_plot import build_gcs_figure
from heliotrace.ui.components.ht_plot import build_ht_figure
from heliotrace.ui.components.sidebar_inputs import render_sidebar
from heliotrace.ui.state import init_session_state

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="GCS Observations — HelioTrace",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Cached helpers
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _cached_derived_params(df: pd.DataFrame, height_error: float) -> DerivedGCSParams:
    """Cache the linear H-T fit — re-runs only when table data or error changes."""
    return derive_gcs_params(df, height_error)


@st.cache_data(show_spinner=False)
def _cached_projection_ratio(
    alpha_deg: float,
    kappa: float,
    cme_lat_deg: float,
    cme_lon_deg: float,
    tilt_deg: float,
    target_lat_deg: float,
    target_lon_deg: float,
) -> float:
    """Cache the (CPU-heavy) GCS mesh projection computation."""
    return get_target_apex_ratio(
        alpha=alpha_deg     * u.deg,
        kappa=kappa,
        cme_lat=cme_lat_deg * u.deg,
        cme_lon=cme_lon_deg * u.deg,
        tilt=tilt_deg        * u.deg,
        target_lat=target_lat_deg * u.deg,
        target_lon=target_lon_deg * u.deg,
    )


# ---------------------------------------------------------------------------
# Initialise session state + render sidebar (no Run button on this page)
# ---------------------------------------------------------------------------
init_session_state()
config, _run_clicked = render_sidebar(show_run_button=False)

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("📡 GCS Observations")
st.caption(
    f"Event: **{config.event_str}** | "
    f"Target: **{config.target.name}** ({config.target.distance:.2f} AU)"
)

# ---------------------------------------------------------------------------
# GCS data table
# ---------------------------------------------------------------------------
st.subheader("GCS Height-Time Measurements")
st.markdown(
    "Enter the GCS height-time measurements below. "
    "Each row is one measurement epoch. "
    "The Height-Time fit and 3D geometry update automatically."
)

col_info, col_table = st.columns([1, 2])

with col_info:
    st.info(
        "**Column guide**\n"
        "- **datetime** — UTC observation time\n"
        "- **lon / lat** — Stonyhurst coordinates [deg]\n"
        "- **tilt** — Flux-rope tilt [deg]\n"
        "- **half_angle** — GCS half-angle α [deg]\n"
        "- **height** — CME front height [R☉]\n"
        "- **kappa** — GCS aspect ratio κ"
    )
    st.caption(f"Height measurement error: **±{config.height_error} R☉** (set in sidebar)")

with col_table:
    edited_df: pd.DataFrame = st.data_editor(
        pd.DataFrame(DEFAULT_GCS_ROWS),
        hide_index=True,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "datetime":   st.column_config.DatetimeColumn("UTC Time",       required=True, format="YYYY-MM-DD HH:mm"),
            "lon":        st.column_config.NumberColumn("Lon [deg]",        min_value=-180.0, max_value=180.0,  step=0.5,  format="%.1f"),
            "lat":        st.column_config.NumberColumn("Lat [deg]",        min_value=-90.0,  max_value=90.0,   step=0.5,  format="%.1f"),
            "tilt":       st.column_config.NumberColumn("Tilt [deg]",       min_value=-90.0,  max_value=90.0,   step=0.5,  format="%.1f"),
            "half_angle": st.column_config.NumberColumn("Half Angle [deg]", min_value=0.0,    max_value=90.0,   step=0.5,  format="%.1f"),
            "height":     st.column_config.NumberColumn("Height [R☉]",      min_value=0.1,    max_value=300.0,  step=0.1,  format="%.2f"),
            "kappa":      st.column_config.NumberColumn("κ (kappa)",        min_value=0.01,   max_value=0.99,   step=0.01, format="%.2f"),
        },
        key="gcs_editor",
    )

if len(edited_df) < 2:
    st.info("ℹ️ Add at least **2 data rows** to see the Height-Time fit and GCS geometry.")
    st.stop()

req_cols = ["datetime", "lon", "lat", "tilt", "half_angle", "height", "kappa"]
clean_df = edited_df.dropna(subset=req_cols).sort_values("datetime").reset_index(drop=True)

if len(clean_df) < 2:
    st.warning("⚠️ Some rows have incomplete data — fill all columns in at least 2 rows.")
    st.stop()

# ---------------------------------------------------------------------------
# H-T fit — persist to session state for Propagation page
# ---------------------------------------------------------------------------
derived: DerivedGCSParams = _cached_derived_params(clean_df, config.height_error)
st.session_state[KEY_DERIVED_PARAMS] = derived
st.session_state[KEY_CLEAN_DF] = clean_df

# ---------------------------------------------------------------------------
# Height-Time diagram
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Height-Time Diagram")

ht_fig = build_ht_figure(
    df=clean_df,
    height_error=config.height_error,
    slope=derived.fit_slope,
    intercept=derived.fit_intercept,
    chi_squared=derived.fit_chi_squared,
    v_apex_kms=derived.v_apex_kms,
    v_apex_error_kms=derived.v_apex_error_kms,
)
st.plotly_chart(ht_fig, use_container_width=True)

# ---------------------------------------------------------------------------
# GCS 3D Geometry & Projection
# ---------------------------------------------------------------------------
st.divider()
st.subheader("GCS Geometry (3D) & Target Projection")

with st.spinner("Computing GCS geometry…  (cached after first run)"):
    proj_ratio = _cached_projection_ratio(
        alpha_deg=derived.alpha_deg,
        kappa=derived.kappa,
        cme_lat_deg=derived.lat_deg,
        cme_lon_deg=derived.lon_deg,
        tilt_deg=derived.tilt_deg,
        target_lat_deg=config.target.lat,
        target_lon_deg=config.target.lon,
    )

target_hit_geometry = proj_ratio > 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("Apex Velocity",    f"{derived.v_apex_kms:.0f} km/s",
          delta=f"±{derived.v_apex_error_kms:.0f}")
m2.metric("Projection Ratio", f"{proj_ratio:.4f}" if target_hit_geometry else "—")
m3.metric("v₀ toward Target", f"{derived.v_apex_kms * proj_ratio:.0f} km/s" if target_hit_geometry else "MISS")
m4.metric("Target",           config.target.name)

if not target_hit_geometry:
    st.error(
        f"**GEOMETRY: MISS** — The CME flank does not encompass **{config.target.name}** "
        "with the current GCS parameters. Adjust longitude, latitude, or half-angle."
    )
else:
    st.success(
        f"✓ **HIT** — The CME flank intercepts **{config.target.name}** at a "
        f"projection ratio of **{proj_ratio:.4f}** "
        f"(v₀ = {derived.v_apex_kms * proj_ratio:.0f} km/s toward target)."
    )

gcs_fig = build_gcs_figure(
    alpha_deg=derived.alpha_deg,
    kappa=derived.kappa,
    lat_deg=derived.lat_deg,
    lon_deg=derived.lon_deg,
    tilt_deg=derived.tilt_deg,
    target_lat_deg=config.target.lat,
    target_lon_deg=config.target.lon,
    projection_ratio=proj_ratio,
    target_name=config.target.name,
)
st.plotly_chart(gcs_fig, use_container_width=True)

st.divider()
st.info(
    "✅ GCS parameters saved. Navigate to **🌌 ICME Propagation** in the sidebar "
    "to configure drag model parameters and run the simulation."
)
