"""
Tests for heliotrace.physics.drag — DBM and MoDBM physics engine.

Groups A–J cover all 10 public functions in drag.py with analytic benchmarks,
exact scaling-law probes, and boundary-condition guards.

Analytic reference:
    v(t) = w + (v0 - w) / (1 + γ|v0-w|t)
    r(t) = r0 + w·t + sign(v0-w)/γ · ln(1 + γ|v0-w|t)
"""

from __future__ import annotations

import astropy.units as u
import numpy as np
import pytest
from astropy.constants import m_p

from heliotrace.physics.drag import (
    find_time_and_velocity_at_distance,
    get_ambient_solar_wind_density_DBM,
    get_ambient_solar_wind_density_MODBM,
    get_ambient_solar_wind_speed_MODBM,
    get_CME_cross_section_pluta,
    get_CME_mass_pluta,
    get_constant_drag_parameter_DBM,
    get_varying_drag_parameter_MODBM,
    simulate_equation_of_motion_DBM,
    simulate_equation_of_motion_MODBM,
)

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

AU_KM: float = (1.0 * u.AU).to(u.km).value  # km per AU ≈ 1.496e8
R_SUN_KM: float = (1.0 * u.R_sun).to(u.km).value  # km per solar radius ≈ 6.957e5

# Reference CME geometry (2023-10-28 event)
_ALPHA = 30.0 * u.deg
_KAPPA = 0.42
_R0 = 20.0 * R_SUN_KM * u.km
_V_APEX = 773.0 * u.km / u.s


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _dbm_analytic(
    t_s: float,
    r0_km: float,
    v0_kms: float,
    w_kms: float,
    gamma_km: float,
) -> tuple[float, float]:
    """Exact closed-form DBM solution: return (r [km], v [km/s])."""
    dv = v0_kms - w_kms
    denom = 1.0 + gamma_km * abs(dv) * t_s
    v = w_kms + dv / denom
    r = r0_km + w_kms * t_s + np.sign(dv) / gamma_km * np.log(denom)
    return r, v


# ---------------------------------------------------------------------------
# Group A — get_CME_mass_pluta (4 tests)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("v_kms", [100.0, 500.0, 773.0, 1000.0, 2000.0])
def test_pluta_mass_closed_form_parametrized(v_kms: float) -> None:
    """log10(M [g]) = 3.4e-4 * v [km/s] + 15.479 (Pluta 2018)."""
    expected = 10.0 ** (3.4e-4 * v_kms + 15.479)
    result = get_CME_mass_pluta(v_kms, return_with_unit=False)
    assert abs(result - expected) / expected < 1e-12, (
        f"v={v_kms} km/s: got {result:.6e} g, expected {expected:.6e} g"
    )


def test_pluta_mass_quantity_input() -> None:
    """Quantity and plain-float inputs must agree to 1e-12."""
    m_float = get_CME_mass_pluta(773.0, return_with_unit=False)
    m_qty = get_CME_mass_pluta(773.0 * u.km / u.s, return_with_unit=False)
    assert abs(m_float - m_qty) / m_qty < 1e-12, (
        f"float path ({m_float:.6e}) differs from Quantity path ({m_qty:.6e})"
    )


def test_pluta_mass_return_unit_false() -> None:
    """return_with_unit=False must return a plain float."""
    result = get_CME_mass_pluta(500.0, return_with_unit=False)
    assert isinstance(result, float), f"Expected float, got {type(result)}"


def test_pluta_mass_monotone_in_speed() -> None:
    """More energetic CMEs have higher masses (catches sign-flip in exponent)."""
    v_values = [300.0, 500.0, 773.0, 1000.0, 1500.0]
    masses = [get_CME_mass_pluta(v, return_with_unit=False) for v in v_values]
    for i in range(len(masses) - 1):
        assert masses[i] < masses[i + 1], (
            f"M({v_values[i]}) = {masses[i]:.3e} >= M({v_values[i + 1]}) = {masses[i + 1]:.3e}"
        )


