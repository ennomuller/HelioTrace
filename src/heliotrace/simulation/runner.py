"""
Simulation orchestrator — bridges the UI input layer with the pure-physics modules.

No Streamlit imports here; this module is fully testable in isolation.
"""

from __future__ import annotations

import logging

import astropy.units as u
import numpy as np
import pandas as pd

from heliotrace.models.schemas import (
    DerivedGCSParams,
    PropagationSeries,
    SimulationConfig,
    SimulationResults,
)
from heliotrace.physics.apex_ratio import get_target_apex_ratio
from heliotrace.physics.drag import (
    find_time_and_velocity_at_distance,
    get_constant_drag_parameter_DBM,
    simulate_equation_of_motion_DBM,
    simulate_equation_of_motion_MODBM,
)
from heliotrace.physics.fitting import perform_linear_fit

logger = logging.getLogger(__name__)

_RSUN_TO_KM: float = float((1 * u.R_sun).to(u.km).value)


# ---------------------------------------------------------------------------
# Step 1 — GCS data → derived initial conditions
# ---------------------------------------------------------------------------


def derive_gcs_params(df: pd.DataFrame, height_error: float) -> DerivedGCSParams:
    """
    Compute initial conditions from the GCS observation table.

    Performs a weighted linear fit to the height-time data and extracts
    median GCS geometry parameters.

    :param df:           DataFrame with columns: ``datetime``, ``lon``, ``lat``,
                         ``tilt``, ``half_angle``, ``height``, ``kappa``.
    :param height_error: ± measurement uncertainty applied to every height point [R_sun].
    :return: :class:`~heliotrace.models.schemas.DerivedGCSParams`.
    """
    df = df.sort_values("datetime").reset_index(drop=True)
    df["_dt_s"] = (df["datetime"] - df["datetime"].iloc[0]).dt.total_seconds()

    fit = perform_linear_fit(
        x_data=df["_dt_s"].to_numpy(),
        y_data=df["height"].to_numpy(),
        y_error=float(height_error),
    )

    v_apex_kms = float((fit["slope"] * u.R_sun / u.s).to(u.km / u.s).value)
    v_apex_error_kms = float((fit["slope_error"] * u.R_sun / u.s).to(u.km / u.s).value)

    logger.info(
        "Derived GCS params: v_apex=%.1f km/s, r0=%.2f R☉",
        v_apex_kms,
        float(df["height"].max()),
    )

    return DerivedGCSParams(
        r0_rsun=float(df["height"].max()),
        t0=df["datetime"].max(),
        alpha_deg=float(df["half_angle"].median()),
        kappa=float(df["kappa"].median()),
        lon_deg=float(df["lon"].median()),
        lat_deg=float(df["lat"].median()),
        tilt_deg=float(df["tilt"].median()),
        v_apex_kms=v_apex_kms,
        v_apex_error_kms=v_apex_error_kms,
        fit_chi_squared=float(fit["chi_squared"]),
        fit_slope=float(fit["slope"]),
        fit_intercept=float(fit["intercept"]),
    )


# ---------------------------------------------------------------------------
# Internal helper — ODE solution → plottable arrays
# ---------------------------------------------------------------------------


def _sample_solution(sol: object, elapsed_s: float, extra_hours: float = 3.0) -> PropagationSeries:
    """
    Sample a ``solve_ivp`` dense solution into plain Python lists for Plotly.

    :param sol:         Dense ODE solution (``sol.sol`` callable).
    :param elapsed_s:   Arrival time [s] — used to extend the plot window slightly.
    :param extra_hours: Hours to show past the arrival time.
    :return: :class:`~heliotrace.models.schemas.PropagationSeries`.
    """
    t_end = elapsed_s + extra_hours * 3600.0
    t_arr = np.linspace(sol.t[0], min(t_end, sol.t[-1]), 300)
    y_arr = sol.sol(t_arr)
    return PropagationSeries(
        t_hours=list(t_arr / 3600.0),
        r_rsun=list(y_arr[0] / _RSUN_TO_KM),
        v_kms=list(y_arr[1]),
    )


# ---------------------------------------------------------------------------
# Step 2 — Full simulation pipeline
# ---------------------------------------------------------------------------


