"""
Tests for the sidebar task-status helpers.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import pytest

from heliotrace.ui.components.sidebar_inputs import (
    _compute_task_states,
    _get_status_led,
    _normalise_obs_df,
    render_sidebar,
)


def _obs_frame(rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["datetime", "height"])


def _sources(**overrides: str) -> dict[str, str]:
    sources = {
        "event": "system_default",
        "target": "system_default",
        "gcs": "system_default",
        "ht": "system_default",
        "drag": "system_default",
    }
    sources.update(overrides)
    return sources


def _complete_obs_frame() -> pd.DataFrame:
    return _obs_frame(
        [
            {"datetime": datetime(2023, 10, 28, 14, 0), "height": 10.0},
            {"datetime": datetime(2023, 10, 28, 14, 30), "height": 12.0},
        ]
    )


def test_render_sidebar_importable() -> None:
    assert callable(render_sidebar)


@pytest.mark.parametrize(
    ("state", "expected_led"),
    [
        ("missing", ":gray[☐]"),
        ("default", ":gray[☐]"),
        ("ready", ":green[⏹]"),
    ],
)
def test_get_status_led_returns_expected_marker(state: str, expected_led: str) -> None:
    assert _get_status_led(state) == expected_led


def test_compute_task_states_marks_empty_event_as_default() -> None:
    states = _compute_task_states(
        event_str_raw="   ",
        target_choice="Earth",
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_complete_obs_frame(),
        w=420,
        w_type="slow",
        ssn=100,
        sources=_sources(),
    )

    assert states["event"] == "default"


def test_compute_task_states_marks_example_named_event_as_ready() -> None:
    states = _compute_task_states(
        event_str_raw="Halo CME · 2023-10-28",
        target_choice="Earth",
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_complete_obs_frame(),
        w=420,
        w_type="slow",
        ssn=100,
        sources=_sources(event="example"),
    )

    assert states["event"] == "ready"


def test_compute_task_states_marks_system_default_target_as_default() -> None:
    states = _compute_task_states(
        event_str_raw="Event",
        target_choice="Earth",
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_complete_obs_frame(),
        w=420,
        w_type="slow",
        ssn=100,
        sources=_sources(event="user"),
    )

    assert states["target"] == "default"


@pytest.mark.parametrize(
    ("target_choice", "source"),
    [("Earth", "example"), ("Parker Solar Probe (example)", "user"), ("Custom", "user")],
)
def test_compute_task_states_marks_example_or_custom_target_as_ready(
    target_choice: str, source: str
) -> None:
    states = _compute_task_states(
        event_str_raw="Event",
        target_choice=target_choice,
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_complete_obs_frame(),
        w=420,
        w_type="slow",
        ssn=100,
        sources=_sources(event="user", target=source),
    )

    assert states["target"] == "ready"


def test_compute_task_states_marks_incomplete_gcs_as_missing() -> None:
    states = _compute_task_states(
        event_str_raw="Event",
        target_choice="Earth",
        gcs_values=(1.0, None, 3.0, 4.0, 0.5),
        obs_df=_complete_obs_frame(),
        w=420,
        w_type="slow",
        ssn=100,
        sources=_sources(event="user"),
    )

    assert states["gcs"] == "missing"


def test_compute_task_states_marks_complete_default_gcs_as_default() -> None:
    states = _compute_task_states(
        event_str_raw="Event",
        target_choice="Earth",
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_complete_obs_frame(),
        w=420,
        w_type="slow",
        ssn=100,
        sources=_sources(event="user"),
    )

    assert states["gcs"] == "default"


def test_compute_task_states_marks_example_complete_gcs_as_ready() -> None:
    states = _compute_task_states(
        event_str_raw="Event",
        target_choice="Earth",
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_complete_obs_frame(),
        w=420,
        w_type="slow",
        ssn=100,
        sources=_sources(event="user", gcs="example"),
    )

    assert states["gcs"] == "ready"


@pytest.mark.parametrize(
    ("rows", "expected"),
    [
        ([], "missing"),
        ([{"datetime": datetime(2023, 10, 28, 14, 0), "height": 10.0}], "missing"),
        (
            [
                {"datetime": datetime(2023, 10, 28, 14, 0), "height": 10.0},
                {"datetime": datetime(2023, 10, 28, 14, 30), "height": 12.0},
            ],
            "default",
        ),
    ],
)
def test_compute_task_states_marks_ht_status_from_cleaned_observations(
    rows: list[dict[str, object]], expected: str
) -> None:
    states = _compute_task_states(
        event_str_raw="Event",
        target_choice="Earth",
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_obs_frame(rows),
        w=420,
        w_type="slow",
        ssn=100,
        sources=_sources(event="user"),
    )

    assert states["ht"] == expected


def test_compute_task_states_marks_example_ht_data_as_ready() -> None:
    states = _compute_task_states(
        event_str_raw="Event",
        target_choice="Earth",
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_complete_obs_frame(),
        w=420,
        w_type="slow",
        ssn=100,
        sources=_sources(event="user", ht="example"),
    )

    assert states["ht"] == "ready"


def test_compute_task_states_ignores_invalid_ht_rows_during_cleaning() -> None:
    states = _compute_task_states(
        event_str_raw="Event",
        target_choice="Earth",
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_obs_frame(
            [
                {"datetime": datetime(2023, 10, 28, 14, 0), "height": -1.0},
                {"datetime": None, "height": 10.0},
                {"datetime": datetime(2023, 10, 28, 14, 30), "height": 12.0},
                {"datetime": datetime(2023, 10, 28, 15, 0), "height": 14.0},
            ]
        ),
        w=420,
        w_type="slow",
        ssn=100,
        sources=_sources(event="user", ht="user"),
    )

    assert states["ht"] == "ready"


def test_normalise_obs_df_coerces_string_datetime_and_height_types() -> None:
    obs_df = _normalise_obs_df(
        pd.DataFrame(
            [
                {"datetime": "2023-10-28 14:00:00", "height": "10.5"},
                {"datetime": "invalid", "height": "bad"},
            ]
        )
    )

    assert pd.api.types.is_datetime64_any_dtype(obs_df["datetime"])
    assert pd.api.types.is_numeric_dtype(obs_df["height"])
    assert pd.isna(obs_df.loc[1, "datetime"])
    assert pd.isna(obs_df.loc[1, "height"])


def test_normalise_obs_df_resets_to_range_index() -> None:
    obs_df = _normalise_obs_df(
        pd.DataFrame(
            [{"datetime": "2023-10-28 14:00:00", "height": "10.5"}],
            index=pd.Index([7], name="row_id"),
        )
    )

    assert isinstance(obs_df.index, pd.RangeIndex)
    assert list(obs_df.index) == [0]


def test_compute_task_states_marks_default_drag_values_as_default() -> None:
    states = _compute_task_states(
        event_str_raw="Event",
        target_choice="Earth",
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_complete_obs_frame(),
        w=420,
        w_type="slow",
        ssn=100,
        sources=_sources(event="user"),
    )

    assert states["drag"] == "default"


def test_compute_task_states_marks_example_default_drag_values_as_ready() -> None:
    states = _compute_task_states(
        event_str_raw="Event",
        target_choice="Earth",
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_complete_obs_frame(),
        w=390,
        w_type="slow",
        ssn=100,
        sources=_sources(event="user", drag="example"),
    )

    assert states["drag"] == "ready"


@pytest.mark.parametrize(
    ("w", "w_type", "ssn"),
    [(400, "slow", 100), (420, "fast", 100), (420, "slow", 101)],
)
def test_compute_task_states_marks_modified_drag_values_as_ready(
    w: int, w_type: str, ssn: int
) -> None:
    states = _compute_task_states(
        event_str_raw="Event",
        target_choice="Earth",
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_complete_obs_frame(),
        w=w,
        w_type=w_type,
        ssn=ssn,
        sources=_sources(event="user", drag="user"),
    )

    assert states["drag"] == "ready"


def test_run_button_disable_rule_matches_missing_only() -> None:
    states = _compute_task_states(
        event_str_raw="Event",
        target_choice="Earth",
        gcs_values=(1.0, 2.0, 3.0, 4.0, 0.5),
        obs_df=_complete_obs_frame(),
        w=420,
        w_type="slow",
        ssn=100,
        sources=_sources(event="user"),
    )

    run_disabled = states["gcs"] == "missing" or states["ht"] == "missing"

    assert states["gcs"] == "default"
    assert states["ht"] == "default"
    assert not run_disabled
