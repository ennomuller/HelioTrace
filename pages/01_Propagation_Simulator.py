"""
CME Propagation — Main simulation page.

Tab 1: GCS Geometry              (live; updates reactively)
Tab 2: CME Kinematics            (live; HT diagram + velocity KPIs + fit details)
Tab 3: Propagation Results       (triggered by "Run Simulation" button)
"""

from __future__ import annotations

import contextlib
from datetime import datetime

import astropy.units as u
import pandas as pd
import streamlit as st

from heliotrace.config import KEY_SIM_CONFIG, KEY_SIM_RESULTS
from heliotrace.i18n import render_lang_toggle, t
from heliotrace.models.schemas import (
    DerivedGCSParams,
    SimulationConfig,
    SimulationResults,
)
from heliotrace.physics.apex_ratio import get_target_apex_ratio
from heliotrace.physics.drag import get_CME_mass_pluta
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


def _kpi_card(
    label: str,
    value: str,
    subtitle: str | None = None,
    accent_color: str = "#1f77b4",
) -> str:
    """Return an HTML snippet for a dashboard-style KPI card with a colored left border."""
    _sub = (
        f'<div class="kpi-card-subtitle" style="font-size:0.9rem;color:#888;'
        f'margin-top:2px">{subtitle}</div>'
        if subtitle
        else ""
    )
    return (
        f'<div class="kpi-card" style="border-left:4px solid {accent_color};'
        "padding:10px 14px;border-radius:6px;"
        'background:var(--background-color, #f8f9fa);margin-bottom:8px">'
        f'<div class="kpi-card-label" style="font-size:0.8rem;color:#888;'
        f'text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px">{label}</div>'
        f'<div class="kpi-card-value" style="font-size:1.6rem;font-weight:700;'
        f'line-height:1.3">{value}</div>'
        f"{_sub}"
        "</div>"
    )


def _format_cme_mass(m_override_g: float | None) -> str:
    """Return the CME mass value shown in the inputs-used section."""
    return f"{m_override_g:.2e} g" if m_override_g is not None else ""


def _format_cme_mass_from_v_apex(v_apex_kms: float, m_override_g: float | None) -> str:
    """Return the displayed CME mass, using Pluta when no override is set."""
    if m_override_g is not None:
        return _format_cme_mass(m_override_g)
    mass_g = get_CME_mass_pluta(v_apex_kms, return_with_unit=False)
    return f"{mass_g:.2e} g"


# ---------------------------------------------------------------------------
# Initialise session state + render sidebar
# ---------------------------------------------------------------------------
init_session_state()
config, gcs_params, obs_df, run_clicked, task_states = render_sidebar()
gcs_params_entered = task_states["gcs"] == "ready"
render_lang_toggle(t("page.sim.title"))

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.caption(
    t("page.sim.caption").format(
        event=config.event_str,
        target=config.target.name,
        dist=config.target.distance,
    )
)

# ---------------------------------------------------------------------------
# Build the merged 7-column DataFrame (obs rows + GCS param columns broadcast)
# This is required by derive_gcs_params and run_full_simulation.
# ---------------------------------------------------------------------------
_obs_clean = (
    obs_df.dropna(subset=["datetime", "height"])
    .loc[lambda df: df["height"] > 0]
    .sort_values(by="datetime")  # pyright: ignore[reportCallIssue]
    .reset_index(drop=True)
)
has_obs = len(_obs_clean) >= 2

if has_obs:
    clean_df = _obs_clean.copy()
    clean_df["lon"] = gcs_params.lon_deg
    clean_df["lat"] = gcs_params.lat_deg
    clean_df["tilt"] = gcs_params.tilt_deg
    clean_df["half_angle"] = gcs_params.half_angle_deg
    clean_df["kappa"] = gcs_params.kappa
else:
    clean_df = None

# ---------------------------------------------------------------------------
# Pre-compute GCS projection ratio (needed by multiple tabs)
# ---------------------------------------------------------------------------
proj_ratio = 0.0
target_hit_geometry = False

if gcs_params_entered:
    with st.spinner(t("page.sim.gcs_spinner")):
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

# ---------------------------------------------------------------------------
# Main tabs
# ---------------------------------------------------------------------------
tab1, tab_kin, tab2 = st.tabs(
    [t("page.sim.tab_gcs"), t("page.sim.tab_kinematics"), t("page.sim.tab_prop")]
)


# ============================================================
# TAB 1 — GCS Geometry (3D plot only)
# ============================================================
with tab1:
    st.subheader(t("page.sim.gcs_subheader"))

    if not gcs_params_entered:
        st.info(t("page.sim.gcs_info"))
    else:
        if target_hit_geometry:
            st.success(t("page.sim.gcs_hit").format(target=config.target.name, ratio=proj_ratio))
        else:
            st.error(t("page.sim.gcs_miss").format(ratio=proj_ratio))

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
        st.plotly_chart(gcs_fig, width="stretch")