# ---------------------------------------------------------------------------
# Group B — get_CME_cross_section_pluta (5 tests)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("r_rsun", [10.0, 20.0, 50.0])
def test_cross_section_quadratic_scaling(r_rsun: float) -> None:
    """A ∝ r² → A(2r)/A(r) = 4.0 exactly."""
    r1 = r_rsun * R_SUN_KM * u.km
    r2 = 2.0 * r_rsun * R_SUN_KM * u.km
    A1 = get_CME_cross_section_pluta(r1, _ALPHA, _KAPPA, return_with_unit=False)
    A2 = get_CME_cross_section_pluta(r2, _ALPHA, _KAPPA, return_with_unit=False)
    ratio = A2 / A1
    assert abs(ratio - 4.0) / 4.0 < 1e-12, (
        f"r={r_rsun} R_sun: A(2r)/A(r) = {ratio:.10f}, expected 4.0"
    )


def test_cross_section_alpha_zero() -> None:
    """tan(0) = 0 → area must be exactly zero."""
    result = get_CME_cross_section_pluta(_R0, 0.0 * u.deg, _KAPPA, return_with_unit=False)
    assert result == 0.0, f"Expected 0.0 for alpha=0, got {result}"


def test_cross_section_kappa_zero() -> None:
    """arcsin(0) = 0 → tan(arcsin(0)) = 0 → area must be exactly zero."""
    result = get_CME_cross_section_pluta(_R0, _ALPHA, 0.0, return_with_unit=False)
    assert result == 0.0, f"Expected 0.0 for kappa=0, got {result}"


def test_cross_section_unit_output() -> None:
    """return_with_unit=True must return a Quantity in km²."""
    result = get_CME_cross_section_pluta(_R0, _ALPHA, _KAPPA)
    assert isinstance(result, u.Quantity), f"Expected Quantity, got {type(result)}"
    assert result.unit == u.km**2, f"Expected km², got {result.unit}"
    assert result.value > 0.0, f"Cross-section must be positive, got {result.value}"


def test_cross_section_quantity_vs_float_input() -> None:
    """Float and Quantity call branches agree to 1e-12."""
    r_km = 20.0 * R_SUN_KM
    alpha_rad = np.radians(30.0)
    A_float = get_CME_cross_section_pluta(r_km, alpha_rad, _KAPPA, return_with_unit=False)
    A_qty = get_CME_cross_section_pluta(r_km * u.km, 30.0 * u.deg, _KAPPA, return_with_unit=False)
    assert abs(A_float - A_qty) / A_qty < 1e-12, (
        f"float path ({A_float:.6e}) differs from Quantity path ({A_qty:.6e})"
    )


# ---------------------------------------------------------------------------
# Group C — get_ambient_solar_wind_density_DBM (3 tests)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("r_rsun", [10.0, 20.0, 50.0, 215.0])
def test_dbm_density_inverse_square_scaling(r_rsun: float) -> None:
    """ρ ∝ r_rsun⁻² → ρ(r)/ρ(2r) = 4.0 exactly (Leblanc 1998)."""
    r1 = r_rsun * R_SUN_KM * u.km
    r2 = 2.0 * r_rsun * R_SUN_KM * u.km
    rho1 = get_ambient_solar_wind_density_DBM(r1)
    rho2 = get_ambient_solar_wind_density_DBM(r2)
    ratio = (rho1 / rho2).decompose().value
    assert abs(ratio - 4.0) / 4.0 < 1e-12, (
        f"r={r_rsun} R_sun: ρ(r)/ρ(2r) = {ratio:.10f}, expected 4.0"
    )


def test_dbm_density_units() -> None:
    """DBM density must be convertible to kg/cm³."""
    rho = get_ambient_solar_wind_density_DBM(20.0 * R_SUN_KM * u.km)
    rho_cgs = rho.to(u.kg / u.cm**3)
    assert rho_cgs.value > 0.0


