"""
Drag-Based Model (DBM) and Modified DBM (MODBM) physics engine.

References
----------
- Vršnak et al. (2013) — DBM formulation
- Leblanc et al. (1998) — DBM solar wind density profile
- Venzmer & Bothmer (2018) — MODBM solar wind density and speed profiles
- Pluta (2018) — CME mass / cross-section empirical formulae
- Cargill (2004) — drag coefficient convergence
"""
from __future__ import annotations

import logging
from typing import Optional

import astropy.units as u
import numpy as np
from astropy.constants import m_p
from scipy.integrate import solve_ivp, OdeSolution
from scipy.interpolate import interp1d
from scipy.optimize import root_scalar

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# CME mass and cross-section (Pluta 2018)
# ---------------------------------------------------------------------------

def get_CME_mass_pluta(
    v_apex: u.Quantity | float,
    return_with_unit: bool = True,
) -> u.Quantity | float:
    """
    Estimate CME mass from the Pluta (2018) empirical formula.

    The formula is: ``log10(M [g]) = 3.4e-4 * v [km/s] + 15.479``
    This is solved analytically as a closed-form expression (no symbolic algebra).

    :param v_apex:           CME apex speed [length / time Quantity, or plain km/s float].
    :param return_with_unit: When ``True`` (default) return an Astropy ``Quantity`` in grams.
    :return: CME mass [g] as a Quantity or plain float.
    """
    v_kms = v_apex.to(u.km / u.s).value if isinstance(v_apex, u.Quantity) else float(v_apex)
    mass_g = 10.0 ** (3.4e-4 * v_kms + 15.479)
    logger.debug("Pluta CME mass: %.3e g  (v_apex = %.1f km/s)", mass_g, v_kms)
    return mass_g * u.g if return_with_unit else mass_g


def get_CME_cross_section_pluta(
    r: u.Quantity | float,
    alpha: u.Quantity | float,
    kappa: float,
    return_with_unit: bool = True,
) -> u.Quantity | float:
    """
    Estimate the GCS cross-sectional area of a CME (Pluta 2018).

    :param r:               Radial distance from the Sun [length Quantity or km].
    :param alpha:           CME half-angle [angle Quantity or rad].
    :param kappa:           GCS aspect ratio κ (dimensionless).
    :param return_with_unit: When ``True`` return an Astropy ``Quantity`` in km².
    :return: Cross-section area [km²] as a Quantity or plain float.
    """
    r_km    = r.to(u.km).value     if isinstance(r,     u.Quantity) else float(r)
    a_rad   = alpha.to(u.rad).value if isinstance(alpha, u.Quantity) else float(alpha)

    r_c = r_km / (1.0 + kappa)
    area = np.pi * np.tan(a_rad) * np.tan(np.arcsin(kappa)) * r_c ** 2

    return area * u.km ** 2 if return_with_unit else float(area)


# ---------------------------------------------------------------------------
# DBM ambient conditions (Leblanc et al. 1998)
# ---------------------------------------------------------------------------

def get_ambient_solar_wind_density_DBM(r: u.Quantity) -> u.Quantity:
    """
    Radial solar wind density profile for the standard DBM (Leblanc 1998).

    :param r: Radial distance from the Sun [length Quantity].
    :return: Mass density [kg / cm³].
    """
    r_rsun = r.to(u.R_sun).value
    n_init = 3.3e5 * u.cm ** (-3)
    rho_w  = m_p * n_init / r_rsun ** 2
    return rho_w


def get_constant_drag_parameter_DBM(
    r: u.Quantity,
    alpha: u.Quantity,
    kappa: float,
    v_apex: u.Quantity,
    M: Optional[u.Quantity] = None,
    c_d: float = 1.0,
) -> u.Quantity:
    """
    Constant drag parameter γ for the standard DBM.

    :param r:      Radial distance from the Sun [length Quantity].
    :param alpha:  CME half-angle [angle Quantity].
    :param kappa:  GCS aspect ratio κ.
    :param v_apex: CME apex velocity [length / time Quantity].
    :param M:      CME mass [mass Quantity].  ``None`` → computed via Pluta formula.
    :param c_d:    Drag coefficient (dimensionless).  Converges to ~1 beyond ~12 R☉.
    :return: Drag parameter γ [1 / km].
    """
    if M is None:
        M = get_CME_mass_pluta(v_apex).to(u.kg)
    else:
        M = M.to(u.kg)

    rho_w = get_ambient_solar_wind_density_DBM(r)
    A     = get_CME_cross_section_pluta(r, alpha, kappa)
    gamma = (c_d * A * rho_w / M).to(1 / u.km)
    logger.debug("DBM drag parameter γ = %.4e 1/km", gamma.value)
    return gamma


