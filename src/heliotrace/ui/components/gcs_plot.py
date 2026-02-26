"""
Plotly 3D GCS mesh visualisation with target projection indicator.

Replaces the notebook's ``plot_rotated_gcs_mesh_with_ear()`` with a fully
interactive Plotly 3D figure.

Note: triangulation uses ``scipy.spatial.Delaunay`` — no matplotlib dependency.
"""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from scipy.spatial import Delaunay

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
    res: int = 20,
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
    :param res:              Mesh resolution (rings per dimension).
    :return: Plotly :class:`~plotly.graph_objects.Figure`.
    """
    rel_lon   = float((lon_deg   - target_lon_deg) * np.pi / 180.0)
    rel_lat   = float((lat_deg   - target_lat_deg) * np.pi / 180.0)
    alpha_rad = float(alpha_deg  * np.pi / 180.0)
    tilt_rad  = float(tilt_deg   * np.pi / 180.0)

    mesh, uu, vv = gcs_mesh_rotated(
        alpha_rad, height, res, res, res, kappa, rel_lat, rel_lon, tilt_rad
    )

    # Delaunay triangulation on the parametric (u, v) plane
    tri = Delaunay(np.column_stack([uu, vv]))
    triangles = tri.simplices

    fig = go.Figure()

    # --- GCS surface (semi-transparent) ---
    fig.add_trace(
        go.Mesh3d(
            x=mesh[:, 0],
            y=mesh[:, 1],
            z=mesh[:, 2],
            i=triangles[:, 0],
            j=triangles[:, 1],
            k=triangles[:, 2],
            color="#457B9D",
            opacity=0.25,
            name="GCS mesh",
            showscale=False,
            hoverinfo="skip",
        )
    )

    # --- Wireframe (sampled for performance) ---
    step = max(1, len(triangles) // 300)
    edge_x: list[float | None] = []
    edge_y: list[float | None] = []
    edge_z: list[float | None] = []
    for tri_idx in triangles[::step]:
        for a, b in [(tri_idx[0], tri_idx[1]), (tri_idx[1], tri_idx[2]), (tri_idx[2], tri_idx[0])]:
            edge_x += [mesh[a, 0], mesh[b, 0], None]
            edge_y += [mesh[a, 1], mesh[b, 1], None]
            edge_z += [mesh[a, 2], mesh[b, 2], None]

    fig.add_trace(
        go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            mode="lines",
            line=dict(color="#1D3557", width=0.5),
            name="GCS wireframe",
            hoverinfo="skip",
        )
    )

    # --- Sun-to-Target Z-axis line ---
    if projection_ratio > 0:
        fig.add_trace(
            go.Scatter3d(
                x=[0, 0], y=[0, 0], z=[0, projection_ratio],
                mode="lines",
                line=dict(color="#A8DADC", width=4),
                name=f"Sun → {target_name} (inside CME)",
            )
        )
        fig.add_trace(
            go.Scatter3d(
                x=[0, 0], y=[0, 0], z=[projection_ratio, 1.0],
                mode="lines",
                line=dict(color="#E63946", width=4),
                name=f"Sun → {target_name} (outside CME)",
            )
        )
        fig.add_trace(
            go.Scatter3d(
                x=[0], y=[0], z=[projection_ratio],
                mode="markers",
                marker=dict(color="#E63946", size=8, symbol="circle"),
                name=f"Projection point ({target_name}): {projection_ratio:.4f}",
            )
        )
    else:
        fig.add_trace(
            go.Scatter3d(
                x=[0, 0], y=[0, 0], z=[0, 1.0],
                mode="lines",
                line=dict(color="#aaa", width=3, dash="dash"),
                name=f"{target_name} direction (MISS)",
            )
        )

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X", range=[-1.1, 1.1], showgrid=True, gridcolor="#ddd",
                       title_font=dict(size=13), tickfont=dict(size=11)),
            yaxis=dict(title="Y", range=[-1.1, 1.1], showgrid=True, gridcolor="#ddd",
                       title_font=dict(size=13), tickfont=dict(size=11)),
            zaxis=dict(title=f"Z \u2192 {target_name}", range=[0, 1.1], showgrid=True, gridcolor="#ddd",
                       title_font=dict(size=13), tickfont=dict(size=11)),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=0.5),
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.7)),
        ),
        margin=dict(t=10, b=10, l=0, r=0),
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)", bordercolor="#ccc", borderwidth=1,
                    font=dict(size=13)),
    )

    return fig