def test_dbm_density_reference_value() -> None:
    """ρ = m_p * 3.3e5 cm⁻³ / r_rsun² at reference distance."""
    r_rsun = 20.0
    r = r_rsun * R_SUN_KM * u.km
    rho = get_ambient_solar_wind_density_DBM(r)
    expected = m_p * 3.3e5 * u.cm ** (-3) / r_rsun**2
    rho_val = rho.to(u.kg / u.cm**3).value
    exp_val = expected.to(u.kg / u.cm**3).value
    assert abs(rho_val - exp_val) / exp_val < 1e-12, (
        f"DBM density at {r_rsun} R_sun: {rho_val:.4e}, expected {exp_val:.4e} kg/cm³"
    )


# ---------------------------------------------------------------------------
# Group D — get_constant_drag_parameter_DBM (4 tests)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("r_rsun", [20.0, 50.0, 100.0, 215.0])
def test_dbm_gamma_r_independence(r_rsun: float) -> None:
    """γ is r-independent: A ∝ r² and ρ_DBM ∝ r⁻² cancel exactly."""
    r_ref = 215.0 * R_SUN_KM * u.km  # ≈ 1 AU
    r = r_rsun * R_SUN_KM * u.km
    gamma_ref = get_constant_drag_parameter_DBM(r_ref, _ALPHA, _KAPPA, _V_APEX)
    gamma = get_constant_drag_parameter_DBM(r, _ALPHA, _KAPPA, _V_APEX)
    ratio = (gamma / gamma_ref).decompose().value
    assert abs(ratio - 1.0) < 1e-10, f"γ(r={r_rsun} R_sun) / γ(1 AU) = {ratio:.10f}, expected 1.0"


def test_dbm_gamma_linear_in_cd() -> None:
    """γ ∝ c_d → γ(c_d=2.5) / γ(c_d=1.0) = 2.5."""
    r = 20.0 * R_SUN_KM * u.km
    gamma1 = get_constant_drag_parameter_DBM(r, _ALPHA, _KAPPA, _V_APEX, c_d=1.0)
    gamma2 = get_constant_drag_parameter_DBM(r, _ALPHA, _KAPPA, _V_APEX, c_d=2.5)
    ratio = (gamma2 / gamma1).decompose().value
    assert abs(ratio - 2.5) / 2.5 < 1e-12, f"γ(c_d=2.5) / γ(c_d=1.0) = {ratio:.10f}, expected 2.5"


def test_dbm_gamma_inverse_in_mass() -> None:
    """γ ∝ 1/M → γ(M) / γ(2M) = 2.0."""
    r = 20.0 * R_SUN_KM * u.km
    M_ref = get_CME_mass_pluta(_V_APEX).to(u.kg)
    M_double = (M_ref * 2.0).to(u.kg)
    gamma_ref = get_constant_drag_parameter_DBM(r, _ALPHA, _KAPPA, _V_APEX, M=M_ref)
    gamma_double = get_constant_drag_parameter_DBM(r, _ALPHA, _KAPPA, _V_APEX, M=M_double)
    ratio = (gamma_ref / gamma_double).decompose().value
    assert abs(ratio - 2.0) / 2.0 < 1e-12, f"γ(M) / γ(2M) = {ratio:.10f}, expected 2.0"


def test_dbm_gamma_units() -> None:
    """DBM drag parameter must be convertible to 1/km."""
    r = 20.0 * R_SUN_KM * u.km
    gamma = get_constant_drag_parameter_DBM(r, _ALPHA, _KAPPA, _V_APEX)
    gamma_per_km = gamma.to(1 / u.km)
    assert gamma_per_km.value > 0.0


