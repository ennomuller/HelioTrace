"""
ICME Propagation — HelioTrace page 2.

Provides the simulation setup and ICME propagation interface:
  - Drag-Based Model (DBM) and Modified DBM (MODBM) simulation runner
  - KPI cards: transit time, impact speed, arrival time, ΔToA vs observation
  - Distance-vs-Time and Velocity-vs-Time comparison plots
  - Collapsible simulation parameter summary

Reads ``DerivedGCSParams`` and the cleaned observation DataFrame from
``st.session_state`` (populated by the GCS Observations page).  If the
session state is empty, the user is prompted to visit that page first.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import streamlit as st

from heliotrace.config import KEY_CLEAN_DF, KEY_DERIVED_PARAMS, KEY_SIM_CONFIG, KEY_SIM_RESULTS
from heliotrace.models.schemas import SimulationConfig, SimulationResults
from heliotrace.simulation.runner import run_full_simulation
from heliotrace.ui.components.propagation_plot import build_propagation_comparison_figure
from heliotrace.ui.components.sidebar_inputs import render_sidebar
from heliotrace.ui.state import init_session_state
from heliotrace.ui.utils import format_diff

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ICME Propagation — HelioTrace",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Initialise session state + render full sidebar (with Run button)
# ---------------------------------------------------------------------------
init_session_state()
config, run_clicked = render_sidebar(show_run_button=True)

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🌌 ICME Propagation")
st.caption(
    f"Event: **{config.event_str}** | "
    f"Target: **{config.target.name}** ({config.target.distance:.2f} AU) | "
    f"Models: DBM · MODBM"
)

# ---------------------------------------------------------------------------
# Guard: require GCS data from page 1
# ---------------------------------------------------------------------------
derived = st.session_state.get(KEY_DERIVED_PARAMS)
clean_df = st.session_state.get(KEY_CLEAN_DF)

if derived is None or clean_df is None:
    st.warning(
        "⚠️ No GCS observation data found in session. "
        "Please visit **📡 GCS Observations** first to enter your data and "
        "compute the initial CME velocity."
    )
    st.page_link("pages/01_GCS_Observations.py", label="Go to GCS Observations →", icon="📡")
    st.stop()

# ---------------------------------------------------------------------------
# Context reminder (collapsible)
# ---------------------------------------------------------------------------
with st.expander("📋 GCS Parameters from Previous Page", expanded=False):
    d = derived
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Fitted Initial Conditions**")
        st.markdown(f"- r₀ = {d.r0_rsun:.2f} R☉")
        st.markdown(f"- t₀ = {d.t0.strftime('%Y-%m-%d %H:%M UT')}")
        st.markdown(f"- v_apex = {d.v_apex_kms:.1f} ± {d.v_apex_error_kms:.1f} km/s")
    with col_b:
        st.markdown("**GCS Geometry**")
        st.markdown(f"- α = {d.alpha_deg:.1f}°,  κ = {d.kappa:.3f}")
        st.markdown(f"- lon = {d.lon_deg:.1f}°,  lat = {d.lat_deg:.1f}°,  tilt = {d.tilt_deg:.1f}°")

# ---------------------------------------------------------------------------
# Simulation trigger
# ---------------------------------------------------------------------------
st.subheader("Drag-Based Propagation")
st.markdown(
    "Press **▶ Run Simulation** in the sidebar to compute DBM and MODBM trajectories "
    "and arrival predictions at the selected target."
)

if run_clicked:
    if clean_df is None or len(clean_df) < 2:
        st.warning("⚠️ Need at least 2 complete GCS rows on the GCS Observations page.")
    else:
        with st.spinner("Running DBM & MODBM simulations…"):
            try:
                results: SimulationResults = run_full_simulation(clean_df, config)
                st.session_state[KEY_SIM_RESULTS] = results
                st.session_state[KEY_SIM_CONFIG]  = config
                st.success("✅ Simulation complete!")
            except Exception as exc:
                st.error(f"Simulation failed: {exc}")
                st.session_state[KEY_SIM_RESULTS] = None

# ---------------------------------------------------------------------------
# Display stored results
# ---------------------------------------------------------------------------
results: Optional[SimulationResults] = st.session_state.get(KEY_SIM_RESULTS)
stored_config: Optional[SimulationConfig] = st.session_state.get(KEY_SIM_CONFIG)

if results is None:
    st.info("No results yet. Configure parameters in the sidebar and press **▶ Run Simulation**.")
    st.stop()

if not results.target_hit:
    st.error(
        f"**GEOMETRY: MISS** — The simulation was run but the CME does not intercept "
        f"**{stored_config.target.name}**. No propagation result is available."
    )
    st.stop()

# ---------------------------------------------------------------------------
# Parse expected ToA for comparison
# ---------------------------------------------------------------------------
toa_expected: Optional[datetime] = None
if stored_config and stored_config.toa_raw:
    try:
        toa_expected = datetime.strptime(stored_config.toa_raw, "%d/%m/%Y %H:%M:%S")
    except ValueError:
        pass

# ---------------------------------------------------------------------------
# Summary KPI cards
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Key Results")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Apex Velocity",    f"{results.derived.v_apex_kms:.0f} km/s",
          delta=f"±{results.derived.v_apex_error_kms:.0f}")
c2.metric("Projection Ratio", f"{results.projection_ratio:.4f}")
c3.metric("v₀ → Target",      f"{results.v0_kms:.0f} km/s")
c4.metric("Target Distance",  f"{stored_config.target.distance:.3f} AU")

# ---------------------------------------------------------------------------
# Model-by-model results (two columns)
# ---------------------------------------------------------------------------
st.divider()
col_dbm, col_modbm = st.columns(2)

with col_dbm:
    st.subheader("Drag-Based Model (DBM)")
    if results.arrival_time_DBM:
        d1, d2, d3 = st.columns(3)
        d1.metric("Transit Time",  f"{results.elapsed_time_DBM_h:.2f} h")
        d2.metric("Impact Speed",  f"{results.velocity_arrival_DBM_kms:.1f} km/s")
        d3.metric("Arrival",       results.arrival_time_DBM.strftime("%d %b %H:%M UT"))

        diff_dbm = format_diff(results.arrival_time_DBM, toa_expected)
        if diff_dbm:
            sign_color = "normal" if float(diff_dbm.split()[0]) >= 0 else "inverse"
            st.metric("Δ vs Expected ToA", diff_dbm, delta_color=sign_color)
    else:
        st.warning("DBM solution did not reach the target within the integration window.")

with col_modbm:
    st.subheader("Modified DBM (MODBM)")
    if results.arrival_time_MODBM:
        d1, d2, d3 = st.columns(3)
        d1.metric("Transit Time",  f"{results.elapsed_time_MODBM_h:.2f} h")
        d2.metric("Impact Speed",  f"{results.velocity_arrival_MODBM_kms:.1f} km/s")
        d3.metric("Arrival",       results.arrival_time_MODBM.strftime("%d %b %H:%M UT"))

        diff_modbm = format_diff(results.arrival_time_MODBM, toa_expected)
        if diff_modbm:
            sign_color = "normal" if float(diff_modbm.split()[0]) >= 0 else "inverse"
            st.metric("Δ vs Expected ToA", diff_modbm, delta_color=sign_color)
    else:
        st.warning("MODBM solution did not reach the target within the integration window.")

# ---------------------------------------------------------------------------
# Propagation comparison chart
# ---------------------------------------------------------------------------
if results.dbm_series or results.modbm_series:
    st.divider()
    st.subheader("Model Comparison")
    prop_fig = build_propagation_comparison_figure(
        results=results,
        target_distance_au=stored_config.target.distance,
    )
    st.plotly_chart(prop_fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Input parameters summary (collapsible)
# ---------------------------------------------------------------------------
st.divider()
with st.expander("📋 Simulation Parameters Used", expanded=False):
    d = results.derived
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Initial Conditions (from GCS fit)**")
        st.markdown(f"- r₀ = {d.r0_rsun:.2f} R☉")
        st.markdown(f"- t₀ = {d.t0.strftime('%Y-%m-%d %H:%M UT')}")
        st.markdown(f"- v_apex = {d.v_apex_kms:.1f} ± {d.v_apex_error_kms:.1f} km/s")
        st.markdown(f"- α = {d.alpha_deg:.1f}°,  κ = {d.kappa:.3f}")
        st.markdown(f"- lon = {d.lon_deg:.1f}°,  lat = {d.lat_deg:.1f}°,  tilt = {d.tilt_deg:.1f}°")
    with col_b:
        st.markdown("**Drag Model Settings**")
        st.markdown(f"- w (DBM) = {stored_config.w} km/s")
        st.markdown(f"- w_type (MODBM) = {stored_config.w_type}")
        st.markdown(f"- SSN = {stored_config.ssn}")
        st.markdown(f"- c_d = {stored_config.c_d}")
        if stored_config.m_override_g:
            st.markdown(f"- M (override) = {stored_config.m_override_g:.2e} g")
        else:
            st.markdown("- M = Pluta (2018) formula")
