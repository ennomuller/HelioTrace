"""
Tests for heliotrace.physics.apex_ratio — GCS geometric projection factor.

Group A covers the single public function get_target_apex_ratio with
direct-hit benchmarks, geometric miss verification, monotonicity probes,
and physical sanity guards.

Physics background:
    Rotates the GCS mesh so the Sun-Target axis aligns with Z.
    h_target / h_apex in [0, 1]; 0.0 = complete geometric miss.
    Tolerance band: |x| <= 0.01 and |y| <= 0.01 for Z-axis mask.
    Operationally relevant threshold: ratio >= 0.3 (Möstl et al. 2017).
"""

from __future__ import annotations

import astropy.units as u
import pytest

from heliotrace.physics.apex_ratio import get_target_apex_ratio

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_ALPHA = 30.0 * u.deg
_KAPPA = 0.42
_TILT = 0.0 * u.deg
_CME_LAT = 0.0 * u.deg
_CME_LON = 0.0 * u.deg
_RES = 200


# ---------------------------------------------------------------------------
# Group A — get_target_apex_ratio (11 tests)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("cme_lat_deg", "cme_lon_deg"),
    [(0, 0), (10, 20), (-5, 15)],
)
def test_direct_hit_ratio_near_unity(cme_lat_deg: float, cme_lon_deg: float) -> None:
    """target == CME position → ratio >= 0.99 (limited only by mesh discretization)."""
    cme_lat = cme_lat_deg * u.deg
    cme_lon = cme_lon_deg * u.deg
    ratio = get_target_apex_ratio(
        _ALPHA,
        _KAPPA,
        cme_lat,
        cme_lon,
        _TILT,
        target_lat=cme_lat,
        target_lon=cme_lon,
        res=_RES,
    )
    assert ratio >= 0.99, (
        f"cme=({cme_lat_deg}°,{cme_lon_deg}°): direct-hit ratio={ratio:.6f}, expected >= 0.99"
    )


@pytest.mark.parametrize(
    ("alpha_deg", "kappa"),
    [(15, 0.2), (30, 0.42), (45, 0.6)],
)
def test_direct_hit_ratio_bounded(alpha_deg: float, kappa: float) -> None:
    """Return value is always in [0.99, 1] for a direct (on-axis) hit."""
    alpha = alpha_deg * u.deg
    ratio = get_target_apex_ratio(
        alpha,
        kappa,
        _CME_LAT,
        _CME_LON,
        _TILT,
        target_lat=_CME_LAT,
        target_lon=_CME_LON,
        res=_RES,
    )
    assert 0.99 <= ratio <= 1.0, (
        f"alpha={alpha_deg}°, kappa={kappa}: ratio={ratio:.6f} outside [0.99, 1]"
    )


@pytest.mark.parametrize("sep_deg", [150, 180])
def test_geometric_miss_large_longitude_separation(sep_deg: float) -> None:
    """Longitude separation >= 150° gives ratio == 0.0 (confirmed geometric miss)."""
    ratio = get_target_apex_ratio(
        _ALPHA,
        _KAPPA,
        _CME_LAT,
        _CME_LON,
        _TILT,
        target_lat=_CME_LAT,
        target_lon=sep_deg * u.deg,
        res=_RES,
    )
    assert ratio == 0.0, f"lon_sep={sep_deg}°: ratio={ratio:.6f}, expected 0.0"


@pytest.mark.parametrize("sep_deg", [120, 150])
def test_geometric_miss_large_latitude_separation(sep_deg: float) -> None:
    """Latitude separation >= 120° gives ratio == 0.0 (confirmed geometric miss)."""
    ratio = get_target_apex_ratio(
        _ALPHA,
        _KAPPA,
        _CME_LAT,
        _CME_LON,
        _TILT,
        target_lat=sep_deg * u.deg,
        target_lon=_CME_LON,
        res=_RES,
    )
    assert ratio == 0.0, f"lat_sep={sep_deg}°: ratio={ratio:.6f}, expected 0.0"


@pytest.mark.parametrize("sep_deg", [0, 90, 150])
def test_return_type_is_float(sep_deg: float) -> None:
    """get_target_apex_ratio always returns a Python float."""
    ratio = get_target_apex_ratio(
        _ALPHA,
        _KAPPA,
        _CME_LAT,
        _CME_LON,
        _TILT,
        target_lat=_CME_LAT,
        target_lon=sep_deg * u.deg,
        res=_RES,
    )
    assert isinstance(ratio, float), f"sep={sep_deg}°: got {type(ratio)}, expected float"


def test_ratio_monotone_decrease_with_longitude_offset() -> None:
    """As longitude offset increases from 0° to 30°, ratio decreases monotonically."""
    offsets_deg = [0, 5, 10, 15, 20, 25, 30]
    ratios = [
        get_target_apex_ratio(
            _ALPHA,
            _KAPPA,
            _CME_LAT,
            _CME_LON,
            _TILT,
            target_lat=_CME_LAT,
            target_lon=off * u.deg,
            res=_RES,
        )
        for off in offsets_deg
    ]
    for i in range(len(ratios) - 1):
        assert ratios[i] >= ratios[i + 1], (
            f"ratio not monotone at offset {offsets_deg[i]}°→{offsets_deg[i + 1]}°: "
            f"{ratios[i]:.6f} < {ratios[i + 1]:.6f}"
        )