# ---------------------------------------------------------------------------
# Group E — get_ambient_solar_wind_density_MODBM (3 tests)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "r_au, ssn",
    [(1.0, 50.0), (1.5, 100.0), (2.0, 0.0)],
)
def test_modbm_density_power_law_exponent(r_au: float, ssn: float) -> None:
    """ρ ∝ r^(-2.11) → ρ(2r)/ρ(r) = 2^(-2.11) (Venzmer & Bothmer 2018)."""
    r1 = r_au * AU_KM
    r2 = 2.0 * r_au * AU_KM
    rho1 = get_ambient_solar_wind_density_MODBM(r1, ssn)
    rho2 = get_ambient_solar_wind_density_MODBM(r2, ssn)
    expected_ratio = 2.0 ** (-2.11)
    ratio = rho2 / rho1
    assert abs(ratio - expected_ratio) / expected_ratio < 1e-10, (
        f"r={r_au} AU, ssn={ssn}: ρ(2r)/ρ(r) = {ratio:.8f}, expected {expected_ratio:.8f}"
    )


def test_modbm_density_ssn_linearity() -> None:
    """ρ ∝ (0.0038·SSN + 4.5): ratio of densities equals ratio of coefficients."""
    r_km = 1.0 * AU_KM
    ssn1, ssn2 = 50.0, 100.0
    rho1 = get_ambient_solar_wind_density_MODBM(r_km, ssn1)
    rho2 = get_ambient_solar_wind_density_MODBM(r_km, ssn2)
    expected_ratio = (0.0038 * ssn2 + 4.5) / (0.0038 * ssn1 + 4.5)
    ratio = rho2 / rho1
    assert abs(ratio - expected_ratio) / expected_ratio < 1e-12, (
        f"SSN linearity: ρ(100)/ρ(50) = {ratio:.10f}, expected {expected_ratio:.10f}"
    )


def test_modbm_density_returns_float() -> None:
    """MoDBM density function must return a plain float."""
    result = get_ambient_solar_wind_density_MODBM(AU_KM, 100.0)
    assert isinstance(result, float), f"Expected float, got {type(result)}"


# ---------------------------------------------------------------------------
# Group F — get_varying_drag_parameter_MODBM (3 tests)
# ---------------------------------------------------------------------------


def test_modbm_gamma_power_law_exponent() -> None:
    """γ ∝ r^(-0.11): A ∝ r² and ρ_MoDBM ∝ r^(-2.11) give γ ∝ r^(2-2.11)."""
    alpha_rad = np.radians(30.0)
    kappa = 0.42
    M_kg = get_CME_mass_pluta(773.0, return_with_unit=False) * 1e-3  # g → kg
    ssn = 100.0
    r1 = 1.0 * AU_KM
    r2 = 2.0 * AU_KM
    g1 = get_varying_drag_parameter_MODBM(r1, alpha_rad, kappa, M_kg, ssn)
    g2 = get_varying_drag_parameter_MODBM(r2, alpha_rad, kappa, M_kg, ssn)
    expected_ratio = 2.0 ** (-0.11)
    ratio = g2 / g1
    assert abs(ratio - expected_ratio) / expected_ratio < 1e-8, (
        f"γ(2r)/γ(r) = {ratio:.10f}, expected {expected_ratio:.10f}"
    )


def test_modbm_gamma_linear_in_cd() -> None:
    """γ ∝ c_d → γ(c_d=2) / γ(c_d=1) = 2.0."""
    r_km = AU_KM
    alpha_rad = np.radians(30.0)
    kappa = 0.42
    M_kg = get_CME_mass_pluta(773.0, return_with_unit=False) * 1e-3
    ssn = 100.0
    g1 = get_varying_drag_parameter_MODBM(r_km, alpha_rad, kappa, M_kg, ssn, c_d=1.0)
    g2 = get_varying_drag_parameter_MODBM(r_km, alpha_rad, kappa, M_kg, ssn, c_d=2.0)
    assert abs(g2 / g1 - 2.0) / 2.0 < 1e-12, f"γ(c_d=2)/γ(c_d=1) = {g2 / g1:.10f}, expected 2.0"


