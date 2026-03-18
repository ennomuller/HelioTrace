"""
Plotly 3D GCS mesh visualisation with target projection indicator.

Replaces the notebook's ``plot_rotated_gcs_mesh_with_ear()`` with a fully
interactive Plotly 3D figure using a grid wireframe.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from heliotrace.i18n import t
from heliotrace.physics.geometry import gcs_mesh_rotated


def build_gcs_figure(
    alpha_deg: float,
    kappa: float,
    lat_deg: float,
    lon_deg: float,
    tilt_deg: float,
    target_lat_deg: float,
    target_lon_deg: float,
    projection_ratio: float,
    target_name: str = "Target",
    height: float = 1.0,
) -> go.Figure:
    """
    Build an interactive Plotly 3D figure of the GCS mesh with projection indicator.

    The coordinate system is target-centric: the Z-axis points toward the target,
    so the projection point always appears at ``z = projection_ratio`` on the Z-axis.

    :param alpha_deg:        CME half-angle [deg].
    :param kappa:            GCS aspect ratio κ.
    :param lat_deg:          CME Stonyhurst latitude [deg].
    :param lon_deg:          CME Stonyhurst longitude [deg].
    :param tilt_deg:         CME tilt angle [deg].
    :param target_lat_deg:   Target latitude [deg].
    :param target_lon_deg:   Target longitude [deg].
    :param projection_ratio: Precomputed target/apex height ratio.
    :param target_name:      Display name for the target.
    :param height:           Scale factor (apex = 1 for display purposes).
    :return: Plotly :class:`~plotly.graph_objects.Figure`.
    """
    rel_lon = float((lon_deg - target_lon_deg) * np.pi / 180.0)
    rel_lat = float((lat_deg - target_lat_deg) * np.pi / 180.0)
    alpha_rad = float(alpha_deg * np.pi / 180.0)
    tilt_rad = float(tilt_deg * np.pi / 180.0)

    _straight = 20
    _front = 20
    _circle = 20

    mesh, _u, _v = gcs_mesh_rotated(
        alpha_rad, height, _straight, _front, _circle, kappa, rel_lat, rel_lon, tilt_rad
    )

    # Reshape into (n_rings, circle_vertices, 3) grid
    n_rings = mesh.shape[0] // _circle
    grid = mesh.reshape(n_rings, _circle, 3)

    # Build wireframe: rings + longitudinal spines, None-separated segments
    wx: list[float | None] = []
    wy: list[float | None] = []
    wz: list[float | None] = []

    # Rings (close each ring by appending first point)
    for i in range(n_rings):
        ring = grid[i]  # (circle_vertices, 3)
        wx += list(ring[:, 0]) + [ring[0, 0], None]
        wy += list(ring[:, 1]) + [ring[0, 1], None]
        wz += list(ring[:, 2]) + [ring[0, 2], None]

    # Longitudinal spines
    for j in range(_circle):
        spine = grid[:, j]  # (n_rings, 3)
        wx += list(spine[:, 0]) + [None]
        wy += list(spine[:, 1]) + [None]
        wz += list(spine[:, 2]) + [None]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(
            x=wx,
            y=wy,
            z=wz,
            mode="lines",
            line=dict(color="#1f77b4", width=1),  # tab10 blue
            name=t("plot.gcs.wireframe"),
            hoverinfo="skip",
        )
    )

    # --- Sun-to-Target Z-axis line ---
    if projection_ratio > 0:
        fig.add_trace(
            go.Scatter3d(
                x=[0, 0],
                y=[0, 0],
                z=[0, projection_ratio],
                mode="lines",
                line=dict(color="#ff7f0e", width=5),  # tab10 green
                name=t("plot.gcs.sun_to_target_inside").format(target=target_name),
            )
        )
        fig.add_trace(
            go.Scatter3d(
                x=[0, 0],
                y=[0, 0],
                z=[projection_ratio, 1.0],
                mode="lines",
                line=dict(color="#d62728", width=5),  # tab10 red
                name=t("plot.gcs.sun_to_target_outside").format(target=target_name),
            )
        )
        fig.add_trace(
            go.Scatter3d(
                x=[0],
                y=[0],
                z=[projection_ratio],
                mode="markers",
                marker=dict(color="#d62728", size=8, symbol="circle"),  # tab10 red
                name=t("plot.gcs.proj_point").format(target=target_name, ratio=projection_ratio),
            )
        )
    else:
        fig.add_trace(
            go.Scatter3d(
                x=[0, 0],
                y=[0, 0],
                z=[0, 1.0],
                mode="lines",
                line=dict(color="#7f7f7f", width=3, dash="dash"),  # tab10 gray
                name=t("plot.gcs.target_miss").format(target=target_name),
            )
        )

    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title="X",
                range=[-1.1, 1.1],
                showgrid=True,
                gridcolor="#ddd",
                title_font=dict(size=13),
                tickfont=dict(size=11),
            ),
            yaxis=dict(
                title="Y",
                range=[-1.1, 1.1],
                showgrid=True,
                gridcolor="#ddd",
                title_font=dict(size=13),
                tickfont=dict(size=11),
            ),
            zaxis=dict(
                title=t("plot.gcs.zaxis").format(target=target_name),
                range=[0, 1.1],
                showgrid=True,
                gridcolor="#ddd",
                title_font=dict(size=13),
                tickfont=dict(size=11),
            ),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=0.5),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.7)),
        ),
        margin=dict(t=10, b=10, l=0, r=0),
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#ccc",
            borderwidth=1,
            font=dict(size=13),
        ),
    )

    return fig