def test_ratio_monotone_decrease_with_latitude_offset() -> None:
    """As latitude offset increases from 0° to 30°, ratio decreases monotonically."""
    offsets_deg = [0, 5, 10, 15, 20, 25, 30]
    ratios = [
        get_target_apex_ratio(
            _ALPHA,
            _KAPPA,
            _CME_LAT,
            _CME_LON,
            _TILT,
            target_lat=off * u.deg,
            target_lon=_CME_LON,
            res=_RES,
        )
        for off in offsets_deg
    ]
    for i in range(len(ratios) - 1):
        assert ratios[i] >= ratios[i + 1], (
            f"ratio not monotone at offset {offsets_deg[i]}°→{offsets_deg[i + 1]}°: "
            f"{ratios[i]:.6f} < {ratios[i + 1]:.6f}"
        )


@pytest.mark.parametrize("sep_deg", [15, 25])
def test_wider_cme_catches_more_off_axis(sep_deg: float) -> None:
    """For a fixed off-axis angle, a wider CME (alpha=40°) has a higher ratio than narrow (alpha=10°)."""
    ratio_narrow = get_target_apex_ratio(
        10.0 * u.deg,
        _KAPPA,
        _CME_LAT,
        _CME_LON,
        _TILT,
        target_lat=_CME_LAT,
        target_lon=sep_deg * u.deg,
        res=_RES,
    )
    ratio_wide = get_target_apex_ratio(
        40.0 * u.deg,
        _KAPPA,
        _CME_LAT,
        _CME_LON,
        _TILT,
        target_lat=_CME_LAT,
        target_lon=sep_deg * u.deg,
        res=_RES,
    )
    assert ratio_wide > ratio_narrow, (
        f"sep={sep_deg}°: wide ratio={ratio_wide:.6f} <= narrow ratio={ratio_narrow:.6f}"
    )


@pytest.mark.parametrize("tilt_deg", [0, 45, 90, 135])
def test_tilt_does_not_affect_on_axis_hit(tilt_deg: float) -> None:
    """Tilt angle does not change the ratio for a direct on-axis hit to within 1e-3."""
    ratio_ref = get_target_apex_ratio(
        _ALPHA,
        _KAPPA,
        _CME_LAT,
        _CME_LON,
        0.0 * u.deg,
        target_lat=_CME_LAT,
        target_lon=_CME_LON,
        res=_RES,
    )
    ratio_tilted = get_target_apex_ratio(
        _ALPHA,
        _KAPPA,
        _CME_LAT,
        _CME_LON,
        tilt_deg * u.deg,
        target_lat=_CME_LAT,
        target_lon=_CME_LON,
        res=_RES,
    )
    assert abs(ratio_tilted - ratio_ref) < 1e-3, (
        f"tilt={tilt_deg}°: ratio={ratio_tilted:.6f} vs ref={ratio_ref:.6f}"
    )


@pytest.mark.parametrize(
    ("sep_deg", "expected_above_threshold"),
    [(30, True), (50, True), (150, False)],
)
def test_operationally_relevant_threshold(sep_deg: float, expected_above_threshold: bool) -> None:
    """Documents the 0.3 operational threshold (Möstl et al. 2017): 30° and 50° hits pass it."""
    ratio = get_target_apex_ratio(
        _ALPHA,
        _KAPPA,
        _CME_LAT,
        _CME_LON,
        _TILT,
        target_lat=_CME_LAT,
        target_lon=sep_deg * u.deg,
        res=_RES,
    )
    if expected_above_threshold:
        assert ratio >= 0.3, f"sep={sep_deg}°: ratio={ratio:.6f} < 0.3 operational threshold"
    else:
        assert ratio == 0.0, (
            f"sep={sep_deg}°: ratio={ratio:.6f}, expected complete geometric miss (0.0)"
        )


def test_relative_lon_lat_computed_correctly() -> None:
    """Shifting both CME and target by same absolute offset preserves the ratio."""
    ratio1 = get_target_apex_ratio(
        _ALPHA,
        _KAPPA,
        cme_lat=0.0 * u.deg,
        cme_lon=0.0 * u.deg,
        tilt=_TILT,
        target_lat=0.0 * u.deg,
        target_lon=10.0 * u.deg,
        res=_RES,
    )
    ratio2 = get_target_apex_ratio(
        _ALPHA,
        _KAPPA,
        cme_lat=45.0 * u.deg,
        cme_lon=30.0 * u.deg,
        tilt=_TILT,
        target_lat=45.0 * u.deg,
        target_lon=40.0 * u.deg,
        res=_RES,
    )
    assert abs(ratio1 - ratio2) < 1e-10, (
        f"Relative offset not preserved: ratio1={ratio1:.10f}, ratio2={ratio2:.10f}"
    )