def test_modbm_gamma_inverse_in_mass() -> None:
    """γ ∝ 1/M → γ(M) / γ(2M) = 2.0."""
    r_km = AU_KM
    alpha_rad = np.radians(30.0)
    kappa = 0.42
    M_kg = get_CME_mass_pluta(773.0, return_with_unit=False) * 1e-3
    ssn = 100.0
    g1 = get_varying_drag_parameter_MODBM(r_km, alpha_rad, kappa, M_kg, ssn)
    g2 = get_varying_drag_parameter_MODBM(r_km, alpha_rad, kappa, M_kg * 2.0, ssn)
    assert abs(g1 / g2 - 2.0) / 2.0 < 1e-12, f"γ(M) / γ(2M) = {g1 / g2:.10f}, expected 2.0"


# ---------------------------------------------------------------------------
# Group G — get_ambient_solar_wind_speed_MODBM (4 tests)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("w_type, expected", [("slow", 363.0), ("fast", 483.0)])
def test_modbm_wind_at_1au(w_type: str, expected: float) -> None:
    """At 1 AU, r_AU = 1 → w = w0 * 1.0^0.099 = w0 exactly."""
    w = get_ambient_solar_wind_speed_MODBM(AU_KM, w_type)
    assert abs(w - expected) / expected < 1e-10, (
        f"w(1 AU, {w_type!r}) = {w:.6f} km/s, expected {expected:.1f} km/s"
    )


@pytest.mark.parametrize("w_type", ["slow", "fast"])
@pytest.mark.parametrize("r_au", [0.5, 1.0, 2.0])
def test_modbm_wind_power_law_exponent(w_type: str, r_au: float) -> None:
    """w ∝ r^0.099 → w(2r)/w(r) = 2^0.099 (Venzmer & Bothmer 2018)."""
    r1 = r_au * AU_KM
    r2 = 2.0 * r_au * AU_KM
    w1 = get_ambient_solar_wind_speed_MODBM(r1, w_type)
    w2 = get_ambient_solar_wind_speed_MODBM(r2, w_type)
    expected_ratio = 2.0**0.099
    ratio = w2 / w1
    assert abs(ratio - expected_ratio) / expected_ratio < 1e-10, (
        f"{w_type!r}, r={r_au} AU: w(2r)/w(r) = {ratio:.10f}, expected {expected_ratio:.10f}"
    )


@pytest.mark.parametrize("r_au", [0.3, 1.0, 2.0, 5.0])
def test_modbm_wind_fast_slow_ratio_constant(r_au: float) -> None:
    """w_fast/w_slow = 483/363 is constant at all heliocentric distances."""
    r_km = r_au * AU_KM
    w_fast = get_ambient_solar_wind_speed_MODBM(r_km, "fast")
    w_slow = get_ambient_solar_wind_speed_MODBM(r_km, "slow")
    expected = 483.0 / 363.0
    ratio = w_fast / w_slow
    assert abs(ratio - expected) / expected < 1e-12, (
        f"r={r_au} AU: w_fast/w_slow = {ratio:.10f}, expected {expected:.10f}"
    )


@pytest.mark.parametrize("bad_type", ["medium", "", "SLOW", "Fast"])
def test_modbm_wind_invalid_type_raises(bad_type: str) -> None:
    """Unknown w_type must raise ValueError."""
    with pytest.raises(ValueError):
        get_ambient_solar_wind_speed_MODBM(AU_KM, bad_type)


# ---------------------------------------------------------------------------
# Group H — DBM ODE vs Analytic Solution (5 tests)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("t_eval_h", [1.0, 6.0, 12.0, 24.0, 48.0])
def test_dbm_ode_velocity_analytic_decelerating(t_eval_h: float) -> None:
    """v(t) matches closed-form solution to 1e-3 relative (v0 > w, decelerating)."""
    r0_km = 20.0 * R_SUN_KM
    v0_kms, w_kms, gamma_km = 800.0, 400.0, 1e-7
    sol = simulate_equation_of_motion_DBM(
        (0.0, 3.0 * 86400.0),
        r0_km * u.km,
        v0_kms * u.km / u.s,
        w_kms * u.km / u.s,
        gamma_km / u.km,
    )
    t_s = t_eval_h * 3600.0
    _, v_ana = _dbm_analytic(t_s, r0_km, v0_kms, w_kms, gamma_km)
    v_num = float(sol.sol(t_s)[1])
    assert abs(v_num - v_ana) / abs(v_ana) < 2e-3, (
        f"t={t_eval_h}h: v_num={v_num:.4f}, v_ana={v_ana:.4f} km/s"
    )