def run_full_simulation(df: pd.DataFrame, config: SimulationConfig) -> SimulationResults:
    """
    Execute the complete CME propagation pipeline.

    Steps
    -----
    1. H-T fit → apex velocity and initial conditions.
    2. Geometric projection → target-directed speed v₀.
    3. DBM ODE integration.
    4. MoDBM ODE integration.
    5. Interpolate arrival time and impact speed at target distance.

    :param df:     GCS observation table (from ``st.data_editor``).
    :param config: All user-controlled parameters.
    :return: :class:`~heliotrace.models.schemas.SimulationResults`.
    """
    logger.info(
        "Starting simulation for event %s → target %s", config.event_str, config.target.name
    )

    # --- 1) Derive initial conditions ---
    derived = derive_gcs_params(df, config.height_error)

    alpha = derived.alpha_deg * u.deg
    kappa = derived.kappa
    lat = derived.lat_deg * u.deg
    lon = derived.lon_deg * u.deg
    tilt = derived.tilt_deg * u.deg
    r0 = derived.r0_rsun * u.R_sun
    v_apex = derived.v_apex_kms * u.km / u.s

    # --- 2) Geometry: projection ratio → v₀ ---
    projection_ratio = get_target_apex_ratio(
        alpha=alpha,
        kappa=kappa,
        cme_lat=lat,
        cme_lon=lon,
        tilt=tilt,
        target_lat=config.target.lat * u.deg,
        target_lon=config.target.lon * u.deg,
    )

    target_hit = projection_ratio >= 0.3
    v0 = v_apex * projection_ratio if target_hit else (0.0 * u.km / u.s)

    if config.v0_override_kms is not None and target_hit:
        v0 = config.v0_override_kms * u.km / u.s
        logger.info("v0 override applied: %.1f km/s", config.v0_override_kms)

    # --- 3) Drag parameters ---
    M_override = (config.m_override_g * u.g) if config.m_override_g is not None else None
    gamma = get_constant_drag_parameter_DBM(
        r=r0,
        alpha=alpha,
        kappa=kappa,
        v_apex=v_apex,
        M=M_override,
        c_d=config.c_d,
    )

    # --- 4) Integrate ODEs ---
    t_span: tuple[float, float] = (0.0, 225.0 * 3600.0)

    sol_DBM = simulate_equation_of_motion_DBM(
        t_span,
        r0=r0,
        v0=v0,
        w=config.w * u.km / u.s,
        gamma=gamma,
    )
    sol_MODBM = simulate_equation_of_motion_MODBM(
        t_span,
        r0=r0,
        v_apex=v_apex,
        v0=v0,
        alpha=alpha,
        kappa=kappa,
        w_type=config.w_type,
        ssn=config.ssn,
        c_d=config.c_d,
        M=M_override,
    )

    # --- 5) Arrival at target ---
    target_distance = config.target.distance * u.AU

    elapsed_DBM = elapsed_MODBM = None
    vel_DBM = vel_MODBM = None
    arrival_DBM = arrival_MODBM = None
    series_DBM = series_MODBM = None

    if target_hit:
        try:
            elapsed_DBM, vel_DBM = find_time_and_velocity_at_distance(sol_DBM, target_distance)
            arrival_DBM = derived.t0 + pd.Timedelta(seconds=elapsed_DBM)
            series_DBM = _sample_solution(sol_DBM, elapsed_DBM)
        except (ValueError, Exception) as exc:
            logger.warning("DBM arrival extraction failed: %s", exc)

        try:
            elapsed_MODBM, vel_MODBM = find_time_and_velocity_at_distance(
                sol_MODBM, target_distance
            )
            arrival_MODBM = derived.t0 + pd.Timedelta(seconds=elapsed_MODBM)
            series_MODBM = _sample_solution(sol_MODBM, elapsed_MODBM)
        except (ValueError, Exception) as exc:
            logger.warning("MoDBM arrival extraction failed: %s", exc)

    logger.info(
        "Simulation complete. DBM=%.1f h, MoDBM=%.1f h",
        elapsed_DBM / 3600.0 if elapsed_DBM else float("nan"),
        elapsed_MODBM / 3600.0 if elapsed_MODBM else float("nan"),
    )

    return SimulationResults(
        derived=derived,
        projection_ratio=projection_ratio,
        v0_kms=float(v0.to(u.km / u.s).value),
        target_hit=target_hit,
        dbm_series=series_DBM,
        elapsed_time_DBM_h=elapsed_DBM / 3600.0 if elapsed_DBM is not None else None,
        velocity_arrival_DBM_kms=vel_DBM,
        arrival_time_DBM=arrival_DBM,
        modbm_series=series_MODBM,
        elapsed_time_MODBM_h=elapsed_MODBM / 3600.0 if elapsed_MODBM is not None else None,
        velocity_arrival_MODBM_kms=vel_MODBM,
        arrival_time_MODBM=arrival_MODBM,
    )
