"""
Plotly propagation result charts comparing DBM vs MoDBM.

Two side-by-side panels: Distance vs. Time and Velocity vs. Time.
"""

from __future__ import annotations

from typing import Optional

import astropy.units as u
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from heliotrace.models.schemas import PropagationSeries, SimulationResults

_AU_IN_RSUN: float = float((1 * u.AU).to(u.R_sun).value)

_COLORS: dict[str, str] = {
    "DBM": "#1f77b4",  # tab10 blue
    "MODBM": "#ff7f0e",  # tab10 orange
    "target": "#2ca02c",  # tab10 green — reference line
    "arrival": "#d62728",  # tab10 red — arrival marker
}

# Public alias so the page module can import colours for per-model figures
PLOT_COLORS = _COLORS


def build_single_model_figure(
    series: PropagationSeries,
    elapsed_h: Optional[float],
    target_distance_au: float,
    label: str,
    color: str,
    height_px: int = 420,
) -> go.Figure:
    """
    Build a compact dual-y-axis figure for one model.

    Left axis:  Distance from Sun [R☉] vs. Propagation Time [h].
    Right axis: Radial Velocity [km/s] vs. Propagation Time [h].

    :param series:              Pre-sampled :class:`~heliotrace.models.schemas.PropagationSeries`.
    :param elapsed_h:           Arrival time [h]; draws a vertical dashed line when set.
    :param target_distance_au:  Target distance [AU] for the horizontal reference line.
    :param label:               Model name used in hover tooltips.
    :param color:               Line colour (hex string).
    :param height_px:           Figure height in pixels.
    :return: Plotly :class:`~plotly.graph_objects.Figure`.
    """
    from plotly.subplots import make_subplots as _make_subplots

    target_rsun = target_distance_au * _AU_IN_RSUN

    fig = _make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=series.t_hours,
            y=series.r_rsun,
            mode="lines",
            name=f"Distance [R\u2609] ({label})",
            line=dict(color=color, width=2.5),
            hovertemplate=f"t = %{{x:.1f}} h<br>r = %{{y:.0f}} R\u2609<extra>{label}</extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=series.t_hours,
            y=series.v_kms,
            mode="lines",
            name=f"Velocity [km/s] ({label})",
            line=dict(color=color, width=2, dash="dash"),
            hovertemplate=f"t = %{{x:.1f}} h<br>v = %{{y:.0f}} km/s<extra>{label}</extra>",
        ),
        secondary_y=True,
    )

    # Target reference line — annotation centered above the line
    fig.add_hline(
        y=target_rsun,
        line=dict(color=_COLORS["target"], width=1.5, dash="dot"),
    )
    fig.add_annotation(
        xref="paper",
        yref="y",
        x=0.5,
        y=target_rsun,
        text=f"Target ({target_distance_au:.2f} AU)",
        showarrow=False,
        xanchor="center",
        yanchor="bottom",
        font=dict(size=12, color=_COLORS["target"]),
        bgcolor="rgba(255,255,255,0.7)",
    )

    if elapsed_h is not None:
        fig.add_vline(
            x=elapsed_h,
            line=dict(color=_COLORS["arrival"], width=1.5, dash="dash"),
            annotation_text=f"Arrival {elapsed_h:.1f} h",
            annotation_position="top left",
            annotation_font_size=12,
            annotation_font_color=_COLORS["arrival"],
            annotation_yshift=8,
        )

    _ax = dict(showgrid=True, gridcolor="#eee", title_font=dict(size=13), tickfont=dict(size=11))
    fig.update_xaxes(title_text="Propagation Time [h]", **_ax)
    fig.update_yaxes(title_text="Distance from Sun [R\u2609]", secondary_y=False, **_ax)
    fig.update_yaxes(
        title_text="Radial Velocity [km/s]",
        secondary_y=True,
        showgrid=False,
        title_font=dict(size=13),
        tickfont=dict(size=11),
    )

    fig.update_layout(
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            orientation="h",
            x=0.5,
            y=1.02,
            xanchor="center",
            yanchor="bottom",
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#ccc",
            borderwidth=1,
            font=dict(size=11),
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=50, b=30, l=60, r=60),
        height=height_px,
    )
    return fig


