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
    SimulationConfig,
    SimulationResults,
)
from heliotrace.physics.apex_ratio import get_target_apex_ratio
from heliotrace.simulation.runner import derive_gcs_params, run_full_simulation
from heliotrace.ui.components.gcs_plot import build_gcs_figure
from heliotrace.ui.components.ht_plot import build_ht_figure
from heliotrace.ui.components.propagation_plot import (
    PLOT_COLORS,
    build_propagation_comparison_figure,
    build_single_model_figure,
)
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
        alpha=alpha_deg * u.deg,
        kappa=kappa,
        cme_lat=cme_lat_deg * u.deg,
        cme_lon=cme_lon_deg * u.deg,
        tilt=tilt_deg * u.deg,
        target_lat=target_lat_deg * u.deg,
        target_lon=target_lon_deg * u.deg,
    )


# ---------------------------------------------------------------------------
# Compact metric HTML helper (avoids oversized st.metric in cramped columns)
# ---------------------------------------------------------------------------


def _mini_metric(
    label: str, value: str, delta: str | None = None, delta_positive: bool | None = None
) -> str:
    """Return an HTML snippet for a compact labelled value card."""
    if delta is not None and delta_positive is not None:
        _dc = "#2ca02c" if delta_positive else "#d62728"
        _dh = f'<div style="font-size:1.0rem;color:{_dc};margin-top:2px">{delta}</div>'
    else:
        _dh = ""
    return (
        '<div style="padding:6px 8px 4px 8px">'
        f'<div style="font-size:0.85rem;color:#888;text-transform:uppercase;'
        f'letter-spacing:0.04em;margin-bottom:2px">{label}</div>'
        f'<div style="font-size:1.4rem;font-weight:600;line-height:1.3">{value}</div>'
        f"{_dh}"
        "</div>"
    )


# ---------------------------------------------------------------------------
# Initialise session state + render sidebar
# ---------------------------------------------------------------------------
init_session_state()
config, gcs_params, obs_df, run_clicked, gcs_params_entered = render_sidebar()

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.title("🚀 Propagation Simulator")
st.caption(
    f"Event: **{config.event_str}** | "
    f"Target: **{config.target.name}** ({config.target.distance:.2f} AU) | "
    f"Models: DBM · MoDBM"
)

# ---------------------------------------------------------------------------
# Build the merged 7-column DataFrame (obs rows + GCS param columns broadcast)
# This is required by derive_gcs_params and run_full_simulation.
# ---------------------------------------------------------------------------
_obs_clean = (
    obs_df.dropna(subset=["datetime", "height"])
    .loc[lambda df: df["height"] > 0]
    .sort_values("datetime")
    .reset_index(drop=True)
)
has_obs = len(_obs_clean) >= 2