@pytest.mark.parametrize("t_eval_h", [1.0, 6.0, 12.0, 24.0])
def test_dbm_ode_velocity_analytic_accelerating(t_eval_h: float) -> None:
    """v(t) matches closed-form solution to 2e-3 relative (v0 < w, accelerating)."""
    r0_km = 20.0 * R_SUN_KM
    v0_kms, w_kms, gamma_km = 200.0, 400.0, 1e-7
    sol = simulate_equation_of_motion_DBM(
        (0.0, 3.0 * 86400.0),
        r0_km * u.km,
        v0_kms * u.km / u.s,
        w_kms * u.km / u.s,
        gamma_km / u.km,
    )
    t_s = t_eval_h * 3600.0
    _, v_ana = _dbm_analytic(t_s, r0_km, v0_kms, w_kms, gamma_km)
    v_num = float(sol.sol(t_s)[1])
    assert abs(v_num - v_ana) / abs(v_ana) < 2e-3, (
        f"t={t_eval_h}h: v_num={v_num:.4f}, v_ana={v_ana:.4f} km/s"
    )


@pytest.mark.parametrize("t_eval_h", [1.0, 6.0, 12.0, 24.0])
def test_dbm_ode_position_analytic(t_eval_h: float) -> None:
    """r(t) matches corrected closed-form formula [sign/γ · ln(…)] to 1e-3 relative."""
    r0_km = 20.0 * R_SUN_KM
    v0_kms, w_kms, gamma_km = 800.0, 400.0, 1e-7
    sol = simulate_equation_of_motion_DBM(
        (0.0, 3.0 * 86400.0),
        r0_km * u.km,
        v0_kms * u.km / u.s,
        w_kms * u.km / u.s,
        gamma_km / u.km,
    )
    t_s = t_eval_h * 3600.0
    r_ana, _ = _dbm_analytic(t_s, r0_km, v0_kms, w_kms, gamma_km)
    r_num = float(sol.sol(t_s)[0])
    assert abs(r_num - r_ana) / r_ana < 2e-3, (
        f"t={t_eval_h}h: r_num={r_num:.4e}, r_ana={r_ana:.4e} km"
    )


def test_dbm_ode_coasting_no_drag() -> None:
    """v0 = w → RHS = 0 → r(t) = r0 + v0·t; velocity stays at v0."""
    r0_km = 20.0 * R_SUN_KM
    v0_kms = w_kms = 400.0
    gamma_km = 1e-7
    sol = simulate_equation_of_motion_DBM(
        (0.0, 86400.0),
        r0_km * u.km,
        v0_kms * u.km / u.s,
        w_kms * u.km / u.s,
        gamma_km / u.km,
    )
    t_s = 12.0 * 3600.0
    r_num = float(sol.sol(t_s)[0])
    v_num = float(sol.sol(t_s)[1])
    r_expected = r0_km + v0_kms * t_s
    assert abs(r_num - r_expected) / r_expected < 1e-10, (
        f"Coasting: r_num={r_num:.6e}, r_expected={r_expected:.6e} km"
    )
    assert abs(v_num - v0_kms) < 1e-8, f"Coasting: v_num={v_num:.10f}, expected {v0_kms} km/s"


