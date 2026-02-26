"""
CME Propagation — Main simulation page.

Tab 1: GCS Geometry & Height-Time Diagram  (live; updates reactively)
Tab 2: Propagation Results                  (triggered by "Run Simulation" button)
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import astropy.units as u
import pandas as pd
import streamlit as st

from heliotrace.config import KEY_SIM_CONFIG, KEY_SIM_RESULTS
from heliotrace.models.schemas import (
    DerivedGCSParams,
    GCSParams,
    SimulationConfig,
    SimulationResults,
)
from heliotrace.physics.apex_ratio import get_target_apex_ratio
from heliotrace.simulation.runner import derive_gcs_params, run_full_simulation
from heliotrace.ui.components.gcs_plot import build_gcs_figure
from heliotrace.ui.components.ht_plot import build_ht_figure
from heliotrace.ui.components.propagation_plot import build_propagation_comparison_figure
from heliotrace.ui.components.sidebar_inputs import render_sidebar
from heliotrace.ui.state import init_session_state
from heliotrace.ui.utils import format_diff

# ---------------------------------------------------------------------------
# Cached helpers — plain / hashable args ensure reliable cache keys
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _cached_derived_params(df: pd.DataFrame, height_error: float) -> DerivedGCSParams:
    """Cache the linear H-T fit result — re-runs only when the table data or error changes."""
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
        tilt=tilt_deg       * u.deg,
        target_lat=target_lat_deg * u.deg,
        target_lon=target_lon_deg * u.deg,
    )


# ---------------------------------------------------------------------------
# Initialise session state + render sidebar
# ---------------------------------------------------------------------------
init_session_state()
config, gcs_params, obs_df, run_clicked = render_sidebar()

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🚀 CME Propagation Modelling")
st.caption(
    f"Event: **{config.event_str}** | "
    f"Target: **{config.target.name}** ({config.target.distance:.2f} AU) | "
    f"Models: DBM · MODBM"
)

# ---------------------------------------------------------------------------
# Build the merged 7-column DataFrame (obs rows + GCS param columns broadcast)
# This is required by derive_gcs_params and run_full_simulation.
# ---------------------------------------------------------------------------
_obs_clean = (
    obs_df
    .dropna(subset=["datetime", "height"])
    .sort_values("datetime")
    .reset_index(drop=True)
)
has_obs = len(_obs_clean) >= 2

if has_obs:
    clean_df: Optional[pd.DataFrame] = _obs_clean.copy()
    clean_df["lon"]        = gcs_params.lon_deg
    clean_df["lat"]        = gcs_params.lat_deg
    clean_df["tilt"]       = gcs_params.tilt_deg
    clean_df["half_angle"] = gcs_params.half_angle_deg
    clean_df["kappa"]      = gcs_params.kappa
else:
    clean_df = None

# ---------------------------------------------------------------------------
# Main tabs
# ---------------------------------------------------------------------------
tab1, tab2 = st.tabs(["📡 GCS Geometry & Height-Time", "📈 Propagation Results"])


# ============================================================
# TAB 1 — Reactive GCS geometry + HT fit (no button required)
# ============================================================
with tab1:

    # --------------------------------------------------------
    # GCS 3D Model — always shown using sidebar GCS params
    # --------------------------------------------------------
    st.subheader("GCS Model (3D Geometry)")

    with st.spinner("Computing GCS geometry…  (cached after first run)"):
        proj_ratio = _cached_projection_ratio(
            alpha_deg=gcs_params.half_angle_deg,
            kappa=gcs_params.kappa,
            cme_lat_deg=gcs_params.lat_deg,
            cme_lon_deg=gcs_params.lon_deg,
            tilt_deg=gcs_params.tilt_deg,
            target_lat_deg=config.target.lat,
            target_lon_deg=config.target.lon,
        )

    target_hit_geometry = proj_ratio > 0

    if target_hit_geometry:
        st.success(
            f"✓ **HIT** — The CME flank intercepts **{config.target.name}** "
            f"at a projection ratio of **{proj_ratio:.4f}**."
        )
    else:
        st.error(
            f"**GEOMETRY: MISS** — The CME does not encompass **{config.target.name}** "
            "with the current GCS parameters. Adjust longitude, latitude, or half-angle."
        )

    gcs_fig = build_gcs_figure(
        alpha_deg=gcs_params.half_angle_deg,
        kappa=gcs_params.kappa,
        lat_deg=gcs_params.lat_deg,
        lon_deg=gcs_params.lon_deg,
        tilt_deg=gcs_params.tilt_deg,
        target_lat_deg=config.target.lat,
        target_lon_deg=config.target.lon,
        projection_ratio=proj_ratio,
        target_name=config.target.name,
        height=1.0,
    )
    st.plotly_chart(gcs_fig, use_container_width=True)

    # --------------------------------------------------------
    # Height-Time Diagram — shown once ≥2 observations exist
    # --------------------------------------------------------
    st.divider()
    st.subheader("Height-Time Diagram")

    if not has_obs:
        st.info(
            "ℹ️ Add at least **2 observations** in the sidebar to compute "
            "the H-T fit and apex velocity."
        )
    else:
        derived: DerivedGCSParams = _cached_derived_params(clean_df, config.height_error)

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

        # Velocity result displayed prominently below the plot
        v_col, proj_col, target_col, _ = st.columns([1, 1, 1, 1])
        v_col.metric(
            "Apex Velocity",
            f"{derived.v_apex_kms:.0f} km/s",
            delta=f"±{derived.v_apex_error_kms:.0f} km/s",
            help="CME apex velocity from the weighted linear H-T fit.",
        )
        proj_col.metric(
            "Projection Ratio",
            f"{proj_ratio:.4f}" if target_hit_geometry else "—",
            help="Fraction of apex height reached at the target latitude/longitude.",
        )
        target_col.metric(
            "v₀ toward Target",
            f"{derived.v_apex_kms * proj_ratio:.0f} km/s" if target_hit_geometry else "MISS",
            help="Initial velocity component directed at the selected target.",
        )


# ============================================================
# TAB 2 — Propagation Results (button-triggered)
# ============================================================
with tab2:
    st.subheader("Drag-Based Propagation")
    st.markdown(
        "Press **▶ Run Simulation** in the sidebar to compute DBM and MODBM trajectories "
        "and arrival predictions at the selected target."
    )

    # --------------------------------------------------------
    # Trigger on button press
    # --------------------------------------------------------
    if run_clicked:
        if clean_df is None:
            st.warning("⚠️ Add at least 2 observations in the sidebar before running.")
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

    # --------------------------------------------------------
    # Display stored results
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # Parse expected ToA for comparison
    # --------------------------------------------------------
    toa_expected: Optional[datetime] = None
    if stored_config and stored_config.toa_raw:
        try:
            toa_expected = datetime.strptime(stored_config.toa_raw, "%d/%m/%Y %H:%M:%S")
        except ValueError:
            pass

    # --------------------------------------------------------
    # Summary KPI cards
    # --------------------------------------------------------
    st.divider()
    st.subheader("Key Results")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Apex Velocity",    f"{results.derived.v_apex_kms:.0f} km/s",
              delta=f"±{results.derived.v_apex_error_kms:.0f}")
    c2.metric("Projection Ratio", f"{results.projection_ratio:.4f}")
    c3.metric("v₀ → Target",      f"{results.v0_kms:.0f} km/s")
    c4.metric("Target Distance",  f"{stored_config.target.distance:.3f} AU")

    # --------------------------------------------------------
    # Model-by-model results (two columns)
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # Propagation comparison chart
    # --------------------------------------------------------
    if results.dbm_series or results.modbm_series:
        st.divider()
        st.subheader("Model Comparison")
        prop_fig = build_propagation_comparison_figure(
            results=results,
            target_distance_au=stored_config.target.distance,
        )
        st.plotly_chart(prop_fig, use_container_width=True)

    # --------------------------------------------------------
    # Input parameters summary (collapsible)
    # --------------------------------------------------------
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