# ---------------------------------------------------------------------------
# DBM ODE and integrator
# ---------------------------------------------------------------------------

def _dr_dt_DBM(t: float, S: list[float], w: float, gamma: float) -> list[float]:
    """Two-equation DBM system of ODEs (plain floats for scipy)."""
    r, v = S
    return [v, -gamma * (v - w) * abs(v - w)]


def simulate_equation_of_motion_DBM(
    t_span: tuple[float, float],
    r0: u.Quantity,
    v0: u.Quantity,
    w: u.Quantity,
    gamma: u.Quantity,
) -> OdeSolution:
    """
    Integrate the DBM equation of motion.

    :param t_span: Integration window ``(t_start, t_end)`` [s].
    :param r0:     Initial CME distance from Sun [length Quantity].
    :param v0:     Initial CME speed toward target [length / time Quantity].
    :param w:      Constant ambient solar wind speed [length / time Quantity].
    :param gamma:  Drag parameter γ [1 / length Quantity].
    :return: ``scipy.integrate.solve_ivp`` solution with ``dense_output=True``.
    """
    r0_km    = r0.to(u.km).value
    v0_kms   = v0.to(u.km / u.s).value
    w_kms    = w.to(u.km / u.s).value
    gamma_km = gamma.to(1 / u.km).value

    logger.debug(
        "DBM ODE: r0=%.2f km, v0=%.1f km/s, w=%.1f km/s, γ=%.4e 1/km",
        r0_km, v0_kms, w_kms, gamma_km,
    )
    return solve_ivp(
        _dr_dt_DBM,
        t_span,
        [r0_km, v0_kms],
        args=(w_kms, gamma_km),
        dense_output=True,
    )


# ---------------------------------------------------------------------------
# MODBM ambient conditions (Venzmer & Bothmer 2018)
# ---------------------------------------------------------------------------

def get_ambient_solar_wind_density_MODBM(r_km: float, ssn: float) -> float:
    """
    Position-dependent solar wind density for the MODBM (Venzmer & Bothmer 2018).

    :param r_km: Radial distance from the Sun [km].
    :param ssn:  Monthly smoothed sunspot number (dimensionless).
    :return: Mass density [kg / km³].
    """
    r_au  = r_km * u.km.to(u.AU)
    rho_w = (
        m_p.value
        * (0.0038 * ssn + 4.5)
        * (u.cm ** (-3)).to(u.km ** (-3))
        * r_au ** (-2.11)
    )
    return float(rho_w)


def get_varying_drag_parameter_MODBM(
    r_km: float,
    alpha_rad: float,
    kappa: float,
    M_kg: float,
    ssn: float,
    c_d: float = 1.0,
) -> float:
    """
    Position-dependent drag parameter γ(r) for the MODBM.

    All arguments are plain floats (required by ``scipy.integrate.solve_ivp``).

    :param r_km:      Radial distance [km].
    :param alpha_rad: CME half-angle [rad].
    :param kappa:     GCS aspect ratio κ.
    :param M_kg:      CME mass [kg].
    :param ssn:       Monthly smoothed sunspot number.
    :param c_d:       Drag coefficient.
    :return: Drag parameter γ [1 / km].
    """
    rho_w = get_ambient_solar_wind_density_MODBM(r_km, ssn)
    A_km2 = get_CME_cross_section_pluta(r_km, alpha_rad, kappa, return_with_unit=False)
    return float(c_d * A_km2 * rho_w / M_kg)


def get_ambient_solar_wind_speed_MODBM(r_km: float, w_type: str) -> float:
    """
    Radially varying solar wind speed for the MODBM (Venzmer & Bothmer 2018).

    :param r_km:   Radial distance [km].
    :param w_type: Wind regime — ``'slow'`` (363 km/s at 1 AU) or ``'fast'`` (483 km/s).
    :return: Solar wind speed [km/s].
    :raises ValueError: If ``w_type`` is not ``'slow'`` or ``'fast'``.
    """
    if w_type == "slow":
        w0 = 363.0
    elif w_type == "fast":
        w0 = 483.0
    else:
        raise ValueError(f"Unknown w_type: {w_type!r} — expected 'slow' or 'fast'.")
    return float(w0 * (r_km * u.km.to(u.AU)) ** 0.099)


