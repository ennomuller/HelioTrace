"""
Tests for heliotrace.simulation.runner.

Groups
------
A — derive_gcs_params: analytic slope recovery
B — derive_gcs_params: unit conversion & 1σ error
C — derive_gcs_params: median geometry extraction
D — derive_gcs_params: boundary conditions & error handling
E — _sample_solution: output structure invariants
F — _sample_solution: time-window logic
G — run_full_simulation: geometric miss
H — run_full_simulation: coasting analytic benchmark
I — run_full_simulation: v0 override propagation
J — run_full_simulation: mass override
K — run_full_simulation: monotone scaling in v_apex
L — run_full_simulation: reference event regression
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta

import astropy.units as u
import numpy as np
import pandas as pd
import pytest

from heliotrace.models.schemas import SimulationConfig, TargetConfig
from heliotrace.physics.drag import (
    get_constant_drag_parameter_DBM,
    simulate_equation_of_motion_DBM,
)
from heliotrace.simulation.runner import (
    _sample_solution,
    derive_gcs_params,
    run_full_simulation,
)

_RSUN_TO_KM: float = float((1 * u.R_sun).to(u.km).value)
_AU_TO_KM: float = float((1 * u.AU).to(u.km).value)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def aligned_df() -> pd.DataFrame:
    """3 observations with CME at lon=lat=0, v_apex ≈ 500 km/s."""
    dt = 1800.0  # 30-min cadence [s]
    t0 = datetime(2024, 1, 1, 12, 0)
    v = 500.0 / _RSUN_TO_KM  # R_sun/s for v_apex = 500 km/s
    h0 = 10.0
    return pd.DataFrame(
        {
            "datetime": [t0 + timedelta(seconds=i * dt) for i in range(3)],
            "lon": [0.0] * 3,
            "lat": [0.0] * 3,
            "tilt": [0.0] * 3,
            "half_angle": [30.0] * 3,
            "height": [h0 + v * i * dt for i in range(3)],
            "kappa": [0.42] * 3,
        }
    )


@pytest.fixture
def aligned_config() -> SimulationConfig:
    """Earth target at lon=lat=0, standard DBM/MoDBM parameters."""
    return SimulationConfig(
        event_str="Test event",
        target=TargetConfig(name="Earth", lon=0.0, lat=0.0, distance=1.0),
        height_error=0.5,
        w=400.0,
        w_type="slow",
        ssn=50.0,
        c_d=1.0,
    )


@pytest.fixture
def reference_event_df() -> pd.DataFrame:
    """2023-10-28 CME — identical data to test_smoke.py reference_gcs_df."""
    return pd.DataFrame(
        [
            {
                "datetime": datetime(2023, 10, 28, 14, 0),
                "lon": 5.5,
                "lat": -20.1,
                "tilt": -7.5,
                "half_angle": 30.0,
                "height": 10.0,
                "kappa": 0.42,
            },
            {
                "datetime": datetime(2023, 10, 28, 14, 30),
                "lon": 5.5,
                "lat": -20.1,
                "tilt": -7.5,
                "half_angle": 30.0,
                "height": 12.1,
                "kappa": 0.42,
            },
            {
                "datetime": datetime(2023, 10, 28, 15, 0),
                "lon": 5.5,
                "lat": -20.1,
                "tilt": -7.5,
                "half_angle": 30.0,
                "height": 14.0,
                "kappa": 0.42,
            },
        ]
    )


@pytest.fixture
def reference_config() -> SimulationConfig:
    """Reference simulation config for the 2023-10-28 event (Earth target)."""
    return SimulationConfig(
        event_str="Halo CME · 2023-10-28",
        target=TargetConfig(name="Earth", lon=0.0, lat=0.0, distance=1.0),
        height_error=0.5,
        w=400.0,
        w_type="slow",
        ssn=70.0,
        c_d=1.0,
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _two_point_df(v_rsun_per_s: float, dt_s: float, h0: float = 10.0) -> pd.DataFrame:
    """Two-row DataFrame that defines a line exactly: slope = v_rsun_per_s."""
    t0 = datetime(2024, 1, 1, 12, 0)
    return pd.DataFrame(
        {
            "datetime": [t0, t0 + timedelta(seconds=dt_s)],
            "lon": [0.0, 0.0],
            "lat": [0.0, 0.0],
            "tilt": [0.0, 0.0],
            "half_angle": [30.0, 30.0],
            "height": [h0, h0 + v_rsun_per_s * dt_s],
            "kappa": [0.42, 0.42],
        }
    )


def _uniform_df(N: int, dt_s: float, v: float = 7e-4, h0: float = 10.0) -> pd.DataFrame:
    """N uniformly-spaced observations on a perfect linear H-T trend."""
    t0 = datetime(2024, 1, 1, 12, 0)
    return pd.DataFrame(
        {
            "datetime": [t0 + timedelta(seconds=i * dt_s) for i in range(N)],
            "lon": [0.0] * N,
            "lat": [0.0] * N,
            "tilt": [0.0] * N,
            "half_angle": [30.0] * N,
            "height": [h0 + v * i * dt_s for i in range(N)],
            "kappa": [0.42] * N,
        }
    )


# ---------------------------------------------------------------------------
# Group A — derive_gcs_params: analytic slope recovery
# ---------------------------------------------------------------------------


def test_a1_v_apex_kms_slope_1e3() -> None:
    """2-point perfect fit: v = 1e-3 R_sun/s → v_apex_kms matches conversion."""
    v = 1e-3  # R_sun/s
    df = _two_point_df(v, dt_s=3600.0)
    derived = derive_gcs_params(df, height_error=0.5)
    assert math.isclose(derived.v_apex_kms, v * _RSUN_TO_KM, rel_tol=1e-9)


def test_a2_v_apex_kms_slope_2e3() -> None:
    """2-point perfect fit: v = 2e-3 R_sun/s → v_apex_kms matches conversion."""
    v = 2e-3  # R_sun/s
    df = _two_point_df(v, dt_s=7200.0)
    derived = derive_gcs_params(df, height_error=0.5)
    assert math.isclose(derived.v_apex_kms, v * _RSUN_TO_KM, rel_tol=1e-9)


def test_a3_r0_rsun_equals_max_height() -> None:
    """r0_rsun must equal the maximum observed height (last row of a 2-point fit)."""
    v, dt, h0 = 1e-3, 3600.0, 10.0
    df = _two_point_df(v, dt_s=dt, h0=h0)
    derived = derive_gcs_params(df, height_error=0.5)
    assert abs(derived.r0_rsun - (h0 + v * dt)) < 1e-10


def test_a4_chi_squared_zero_two_points() -> None:
    """2 points define a line exactly → residuals = 0 → chi_squared = 0."""
    df = _two_point_df(1e-3, dt_s=3600.0)
    derived = derive_gcs_params(df, height_error=0.5)
    assert abs(derived.fit_chi_squared) < 1e-10


def test_a5_t0_equals_max_datetime() -> None:
    """t0 must be the timestamp of the maximum-height observation."""
    df = _two_point_df(1e-3, dt_s=3600.0)
    derived = derive_gcs_params(df, height_error=0.5)
    assert derived.t0 == df["datetime"].max()


# ---------------------------------------------------------------------------
# Group B — derive_gcs_params: unit conversion & 1σ error
# ---------------------------------------------------------------------------


def test_b1_slope_error_closed_form() -> None:
    """
    For N uniformly-spaced observations with equal height_error σ:
        S_xx = (N-1)·N·(N+1)/12 · Δt²
        v_apex_error_kms = (σ / √S_xx) · _RSUN_TO_KM
    """
    N, dt, height_error = 5, 1800.0, 0.5
    df = _uniform_df(N, dt)
    derived = derive_gcs_params(df, height_error=height_error)

    S_xx = (N - 1) * N * (N + 1) / 12.0 * dt**2
    expected = (height_error / math.sqrt(S_xx)) * _RSUN_TO_KM
    assert math.isclose(derived.v_apex_error_kms, expected, rel_tol=1e-6)


def test_b2_height_error_doubles_v_error() -> None:
    """Doubling height_error must double v_apex_error_kms (linear propagation)."""
    N, dt = 5, 1800.0
    df = _uniform_df(N, dt)
    d1 = derive_gcs_params(df, height_error=0.5)
    d2 = derive_gcs_params(df, height_error=1.0)
    assert math.isclose(d2.v_apex_error_kms, 2.0 * d1.v_apex_error_kms, rel_tol=1e-9)


def test_b3_height_error_zero_completes() -> None:
    """height_error=0 (unweighted path via sigma=0): function completes, chi_squared ≥ 0."""
    df = _uniform_df(5, 1800.0)
    derived = derive_gcs_params(df, height_error=0.0)
    assert derived.fit_chi_squared >= 0.0


# ---------------------------------------------------------------------------
# Group C — derive_gcs_params: median geometry extraction
# ---------------------------------------------------------------------------


@pytest.fixture
def geo_df() -> pd.DataFrame:
    """3-row DataFrame with distinct (alpha, kappa, lon, lat) values for median tests."""
    t0 = datetime(2024, 1, 1, 12, 0)
    return pd.DataFrame(
        {
            "datetime": [t0 + timedelta(hours=i) for i in range(3)],
            "lon": [10.0, 20.0, 30.0],
            "lat": [-5.0, 0.0, 5.0],
            "tilt": [0.0, 0.0, 0.0],
            "half_angle": [20.0, 30.0, 40.0],
            "height": [10.0, 12.0, 14.0],  # perfect linear trend
            "kappa": [0.3, 0.5, 0.7],
        }
    )


def test_c1_alpha_deg_median(geo_df: pd.DataFrame) -> None:
    derived = derive_gcs_params(geo_df, height_error=0.5)
    assert derived.alpha_deg == 30.0


def test_c2_kappa_median(geo_df: pd.DataFrame) -> None:
    derived = derive_gcs_params(geo_df, height_error=0.5)
    assert derived.kappa == 0.5


def test_c3_lon_deg_median(geo_df: pd.DataFrame) -> None:
    derived = derive_gcs_params(geo_df, height_error=0.5)
    assert derived.lon_deg == 20.0


def test_c4_lat_deg_median(geo_df: pd.DataFrame) -> None:
    derived = derive_gcs_params(geo_df, height_error=0.5)
    assert derived.lat_deg == 0.0


# ---------------------------------------------------------------------------
# Group D — derive_gcs_params: boundary conditions & error handling
# ---------------------------------------------------------------------------

_DF_COLS = ["datetime", "lon", "lat", "tilt", "half_angle", "height", "kappa"]


_INSUFFICIENT_OBS = "At least 2 valid observations"


def test_d1_empty_df_raises() -> None:
    df = pd.DataFrame(columns=_DF_COLS)
    with pytest.raises(ValueError, match=_INSUFFICIENT_OBS):
        derive_gcs_params(df, height_error=0.5)


def test_d2_one_row_raises() -> None:
    df = pd.DataFrame(
        [
            {
                "datetime": datetime(2024, 1, 1),
                "lon": 0.0,
                "lat": 0.0,
                "tilt": 0.0,
                "half_angle": 30.0,
                "height": 10.0,
                "kappa": 0.42,
            }
        ]
    )
    with pytest.raises(ValueError, match=_INSUFFICIENT_OBS):
        derive_gcs_params(df, height_error=0.5)


def test_d3_all_nan_heights_raises() -> None:
    t0 = datetime(2024, 1, 1)
    df = pd.DataFrame(
        {
            "datetime": [t0, t0 + timedelta(hours=1)],
            "lon": [0.0, 0.0],
            "lat": [0.0, 0.0],
            "tilt": [0.0, 0.0],
            "half_angle": [30.0, 30.0],
            "height": [float("nan"), float("nan")],
            "kappa": [0.42, 0.42],
        }
    )
    with pytest.raises(ValueError, match=_INSUFFICIENT_OBS):
        derive_gcs_params(df, height_error=0.5)


def test_d4_one_nan_height_runs() -> None:
    """3 rows with 1 NaN height → 2 valid after dropna → fit succeeds."""
    t0 = datetime(2024, 1, 1)
    df = pd.DataFrame(
        {
            "datetime": [t0, t0 + timedelta(hours=1), t0 + timedelta(hours=2)],
            "lon": [0.0] * 3,
            "lat": [0.0] * 3,
            "tilt": [0.0] * 3,
            "half_angle": [30.0] * 3,
            "height": [10.0, float("nan"), 12.0],
            "kappa": [0.42] * 3,
        }
    )
    derived = derive_gcs_params(df, height_error=0.5)
    assert derived.v_apex_kms > 0.0


# ---------------------------------------------------------------------------
# Group E — _sample_solution: output structure invariants
# ---------------------------------------------------------------------------


@pytest.fixture
def dbm_solution():
    """Real DBM ODE solution with r0=20 R_sun, v0=w=400 km/s, γ≈1e-7."""
    r0 = 20.0 * u.R_sun
    v0 = 400.0 * u.km / u.s
    w = 400.0 * u.km / u.s
    alpha = 30.0 * u.deg
    kappa = 0.42
    # v_apex slightly above v0 to give realistic Pluta mass → γ ≈ 1e-7
    gamma = get_constant_drag_parameter_DBM(r0, alpha, kappa, v0 + 100.0 * u.km / u.s)
    return simulate_equation_of_motion_DBM(
        (0.0, 225.0 * 3600.0),
        r0=r0,
        v0=v0,
        w=w,
        gamma=gamma,
    )


def test_e1_t_hours_length_300(dbm_solution) -> None:
    series = _sample_solution(dbm_solution, elapsed_s=3600.0)
    assert len(series.t_hours) == 300


def test_e2_r_rsun_length_300(dbm_solution) -> None:
    series = _sample_solution(dbm_solution, elapsed_s=3600.0)
    assert len(series.r_rsun) == 300


def test_e3_v_kms_length_300(dbm_solution) -> None:
    series = _sample_solution(dbm_solution, elapsed_s=3600.0)
    assert len(series.v_kms) == 300


def test_e4_t_hours_first_matches_sol(dbm_solution) -> None:
    sol = dbm_solution
    series = _sample_solution(sol, elapsed_s=3600.0)
    assert abs(series.t_hours[0] - sol.t[0] / 3600.0) < 1e-12


def test_e5_r_rsun_first_and_last(dbm_solution) -> None:
    sol = dbm_solution
    elapsed_s = 3600.0
    series = _sample_solution(sol, elapsed_s=elapsed_s)
    t_arr = np.linspace(sol.t[0], min(elapsed_s + 3.0 * 3600.0, sol.t[-1]), 300)
    for idx in [0, -1]:
        expected = sol.sol(t_arr)[0][idx] / _RSUN_TO_KM
        assert abs(series.r_rsun[idx] - expected) < 1e-9


def test_e6_v_kms_first_and_last(dbm_solution) -> None:
    sol = dbm_solution
    elapsed_s = 3600.0
    series = _sample_solution(sol, elapsed_s=elapsed_s)
    t_arr = np.linspace(sol.t[0], min(elapsed_s + 3.0 * 3600.0, sol.t[-1]), 300)
    for idx in [0, -1]:
        expected = sol.sol(t_arr)[1][idx]
        assert abs(series.v_kms[idx] - expected) < 1e-9


# ---------------------------------------------------------------------------
# Group F — _sample_solution: time-window logic
# ---------------------------------------------------------------------------


def test_f1_window_within_sol(dbm_solution) -> None:
    """elapsed + 3 h < sol.t[-1] → t_hours[-1] == (elapsed + 3 h) / 3600."""
    sol = dbm_solution
    elapsed_s = 3600.0  # 1 h; 1 + 3 = 4 h << 225 h
    series = _sample_solution(sol, elapsed_s=elapsed_s, extra_hours=3.0)
    expected = (elapsed_s + 3.0 * 3600.0) / 3600.0
    assert abs(series.t_hours[-1] - expected) < 1e-6


def test_f2_window_clamped_to_sol(dbm_solution) -> None:
    """elapsed + 3 h > sol.t[-1] → t_hours[-1] clamped at sol.t[-1] / 3600."""
    sol = dbm_solution
    elapsed_s = 223.0 * 3600.0  # 223 + 3 = 226 h > 225 h = sol.t[-1]
    series = _sample_solution(sol, elapsed_s=elapsed_s, extra_hours=3.0)
    expected = sol.t[-1] / 3600.0
    assert abs(series.t_hours[-1] - expected) < 1e-6


def test_f3_extra_hours_zero(dbm_solution) -> None:
    """extra_hours=0 → t_hours[-1] == elapsed_s / 3600."""
    sol = dbm_solution
    elapsed_s = 3600.0
    series = _sample_solution(sol, elapsed_s=elapsed_s, extra_hours=0.0)
    assert abs(series.t_hours[-1] - elapsed_s / 3600.0) < 1e-6


# ---------------------------------------------------------------------------
# Group G — run_full_simulation: geometric miss
# ---------------------------------------------------------------------------


@pytest.fixture
def miss_results(aligned_df: pd.DataFrame):
    """CME at lon=lat=0, target at lon=90° → orthogonal → projection_ratio < 0.3."""
    config = SimulationConfig(
        event_str="Test miss",
        target=TargetConfig(name="Side", lon=90.0, lat=0.0, distance=1.0),
        height_error=0.5,
        w=400.0,
        w_type="slow",
        ssn=50.0,
        c_d=1.0,
    )
    return run_full_simulation(aligned_df, config)


def test_g1_miss_target_hit_false(miss_results) -> None:
    assert miss_results.target_hit is False


def test_g2_miss_v0_zero(miss_results) -> None:
    assert miss_results.v0_kms == 0.0


def test_g3_miss_dbm_series_none(miss_results) -> None:
    assert miss_results.dbm_series is None


def test_g4_miss_modbm_series_none(miss_results) -> None:
    assert miss_results.modbm_series is None


def test_g5_miss_elapsed_time_none(miss_results) -> None:
    assert miss_results.elapsed_time_DBM_h is None


# ---------------------------------------------------------------------------
# Group H — run_full_simulation: coasting analytic benchmark (v0 = w)
# ---------------------------------------------------------------------------


@pytest.fixture
def coasting_results(aligned_df: pd.DataFrame):
    """
    v0 = w = 400 km/s → drag force = 0 → constant-velocity propagation.

    Returns (SimulationResults, DerivedGCSParams) so tests can compute
    the closed-form arrival time independently.
    """
    config = SimulationConfig(
        event_str="Coasting test",
        target=TargetConfig(name="Earth", lon=0.0, lat=0.0, distance=1.0),
        height_error=0.5,
        w=400.0,
        w_type="slow",
        ssn=50.0,
        c_d=1.0,
        v0_override_kms=400.0,
    )
    results = run_full_simulation(aligned_df, config)
    derived = derive_gcs_params(aligned_df, height_error=0.5)
    return results, derived


def test_h1_coasting_target_hit(coasting_results) -> None:
    results, _ = coasting_results
    assert results.target_hit is True


def test_h2_coasting_arrival_time(coasting_results) -> None:
    """t_arr = (d_target - r0) / w matches DBM output to within 0.1 %."""
    results, derived = coasting_results
    r0_km = derived.r0_rsun * _RSUN_TO_KM
    expected_h = (_AU_TO_KM - r0_km) / 400.0 / 3600.0
    assert math.isclose(results.elapsed_time_DBM_h, expected_h, rel_tol=1e-3)


def test_h3_coasting_arrival_velocity(coasting_results) -> None:
    """Impact velocity must remain ≈ 400 km/s (no drag → no deceleration)."""
    results, _ = coasting_results
    assert math.isclose(results.velocity_arrival_DBM_kms, 400.0, rel_tol=1e-2)


# ---------------------------------------------------------------------------
# Group I — run_full_simulation: v0 override propagation
# ---------------------------------------------------------------------------


@pytest.fixture
def override_results(aligned_df: pd.DataFrame):
    """Two direct-hit runs with v0=600 km/s and v0=500 km/s for comparison."""

    def _run(v0_kms: float):
        config = SimulationConfig(
            event_str="Override test",
            target=TargetConfig(name="Earth", lon=0.0, lat=0.0, distance=1.0),
            height_error=0.5,
            w=400.0,
            w_type="slow",
            ssn=50.0,
            c_d=1.0,
            v0_override_kms=v0_kms,
        )
        return run_full_simulation(aligned_df, config)

    return _run(600.0), _run(500.0)


def test_i1_v0_kms_equals_override(override_results) -> None:
    results_600, _ = override_results
    assert results_600.v0_kms == 600.0


def test_i2_override_target_hit(override_results) -> None:
    results_600, _ = override_results
    assert results_600.target_hit is True


def test_i3_faster_v0_shorter_transit(override_results) -> None:
    results_600, results_500 = override_results
    assert results_600.elapsed_time_DBM_h < results_500.elapsed_time_DBM_h


# ---------------------------------------------------------------------------
# Group J — run_full_simulation: mass override
# ---------------------------------------------------------------------------


@pytest.fixture
def mass_results(aligned_df: pd.DataFrame):
    """
    Two runs: light (1e15 g) vs heavy (1e16 g) CME.

    v0_override=300 km/s < w=400 km/s so drag *accelerates* the CME.
    Lower γ (heavier mass) → weaker acceleration → longer transit.
    """

    def _run(m_g: float):
        config = SimulationConfig(
            event_str="Mass test",
            target=TargetConfig(name="Earth", lon=0.0, lat=0.0, distance=1.0),
            height_error=0.5,
            w=400.0,
            w_type="slow",
            ssn=50.0,
            c_d=1.0,
            v0_override_kms=300.0,  # v0 < w → solar wind accelerates CME
            m_override_g=m_g,
        )
        return run_full_simulation(aligned_df, config)

    return _run(1e15), _run(1e16)


def test_j1_heavier_cme_longer_transit(mass_results) -> None:
    """With v0 < w, heavier CME (lower γ) → less acceleration → longer transit."""
    results_light, results_heavy = mass_results
    assert results_heavy.elapsed_time_DBM_h > results_light.elapsed_time_DBM_h


def test_j2_both_arrive(mass_results) -> None:
    results_light, results_heavy = mass_results
    assert results_light.elapsed_time_DBM_h is not None
    assert results_heavy.elapsed_time_DBM_h is not None


# ---------------------------------------------------------------------------
# Group K — run_full_simulation: monotone scaling in v_apex
# ---------------------------------------------------------------------------


@pytest.fixture
def monotone_results(aligned_df: pd.DataFrame):
    """Three direct-hit runs with v0 = 400, 800, 1200 km/s."""

    def _run(v0_kms: float):
        config = SimulationConfig(
            event_str="Monotone test",
            target=TargetConfig(name="Earth", lon=0.0, lat=0.0, distance=1.0),
            height_error=0.5,
            w=400.0,
            w_type="slow",
            ssn=50.0,
            c_d=1.0,
            v0_override_kms=v0_kms,
        )
        return run_full_simulation(aligned_df, config)

    return _run(400.0), _run(800.0), _run(1200.0)


def test_k1_strictly_decreasing_transit(monotone_results) -> None:
    """Faster CME → shorter transit for both DBM and MoDBM."""
    r400, r800, r1200 = monotone_results
    assert r400.elapsed_time_DBM_h > r800.elapsed_time_DBM_h > r1200.elapsed_time_DBM_h
    assert r400.elapsed_time_MODBM_h > r800.elapsed_time_MODBM_h > r1200.elapsed_time_MODBM_h


def test_k2_all_target_hit(monotone_results) -> None:
    for r in monotone_results:
        assert r.target_hit is True


# ---------------------------------------------------------------------------
# Group L — run_full_simulation: reference event regression
# ---------------------------------------------------------------------------


@pytest.fixture
def reference_results(reference_event_df: pd.DataFrame, reference_config: SimulationConfig):
    return run_full_simulation(reference_event_df, reference_config)


def test_l1_reference_target_hit(reference_results) -> None:
    assert reference_results.target_hit is True


def test_l2_dbm_transit_physically_plausible(reference_results) -> None:
    assert 40 <= reference_results.elapsed_time_DBM_h <= 100


def test_l3_modbm_transit_physically_plausible(reference_results) -> None:
    assert 40 <= reference_results.elapsed_time_MODBM_h <= 120


def test_l4_dbm_transit_regression_guard(reference_results) -> None:
    """DBM transit time must stay within ±5 h of the 69.4 h reference value."""
    assert abs(reference_results.elapsed_time_DBM_h - 69.4) <= 5.0


def test_l5_arrival_velocity_plausible(reference_results) -> None:
    assert 300 <= reference_results.velocity_arrival_DBM_kms <= 900


def test_l6_arrival_time_is_datetime(reference_results) -> None:
    from datetime import datetime as _dt

    assert isinstance(reference_results.arrival_time_DBM, _dt)


def test_l7_dbm_series_length_300(reference_results) -> None:
    assert reference_results.dbm_series is not None
    assert len(reference_results.dbm_series.t_hours) == 300