def build_propagation_comparison_figure(
    results: SimulationResults,
    target_distance_au: float,
) -> go.Figure:
    """
    Build a two-panel Plotly figure comparing DBM and MoDBM propagation.

    - **Left panel**: Distance from Sun [R_sun] vs. Propagation Time [h]
    - **Right panel**: Radial Velocity [km/s] vs. Propagation Time [h]

    :param results:             Completed :class:`~heliotrace.models.schemas.SimulationResults`.
    :param target_distance_au:  Target distance from the Sun [AU], for the reference line.
    :return: Plotly :class:`~plotly.graph_objects.Figure` with two subplots.
    """
    target_rsun = target_distance_au * _AU_IN_RSUN

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Distance vs. Time", "Velocity vs. Time"),
        shared_xaxes=False,
        horizontal_spacing=0.10,
    )

    def _add_model(
        series: Optional[PropagationSeries],
        elapsed_h: Optional[float],
        label: str,
        color: str,
    ) -> None:
        if series is None:
            return

        fig.add_trace(
            go.Scatter(
                x=series.t_hours,
                y=series.r_rsun,
                mode="lines",
                name=label,
                line=dict(color=color, width=2.5),
                legendgroup=label,
                hovertemplate=(
                    f"<b>{label}</b><br>t = %{{x:.1f}} h<br>r = %{{y:.0f}} R☉<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=series.t_hours,
                y=series.v_kms,
                mode="lines",
                name=label,
                line=dict(color=color, width=2.5),
                legendgroup=label,
                showlegend=False,
                hovertemplate=(
                    f"<b>{label}</b><br>t = %{{x:.1f}} h<br>v = %{{y:.0f}} km/s<extra></extra>"
                ),
            ),
            row=1,
            col=2,
        )

    _add_model(results.dbm_series, results.elapsed_time_DBM_h, "DBM", _COLORS["DBM"])
    _add_model(results.modbm_series, results.elapsed_time_MODBM_h, "MoDBM", _COLORS["MODBM"])

    # Target reference line in distance panel — annotation centered above the line
    # Col 1 occupies paper x ≈ [0, 0.45]; center ≈ 0.225 with horizontal_spacing=0.10
    fig.add_hline(
        y=target_rsun,
        line=dict(color=_COLORS["target"], width=1.5, dash="dot"),
        row=1,
        col=1,
    )
    fig.add_annotation(
        xref="paper",
        yref="y",
        x=0.225,
        y=target_rsun,
        text=f"Target ({target_distance_au:.2f} AU)",
        showarrow=False,
        xanchor="center",
        yanchor="bottom",
        font=dict(size=13, color=_COLORS["target"]),
        bgcolor="rgba(255,255,255,0.7)",
    )

    # Smart arrival annotations: earlier model → label left, later model → label right
    dbm_t = results.elapsed_time_DBM_h
    modbm_t = results.elapsed_time_MODBM_h

    if dbm_t is not None:
        dbm_pos = "top left" if (modbm_t is None or dbm_t <= modbm_t) else "top right"
        fig.add_vline(
            x=dbm_t, line=dict(color=_COLORS["DBM"], width=1.5, dash="dash"), row=1, col=1
        )
        fig.add_vline(
            x=dbm_t,
            line=dict(color=_COLORS["DBM"], width=1.5, dash="dash"),
            row=1,
            col=2,
            annotation_text="DBM arrival",
            annotation_position=dbm_pos,
            annotation_font_size=13,
            annotation_font_color=_COLORS["DBM"],
        )

    if modbm_t is not None:
        modbm_pos = "top right" if (dbm_t is None or dbm_t <= modbm_t) else "top left"
        fig.add_vline(
            x=modbm_t, line=dict(color=_COLORS["MODBM"], width=1.5, dash="dash"), row=1, col=1
        )
        fig.add_vline(
            x=modbm_t,
            line=dict(color=_COLORS["MODBM"], width=1.5, dash="dash"),
            row=1,
            col=2,
            annotation_text="MoDBM arrival",
            annotation_position=modbm_pos,
            annotation_font_size=13,
            annotation_font_color=_COLORS["MODBM"],
        )

    _ax = dict(showgrid=True, gridcolor="#eee", title_font=dict(size=13), tickfont=dict(size=12))
    fig.update_xaxes(title_text="Propagation Time [h]", **_ax)
    fig.update_yaxes(showgrid=True, gridcolor="#eee", tickfont=dict(size=12))
    fig.update_yaxes(
        title_text="Distance from Sun [R\u2609]", title_font=dict(size=13), row=1, col=1
    )
    fig.update_yaxes(title_text="Radial Velocity [km/s]", title_font=dict(size=13), row=1, col=2)

    fig.update_layout(
        hovermode="x unified",
        legend=dict(
            orientation="h",
            x=0.5,
            y=1.05,
            xanchor="center",
            yanchor="bottom",
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#ccc",
            borderwidth=1,
            font=dict(size=13),
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=70, b=50, l=60, r=20),
    )

    return fig