# ---------------------------------------------------------------------------
# MODBM ODE and integrator
# ---------------------------------------------------------------------------

def _dr_dt_MODBM(
    t: float,
    S: list[float],
    M_kg: float,
    alpha_rad: float,
    kappa: float,
    w_type: str,
    ssn: float,
    c_d: float,
) -> list[float]:
    """Two-equation MODBM system of ODEs (plain floats for scipy)."""
    r, v = S
    gamma = get_varying_drag_parameter_MODBM(r, alpha_rad, kappa, M_kg, ssn, c_d)
    w     = get_ambient_solar_wind_speed_MODBM(r, w_type)
    return [v, -gamma * (v - w) * abs(v - w)]


def simulate_equation_of_motion_MODBM(
    t_span: tuple[float, float],
    r0: u.Quantity,
    v_apex: u.Quantity,
    v0: u.Quantity,
    alpha: u.Quantity,
    kappa: float,
    w_type: str,
    ssn: float,
    M: Optional[u.Quantity] = None,
    c_d: float = 1.0,
) -> OdeSolution:
    """
    Integrate the MODBM equation of motion.

    :param t_span:  Integration window ``(t_start, t_end)`` [s].
    :param r0:      Initial CME distance [length Quantity].
    :param v_apex:  CME apex speed near the Sun [length / time Quantity].
                    Used to compute the Pluta mass if ``M`` is not supplied.
    :param v0:      Initial CME speed toward target [length / time Quantity].
    :param alpha:   CME half-angle [angle Quantity].
    :param kappa:   GCS aspect ratio κ.
    :param w_type:  Wind regime — ``'slow'`` or ``'fast'``.
    :param ssn:     Monthly smoothed sunspot number.
    :param M:       CME mass [mass Quantity].  ``None`` → Pluta formula.
    :param c_d:     Drag coefficient.
    :return: ``scipy.integrate.solve_ivp`` solution with ``dense_output=True``.
    """
    if M is None:
        M = get_CME_mass_pluta(v_apex)

    r0_km      = r0.to(u.km).value
    v0_kms     = v0.to(u.km / u.s).value
    alpha_rad  = alpha.to(u.rad).value
    M_kg       = M.to(u.kg).value

    logger.debug(
        "MODBM ODE: r0=%.2f km, v0=%.1f km/s, w_type=%s, ssn=%.0f",
        r0_km, v0_kms, w_type, ssn,
    )
    return solve_ivp(
        _dr_dt_MODBM,
        t_span,
        [r0_km, v0_kms],
        args=(M_kg, alpha_rad, kappa, w_type, ssn, c_d),
        dense_output=True,
    )


# ---------------------------------------------------------------------------
# Arrival extraction
# ---------------------------------------------------------------------------

def find_time_and_velocity_at_distance(
    sol: OdeSolution,
    distance: u.Quantity,
) -> tuple[float, float]:
    """
    Interpolate the ODE solution to find the transit time and impact speed.

    Uses cubic interpolation then Brent's root-finding method to locate
    the precise crossing of ``distance``.

    :param sol:      ODE solution object (requires ``dense_output=True``).
    :param distance: Target distance from the Sun [length Quantity].
    :return: Tuple ``(elapsed_seconds, impact_speed_kms)``.
    :raises ValueError: If the solution never reaches ``distance`` within the
                        integration window.
    """
    r_interp = interp1d(sol.t, sol.y[0], kind="cubic")
    v_interp = interp1d(sol.t, sol.y[1], kind="cubic")
    d_km     = distance.to(u.km).value

    result = root_scalar(
        lambda t: r_interp(t) - d_km,
        bracket=[sol.t[0], sol.t[-1]],
        method="brentq",
    )

    if not result.converged:
        raise ValueError(
            f"Root-finding did not converge when looking for distance = {distance}."
        )

    t_arr = float(result.root)
    v_arr = float(v_interp(t_arr))
    logger.info(
        "Arrival at %.3f AU: t = %.2f h, v = %.1f km/s",
        float(distance.to(u.AU).value),
        t_arr / 3600.0,
        v_arr,
    )
    return t_arr, v_arr