# ============================================================
# TAB 2 — CME Kinematics (HT diagram + velocity KPIs + fit details)
# ============================================================
with tab_kin:
    st.subheader(t("page.sim.ht_subheader"))

    if not has_obs:
        st.info(t("page.sim.ht_info"))
    else:
        assert clean_df is not None
        derived: DerivedGCSParams = _cached_derived_params(clean_df, config.height_error)

        # --- Enhanced KPI cards ---
        _v_sub = f"± {derived.v_apex_error_kms:.0f} km/s"
        if target_hit_geometry:
            _pr_val = f"{proj_ratio:.4f}"
            _pr_sub = '<span style="color:#2ca02c;font-weight:600">HIT</span>'
            _pr_accent = "#2ca02c"
            _vt_val = f"{derived.v_apex_kms * proj_ratio:.0f} km/s"
            _vt_sub = f"toward {config.target.name}"
            _vt_accent = "#1f77b4"
        else:
            _pr_val = f"{proj_ratio:.4f}" if gcs_params_entered else "—"
            _pr_sub = '<span style="color:#d62728;font-weight:600">MISS</span>'
            _pr_accent = "#d62728"
            _vt_val = "MISS"
            _vt_sub = None
            _vt_accent = "#d62728"

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.markdown(
            _kpi_card(
                t("page.sim.metric.apex_velocity"),
                f"{derived.v_apex_kms:.0f} km/s",
                subtitle=_v_sub,
                accent_color="#1f77b4",
            ),
            unsafe_allow_html=True,
        )
        kpi2.markdown(
            _kpi_card(
                t("page.sim.metric.proj_ratio"),
                _pr_val,
                subtitle=_pr_sub,
                accent_color=_pr_accent,
            ),
            unsafe_allow_html=True,
        )
        kpi3.markdown(
            _kpi_card(
                t("page.sim.metric.v0_target"),
                _vt_val,
                subtitle=_vt_sub,
                accent_color=_vt_accent,
            ),
            unsafe_allow_html=True,
        )

        # --- Height-Time plot ---
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
        st.plotly_chart(ht_fig, width="stretch")

        # --- Fit Details expander ---
        with st.expander(t("page.sim.fit_details_subheader"), expanded=False):
            fd1, fd2, fd3 = st.columns(3)
            fd1.metric(t("page.sim.fit_detail.slope"), f"{derived.fit_slope:.2e} R☉/s")
            fd2.metric(t("page.sim.fit_detail.intercept"), f"{derived.fit_intercept:.2f} R☉")
            fd3.metric(t("page.sim.fit_detail.chi_squared"), f"{derived.fit_chi_squared:.2f}")
            fd4, fd5, _ = st.columns(3)
            fd4.metric(t("page.sim.fit_detail.n_obs"), f"{len(clean_df)}")
            fd5.metric(t("page.sim.fit_detail.height_error"), f"± {config.height_error} R☉")


