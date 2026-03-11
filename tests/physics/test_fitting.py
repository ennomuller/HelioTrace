"""
Tests for heliotrace.physics.fitting — linear least-squares fitting.

Group A covers the single public function perform_linear_fit with analytic
benchmarks, WLS formula verification, chi-squared derivation, and scaling probes.

Analytic references:
    model:          y = m*x + b
    slope_error:    sigma / sqrt(Sxx)  where Sxx = sum((x - xbar)^2)
    chi_squared:    sum((y - model)^2 / sigma^2)   [weighted]
                    sum((y - model)^2)              [unweighted]
    WLS Sxx formula for uniform x=1..N: Sxx = N(N^2-1)/12
"""

from __future__ import annotations

import numpy as np
import pytest

from heliotrace.physics.fitting import perform_linear_fit

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_SLOPE = 2.0
_INTERCEPT = 5.0
_SIGMA = 0.2
_X_REF = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
_Y_REF = _SLOPE * _X_REF + _INTERCEPT


# ---------------------------------------------------------------------------
# Analytic helper functions
# ---------------------------------------------------------------------------


def _wls_slope_error(sigma: float, x: np.ndarray) -> float:
    """WLS closed-form slope error: sigma / sqrt(sum((x - mean(x))^2))."""
    return sigma / np.sqrt(np.sum((x - np.mean(x)) ** 2))


def _wls_slope_error_uniform(sigma: float, N: int) -> float:
    """Closed form for x = 1..N: sigma * sqrt(12 / (N*(N**2 - 1)))."""
    return sigma * np.sqrt(12.0 / (N * (N**2 - 1)))


def _linear(x: np.ndarray, m: float, b: float) -> np.ndarray:
    """Reference linear model."""
    return m * x + b


# ---------------------------------------------------------------------------
# Group A — perform_linear_fit (11 tests)
# ---------------------------------------------------------------------------


def test_perfect_linear_data_exact_params() -> None:
    """For y = 2x + 5 with no noise, recovered slope and intercept are exact to 1e-12."""
    result = perform_linear_fit(_X_REF, _Y_REF)
    assert abs(result["slope"] - _SLOPE) / _SLOPE < 1e-12, (
        f"slope: got {result['slope']:.10f}, expected {_SLOPE}"
    )
    assert abs(result["intercept"] - _INTERCEPT) / _INTERCEPT < 1e-12, (
        f"intercept: got {result['intercept']:.10f}, expected {_INTERCEPT}"
    )


@pytest.mark.parametrize("y_error", [None, 1.0, 0.5])
def test_perfect_linear_data_chi_squared_zero(y_error: float | None) -> None:
    """Perfect data → residuals identically zero → chi_squared == 0.0."""
    result = perform_linear_fit(_X_REF, _Y_REF, y_error=y_error)
    assert result["chi_squared"] == 0.0, (
        f"y_error={y_error}: chi_squared={result['chi_squared']:.3e}, expected 0.0"
    )


def test_return_type_is_dict_of_floats() -> None:
    """Return value is dict with exactly 5 keys; all values are Python float."""
    result = perform_linear_fit(_X_REF, _Y_REF)
    expected_keys = {"slope", "intercept", "slope_error", "intercept_error", "chi_squared"}
    assert set(result.keys()) == expected_keys, f"Key mismatch: got {set(result.keys())}"
    for key, val in result.items():
        assert isinstance(val, float), f"result['{key}'] is {type(val)}, expected float"


@pytest.mark.parametrize("mean_y", [0.0, 3.0, -7.5])
@pytest.mark.filterwarnings("ignore::scipy.optimize.OptimizeWarning")
def test_slope_zero_homogeneous_data(mean_y: float) -> None:
    """Constant y-data → slope ≈ 0, intercept ≈ mean(y) to within 1e-10."""
    y_const = np.full_like(_X_REF, mean_y)
    result = perform_linear_fit(_X_REF, y_const)
    assert abs(result["slope"]) < 1e-10, (
        f"mean_y={mean_y}: slope={result['slope']:.3e}, expected ~0"
    )
    assert abs(result["intercept"] - mean_y) < 1e-10, (
        f"mean_y={mean_y}: intercept={result['intercept']:.10f}, expected {mean_y}"
    )


def test_negative_slope_recovery() -> None:
    """For y = -3x + 10, slope=-3 and intercept=10 are recovered to 1e-12."""
    slope_true, intercept_true = -3.0, 10.0
    y = slope_true * _X_REF + intercept_true
    result = perform_linear_fit(_X_REF, y)
    assert abs(result["slope"] - slope_true) / abs(slope_true) < 1e-12, (
        f"slope: got {result['slope']:.10f}, expected {slope_true}"
    )
    assert abs(result["intercept"] - intercept_true) / intercept_true < 1e-12, (
        f"intercept: got {result['intercept']:.10f}, expected {intercept_true}"
    )