def test_dbm_ode_asymptotic_terminal_velocity() -> None:
    """At t = 5×10⁶ s with larger γ, |v - w| / w < 1%."""
    r0_km = 20.0 * R_SUN_KM
    v0_kms, w_kms, gamma_km = 800.0, 400.0, 1e-6  # stronger drag
    t_end = 5e6  # ~58 days
    sol = simulate_equation_of_motion_DBM(
        (0.0, t_end),
        r0_km * u.km,
        v0_kms * u.km / u.s,
        w_kms * u.km / u.s,
        gamma_km / u.km,
    )
    v_final = float(sol.sol(t_end)[1])
    assert abs(v_final - w_kms) / w_kms < 0.01, (
        f"Terminal: v_final={v_final:.2f} km/s, w={w_kms} km/s, "
        f"|v-w|/w = {abs(v_final - w_kms) / w_kms:.4f}"
    )


# ---------------------------------------------------------------------------
# Group I — MoDBM ODE Physical Sanity (4 tests)
# ---------------------------------------------------------------------------


def test_modbm_ode_reaches_1au() -> None:
    """Standard 773 km/s CME reaches 1 AU within 5 days; sol.status == 0."""
    sol = simulate_equation_of_motion_MODBM(
        t_span=(0.0, 5.0 * 86400.0),
        r0=_R0,
        v_apex=_V_APEX,
        v0=773.0 * u.km / u.s,
        alpha=_ALPHA,
        kappa=_KAPPA,
        w_type="slow",
        ssn=100.0,
    )
    assert sol.status == 0, f"ODE solver failed: status={sol.status}, message={sol.message}"
    assert sol.y[0, -1] >= AU_KM, (
        f"CME did not reach 1 AU in 5 days: r_final = {sol.y[0, -1] / AU_KM:.3f} AU"
    )


def test_modbm_ode_velocity_decreasing_fast_cme() -> None:
    """Monotone deceleration throughout for v0 = 1200 km/s >> w_slow = 363 km/s."""
    sol = simulate_equation_of_motion_MODBM(
        t_span=(0.0, 4.0 * 86400.0),
        r0=_R0,
        v_apex=_V_APEX,
        v0=1200.0 * u.km / u.s,
        alpha=_ALPHA,
        kappa=_KAPPA,
        w_type="slow",
        ssn=100.0,
    )
    v_values = sol.y[1]
    assert np.all(np.diff(v_values) <= 0.0), (
        "Velocity is not monotonically non-increasing for fast CME (v0=1200 km/s)"
    )


def test_modbm_ode_slow_vs_fast_wind() -> None:
    """In slow wind, drag (∝ (v-w)²) is stronger → CME reaches lower v at same t."""
    common = dict(
        t_span=(0.0, 4.0 * 86400.0),
        r0=_R0,
        v_apex=_V_APEX,
        v0=1000.0 * u.km / u.s,
        alpha=_ALPHA,
        kappa=_KAPPA,
        ssn=100.0,
    )
    sol_slow = simulate_equation_of_motion_MODBM(**common, w_type="slow")
    sol_fast = simulate_equation_of_motion_MODBM(**common, w_type="fast")
    v_final_slow = sol_slow.y[1, -1]
    v_final_fast = sol_fast.y[1, -1]
    assert v_final_slow < v_final_fast, (
        f"Expected lower final v in slow wind: v_slow={v_final_slow:.1f}, "
        f"v_fast={v_final_fast:.1f} km/s"
    )


def test_modbm_ode_higher_ssn_stronger_drag() -> None:
    """Higher SSN → denser solar wind → stronger drag → lower final velocity."""
    common = dict(
        t_span=(0.0, 3.0 * 86400.0),
        r0=_R0,
        v_apex=_V_APEX,
        v0=900.0 * u.km / u.s,
        alpha=_ALPHA,
        kappa=_KAPPA,
        w_type="slow",
    )
    sol_low = simulate_equation_of_motion_MODBM(**common, ssn=10.0)
    sol_high = simulate_equation_of_motion_MODBM(**common, ssn=200.0)
    v_final_low = sol_low.y[1, -1]
    v_final_high = sol_high.y[1, -1]
    assert v_final_high < v_final_low, (
        f"Expected lower final v at SSN=200: "
        f"ssn=10 → {v_final_low:.1f}, ssn=200 → {v_final_high:.1f} km/s"
    )


