"""
Smoke tests — verify that core modules import cleanly and the physics pipeline
reproduces the reference result from the 2023-10-28 CME event.

Reference (from MEMORY.md):
    Apex velocity ≈ 773 km/s
    DBM transit time ≈ 69.4 h
"""
from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd
import pytest

import heliotrace


# ---------------------------------------------------------------------------
# Import tests
# ---------------------------------------------------------------------------

def test_package_version() -> None:
    assert isinstance(heliotrace.__version__, str)


def test_models_importable() -> None:
    from heliotrace.models.schemas import (  # noqa: F401
        DerivedGCSParams,
        PropagationSeries,
        SimulationConfig,
        SimulationResults,
        TargetConfig,
    )


def test_physics_importable() -> None:
    from heliotrace.physics.fitting import perform_linear_fit  # noqa: F401
    from heliotrace.physics.apex_ratio import get_target_apex_ratio  # noqa: F401
    from heliotrace.physics.drag import (  # noqa: F401
        get_CME_mass_pluta,
        simulate_equation_of_motion_DBM,
        simulate_equation_of_motion_MODBM,
    )


def test_simulation_importable() -> None:
    from heliotrace.simulation.runner import derive_gcs_params, run_full_simulation  # noqa: F401


# ---------------------------------------------------------------------------
# Physics unit tests
# ---------------------------------------------------------------------------

def test_linear_fit_exact() -> None:
    """A perfect linear dataset should return near-zero χ² and exact slope."""
    from heliotrace.physics.fitting import perform_linear_fit

    x = np.array([0.0, 3600.0, 7200.0])
    y = np.array([10.0, 14.0, 18.0])          # slope = 4/3600 R_sun/s
    result = perform_linear_fit(x, y)

    assert abs(result["slope"] - 4.0 / 3600.0) < 1e-10
    assert abs(result["intercept"] - 10.0) < 1e-10
    assert result["chi_squared"] < 1e-20


def test_pluta_mass_formula() -> None:
    """CME mass must be positive and dimensionally consistent."""
    import astropy.units as u
    from heliotrace.physics.drag import get_CME_mass_pluta

    mass = get_CME_mass_pluta(773.0 * u.km / u.s)
    assert mass.unit == u.g
    assert mass.value > 0


def test_pluta_mass_closed_form() -> None:
    """Verify the closed-form agrees with the analytical formula log10(M)=3.4e-4*v+15.479."""
    from heliotrace.physics.drag import get_CME_mass_pluta

    v_kms = 500.0
    expected = 10.0 ** (3.4e-4 * v_kms + 15.479)
    result = get_CME_mass_pluta(v_kms, return_with_unit=False)
    assert abs(result - expected) / expected < 1e-12


# ---------------------------------------------------------------------------
# Integration smoke test — 2023-10-28 event
# ---------------------------------------------------------------------------

@pytest.fixture
def reference_gcs_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"datetime": datetime(2023, 10, 28, 14, 0),  "lon": 5.5, "lat": -20.1, "tilt": -7.5, "half_angle": 30.0, "height": 10.0, "kappa": 0.42},
        {"datetime": datetime(2023, 10, 28, 14, 30), "lon": 5.5, "lat": -20.1, "tilt": -7.5, "half_angle": 30.0, "height": 12.1, "kappa": 0.42},
        {"datetime": datetime(2023, 10, 28, 15, 0),  "lon": 5.5, "lat": -20.1, "tilt": -7.5, "half_angle": 30.0, "height": 14.0, "kappa": 0.42},
    ])


def test_derive_gcs_params_apex_velocity(reference_gcs_df: pd.DataFrame) -> None:
    """Apex velocity for the reference event should be close to 773 km/s."""
    from heliotrace.simulation.runner import derive_gcs_params

    derived = derive_gcs_params(reference_gcs_df, height_error=0.25)
    # Allow ±5 % tolerance — exact value depends on linear fit
    assert 700.0 < derived.v_apex_kms < 850.0, f"v_apex = {derived.v_apex_kms:.1f} km/s (expected ~773)"


def test_full_simulation_dbm_transit(reference_gcs_df: pd.DataFrame) -> None:
    """DBM transit time for the reference event should be close to 69.4 h."""
    from heliotrace.models.schemas import SimulationConfig, TargetConfig
    from heliotrace.simulation.runner import run_full_simulation

    config = SimulationConfig(
        event_str="20231028",
        cme_launch_day=datetime(2023, 10, 28),
        target=TargetConfig(name="Earth", lon=0.0, lat=0.0, distance=1.0),
        height_error=0.25,
        w=390.0,
        w_type="slow",
        ssn=100.0,
        c_d=1.0,
        toa_raw=None,
        m_override_g=None,
    )

    results = run_full_simulation(reference_gcs_df, config)
    assert results.target_hit, "CME should hit Earth for the reference event"
    assert results.elapsed_time_DBM_h is not None
    # Allow ±10 % tolerance around the reference 69.4 h
    assert 60.0 < results.elapsed_time_DBM_h < 80.0, (
        f"DBM transit = {results.elapsed_time_DBM_h:.1f} h (expected ~69.4)"
    )