@pytest.mark.parametrize(
    "N, sigma",
    [(5, 0.2), (10, 1.0), (20, 0.5), (50, 2.0)],
)
def test_weighted_slope_error_closed_form(N: int, sigma: float) -> None:
    """WLS slope_error matches sigma/sqrt(Sxx) to 1e-10 relative for uniform x=1..N."""
    x = np.arange(1, N + 1, dtype=float)
    y = _SLOPE * x + _INTERCEPT  # perfect data — chi_squared = 0
    result = perform_linear_fit(x, y, y_error=sigma)
    expected = _wls_slope_error(sigma, x)
    rel_err = abs(result["slope_error"] - expected) / expected
    assert rel_err < 1e-10, (
        f"N={N}, sigma={sigma}: slope_error={result['slope_error']:.8e}, "
        f"expected {expected:.8e}, rel_err={rel_err:.3e}"
    )


def test_weighted_slope_error_monotone_decreasing() -> None:
    """For uniform x=1..N and sigma=1.0, slope_error decreases as N increases."""
    N_values = [5, 10, 20, 50, 100, 200]
    errors = []
    for N in N_values:
        x = np.arange(1, N + 1, dtype=float)
        y = _SLOPE * x + _INTERCEPT
        r = perform_linear_fit(x, y, y_error=1.0)
        errors.append(r["slope_error"])
    for i in range(len(errors) - 1):
        assert errors[i] > errors[i + 1], (
            f"slope_error not decreasing: N={N_values[i]} → {errors[i]:.6e}, "
            f"N={N_values[i + 1]} → {errors[i + 1]:.6e}"
        )


def test_chi_squared_formula_weighted() -> None:
    """Weighted chi_squared equals sum((y - model)^2 / sigma^2) using fitted params."""
    sigma = 0.2
    perturbations = np.array([0.1, -0.2, 0.15, -0.05, 0.1])
    y_noisy = _Y_REF + perturbations
    result = perform_linear_fit(_X_REF, y_noisy, y_error=sigma)
    slope_fit = result["slope"]
    intercept_fit = result["intercept"]
    residuals = (y_noisy - _linear(_X_REF, slope_fit, intercept_fit)) / sigma
    chi2_manual = float(np.sum(residuals**2))
    rel_err = abs(result["chi_squared"] - chi2_manual) / max(abs(chi2_manual), 1e-15)
    assert rel_err < 1e-10, (
        f"chi_squared={result['chi_squared']:.8e}, manual={chi2_manual:.8e}, rel_err={rel_err:.3e}"
    )


def test_array_y_error_accepted() -> None:
    """Passing a numpy array as y_error (heteroscedastic) returns dict with all 5 keys."""
    y_error_arr = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
    result = perform_linear_fit(_X_REF, _Y_REF, y_error=y_error_arr)
    expected_keys = {"slope", "intercept", "slope_error", "intercept_error", "chi_squared"}
    assert set(result.keys()) == expected_keys, f"Key mismatch: {set(result.keys())}"


def test_initial_guess_recovers_correct_params() -> None:
    """Even with a far-from-true initial guess [100, 200], fit converges to true params."""
    result = perform_linear_fit(_X_REF, _Y_REF, initial_guess=[100.0, 200.0])
    assert abs(result["slope"] - _SLOPE) / _SLOPE < 1e-12, (
        f"slope: got {result['slope']:.10f}, expected {_SLOPE}"
    )
    assert abs(result["intercept"] - _INTERCEPT) / _INTERCEPT < 1e-12, (
        f"intercept: got {result['intercept']:.10f}, expected {_INTERCEPT}"
    )


@pytest.mark.parametrize("sigma", [0.1, 1.0, 10.0])
def test_weighted_unweighted_agree_for_perfect_data(sigma: float) -> None:
    """For perfect linear data, weighted and unweighted calls return identical slope and intercept."""
    r_unweighted = perform_linear_fit(_X_REF, _Y_REF)
    r_weighted = perform_linear_fit(_X_REF, _Y_REF, y_error=sigma)
    assert abs(r_weighted["slope"] - r_unweighted["slope"]) / _SLOPE < 1e-12, (
        f"sigma={sigma}: slope mismatch: weighted={r_weighted['slope']:.10f}, "
        f"unweighted={r_unweighted['slope']:.10f}"
    )
    assert abs(r_weighted["intercept"] - r_unweighted["intercept"]) / _INTERCEPT < 1e-12, (
        f"sigma={sigma}: intercept mismatch: weighted={r_weighted['intercept']:.10f}, "
        f"unweighted={r_unweighted['intercept']:.10f}"
    )
