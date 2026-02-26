"""
Geometric projection factor for the CME-to-target height ratio.

The Target-to-Apex Height Ratio (also called the Geometric Projection Factor)
quantifies the radial extent of the GCS mesh along the Sun–Target line of sight.
A return value of 0.0 indicates the CME misses the target entirely.
"""
from __future__ import annotations

import logging

import astropy.units as u
import numpy as np

from heliotrace.physics.geometry import gcs_mesh_rotated

logger = logging.getLogger(__name__)


def get_target_apex_ratio(
    alpha: u.Quantity,
    kappa: float,
    cme_lat: u.Quantity,
    cme_lon: u.Quantity,
    tilt: u.Quantity,
    target_lat: u.Quantity,
    target_lon: u.Quantity,
    res: int = 500,
) -> float:
    """
    Calculate the Target-to-Apex Height Ratio (Geometric Projection Factor).

    Rotates the coordinate system so the target lies on the Z-axis, then
    measures the maximum Z-extent of the GCS mesh along that axis.

    :param alpha:       CME half-angle [angle Quantity].
    :param kappa:       GCS aspect ratio κ (dimensionless).
    :param cme_lat:     CME source latitude [angle Quantity].
    :param cme_lon:     CME source longitude [angle Quantity].
    :param tilt:        CME tilt angle [angle Quantity].
    :param target_lat:  Target latitude [angle Quantity].
    :param target_lon:  Target longitude [angle Quantity].
    :param res:         Mesh resolution (vertices per ring).  Default 500.
    :return: Ratio ``h_target / h_apex`` in ``[0, 1]``.
             A value of **0.0** means the GCS mesh never intersects the Sun–target axis
             (geometric miss). A value > 0 but < 0.3 indicates a marginal grazing
             encounter where the target is near the outer edge of the CME sheath;
             physically, at such low ratios the sheath density and magnetic field
             strength at the target are too negligible for a meaningful in-situ
             signature. A threshold of **≥ 0.3** (i.e. the target is reached at
             at least 30 % of the apex height) is adopted as the minimum condition
             for a operationally relevant CME hit, consistent with the ‘half-width
             at half-maximum’ convention used in GCS-based hit/miss studies
             (e.g. Möstl et al. 2017, *Space Weather*).
    """
    alpha_rad    = float(alpha.to(u.rad).value)
    tilt_rad     = float(tilt.to(u.rad).value)
    relative_lon = float((cme_lon - target_lon).to(u.rad).value)
    relative_lat = float((cme_lat - target_lat).to(u.rad).value)

    mesh, _, _ = gcs_mesh_rotated(
        alpha_rad, 1.0, res, res, res, kappa, relative_lat, relative_lon, tilt_rad
    )

    # Narrow mask along the Z-axis (Sun–Target line); ε-tolerance for discrete mesh
    z_axis_mask = (np.abs(mesh[:, 0]) <= 0.01) & (np.abs(mesh[:, 1]) <= 0.01)

    if np.any(z_axis_mask):
        ratio = float(np.max(mesh[z_axis_mask, 2]))
        logger.debug("Projection ratio for target (%s): %.4f", target_lon, ratio)
        return ratio

    logger.info(
        "CME misses target at lon=%.1f°, lat=%.1f° — projection ratio = 0.0",
        float(target_lon.to(u.deg).value),
        float(target_lat.to(u.deg).value),
    )
    return 0.0