if has_obs:
    clean_df: Optional[pd.DataFrame] = _obs_clean.copy()
    clean_df["lon"] = gcs_params.lon_deg
    clean_df["lat"] = gcs_params.lat_deg
    clean_df["tilt"] = gcs_params.tilt_deg
    clean_df["half_angle"] = gcs_params.half_angle_deg
    clean_df["kappa"] = gcs_params.kappa
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
    # GCS 3D Model — shown once all five GCS params are entered
    # --------------------------------------------------------
    st.subheader("GCS Model (3D Geometry)")

    # Defaults used when GCS params are not yet entered
    proj_ratio = 0.0
    target_hit_geometry = False

    if not gcs_params_entered:
        st.info(
            "ℹ️ Enter all five **GCS parameters** in the sidebar — or press "
            "**⚡ Fill with example** — to view the 3D geometry."
        )
    else:
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

        target_hit_geometry = proj_ratio >= 0.3

        if target_hit_geometry:
            st.success(
                f"✓ **HIT** — The CME flank intercepts **{config.target.name}** "
                f"at a projection ratio of **{proj_ratio:.4f}** (≥ 0.3 threshold)."
            )
        else:
            st.error(
                f"**GEOMETRY: MISS** — Projection ratio {proj_ratio:.4f} < 0.3. "
                "The GCS CME body does not sufficiently encompass the target direction. "
                "Adjust longitude, latitude, or half-angle."
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
        assert clean_df is not None
        derived: DerivedGCSParams = _cached_derived_params(clean_df, config.height_error)

        ht_fig = build_ht_figure(
            df=clean_df,
            height_error=config.height_error,
            slope=derived.fit_slope,
            intercept=derived.fit_intercept,
            chi_squared=derived.fit_chi_squared,
            v_apex_kms=derived.v_apex_kms,
            v_apex_error_kms=derived.v_apex_error_kms,
            event_label=config.event_str,
        )
        st.plotly_chart(ht_fig, use_container_width=True)

        # Velocity result displayed prominently below the plot
        v_col, proj_col, target_col, _ = st.columns([1, 1, 1, 1])
        v_col.metric(
            "Apex Velocity",
            f"{derived.v_apex_kms:.0f} ± {derived.v_apex_error_kms:.0f} km/s",
            help="CME apex velocity and 1σ uncertainty from the weighted linear H-T fit.",
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
        "Press **▶ Run Simulation** in the sidebar to compute DBM and MoDBM trajectories "
        "and arrival predictions at the selected target."
    )

    # --------------------------------------------------------
    # Trigger on button press
    # --------------------------------------------------------
    if run_clicked:
        if clean_df is None:
            st.warning("⚠️ Add at least 2 observations in the sidebar before running.")
        else:
            with st.spinner("Running DBM & MoDBM simulations…"):
                try:
                    results = run_full_simulation(clean_df, config)
                    st.session_state[KEY_SIM_RESULTS] = results
                    st.session_state[KEY_SIM_CONFIG] = config
                    st.success("✅ Simulation complete!")
                except ValueError as exc:
                    st.error(f"⚠️ Invalid input: {exc}")
                    st.session_state[KEY_SIM_RESULTS] = None
                except Exception as exc:
                    st.error(
                        f"Simulation failed with an unexpected error: {type(exc).__name__}: {exc}"
                    )
                    st.session_state[KEY_SIM_RESULTS] = None

    # --------------------------------------------------------
    # Display stored results
    # --------------------------------------------------------
    results: Optional[SimulationResults] = st.session_state.get(KEY_SIM_RESULTS)
    stored_config: Optional[SimulationConfig] = st.session_state.get(KEY_SIM_CONFIG)

    if results is None:
        st.info(
            "No results yet. Configure parameters in the sidebar and press **▶ Run Simulation**."
        )
        st.stop()

    assert stored_config is not None

    if not results.target_hit:
        st.error(
            f"**GEOMETRY: MISS** — The simulation was run but the ICME does not intercept "
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
    st.markdown(
        """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 1.4rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )
    st.subheader("Key Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        "Apex Velocity",
        f"{results.derived.v_apex_kms:.0f} ± {results.derived.v_apex_error_kms:.0f} km/s",
        help="CME apex velocity and 1σ uncertainty from the weighted linear H-T fit.",
    )
    c2.metric("Projection Ratio", f"{results.projection_ratio:.4f}")
    _v0_delta = (
        "overridden" if (stored_config and stored_config.v0_override_kms is not None) else None
    )
    c3.metric("v₀ → Target", f"{results.v0_kms:.0f} km/s", delta=_v0_delta, delta_color="off")
    c4.metric("Target Distance", f"{stored_config.target.distance:.3f} AU")

    # --------------------------------------------------------
    # Side-by-side model results
    # --------------------------------------------------------
    st.subheader("Model Results")
    col_dbm, col_modbm = st.columns(2)

    with col_dbm:
        st.markdown(
            '<div style="text-align:center;font-size:1.2rem;font-weight:700;color:#1f77b4;'
            "border:2px solid #1f77b4;background:#eaf2fb;border-radius:6px;"
            'padding:5px 0;margin:0 0 10px 0;">DBM</div>',
            unsafe_allow_html=True,
        )
        if results.arrival_time_DBM:
            diff_dbm = format_diff(results.arrival_time_DBM, toa_expected)
            mc1, mc2 = st.columns(2)
            mc1.markdown(
                _mini_metric("Arrival", results.arrival_time_DBM.strftime("%d.%m. %H:%M")),
                unsafe_allow_html=True,
            )
            if diff_dbm:
                _pos = not diff_dbm.startswith("-")
                mc2.markdown(
                    _mini_metric("Δ vs Expected", diff_dbm, delta=diff_dbm, delta_positive=_pos),
                    unsafe_allow_html=True,
                )
            mc3, mc4 = st.columns(2)
            mc3.markdown(
                _mini_metric("Transit", f"{results.elapsed_time_DBM_h:.1f} h"),
                unsafe_allow_html=True,
            )
            mc4.markdown(
                _mini_metric("Impact", f"{results.velocity_arrival_DBM_kms:.0f} km/s"),
                unsafe_allow_html=True,
            )
        else:
            st.warning("DBM did not reach the target within the integration window.")

        with st.expander("Inputs used — DBM", expanded=False):
            d = results.derived
            _v0_note = " *(override)*" if stored_config.v0_override_kms is not None else ""
            ec1, ec2 = st.columns(2)
            ec1.metric(
                "𝒓₀ [R☉]",
                f"{d.r0_rsun:.2f}",
                help="Initial apex height 𝒓₀: greatest observed coronagraph height, used as the "
                "starting position r(t=0) of the drag ODE [R☉].",
            )
            ec2.metric(
                "t₀",
                d.t0.strftime("%d.%m. %H:%M"),
                help="Reference launch time: timestamp of the last (highest) coronagraph "
                "observation, used as t=0 for the ODE integration.",
            )
            st.metric(
                "v_apex [km/s]",
                f"{d.v_apex_kms:.1f} ± {d.v_apex_error_kms:.1f}",
                help="CME apex velocity and $1\\sigma$ uncertainty from the weighted linear "
                "height-time fit. Represents the outward speed of the outermost "
                "point of the GCS flux rope.",
            )
            st.metric(
                f"v₀ → {stored_config.target.name} [km/s]",
                f"{results.v0_kms:.0f}{_v0_note}",
                help="Initial CME speed projected onto the Sun–target line of sight: "
                "$v_0 = v_{\\rm apex} \\times$ projection ratio. This is the starting velocity "
                "fed into the 1-D drag equation.",
            )
            ea1, ea2 = st.columns(2)
            ea1.metric(
                "𝜶 [deg]",
                f"{d.alpha_deg:.1f}",
                help="GCS half-angle 𝜶: angular half-width of the CME flux-rope shell. "
                "Controls the lateral (longitudinal) extent of the ejecta.",
            )
            ea2.metric(
                "𝜿",
                f"{d.kappa:.3f}",
                help="GCS aspect ratio 𝜿: ratio of the cross-section radius to the apex "
                "distance. Determines how 'fat' the flux rope appears in projection.",
            )
            eb1, eb2 = st.columns(2)
            eb1.metric(
                "𝝓 [deg]",
                f"{d.lon_deg:.1f}",
                help="Stonyhurst heliographic longitude 𝝓 of the CME source region "
                "(Carrington frame, Earth at 0°).",
            )
            eb2.metric(
                "𝜽 [deg]",
                f"{d.lat_deg:.1f}",
                help="Stonyhurst heliographic latitude 𝜽 of the CME source region.",
            )
            st.metric(
                "𝜸 [deg]",
                f"{d.tilt_deg:.1f}",
                help="Tilt 𝜸 of the CME flux-rope axis relative to the solar equatorial plane. "
                "Positive tilt = north-east orientation of the axis.",
            )
            st.metric(
                "w [km/s]",
                f"{stored_config.w:.0f}",
                help="Constant ambient solar wind speed used by the standard DBM as the "
                "asymptotic drag velocity (CME decelerates toward w). Typical: 300–600 km/s.",
            )
            st.metric(
                "cₙ (drag coeff.)",
                f"{stored_config.c_d}",
                help="Dimensionless aerodynamic drag coefficient. Theoretical value ≈1 for a "
                "sphere; converges to ≈1 for CMEs beyond ∼12 R☉ (Cargill 2004).",
            )

        if results.dbm_series:
            dbm_fig = build_single_model_figure(
                series=results.dbm_series,
                elapsed_h=results.elapsed_time_DBM_h,
                target_distance_au=stored_config.target.distance,
                label="DBM",
                color=PLOT_COLORS["DBM"],
            )
            st.plotly_chart(dbm_fig, use_container_width=True)

    with col_modbm:
        st.markdown(
            '<div style="text-align:center;font-size:1.2rem;font-weight:700;color:#ff7f0e;'
            "border:2px solid #ff7f0e;background:#fff3e6;border-radius:6px;"
            'padding:5px 0;margin:0 0 10px 0;">MoDBM</div>',
            unsafe_allow_html=True,
        )
        if results.arrival_time_MODBM:
            diff_modbm = format_diff(results.arrival_time_MODBM, toa_expected)
            mc1, mc2 = st.columns(2)
            mc1.markdown(
                _mini_metric("Arrival", results.arrival_time_MODBM.strftime("%d.%m. %H:%M")),
                unsafe_allow_html=True,
            )
            if diff_modbm:
                _pos = not diff_modbm.startswith("-")
                mc2.markdown(
                    _mini_metric(
                        "Δ vs Expected", diff_modbm, delta=diff_modbm, delta_positive=_pos
                    ),
                    unsafe_allow_html=True,
                )
            mc3, mc4 = st.columns(2)
            mc3.markdown(
                _mini_metric("Transit", f"{results.elapsed_time_MODBM_h:.1f} h"),
                unsafe_allow_html=True,
            )
            mc4.markdown(
                _mini_metric("Impact", f"{results.velocity_arrival_MODBM_kms:.0f} km/s"),
                unsafe_allow_html=True,
            )
        else:
            st.warning("MoDBM did not reach the target within the integration window.")

        with st.expander("Inputs used — MoDBM", expanded=False):
            d = results.derived
            _v0_note = " *(override)*" if stored_config.v0_override_kms is not None else ""
            _mass = (
                f"{stored_config.m_override_g:.2e} g"
                if stored_config.m_override_g
                else "Pluta (2018)"
            )
            ec1, ec2 = st.columns(2)
            ec1.metric(
                "𝒓₀ [R☉]",
                f"{d.r0_rsun:.2f}",
                help="Initial apex height 𝒓₀: greatest observed coronagraph height, used as the "
                "starting position r(t=0) of the drag ODE [R☉].",
            )
            ec2.metric(
                "t₀",
                d.t0.strftime("%d.%m. %H:%M"),
                help="Reference launch time: timestamp of the last (highest) coronagraph "
                "observation, used as t=0 for the ODE integration.",
            )
            st.metric(
                "v_apex [km/s]",
                f"{d.v_apex_kms:.1f} ± {d.v_apex_error_kms:.1f}",
                help="CME apex velocity and $1\\sigma$ uncertainty from the weighted linear "
                "height-time fit. Represents the outward speed of the outermost "
                "point of the GCS flux rope.",
            )
            st.metric(
                f"v₀ → {stored_config.target.name} [km/s]",
                f"{results.v0_kms:.0f}{_v0_note}",
                help="Initial CME speed projected onto the Sun–target line of sight: "
                "$v_0 = v_{\\rm apex} \\times$ projection ratio. This is the starting velocity "
                "fed into the 1-D drag equation.",
            )
            ea1, ea2 = st.columns(2)
            ea1.metric(
                "𝜶 [deg]",
                f"{d.alpha_deg:.1f}",
                help="GCS half-angle 𝜶: angular half-width of the CME flux-rope shell. "
                "Controls the lateral (longitudinal) extent of the ejecta.",
            )
            ea2.metric(
                "𝜿",
                f"{d.kappa:.3f}",
                help="GCS aspect ratio 𝜿: ratio of the cross-section radius to the apex "
                "distance. Determines how 'fat' the flux rope appears in projection.",
            )
            eb1, eb2 = st.columns(2)
            eb1.metric(
                "𝝓 [deg]",
                f"{d.lon_deg:.1f}",
                help="Stonyhurst heliographic longitude 𝝓 of the CME source region "
                "(Carrington frame, Earth at 0°).",
            )
            eb2.metric(
                "𝜽 [deg]",
                f"{d.lat_deg:.1f}",
                help="Stonyhurst heliographic latitude 𝜽 of the CME source region.",
            )
            st.metric(
                "𝜸 [deg]",
                f"{d.tilt_deg:.1f}",
                help="Tilt 𝜸 of the CME flux-rope axis relative to the solar equatorial plane. "
                "Positive tilt = north-east orientation of the axis.",
            )
            ew1, ew2 = st.columns(2)
            ew1.metric(
                "Wind regime",
                stored_config.w_type,
                help="Background solar wind regime used by the MoDBM density profile "
                "(Venzmer & Bothmer 2018). 'slow' ≈ 300–400 km/s; 'fast' ≈ 600–800 km/s.",
            )
            ew2.metric(
                "SSN",
                f"{stored_config.ssn:.0f}",
                help="Monthly smoothed total sunspot number. Controls the amplitude of the "
                "structured solar wind density profile in MoDBM (higher SSN = denser wind "
                "near solar maximum).",
            )
            st.metric(
                "cₙ (drag coeff.)",
                f"{stored_config.c_d}",
                help="Dimensionless aerodynamic drag coefficient. Theoretical value ≈1 for a "
                "sphere; converges to ≈1 for CMEs beyond ∼12 R☉ (Cargill 2004).",
            )
            st.metric(
                "CME mass",
                _mass,
                help="Total CME mass used in the momentum equation. Either a manual override "
                r"or the Pluta (2018) empirical formula: "
                r"$\log_{10}(M/{\rm g}) = 3.4\times10^{-4}\,v + 15.479$, "
                "where v is the apex velocity in km/s.",
            )

        if results.modbm_series:
            modbm_fig = build_single_model_figure(
                series=results.modbm_series,
                elapsed_h=results.elapsed_time_MODBM_h,
                target_distance_au=stored_config.target.distance,
                label="MoDBM",
                color=PLOT_COLORS["MODBM"],
            )
            st.plotly_chart(modbm_fig, use_container_width=True)

    # --------------------------------------------------------
    # Full-width combined comparison
    # --------------------------------------------------------
    if results.dbm_series or results.modbm_series:
        st.divider()
        st.subheader("Combined Comparison")
        prop_fig = build_propagation_comparison_figure(
            results=results,
            target_distance_au=stored_config.target.distance,
        )
        st.plotly_chart(prop_fig, use_container_width=True)
