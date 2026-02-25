"""
GCS (Graduated Cylindrical Shell) mesh geometry.

.. rubric:: Third-party attribution

A substantial portion of this module — specifically :func:`skeleton` and
:func:`gcs_mesh`, as well as the rotation helpers derived from them — is
adapted from the **gcs_python** library by **Johan von Forstner**:

    https://github.com/johan12345/gcs_python

gcs_python is itself a Python port of the original IDL reference implementations
by Andreas Thernisien:

- ``shellskeleton.pro``  — axis/skeleton of the GCS shell
- ``cmecloud.pro``       — full point cloud (mesh surface)

If you use this code in academic work, please cite the original GCS model paper:

    Thernisien, A. F. R., Howard, R. A., & Vourlidas, A. (2006).
    *Modeling of Flux Rope Coronal Mass Ejections.*
    ApJ, 652, 763. https://doi.org/10.1086/508254

All public functions use plain NumPy arrays.  ``gcs_mesh_sunpy`` is a
notebook-only convenience wrapper and requires the optional ``sunpy`` package.
"""
from __future__ import annotations

import logging

import numpy as np
from numpy import pi, sin, cos, tan, arcsin, sqrt
from numpy.linalg import norm
from scipy.spatial.transform import Rotation

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# GCS axis skeleton
# ---------------------------------------------------------------------------

