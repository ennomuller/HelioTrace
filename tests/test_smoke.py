"""
Smoke tests — verify that core modules import cleanly and the physics pipeline
reproduces the reference result from the 2023-10-28 CME event.

Reference (from MEMORY.md):
    Apex velocity ≈ 773 km/s
    DBM transit time ≈ 69.4 h
"""

from __future__ import annotations

import ast
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import heliotrace

# ---------------------------------------------------------------------------
# Helper: extract a top-level function from the Streamlit page file without
# triggering module-level side effects (st.set_page_config, etc.).
# ---------------------------------------------------------------------------
_PAGE_PATH = Path(__file__).resolve().parent.parent / "pages" / "01_Propagation_Simulator.py"


def _load_page_function(func_name: str):  # noqa: ANN201
    """Extract and compile a single function from the simulator page module."""
    source = _PAGE_PATH.read_text()
    tree = ast.parse(source)
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            func_source = ast.get_source_segment(source, node)
            assert func_source is not None
            ns: dict = {}
            exec(compile(ast.parse(func_source), "<test>", "exec"), ns)  # noqa: S102
            return ns[func_name]
    raise LookupError(func_name)


# ---------------------------------------------------------------------------
# Import tests
# ---------------------------------------------------------------------------


def test_package_version() -> None:
    assert isinstance(heliotrace.__version__, str)


def test_models_importable() -> None:
    from heliotrace.models.schemas import (  # noqa: F401
        DerivedGCSParams,
        PropagationSeries,
        SimulationConfig,
        SimulationResults,
        TargetConfig,
    )


def test_physics_importable() -> None:
    from heliotrace.physics.apex_ratio import get_target_apex_ratio  # noqa: F401
    from heliotrace.physics.drag import (  # noqa: F401
        get_CME_mass_pluta,
        simulate_equation_of_motion_DBM,
        simulate_equation_of_motion_MODBM,
    )
    from heliotrace.physics.fitting import perform_linear_fit  # noqa: F401


def test_simulation_importable() -> None:
    from heliotrace.simulation.runner import derive_gcs_params, run_full_simulation  # noqa: F401


def test_page_uses_sidebar_task_states() -> None:
    source = _PAGE_PATH.read_text()
    assert "config, gcs_params, obs_df, run_clicked, task_states = render_sidebar()" in source
    assert 'gcs_params_entered = task_states["gcs"] == "ready"' in source


def test_sidebar_fill_example_uses_callback() -> None:
    sidebar_source = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "heliotrace"
        / "ui"
        / "components"
        / "sidebar_inputs.py"
    ).read_text()
    assert 't("sidebar.fill_example")' in sidebar_source
    assert "use_container_width=True" in sidebar_source
    assert "on_click=_fill_example" in sidebar_source


def test_sidebar_mass_override_uses_text_input() -> None:
    sidebar_source = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "heliotrace"
        / "ui"
        / "components"
        / "sidebar_inputs.py"
    ).read_text()
    assert "m_override_str = st.text_input(" in sidebar_source
    assert 'key="sb_mass_override"' in sidebar_source


def test_sidebar_run_button_appears_before_title() -> None:
    sidebar_source = (
        Path(__file__).resolve().parent.parent
        / "src"
        / "heliotrace"
        / "ui"
        / "components"
        / "sidebar_inputs.py"
    ).read_text()

    run_index = sidebar_source.index('with st.container(key="sidebar-run-button")')
    title_index = sidebar_source.index('st.title(t("sidebar.title"))')
    example_index = sidebar_source.index('with st.container(key="sidebar-example-button")')

    assert run_index < title_index < example_index


# ---------------------------------------------------------------------------
# Physics unit tests
# ---------------------------------------------------------------------------


def test_linear_fit_exact() -> None:
    """A perfect linear dataset should return near-zero χ² and exact slope."""
    from heliotrace.physics.fitting import perform_linear_fit

    x = np.array([0.0, 3600.0, 7200.0])
    y = np.array([10.0, 14.0, 18.0])  # slope = 4/3600 R_sun/s
    result = perform_linear_fit(x, y)

    assert abs(result["slope"] - 4.0 / 3600.0) < 1e-10
    assert abs(result["intercept"] - 10.0) < 1e-10
    assert result["chi_squared"] < 1e-20


def test_pluta_mass_formula() -> None:
    """CME mass must be positive and dimensionally consistent."""
    import astropy.units as u

    from heliotrace.physics.drag import get_CME_mass_pluta

    mass = get_CME_mass_pluta(773.0 * u.km / u.s)
    assert mass.unit == u.g
    assert mass.value > 0


def test_pluta_mass_closed_form() -> None:
    """Verify the closed-form agrees with the analytical formula log10(M)=3.4e-4*v+15.479."""
    from heliotrace.physics.drag import get_CME_mass_pluta

    v_kms = 500.0
    expected = 10.0 ** (3.4e-4 * v_kms + 15.479)
    result = get_CME_mass_pluta(v_kms, return_with_unit=False)
    assert abs(result - expected) / expected < 1e-12


