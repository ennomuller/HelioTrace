import plotly.graph_objects as go
import pytest

from heliotrace.ui.components.gcs_plot import build_gcs_figure


def test_build_gcs_figure_with_projection_hit():
    """Test generating the GCS plot figure when the target is hit (ratio > 0)."""
    fig = build_gcs_figure(
        alpha_deg=30.0,
        kappa=0.5,
        lat_deg=10.0,
        lon_deg=-15.0,
        tilt_deg=45.0,
        target_lat_deg=0.0,
        target_lon_deg=0.0,
        projection_ratio=0.8,
        target_name="Earth",
        height=1.0,
    )

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 4

    wireframe, inside_line, outside_line, proj_marker = fig.data

    # Check that wireframe was built
    assert wireframe.mode == "lines"
    assert "x" in wireframe

    # PHYSICS: The Z-axis is aligned towards the target.
    # The inside line trace should go from Sun (z=0) to the projection point (z=0.8)
    assert list(inside_line.z) == pytest.approx([0, 0.8])
    assert list(inside_line.x) == pytest.approx([0, 0])

    # The outside line trace goes from the projection point out to the apex boundary (z=1.0)
    assert list(outside_line.z) == pytest.approx([0.8, 1.0])

    # The marker is exactly at the projection ratio point
    assert list(proj_marker.z) == pytest.approx([0.8])
    assert proj_marker.mode == "markers"


def test_build_gcs_figure_target_miss():
    """Test generating the GCS plot figure when the target misses (ratio <= 0)."""
    fig = build_gcs_figure(
        alpha_deg=30.0,
        kappa=0.5,
        lat_deg=80.0,
        lon_deg=90.0,
        tilt_deg=45.0,
        target_lat_deg=0.0,
        target_lon_deg=0.0,
        projection_ratio=-0.1,
        target_name="Earth",
        height=1.0,
    )

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2

    wireframe, miss_line = fig.data

    # PHYSICS: A miss means we don't display the split line or projection marker.
    # We display a dashed sun-to-target line spanning 0 to 1 on the Z-axis.
    assert list(miss_line.z) == pytest.approx([0, 1.0])
    assert list(miss_line.x) == pytest.approx([0, 0])
    assert miss_line.line.dash == "dash"