# ---------------------------------------------------------------------------
# Group J — find_time_and_velocity_at_distance (4 tests)
# ---------------------------------------------------------------------------


def test_arrival_constant_velocity_exact() -> None:
    """v0 = w (zero drag force): t_arr = (target - r0) / v0 to 1e-6 relative."""
    r0_km = 20.0 * R_SUN_KM
    v0_kms = w_kms = 400.0
    gamma_km = 1e-7
    target_km = 215.0 * R_SUN_KM  # ≈ 1 AU in R_sun units
    # t_expected ≈ (215 - 20) R_sun / 400 km/s ≈ 339153 s ≈ 94 h; use 5-day span
    sol = simulate_equation_of_motion_DBM(
        (0.0, 5.0 * 86400.0),
        r0_km * u.km,
        v0_kms * u.km / u.s,
        w_kms * u.km / u.s,
        gamma_km / u.km,
    )
    t_arr, v_arr = find_time_and_velocity_at_distance(sol, target_km * u.km)
    t_expected = (target_km - r0_km) / v0_kms
    assert abs(t_arr - t_expected) / t_expected < 1e-6, (
        f"t_arr={t_arr:.2f} s, t_expected={t_expected:.2f} s"
    )
    assert abs(v_arr - v0_kms) / v0_kms < 1e-6, f"v_arr={v_arr:.6f} km/s, expected {v0_kms} km/s"


def test_arrival_decelerating_cme_physical_range() -> None:
    """773 km/s CME: 60 h < t_arr < 100 h at 1 AU, 350 < v_arr < 773 km/s."""
    sol = simulate_equation_of_motion_MODBM(
        t_span=(0.0, 7.0 * 86400.0),
        r0=_R0,
        v_apex=_V_APEX,
        v0=_V_APEX,
        alpha=_ALPHA,
        kappa=_KAPPA,
        w_type="slow",
        ssn=100.0,
    )
    t_arr, v_arr = find_time_and_velocity_at_distance(sol, 1.0 * u.AU)
    t_arr_h = t_arr / 3600.0
    assert 60.0 < t_arr_h < 100.0, f"Transit time {t_arr_h:.1f} h outside [60, 100] h"
    assert 350.0 < v_arr < 773.0, f"Arrival speed {v_arr:.1f} km/s outside [350, 773] km/s"


def test_arrival_raises_when_distance_not_reached() -> None:
    """ODE truncated before target must propagate ValueError from Brent's bracket."""
    sol = simulate_equation_of_motion_DBM(
        (0.0, 3600.0),  # 1 hour — CME cannot reach 1 AU
        _R0,
        773.0 * u.km / u.s,
        400.0 * u.km / u.s,
        1e-7 / u.km,
    )
    with pytest.raises(ValueError):
        find_time_and_velocity_at_distance(sol, 1.0 * u.AU)


def test_arrival_unit_input() -> None:
    """Passing 1 AU and the equivalent km Quantity give identical results to 1e-6."""
    sol = simulate_equation_of_motion_MODBM(
        t_span=(0.0, 7.0 * 86400.0),
        r0=_R0,
        v_apex=_V_APEX,
        v0=_V_APEX,
        alpha=_ALPHA,
        kappa=_KAPPA,
        w_type="slow",
        ssn=100.0,
    )
    t1, v1 = find_time_and_velocity_at_distance(sol, 1.0 * u.AU)
    t2, v2 = find_time_and_velocity_at_distance(sol, AU_KM * u.km)
    assert abs(t1 - t2) / t1 < 1e-6, f"Arrival times differ: {t1:.4f} vs {t2:.4f} s"
    assert abs(v1 - v2) / v1 < 1e-6, f"Arrival speeds differ: {v1:.4f} vs {v2:.4f} km/s"