# ============================================================
# TAB 3 — Propagation Results (button-triggered)
# ============================================================
with tab2:
    st.subheader(t("page.sim.prop_subheader"))

    # --------------------------------------------------------
    # Trigger on button press
    # --------------------------------------------------------
    if run_clicked:
        if clean_df is None:
            st.warning(t("page.sim.no_obs_warning"))
        else:
            with st.spinner(t("page.sim.sim_spinner")):
                try:
                    results = run_full_simulation(clean_df, config)
                    st.session_state[KEY_SIM_RESULTS] = results
                    st.session_state[KEY_SIM_CONFIG] = config
                    st.success(t("page.sim.sim_success"))
                except ValueError as exc:
                    st.error(t("page.sim.sim_err_invalid").format(exc=exc))
                    st.session_state[KEY_SIM_RESULTS] = None
                except Exception as exc:
                    st.error(
                        t("page.sim.sim_err_unexpected").format(
                            exc_type=type(exc).__name__, exc=exc
                        )
                    )
                    st.session_state[KEY_SIM_RESULTS] = None

    # --------------------------------------------------------
    # Display stored results
    # --------------------------------------------------------
    results: SimulationResults | None = st.session_state.get(KEY_SIM_RESULTS)
    stored_config: SimulationConfig | None = st.session_state.get(KEY_SIM_CONFIG)

    if results is None:
        st.info(t("page.sim.no_results_info"))
        st.stop()

    assert stored_config is not None

    if not results.target_hit:
        st.error(t("page.sim.geom_miss").format(target=stored_config.target.name))
        st.stop()

    # --------------------------------------------------------
    # Parse expected ToA for comparison
    # --------------------------------------------------------
    toa_expected: datetime | None = None
    if stored_config and stored_config.toa_raw:
        with contextlib.suppress(ValueError):
            toa_expected = datetime.strptime(stored_config.toa_raw, "%d/%m/%Y %H:%M:%S")

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
    st.subheader(t("page.sim.key_results"))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(
        t("page.sim.metric.apex_velocity"),
        f"{results.derived.v_apex_kms:.0f} ± {results.derived.v_apex_error_kms:.0f} km/s",
        help=t("page.sim.metric.apex_velocity_help"),
    )
    c2.metric(t("page.sim.metric.proj_ratio"), f"{results.projection_ratio:.4f}")
    _v0_delta = (
        t("page.sim.metric.v0_override_note")
        if (stored_config and stored_config.v0_override_kms is not None)
        else None
    )
    c3.metric("v₀ → Target", f"{results.v0_kms:.0f} km/s", delta=_v0_delta, delta_color="off")
    c4.metric(t("page.sim.metric.target_dist"), f"{stored_config.target.distance:.3f} AU")

    # --------------------------------------------------------
    # Side-by-side model results
    # --------------------------------------------------------
    st.subheader(t("page.sim.model_results"))
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
                _mini_metric(
                    t("page.sim.metric.arrival"),
                    results.arrival_time_DBM.strftime("%d.%m. %H:%M"),
                ),
                unsafe_allow_html=True,
            )
            if diff_dbm:
                _pos = not diff_dbm.startswith("-")
                mc2.markdown(
                    _mini_metric(
                        t("page.sim.metric.delta_expected"),
                        diff_dbm,
                        delta=diff_dbm,
                        delta_positive=_pos,
                    ),
                    unsafe_allow_html=True,
                )
            mc3, mc4 = st.columns(2)
            mc3.markdown(
                _mini_metric(t("page.sim.metric.transit"), f"{results.elapsed_time_DBM_h:.1f} h"),
                unsafe_allow_html=True,
            )
            mc4.markdown(
                _mini_metric(
                    t("page.sim.metric.impact"),
                    f"{results.velocity_arrival_DBM_kms:.0f} km/s",
                ),
                unsafe_allow_html=True,
            )
        else:
            st.warning(t("page.sim.dbm_no_arrival"))

        with st.expander(t("page.sim.inputs_dbm"), expanded=False):
            d = results.derived
            _v0_note = " *(override)*" if stored_config.v0_override_kms is not None else ""
            _mass = _format_cme_mass_from_v_apex(d.v_apex_kms, stored_config.m_override_g)
            ec1, ec2 = st.columns(2)
            ec1.metric(
                "𝒓₀ [R☉]",
                f"{d.r0_rsun:.2f}",
                help=t("page.sim.metric.r0_help"),
            )
            ec2.metric(
                "t₀",
                d.t0.strftime("%d.%m. %H:%M"),
                help=t("page.sim.metric.t0_help"),
            )
            st.metric(
                "v_apex [km/s]",
                f"{d.v_apex_kms:.1f} ± {d.v_apex_error_kms:.1f}",
                help=t("page.sim.metric.vapex_help"),
            )
            st.metric(
                f"v₀ → {stored_config.target.name} [km/s]",
                f"{results.v0_kms:.0f}{_v0_note}",
                help=t("page.sim.metric.v0_help"),
            )
            ea1, ea2 = st.columns(2)
            ea1.metric(
                "𝜶 [deg]",
                f"{d.alpha_deg:.1f}",
                help=t("page.sim.metric.alpha_help"),
            )
            ea2.metric(
                "𝜿",
                f"{d.kappa:.3f}",
                help=t("page.sim.metric.kappa_help"),
            )
            eb1, eb2 = st.columns(2)
            eb1.metric(
                "𝝓 [deg]",
                f"{d.lon_deg:.1f}",
                help=t("page.sim.metric.phi_help"),
            )
            eb2.metric(
                "𝜽 [deg]",
                f"{d.lat_deg:.1f}",
                help=t("page.sim.metric.theta_help"),
            )
            st.metric(
                "𝜸 [deg]",
                f"{d.tilt_deg:.1f}",
                help=t("page.sim.metric.gamma_help"),
            )
            st.metric(
                "w [km/s]",
                f"{stored_config.w:.0f}",
                help=t("page.sim.metric.w_help"),
            )
            st.metric(
                "cₙ (drag coeff.)",
                f"{stored_config.c_d}",
                help=t("page.sim.metric.cd_help"),
            )
            st.metric(
                "CME mass",
                _mass,
                help=t("page.sim.metric.mass_help"),
            )

        if results.dbm_series:
            dbm_fig = build_single_model_figure(
                series=results.dbm_series,
                elapsed_h=results.elapsed_time_DBM_h,
                target_distance_au=stored_config.target.distance,
                label="DBM",
                color=PLOT_COLORS["DBM"],
            )
            st.plotly_chart(dbm_fig, width="stretch")

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
                _mini_metric(
                    t("page.sim.metric.arrival"),
                    results.arrival_time_MODBM.strftime("%d.%m. %H:%M"),
                ),
                unsafe_allow_html=True,
            )
            if diff_modbm:
                _pos = not diff_modbm.startswith("-")
                mc2.markdown(
                    _mini_metric(
                        t("page.sim.metric.delta_expected"),
                        diff_modbm,
                        delta=diff_modbm,
                        delta_positive=_pos,
                    ),
                    unsafe_allow_html=True,
                )
            mc3, mc4 = st.columns(2)
            mc3.markdown(
                _mini_metric(t("page.sim.metric.transit"), f"{results.elapsed_time_MODBM_h:.1f} h"),
                unsafe_allow_html=True,
            )
            mc4.markdown(
                _mini_metric(
                    t("page.sim.metric.impact"),
                    f"{results.velocity_arrival_MODBM_kms:.0f} km/s",
                ),
                unsafe_allow_html=True,
            )
        else:
            st.warning(t("page.sim.modbm_no_arrival"))

        with st.expander(t("page.sim.inputs_modbm"), expanded=False):
            d = results.derived
            _v0_note = " *(override)*" if stored_config.v0_override_kms is not None else ""
            _mass = _format_cme_mass_from_v_apex(d.v_apex_kms, stored_config.m_override_g)
            ec1, ec2 = st.columns(2)
            ec1.metric(
                "𝒓₀ [R☉]",
                f"{d.r0_rsun:.2f}",
                help=t("page.sim.metric.r0_help"),
            )
            ec2.metric(
                "t₀",
                d.t0.strftime("%d.%m. %H:%M"),
                help=t("page.sim.metric.t0_help"),
            )
            st.metric(
                "v_apex [km/s]",
                f"{d.v_apex_kms:.1f} ± {d.v_apex_error_kms:.1f}",
                help=t("page.sim.metric.vapex_help"),
            )
            st.metric(
                f"v₀ → {stored_config.target.name} [km/s]",
                f"{results.v0_kms:.0f}{_v0_note}",
                help=t("page.sim.metric.v0_help"),
            )
            ea1, ea2 = st.columns(2)
            ea1.metric(
                "𝜶 [deg]",
                f"{d.alpha_deg:.1f}",
                help=t("page.sim.metric.alpha_help"),
            )
            ea2.metric(
                "𝜿",
                f"{d.kappa:.3f}",
                help=t("page.sim.metric.kappa_help"),
            )
            eb1, eb2 = st.columns(2)
            eb1.metric(
                "𝝓 [deg]",
                f"{d.lon_deg:.1f}",
                help=t("page.sim.metric.phi_help"),
            )
            eb2.metric(
                "𝜽 [deg]",
                f"{d.lat_deg:.1f}",
                help=t("page.sim.metric.theta_help"),
            )
            st.metric(
                "𝜸 [deg]",
                f"{d.tilt_deg:.1f}",
                help=t("page.sim.metric.gamma_help"),
            )
            ew1, ew2 = st.columns(2)
            ew1.metric(
                "Wind regime",
                stored_config.w_type,
                help=t("page.sim.metric.wind_regime_help"),
            )
            ew2.metric(
                "SSN",
                f"{stored_config.ssn:.0f}",
                help=t("page.sim.metric.ssn_help"),
            )
            st.metric(
                "cₙ (drag coeff.)",
                f"{stored_config.c_d}",
                help=t("page.sim.metric.cd_help"),
            )
            st.metric(
                "CME mass",
                _mass,
                help=t("page.sim.metric.mass_help"),
            )

        if results.modbm_series:
            modbm_fig = build_single_model_figure(
                series=results.modbm_series,
                elapsed_h=results.elapsed_time_MODBM_h,
                target_distance_au=stored_config.target.distance,
                label="MoDBM",
                color=PLOT_COLORS["MODBM"],
            )
            st.plotly_chart(modbm_fig, width="stretch")

    # --------------------------------------------------------
    # Full-width combined comparison
    # --------------------------------------------------------
    if results.dbm_series or results.modbm_series:
        st.divider()
        st.subheader(t("page.sim.combined_comparison"))
        prop_fig = build_propagation_comparison_figure(
            results=results,
            target_distance_au=stored_config.target.distance,
        )
        st.plotly_chart(prop_fig, width="stretch")
