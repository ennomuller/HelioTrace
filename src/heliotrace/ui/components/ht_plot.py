"""
Plotly Height-Time diagram with linear fit and velocity annotation.
"""

from __future__ import annotations

from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go

from heliotrace.i18n import t


def build_ht_figure(
    df: pd.DataFrame,
    height_error: float,
    slope: float,
    intercept: float,
    chi_squared: float,
    v_apex_kms: float,
    v_apex_error_kms: float,
    event_label: str = "",
) -> go.Figure:
    """
    Build a Plotly Height-Time figure with error bars and a linear fit line.

    :param df:               Sorted GCS DataFrame with ``datetime`` and ``height`` columns.
    :param height_error:     ± measurement uncertainty [R_sun] (constant for all points).
    :param slope:            Fit slope [R_sun / s].
    :param intercept:        Fit intercept [R_sun].
    :param chi_squared:      Reduced χ² of the fit.
    :param v_apex_kms:       Derived apex velocity [km / s].
    :param v_apex_error_kms: 1σ uncertainty on ``v_apex_kms`` [km / s].
    :return: Plotly :class:`~plotly.graph_objects.Figure`.
    """
    df = df.sort_values("datetime").reset_index(drop=True)
    t_ref = df["datetime"].iloc[0]

    t_min = df["datetime"].min() - timedelta(minutes=20)
    t_max = df["datetime"].max() + timedelta(minutes=20)
    t_range = pd.date_range(t_min, t_max, periods=200)
    t_sec = (t_range - t_ref).total_seconds().to_numpy()
    fit_heights = slope * t_sec + intercept

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["datetime"],
            y=df["height"],
            mode="markers",
            name=t("plot.ht.gcs_heights"),
            error_y=dict(type="constant", value=height_error, visible=True, thickness=1.5, width=5),
            marker=dict(color="#d62728", size=9, symbol="circle"),
            hovertemplate="<b>%{x|%Y-%m-%d %H:%M}</b><br>Height: %{y:.2f} R<sub>☉</sub><extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=t_range,
            y=fit_heights,
            mode="lines",
            name=t("plot.ht.linear_fit").format(chi=chi_squared),
            line=dict(color="#1f77b4", width=2),
            hovertemplate="Fit: %{y:.2f} R<sub>☉</sub><extra></extra>",
        )
    )

    fig.add_annotation(
        text=f"<b>v = ({v_apex_kms:.0f} ± {v_apex_error_kms:.0f}) km/s</b>",
        xref="paper",
        yref="paper",
        x=0.98,
        y=0.06,
        showarrow=False,
        align="right",
        bgcolor="white",
        bordercolor="#888",
        borderwidth=1,
        font=dict(size=15, color="#1f77b4"),
    )

    fig.update_layout(
        xaxis_title=t("plot.ht.xaxis"),
        yaxis_title=t("plot.ht.yaxis"),
        xaxis_title_font=dict(size=14),
        yaxis_title_font=dict(size=14),
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#ccc",
            borderwidth=1,
            font=dict(size=13),
        ),
        hovermode="x unified",
        margin=dict(t=30, b=60, l=60, r=20),
        height=480,
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    fig.update_xaxes(
        showgrid=True, gridcolor="#eee", tickformat="%d-%m\n%H:%M", tickfont=dict(size=12)
    )
    fig.update_yaxes(showgrid=True, gridcolor="#eee", tickfont=dict(size=12))

    # if event_label:
    #     fig.update_layout(title=dict(text=event_label, x=0.5))

    return fig
