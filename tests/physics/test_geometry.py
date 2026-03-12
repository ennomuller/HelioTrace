"""
Tests for heliotrace.physics.geometry — GCS CME mesh geometry.

Groups A–F cover all 6 public functions in geometry.py with analytic benchmarks,
exact scaling-law probes, and boundary-condition guards.

Analytic references:
    gamma = arcsin(k)
    rsl   = tan(gamma) * ||pslR||
    r_apex = k * height / (1 + k)
    distjunc = height * (1-k) * cos(alpha) / (1 + sin(alpha))
    skeleton N = (front_vertices + straight_vertices) * 2 - 3
    mesh coord: r[v] * [cos(u), sin(u)*cos(ca[v]), sin(u)*sin(ca[v])] + p[v]
"""

from __future__ import annotations

import sys
import unittest.mock as mock

import numpy as np
import pytest

from heliotrace.physics.geometry import (
    apex_radius,
    gcs_mesh,
    gcs_mesh_rotated,
    gcs_mesh_sunpy,
    rotate_mesh,
    skeleton,
)

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_ALPHA_DEG = 30.0  # reference half-angle [deg]
_ALPHA = np.radians(_ALPHA_DEG)  # [rad]
_KAPPA = 0.42  # reference aspect ratio
_HEIGHT = 1.0  # normalised height [dimensionless]
_SV = 10  # straight_vertices
_FV = 10  # front_vertices
_CV = 10  # circle_vertices

_DISTJUNC = _HEIGHT * (1 - _KAPPA) * np.cos(_ALPHA) / (1 + np.sin(_ALPHA))


# ---------------------------------------------------------------------------
# Analytic helper functions
# ---------------------------------------------------------------------------


def _skeleton_N(sv: int, fv: int) -> int:
    """N = (fv + sv) * 2 - 3 — total skeleton vertices."""
    return (fv + sv) * 2 - 3


def _distjunc(height: float, k: float, alpha: float) -> float:
    """distjunc = height * (1-k) * cos(alpha) / (1 + sin(alpha))"""
    return height * (1 - k) * np.cos(alpha) / (1 + np.sin(alpha))


def _rsl_formula(distjunc: float, sv: int, k: float) -> np.ndarray:
    """rsl[i] = tan(arcsin(k)) * linspace(0, distjunc, sv)[i]"""
    return np.tan(np.arcsin(k)) * np.linspace(0, distjunc, sv)


def _apex_radius_formula(height: float, k: float) -> float:
    """r_apex = k * height / (1 + k)"""
    return k * height / (1 + k)


# ---------------------------------------------------------------------------
# Group A — skeleton (7 tests)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(("sv", "fv"), [(5, 10), (10, 10), (10, 20), (15, 5)])
def test_skeleton_vertex_count_formula(sv: int, fv: int) -> None:
    """Total len(r) equals (fv + sv)*2 - 3 for all vertex count combinations."""
    _, r, _ = skeleton(_ALPHA, _DISTJUNC, sv, fv, _KAPPA)
    assert len(r) == _skeleton_N(sv, fv), (
        f"sv={sv}, fv={fv}: len(r)={len(r)}, expected {_skeleton_N(sv, fv)}"
    )


@pytest.mark.parametrize("k", [0.1, 0.3, 0.42, 0.7])
def test_skeleton_rsl_formula(k: float) -> None:
    """Straight-leg cross-section radii r[:sv] match tan(arcsin(k))*linspace to 1e-12."""
    distjunc = _distjunc(_HEIGHT, k, _ALPHA)
    _, r, _ = skeleton(_ALPHA, distjunc, _SV, _FV, k)
    expected = _rsl_formula(distjunc, _SV, k)
    max_err = np.max(np.abs(r[:_SV] - expected))
    assert max_err < 1e-12, f"k={k}: max rsl error={max_err:.3e}"


@pytest.mark.parametrize("alpha_deg", [15.0, 30.0, 45.0])
def test_skeleton_ca_straight_leg_constant(alpha_deg: float) -> None:
    """Cone angles for straight legs ca[:sv] are all exactly -alpha."""
    alpha = np.radians(alpha_deg)
    distjunc = _distjunc(_HEIGHT, _KAPPA, alpha)
    _, _, ca = skeleton(alpha, distjunc, _SV, _FV, _KAPPA)
    assert np.all(ca[:_SV] == -alpha), f"alpha={alpha_deg}°: ca[:sv] not constant at {-alpha_deg}°"