# ---------------------------------------------------------------------------
# Integration smoke test — 2023-10-28 event
# ---------------------------------------------------------------------------


@pytest.fixture
def reference_gcs_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "datetime": datetime(2023, 10, 28, 14, 0),
                "lon": 5.5,
                "lat": -20.1,
                "tilt": -7.5,
                "half_angle": 30.0,
                "height": 10.0,
                "kappa": 0.42,
            },
            {
                "datetime": datetime(2023, 10, 28, 14, 30),
                "lon": 5.5,
                "lat": -20.1,
                "tilt": -7.5,
                "half_angle": 30.0,
                "height": 12.1,
                "kappa": 0.42,
            },
            {
                "datetime": datetime(2023, 10, 28, 15, 0),
                "lon": 5.5,
                "lat": -20.1,
                "tilt": -7.5,
                "half_angle": 30.0,
                "height": 14.0,
                "kappa": 0.42,
            },
        ]
    )


def test_derive_gcs_params_apex_velocity(reference_gcs_df: pd.DataFrame) -> None:
    """Apex velocity for the reference event should be close to 773 km/s."""
    from heliotrace.simulation.runner import derive_gcs_params

    derived = derive_gcs_params(reference_gcs_df, height_error=0.25)
    # Allow ±5 % tolerance — exact value depends on linear fit
    assert 700.0 < derived.v_apex_kms < 850.0, (
        f"v_apex = {derived.v_apex_kms:.1f} km/s (expected ~773)"
    )


def test_full_simulation_dbm_transit(reference_gcs_df: pd.DataFrame) -> None:
    """DBM transit time for the reference event should be close to 69.4 h."""
    from heliotrace.models.schemas import SimulationConfig, TargetConfig
    from heliotrace.simulation.runner import run_full_simulation

    config = SimulationConfig(
        event_str="Halo CME · 2023-10-28",
        target=TargetConfig(name="Earth", lon=0.0, lat=0.0, distance=1.0),
        height_error=0.25,
        w=390.0,
        w_type="slow",
        ssn=100.0,
        c_d=1.0,
        toa_raw=None,
        m_override_g=None,
    )

    results = run_full_simulation(reference_gcs_df, config)
    assert results.target_hit, "CME should hit Earth for the reference event"
    assert results.elapsed_time_DBM_h is not None
    # Allow ±10 % tolerance around the reference 69.4 h
    assert 60.0 < results.elapsed_time_DBM_h < 80.0, (
        f"DBM transit = {results.elapsed_time_DBM_h:.1f} h (expected ~69.4)"
    )


# ---------------------------------------------------------------------------
# KPI card & mini-metric HTML helpers
# ---------------------------------------------------------------------------

_kpi_card = _load_page_function("_kpi_card")
_mini_metric = _load_page_function("_mini_metric")


class TestKpiCard:
    """Tests for the _kpi_card() dashboard HTML helper."""

    def test_contains_label_and_value(self) -> None:
        html = _kpi_card("Apex Velocity", "773 km/s")
        assert "Apex Velocity" in html
        assert "773 km/s" in html

    def test_subtitle_rendered_when_provided(self) -> None:
        html = _kpi_card("Velocity", "773 km/s", subtitle="± 42 km/s")
        assert "± 42 km/s" in html
        assert "kpi-card-subtitle" in html

    def test_subtitle_absent_when_none(self) -> None:
        html = _kpi_card("Velocity", "773 km/s", subtitle=None)
        assert "kpi-card-subtitle" not in html

    def test_accent_color_applied(self) -> None:
        html = _kpi_card("Ratio", "0.85", accent_color="#2ca02c")
        assert "#2ca02c" in html

    def test_default_accent_color(self) -> None:
        html = _kpi_card("Ratio", "0.85")
        assert "#1f77b4" in html

    def test_returns_single_root_div(self) -> None:
        html = _kpi_card("Label", "Value").strip()
        assert html.startswith("<div")
        assert html.endswith("</div>")

    def test_html_class_names_present(self) -> None:
        html = _kpi_card("Label", "Value", subtitle="sub")
        assert "kpi-card" in html
        assert "kpi-card-label" in html
        assert "kpi-card-value" in html
        assert "kpi-card-subtitle" in html


class TestMiniMetric:
    """Tests for the _mini_metric() compact metric HTML helper."""

    def test_basic_label_and_value(self) -> None:
        html = _mini_metric("Transit", "69.4 h")
        assert "Transit" in html
        assert "69.4 h" in html

    def test_no_delta_when_omitted(self) -> None:
        html = _mini_metric("Transit", "69.4 h")
        # No colored delta div should appear
        assert "#2ca02c" not in html
        assert "#d62728" not in html

    def test_positive_delta_green(self) -> None:
        html = _mini_metric("Δ", "+3.2 h", delta="+3.2 h", delta_positive=True)
        assert "#2ca02c" in html
        assert "+3.2 h" in html

    def test_negative_delta_red(self) -> None:
        html = _mini_metric("Δ", "-1.5 h", delta="-1.5 h", delta_positive=False)
        assert "#d62728" in html
        assert "-1.5 h" in html
