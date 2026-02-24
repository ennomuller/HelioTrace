"""
Plotly propagation result charts comparing DBM vs MODBM.

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
    "DBM":    "#E07B39",   # warm orange
    "MODBM":  "#457B9D",   # cool blue
    "target": "#2A9D8F",   # teal reference line
}


def build_propagation_comparison_figure(
    results: SimulationResults,
    target_distance_au: float,
) -> go.Figure:
    """
    Build a two-panel Plotly figure comparing DBM and MODBM propagation.

    - **Left panel**: Distance from Sun [R_sun] vs. Propagation Time [h]
    - **Right panel**: Radial Velocity [km/s] vs. Propagation Time [h]

    :param results:             Completed :class:`~heliotrace.models.schemas.SimulationResults`.
    :param target_distance_au:  Target distance from the Sun [AU], for the reference line.
    :return: Plotly :class:`~plotly.graph_objects.Figure` with two subplots.
    """
    target_rsun = target_distance_au * _AU_IN_RSUN

    fig = make_subplots(
        rows=1, cols=2,
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
                hovertemplate=f"<b>{label}</b><br>t = %{{x:.1f}} h<br>r = %{{y:.0f}} R☉<extra></extra>",
            ),
            row=1, col=1,
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
                hovertemplate=f"<b>{label}</b><br>t = %{{x:.1f}} h<br>v = %{{y:.0f}} km/s<extra></extra>",
            ),
            row=1, col=2,
        )

        if elapsed_h is not None:
            fig.add_vline(
                x=elapsed_h,
                line=dict(color=color, width=1.5, dash="dash"),
                row=1, col=2,
                annotation_text=f"{label} arrival",
                annotation_position="top right",
                annotation_font_size=10,
                annotation_font_color=color,
            )

    _add_model(results.dbm_series,   results.elapsed_time_DBM_h,   "DBM",   _COLORS["DBM"])
    _add_model(results.modbm_series, results.elapsed_time_MODBM_h, "MODBM", _COLORS["MODBM"])

    fig.add_hline(
        y=target_rsun,
        line=dict(color=_COLORS["target"], width=1.5, dash="dot"),
        row=1, col=1,
        annotation_text=f"Target ({target_distance_au:.2f} AU)",
        annotation_position="bottom right",
        annotation_font_color=_COLORS["target"],
        annotation_font_size=10,
    )

    fig.update_xaxes(title_text="Propagation Time [h]", showgrid=True, gridcolor="#eee")
    fig.update_yaxes(showgrid=True, gridcolor="#eee")
    fig.update_yaxes(title_text="Distance from Sun [R☉]", row=1, col=1)
    fig.update_yaxes(title_text="Radial Velocity [km/s]",  row=1, col=2)

    fig.update_layout(
        hovermode="x unified",
        legend=dict(
            x=0.01, y=0.99,
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#ccc", borderwidth=1,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(t=40, b=50, l=60, r=20),
    )

    return fig