def test_skeleton_pslR_x_coord_zero() -> None:
    """All straight-leg axis points have p[:sv, 0] == 0.0 (skeleton lies in YZ plane)."""
    p, _, _ = skeleton(_ALPHA, _DISTJUNC, _SV, _FV, _KAPPA)
    assert np.all(p[:_SV, 0] == 0.0), f"p[:sv, 0] not zero: max={np.max(np.abs(p[:_SV, 0]))}"


@pytest.mark.parametrize("alpha_deg", [10.0, 30.0, 45.0])
def test_skeleton_pslR_last_point(alpha_deg: float) -> None:
    """Last straight-leg point p[sv-1] == [0, sin(alpha)*distjunc, cos(alpha)*distjunc]."""
    alpha = np.radians(alpha_deg)
    distjunc = 0.3  # fixed reference — formula holds for any distjunc
    p, _, _ = skeleton(alpha, distjunc, _SV, _FV, _KAPPA)
    expected = np.array([0.0, np.sin(alpha) * distjunc, np.cos(alpha) * distjunc])
    max_err = np.max(np.abs(p[_SV - 1] - expected))
    assert max_err < 1e-12, (
        f"alpha={alpha_deg}°: p[sv-1]={p[_SV - 1]}, expected={expected}, err={max_err:.3e}"
    )


def test_skeleton_k_zero_all_r_zero() -> None:
    """k=0 → arcsin(0)=0 → tan(0)=0 → all straight-leg radii are exactly zero."""
    distjunc = _distjunc(_HEIGHT, 0.0, _ALPHA)
    _, r, _ = skeleton(_ALPHA, distjunc, _SV, _FV, 0.0)
    assert np.all(r[:_SV] == 0.0), f"k=0: r[:sv] not zero, max={np.max(np.abs(r[:_SV]))}"


def test_skeleton_output_shapes() -> None:
    """p, r, ca shapes are (N, 3), (N,), (N,) where N = _skeleton_N(sv, fv)."""
    N = _skeleton_N(_SV, _FV)
    p, r, ca = skeleton(_ALPHA, _DISTJUNC, _SV, _FV, _KAPPA)
    assert p.shape == (N, 3), f"p.shape={p.shape}, expected ({N}, 3)"
    assert r.shape == (N,), f"r.shape={r.shape}, expected ({N},)"
    assert ca.shape == (N,), f"ca.shape={ca.shape}, expected ({N},)"


# ---------------------------------------------------------------------------
# Group B — gcs_mesh (7 tests)
# ---------------------------------------------------------------------------


def test_gcs_mesh_output_shapes() -> None:
    """mesh.shape == (N_skeleton * cv, 3); u and v are 1D of same length."""
    N_skel = _skeleton_N(_SV, _FV)
    N_total = N_skel * _CV
    mesh, u, v = gcs_mesh(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA)
    assert mesh.shape == (N_total, 3), f"mesh.shape={mesh.shape}, expected ({N_total}, 3)"
    assert u.ndim == 1, "u must be 1D"
    assert v.ndim == 1, "v must be 1D"
    assert u.shape == v.shape, f"u.shape={u.shape} != v.shape={v.shape}"
    assert len(u) == N_total, f"len(u)={len(u)}, expected {N_total}"


@pytest.mark.parametrize("height", [1.0, 2.0, 5.0])
def test_gcs_mesh_linear_scale(height: float) -> None:
    """gcs_mesh(alpha, 2*height) / gcs_mesh(alpha, height) == 2.0 for non-zero elements."""
    mesh_h, _, _ = gcs_mesh(_ALPHA, height, _SV, _FV, _CV, _KAPPA)
    mesh_2h, _, _ = gcs_mesh(_ALPHA, 2.0 * height, _SV, _FV, _CV, _KAPPA)
    mask = np.abs(mesh_h) > 1e-10
    ratios = mesh_2h[mask] / mesh_h[mask]
    max_err = np.max(np.abs(ratios - 2.0))
    assert max_err < 1e-12, f"height={height}: max ratio deviation={max_err:.3e}"


def test_gcs_mesh_y_centroid_zero() -> None:
    """np.mean(mesh[:, 1]) is zero — the mesh is left-right symmetric in Y."""
    mesh, _, _ = gcs_mesh(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA)
    centroid_y = np.mean(mesh[:, 1])
    assert abs(centroid_y) < 1e-14, f"Y centroid={centroid_y:.3e}, expected ~0.0"


