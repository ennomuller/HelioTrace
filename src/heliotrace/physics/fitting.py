"""
Linear least-squares fitting for CME Height-Time analysis.
"""

from __future__ import annotations

import logging
from typing import Optional

import numpy as np
from numpy.typing import ArrayLike
from scipy.optimize import curve_fit

logger = logging.getLogger(__name__)


def perform_linear_fit(
    x_data: ArrayLike,
    y_data: ArrayLike,
    y_error: Optional[float | ArrayLike] = None,
    initial_guess: Optional[list[float]] = None,
) -> dict[str, float]:
    """
    Fit a linear model ``y = m * x + b`` to the provided data.

    :param x_data:        Independent variable data points.
    :param y_data:        Dependent variable data points.
    :param y_error:       Symmetric errors on ``y_data`` (scalar or array).
                          When ``None``, unweighted least-squares is used.
    :param initial_guess: Initial values for ``[slope, intercept]``.
                          Defaults to ``None`` (scipy chooses automatically).
    :return: Dictionary with keys:
             ``slope``, ``intercept``, ``slope_error``, ``intercept_error``,
             ``chi_squared`` (reduced χ²).
    """
    x_data = np.asarray(x_data, dtype=float)
    y_data = np.asarray(y_data, dtype=float)

    def _linear(x: np.ndarray, m: float, b: float) -> np.ndarray:
        return m * x + b

    if y_error is not None:
        sigma = (
            np.full_like(y_data, float(y_error))
            if np.isscalar(y_error)
            else np.asarray(y_error, dtype=float)
        )
        popt, pcov = curve_fit(
            _linear,
            x_data,
            y_data,
            sigma=sigma,
            absolute_sigma=True,
            p0=initial_guess,
        )
        residuals = (y_data - _linear(x_data, *popt)) / sigma
    else:
        popt, pcov = curve_fit(_linear, x_data, y_data, p0=initial_guess)
        residuals = y_data - _linear(x_data, *popt)

    slope, intercept = popt
    slope_error, intercept_error = np.sqrt(np.diag(pcov))
    chi_squared = float(np.sum(residuals**2))

    logger.debug(
        "Linear fit: slope=%.4e, intercept=%.4f, chi²=%.4f",
        slope,
        intercept,
        chi_squared,
    )

    return {
        "slope": float(slope),
        "intercept": float(intercept),
        "slope_error": float(slope_error),
        "intercept_error": float(intercept_error),
        "chi_squared": chi_squared,
    }