def skeleton(
    alpha: float,
    distjunc: float,
    straight_vertices: int,
    front_vertices: int,
    k: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute the parametric axis (skeleton) of the GCS CME model.

    .. note::
        **Adapted from gcs_python** (Johan von Forstner, MIT License):
        https://github.com/johan12345/gcs_python
        Which is a Python port of the IDL routine ``shellskeleton.pro``
        (Andreas Thernisien).

    Based on the IDL reference: ``shellskeleton.pro``.

    :param alpha:             CME half-angle [rad].
    :param distjunc:          Junction distance — height of the straight legs [length units].
    :param straight_vertices: Number of vertices along each straight leg.
    :param front_vertices:    Number of vertices along the circular front.
    :param k:                 GCS aspect ratio κ (dimensionless).
    :return: Tuple ``(p, r, ca)`` — axis points, cross-section radii, and cone angles.
    """
    gamma = arcsin(k)

    pslR = np.outer(
        np.linspace(0, distjunc, straight_vertices),
        np.array([0.0, sin(alpha), cos(alpha)]),
    )
    pslL = np.outer(
        np.linspace(0, distjunc, straight_vertices),
        np.array([0.0, -sin(alpha), cos(alpha)]),
    )
    rsl  = tan(gamma) * norm(pslR, axis=1)
    casl = np.full(straight_vertices, -alpha)

    beta = np.linspace(-alpha, pi / 2, front_vertices)
    hf   = distjunc
    h    = hf / cos(alpha)
    rho  = hf * tan(alpha)

    X0 = (rho + h * k ** 2 * sin(beta)) / (1 - k ** 2)
    rc = sqrt((h ** 2 * k ** 2 - rho ** 2) / (1 - k ** 2) + X0 ** 2)
    cac = beta

    pcR = np.array([np.zeros(beta.shape), X0 * cos(beta), h + X0 * sin(beta)]).T
    pcL = np.array([np.zeros(beta.shape), -X0 * cos(beta), h + X0 * sin(beta)]).T

    r  = np.concatenate((rsl, rc[1:], np.flipud(rc)[1:], np.flipud(rsl)[1:]))
    ca = np.concatenate((casl, cac[1:], pi - np.flipud(cac)[1:], pi - np.flipud(casl)[1:]))
    p  = np.concatenate((pslR, pcR[1:], np.flipud(pcL)[1:], np.flipud(pslL)[1:]))

    return p, r, ca


# ---------------------------------------------------------------------------
# GCS mesh
# ---------------------------------------------------------------------------

def gcs_mesh(
    alpha: float,
    height: float,
    straight_vertices: int,
    front_vertices: int,
    circle_vertices: int,
    k: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build the full GCS point cloud from the skeleton.

    .. note::
        **Adapted from gcs_python** (Johan von Forstner, MIT License):
        https://github.com/johan12345/gcs_python
        Which is a Python port of the IDL routine ``cmecloud.pro``
        (Andreas Thernisien).

    Based on the IDL reference: ``cmecloud.pro``.

    The returned mesh is in Heliographic Stonyhurst coordinates (before rotation):
    - Z-axis: Sun–Earth line projected onto the solar equatorial plane.
    - Y-axis: solar north pole.
    - Origin: centre of the Sun.

    :param alpha:             CME half-angle [rad].
    :param height:            CME front height [length units, e.g. R_sun].
    :param straight_vertices: Vertices along each straight leg.
    :param front_vertices:    Vertices along the circular front.
    :param circle_vertices:   Vertices along each cross-section ring.
    :param k:                 GCS aspect ratio κ.
    :return: Tuple ``(mesh, u, v)`` — ``(N, 3)`` mesh array and the flattened
             parametric coordinates used for triangulation.
    """
    distjunc = height * (1 - k) * cos(alpha) / (1.0 + sin(alpha))
    p, r, ca = skeleton(alpha, distjunc, straight_vertices, front_vertices, k)

    theta = np.linspace(0, 2 * pi, circle_vertices)
    pspace = np.arange(0, (front_vertices + straight_vertices) * 2 - 3)
    u, v = np.meshgrid(theta, pspace)
    u, v = u.flatten(), v.flatten()

    mesh = (
        r[v, np.newaxis]
        * np.array([cos(u), sin(u) * cos(ca[v]), sin(u) * sin(ca[v])]).T
        + p[v]
    )

    return mesh, u, v


# ---------------------------------------------------------------------------
# Rotation
# ---------------------------------------------------------------------------

def rotate_mesh(mesh: np.ndarray, neang: list[float] | np.ndarray) -> np.ndarray:
    """
    Rotate the GCS mesh into the correct heliographic orientation.

    :param mesh:  ``(N, 3)`` mesh array from :func:`gcs_mesh`.
    :param neang: ``[longitude, latitude, tilt]`` Euler angles [rad].
    :return: Rotated ``(N, 3)`` mesh array.
    """
    return Rotation.from_euler("zyx", [neang[2], neang[1], neang[0]]).apply(mesh)


def gcs_mesh_rotated(
    alpha: float,
    height: float,
    straight_vertices: int,
    front_vertices: int,
    circle_vertices: int,
    k: float,
    lat: float,
    lon: float,
    tilt: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Build and rotate the GCS mesh in one call.

    Convenience wrapper combining :func:`gcs_mesh` and :func:`rotate_mesh`.

    :param alpha:             CME half-angle [rad].
    :param height:            CME front height [length units].
    :param straight_vertices: Vertices along each straight leg.
    :param front_vertices:    Vertices along the circular front.
    :param circle_vertices:   Vertices along each cross-section ring.
    :param k:                 GCS aspect ratio κ.
    :param lat:               CME latitude [rad].
    :param lon:               CME longitude [rad] (0 = Earth-directed).
    :param tilt:              CME tilt angle [rad].
    :return: Tuple ``(mesh, u, v)`` — rotated mesh and parametric coordinates.
    """
    mesh, u, v = gcs_mesh(alpha, height, straight_vertices, front_vertices, circle_vertices, k)
    mesh = rotate_mesh(mesh, [lon, lat, tilt])
    return mesh, u, v


# ---------------------------------------------------------------------------
# Derived quantities
# ---------------------------------------------------------------------------

def apex_radius(height: float, k: float) -> float:
    """
    Cross-section radius of the flux rope at the apex.

    :param height: CME apex height [length units].
    :param k:      GCS aspect ratio κ.
    :return: Apex cross-section radius in the same length units as ``height``.
    """
    return k * height / (1 + k)


# ---------------------------------------------------------------------------
# Notebook-only: SunPy SkyCoord output (requires optional sunpy dep)
# ---------------------------------------------------------------------------

def gcs_mesh_sunpy(
    date: object,
    alpha: float,
    height: float,
    straight_vertices: int,
    front_vertices: int,
    circle_vertices: int,
    k: float,
    lat: float,
    lon: float,
    tilt: float,
) -> object:
    """
    Return the GCS mesh as a SunPy ``SkyCoord`` (notebook use only).

    Requires the optional ``sunpy`` package::

        pip install heliotrace[notebooks]

    :param date: Observation datetime (Python ``datetime`` instance).
    :param alpha: CME half-angle [rad].
    :param height: CME front height [R_sun].
    :param straight_vertices: Vertices along each straight leg.
    :param front_vertices: Vertices along the circular front.
    :param circle_vertices: Vertices along each cross-section ring.
    :param k: GCS aspect ratio κ.
    :param lat: CME latitude [rad].
    :param lon: CME longitude [rad].
    :param tilt: CME tilt angle [rad].
    :return: SunPy ``SkyCoord`` in ``HeliographicStonyhurst`` frame.
    """
    try:
        from astropy.coordinates import SkyCoord
        from sunpy.coordinates import frames, sun  # noqa: F401 — checked at call time
    except ImportError as exc:
        raise ImportError(
            "gcs_mesh_sunpy requires sunpy. "
            "Install it with: pip install heliotrace[notebooks]"
        ) from exc

    mesh, _u, _v = gcs_mesh_rotated(
        alpha, height, straight_vertices, front_vertices, circle_vertices, k, lat, lon, tilt
    )
    m = mesh.T[[2, 1, 0], :] * sun.constants.radius
    m[1, :] *= -1
    mesh_coord = SkyCoord(
        *m,
        frame=frames.HeliographicStonyhurst,
        obstime=date,
        representation_type="cartesian",
    )
    return mesh_coord