@pytest.mark.parametrize("alpha_deg", [15.0, 30.0, 45.0])
def test_gcs_mesh_distjunc_formula(alpha_deg: float) -> None:
    """gcs_mesh uses distjunc = height*(1-k)*cos(alpha)/(1+sin(alpha)) internally."""
    alpha = np.radians(alpha_deg)
    distjunc = _distjunc(_HEIGHT, _KAPPA, alpha)

    # Build mesh from gcs_mesh (uses distjunc formula internally)
    mesh_gcs, u, v = gcs_mesh(alpha, _HEIGHT, _SV, _FV, _CV, _KAPPA)

    # Build mesh directly from skeleton with the analytic distjunc
    N_skel = _skeleton_N(_SV, _FV)
    p_dir, r_dir, ca_dir = skeleton(alpha, distjunc, _SV, _FV, _KAPPA)
    pspace = np.arange(0, N_skel)
    theta = np.linspace(0, 2 * np.pi, _CV)
    u_g, v_g = np.meshgrid(theta, pspace)
    u_g, v_g = u_g.flatten(), v_g.flatten()
    mesh_dir = (
        r_dir[v_g, np.newaxis]
        * np.array(
            [np.cos(u_g), np.sin(u_g) * np.cos(ca_dir[v_g]), np.sin(u_g) * np.sin(ca_dir[v_g])]
        ).T
        + p_dir[v_g]
    )

    max_diff = np.max(np.abs(mesh_dir - mesh_gcs))
    assert max_diff < 1e-12, f"alpha={alpha_deg}°: max mesh deviation={max_diff:.3e}"


@pytest.mark.parametrize("height", [1.0, 5.0, 10.0])
def test_gcs_mesh_max_z_approaches_height(height: float) -> None:
    """max(mesh[:,2]) / height is in [0.99, 1.0] — mesh approaches but does not exceed height."""
    mesh, _, _ = gcs_mesh(_ALPHA, height, _SV, _FV, _CV, _KAPPA)
    ratio = np.max(mesh[:, 2]) / height
    assert 0.99 <= ratio <= 1.0, f"height={height}: max_z/height={ratio:.6f}"


def test_gcs_mesh_alpha_zero_collapses_to_spine() -> None:
    """With alpha=0, distjunc=0: straight legs collapse, y-centroid remains zero."""
    mesh, _, _ = gcs_mesh(0.0, _HEIGHT, _SV, _FV, _CV, _KAPPA)
    centroid_y = np.mean(mesh[:, 1])
    assert abs(centroid_y) < 1e-14, f"Y centroid with alpha=0: {centroid_y:.3e}"
    assert np.max(mesh[:, 2]) > 0.0, "max Z must be positive — front arc must exist"


def test_gcs_mesh_u_v_parametric_coords() -> None:
    """u values lie in [0, 2*pi]; v values are non-negative integers in [0, N_skeleton-1]."""
    N_skel = _skeleton_N(_SV, _FV)
    mesh, u, v = gcs_mesh(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA)
    assert np.min(u) >= 0.0, f"u min={np.min(u)} < 0"
    assert np.max(u) <= 2 * np.pi + 1e-12, f"u max={np.max(u)} > 2*pi"
    assert np.min(v) >= 0, f"v min={np.min(v)} < 0"
    assert np.max(v) <= N_skel - 1, f"v max={np.max(v)} > N_skel-1={N_skel - 1}"


# ---------------------------------------------------------------------------
# Group C — rotate_mesh (5 tests)
# ---------------------------------------------------------------------------


def test_rotate_mesh_identity() -> None:
    """rotate_mesh(mesh, [0, 0, 0]) returns array numerically identical to input."""
    mesh, _, _ = gcs_mesh(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA)
    mesh_r = rotate_mesh(mesh, [0.0, 0.0, 0.0])
    assert np.max(np.abs(mesh_r - mesh)) == 0.0, (
        f"Identity rotation deviated: max diff={np.max(np.abs(mesh_r - mesh)):.3e}"
    )


def test_rotate_mesh_preserves_shape() -> None:
    """Output shape equals input shape."""
    mesh, _, _ = gcs_mesh(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA)
    mesh_r = rotate_mesh(mesh, [0.1, 0.2, 0.3])
    assert mesh_r.shape == mesh.shape, f"Shape changed: {mesh.shape} → {mesh_r.shape}"


@pytest.mark.parametrize(
    ("lon", "lat", "tilt"),
    [(0.1, 0.2, 0.3), (1.0, 0.5, -0.5), (np.pi / 4, np.pi / 6, 0.0)],
)
def test_rotate_mesh_preserves_point_norms(lon: float, lat: float, tilt: float) -> None:
    """Rotation is an isometry: ||rotated_point|| == ||original_point|| for all points."""
    mesh, _, _ = gcs_mesh(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA)
    mesh_r = rotate_mesh(mesh, [lon, lat, tilt])
    norms_orig = np.linalg.norm(mesh, axis=1)
    norms_rot = np.linalg.norm(mesh_r, axis=1)
    nonzero = norms_orig > 1e-12
    max_err = np.max(np.abs(norms_rot[nonzero] / norms_orig[nonzero] - 1.0))
    assert max_err < 1e-12, (
        f"lon={lon:.2f}, lat={lat:.2f}, tilt={tilt:.2f}: norm error={max_err:.3e}"
    )


def test_rotate_mesh_tilt_rotation_preserves_z() -> None:
    """Pure tilt rotation (neang=[0,0,tilt]) is a Z-axis rotation and preserves max Z."""
    mesh, _, _ = gcs_mesh(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA)
    # neang=[lon=0, lat=0, tilt=pi/2] → from_euler("zyx", [pi/2, 0, 0]) = pure Z rotation
    mesh_r = rotate_mesh(mesh, [0.0, 0.0, np.pi / 2])
    max_z_orig = np.max(mesh[:, 2])
    max_z_rot = np.max(mesh_r[:, 2])
    assert abs(max_z_rot - max_z_orig) / max_z_orig < 1e-12, (
        f"Z-axis (tilt) rotation changed max Z: {max_z_orig:.6f} → {max_z_rot:.6f}"
    )


def test_rotate_mesh_180_double_rotation_recovers_input() -> None:
    """Applying lon=pi rotation twice (total 2pi) recovers the original mesh."""
    mesh, _, _ = gcs_mesh(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA)
    mesh_r1 = rotate_mesh(mesh, [np.pi, 0.0, 0.0])
    mesh_r2 = rotate_mesh(mesh_r1, [np.pi, 0.0, 0.0])
    max_err = np.max(np.abs(mesh_r2 - mesh))
    assert max_err < 1e-12, f"Double 180° rotation error: {max_err:.3e}"


# ---------------------------------------------------------------------------
# Group D — gcs_mesh_rotated (4 tests)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("lat_deg", "lon_deg", "tilt_deg"),
    [(0, 0, 0), (10, 20, 5), (-5, 45, 30)],
)
def test_gcs_mesh_rotated_identical_to_sequential_call(
    lat_deg: float, lon_deg: float, tilt_deg: float
) -> None:
    """gcs_mesh_rotated matches rotate_mesh(gcs_mesh(...)[0], [lon, lat, tilt]) exactly."""
    lat = np.radians(lat_deg)
    lon = np.radians(lon_deg)
    tilt = np.radians(tilt_deg)
    mesh_combined, _, _ = gcs_mesh_rotated(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA, lat, lon, tilt)
    mesh_seq, _, _ = gcs_mesh(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA)
    mesh_seq = rotate_mesh(mesh_seq, [lon, lat, tilt])
    max_err = np.max(np.abs(mesh_combined - mesh_seq))
    assert max_err == 0.0, (
        f"lat={lat_deg}°, lon={lon_deg}°, tilt={tilt_deg}°: deviation={max_err:.3e}"
    )


def test_gcs_mesh_rotated_output_shapes() -> None:
    """Output (mesh, u, v) has same shapes as gcs_mesh output."""
    N_total = _skeleton_N(_SV, _FV) * _CV
    mesh_r, u_r, v_r = gcs_mesh_rotated(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA, 0.0, 0.0, 0.0)
    assert mesh_r.shape == (N_total, 3), f"mesh.shape={mesh_r.shape}, expected ({N_total}, 3)"
    assert u_r.shape == (N_total,), f"u.shape={u_r.shape}"
    assert v_r.shape == (N_total,), f"v.shape={v_r.shape}"


def test_gcs_mesh_rotated_zero_angles_identity() -> None:
    """gcs_mesh_rotated(..., lat=0, lon=0, tilt=0) returns same mesh as gcs_mesh(...)."""
    mesh_plain, _, _ = gcs_mesh(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA)
    mesh_rot, _, _ = gcs_mesh_rotated(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA, 0.0, 0.0, 0.0)
    assert np.max(np.abs(mesh_rot - mesh_plain)) == 0.0, (
        f"Zero-angle gcs_mesh_rotated deviated: {np.max(np.abs(mesh_rot - mesh_plain)):.3e}"
    )


def test_gcs_mesh_rotated_preserves_norm_distribution() -> None:
    """The sorted point-norm arrays of rotated vs unrotated mesh agree to 1e-12."""
    mesh_plain, _, _ = gcs_mesh(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA)
    mesh_rot, _, _ = gcs_mesh_rotated(_ALPHA, _HEIGHT, _SV, _FV, _CV, _KAPPA, 0.2, 0.3, 0.1)
    norms_plain = np.sort(np.linalg.norm(mesh_plain, axis=1))
    norms_rot = np.sort(np.linalg.norm(mesh_rot, axis=1))
    nonzero = norms_plain > 1e-12
    max_err = np.max(np.abs(norms_rot[nonzero] / norms_plain[nonzero] - 1.0))
    assert max_err < 1e-12, f"Norm distribution deviated after rotation: {max_err:.3e}"


# ---------------------------------------------------------------------------
# Group E — apex_radius (5 tests)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("height", "k"),
    [(1.0, 0.1), (1.0, 0.42), (1.0, 0.7), (5.0, 0.42), (10.0, 0.3)],
)
def test_apex_radius_closed_form(height: float, k: float) -> None:
    """apex_radius(h, k) == k * h / (1 + k) to 1e-12 relative."""
    result = apex_radius(height, k)
    expected = _apex_radius_formula(height, k)
    assert abs(result - expected) / expected < 1e-12, (
        f"h={height}, k={k}: got {result:.8f}, expected {expected:.8f}"
    )


@pytest.mark.parametrize(("height", "k"), [(1.0, 0.2), (3.0, 0.5), (7.0, 0.42)])
def test_apex_radius_linear_in_height(height: float, k: float) -> None:
    """apex_radius(2h, k) / apex_radius(h, k) == 2.0 exactly (linear in height)."""
    r1 = apex_radius(height, k)
    r2 = apex_radius(2.0 * height, k)
    assert r2 / r1 == 2.0, f"h={height}, k={k}: ratio={r2 / r1:.15f}, expected 2.0"


def test_apex_radius_k_zero() -> None:
    """apex_radius(height, 0.0) == 0.0 exactly (no cross-section)."""
    assert apex_radius(_HEIGHT, 0.0) == 0.0, f"k=0: got {apex_radius(_HEIGHT, 0.0)}"


@pytest.mark.parametrize("k", [0.1, 0.3, 0.5, 0.7, 0.9])
def test_apex_radius_upper_bound(k: float) -> None:
    """apex_radius(h, k) < h / 2 for all 0 < k < 1 strictly."""
    r = apex_radius(_HEIGHT, k)
    assert r < _HEIGHT / 2, f"k={k}: apex_radius={r:.6f} >= h/2={_HEIGHT / 2:.6f}"


def test_apex_radius_monotone_in_k() -> None:
    """As k increases from 0.1 to 0.9, apex_radius(1.0, k) increases monotonically."""
    k_values = [0.1, 0.2, 0.3, 0.42, 0.5, 0.7, 0.9]
    radii = [apex_radius(1.0, k) for k in k_values]
    for i in range(len(radii) - 1):
        assert radii[i] < radii[i + 1], (
            f"apex_radius({k_values[i]})={radii[i]:.6f} >= apex_radius({k_values[i + 1]})={radii[i + 1]:.6f}"
        )


# ---------------------------------------------------------------------------
# Group F — gcs_mesh_sunpy (2 tests)
# ---------------------------------------------------------------------------


def test_gcs_mesh_sunpy_import_error_message() -> None:
    """When sunpy is not importable, calling gcs_mesh_sunpy raises ImportError
    whose message contains 'heliotrace[notebooks]'."""
    patch = {
        "sunpy": None,
        "sunpy.coordinates": None,
        "sunpy.coordinates.frames": None,
    }
    with mock.patch.dict(sys.modules, patch):
        with pytest.raises(ImportError) as exc:
            gcs_mesh_sunpy(
                object(),
                _ALPHA,
                _HEIGHT,
                _SV,
                _FV,
                _CV,
                _KAPPA,
                0.0,
                0.0,
                0.0,
            )
        assert "heliotrace[notebooks]" in str(exc.value), (
            f"ImportError message does not contain 'heliotrace[notebooks]': {exc.value}"
        )


def test_gcs_mesh_sunpy_returns_skycoord_if_available() -> None:
    """When sunpy is available, gcs_mesh_sunpy returns an astropy SkyCoord instance."""
    import datetime

    from astropy.coordinates import SkyCoord

    pytest.importorskip("sunpy")
    date = datetime.datetime(2023, 10, 28, 12, 0, 0)
    result = gcs_mesh_sunpy(
        date,
        _ALPHA,
        _HEIGHT,
        _SV,
        _FV,
        _CV,
        _KAPPA,
        0.0,
        0.0,
        0.0,
    )
    assert isinstance(result, SkyCoord), f"Expected SkyCoord, got {type(result)}"
