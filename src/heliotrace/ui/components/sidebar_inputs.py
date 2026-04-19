"""
Sidebar input panel for HelioTrace.

Renders all user-controllable parameters and returns a
``(SimulationConfig, GCSParams, obs_df, run_clicked, task_states)`` tuple.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

import pandas as pd
import streamlit as st

from heliotrace.config import DEFAULT_OBS_ROWS, TARGET_PRESETS
from heliotrace.i18n import t
from heliotrace.models.schemas import GCSParams, SimulationConfig, TargetConfig

TaskStatus = Literal["missing", "default", "ready"]
TaskStates = dict[str, TaskStatus]
TaskSource = Literal["system_default", "example", "user"]

# ---------------------------------------------------------------------------
# Example event: 2023-10-28 Halloween CME
# ---------------------------------------------------------------------------
_EXAMPLE: dict = {
    "sb_event_str": "Halo CME · 2023-10-28",
    "sb_gcs_lon": "5.5",
    "sb_gcs_lat": "-20.1",
    "sb_gcs_tilt": "-7.5",
    "sb_gcs_half_angle": "30.0",
    "sb_gcs_kappa": "0.42",
    "sb_w": 390,
    "sb_w_type": "slow",
    "sb_ssn": 100,
    "sb_toa_raw": "31/10/2023 14:00:00",
}

_EMPTY_OBS_DF = pd.DataFrame(
    {"datetime": pd.Series(dtype="object"), "height": pd.Series(dtype=float)}
)
_TASK_ORDER: tuple[str, ...] = ("event", "target", "gcs", "ht", "drag")
_SOURCE_KEYS: dict[str, str] = {
    "event": "sb_event_source",
    "target": "sb_target_source",
    "gcs": "sb_gcs_source",
    "ht": "sb_ht_source",
    "drag": "sb_drag_source",
}
_GCS_FALLBACKS = {
    "lon_deg": 0.0,
    "lat_deg": 0.0,
    "tilt_deg": 0.0,
    "half_angle_deg": 25.0,
    "kappa": 0.25,
}

_SIDEBAR_LAYOUT_CSS = """
<style>
section[data-testid="stSidebar"] .st-key-sidebar-example-button,
section[data-testid="stSidebar"] .st-key-sidebar-run-button,
section[data-testid="stSidebar"] .st-key-sidebar-status {
    margin-bottom: 0.5rem;
}

section[data-testid="stSidebar"] .st-key-sidebar-example-button button {
    width: 100% !important;
    justify-content: center;
    background-color: #3572f0 !important;
    border-color: #2551d4 !important;
    color: white !important;
}

section[data-testid="stSidebar"] .st-key-sidebar-example-button button:hover {
    background-color: #4a82ff !important;
    border-color: #1f47c2 !important;
    color: white !important;
}

section[data-testid="stSidebar"] .st-key-sidebar-sections [data-testid="stExpander"] {
    margin-top: 0;
    margin-bottom: 0.5rem;
}

</style>
"""


def _parse_float(text: str | None, default: float | None = None) -> float | None:
    """Parse a text-input string to float; returns ``default`` on empty or invalid input."""
    if not text or not text.strip():
        return default
    try:
        return float(text.strip())
    except ValueError:
        return default


def _get_status_led(state: TaskStatus) -> str:
    """Return the visual LED marker for a task status."""
    if state in {"missing", "default"}:
        return ":gray[☐]"
    return ":green[⏹]"


def _mark_section_source(section: str, source: TaskSource = "user") -> None:
    """Mark the provenance for a sidebar section."""
    st.session_state[_SOURCE_KEYS[section]] = source


def _get_section_source(section: str) -> TaskSource:
    """Return the stored provenance for a sidebar section."""
    return st.session_state.get(_SOURCE_KEYS[section], "system_default")


def _format_section_title(label: str, state: TaskStatus) -> str:
    """Return a compact expander title with trailing status marker."""
    return f"{label} · {_get_status_led(state)}"


def _init_sidebar_state() -> None:
    """Ensure all sidebar widget keys exist before top-down status evaluation."""
    preset_names = list(TARGET_PRESETS.keys())
    defaults: dict[str, object] = {
        "sb_event_str": "",
        "sb_target_body": preset_names[0],
        "sb_target_name": "Custom",
        "sb_target_lon": 0.0,
        "sb_target_lat": 0.0,
        "sb_target_dist": 1.0,
        "sb_gcs_lon": "",
        "sb_gcs_lat": "",
        "sb_gcs_tilt": "",
        "sb_gcs_half_angle": "",
        "sb_gcs_kappa": "",
        "sb_height_error": "0.25",
        "sb_w": 420,
        "sb_w_type": "slow",
        "sb_ssn": 100,
        "sb_c_d": "1.0",
        "sb_toa_raw": "",
        "sb_mass_override": "",
        "sb_v0_override": "",
        "sb_editor_counter": 0,
        "_obs_counter_applied": 0,
        "sb_event_source": "system_default",
        "sb_target_source": "system_default",
        "sb_gcs_source": "system_default",
        "sb_ht_source": "system_default",
        "sb_drag_source": "system_default",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _fill_example() -> None:
    """Populate session state with the 2023-10-28 example event and trigger a rerun."""
    for key, val in _EXAMPLE.items():
        st.session_state[key] = val
    st.session_state["sb_target_body"] = "Earth"
    st.session_state["sb_target_name"] = "Custom"
    st.session_state["sb_target_lon"] = 0.0
    st.session_state["sb_target_lat"] = 0.0
    st.session_state["sb_target_dist"] = 1.0
    st.session_state["sb_editor_counter"] = st.session_state.get("sb_editor_counter", 0) + 1
    for section in _TASK_ORDER:
        _mark_section_source(section, "example")
    st.session_state.pop("sb_obs_data", None)
    st.rerun()


def _clean_observations(obs_df: pd.DataFrame) -> pd.DataFrame:
    """Return only observations that can participate in the H-T fit."""
    if obs_df.empty:
        return _EMPTY_OBS_DF.copy()
    return (
        obs_df.dropna(subset=["datetime", "height"])
        .loc[lambda df: df["height"] > 0]
        .reset_index(drop=True)
    )


def _normalise_obs_df(obs_df: pd.DataFrame) -> pd.DataFrame:
    """Return an observation frame with stable editor-compatible dtypes."""
    if obs_df.empty:
        return _EMPTY_OBS_DF.copy()

    normalised = obs_df.copy()
    for column in ("datetime", "height"):
        if column not in normalised.columns:
            normalised[column] = pd.Series(dtype="object")

    normalised = normalised.loc[:, ["datetime", "height"]].reset_index(drop=True)
    normalised["datetime"] = pd.to_datetime(normalised["datetime"], errors="coerce")
    normalised["height"] = pd.to_numeric(normalised["height"], errors="coerce")
    return normalised


def _coerce_obs_df(value: object) -> pd.DataFrame | None:
    """Best-effort conversion of session-backed editor state to a DataFrame."""
    if isinstance(value, pd.DataFrame):
        return _normalise_obs_df(value)
    if isinstance(value, list):
        return _normalise_obs_df(pd.DataFrame(value))
    if isinstance(value, dict):
        try:
            return _normalise_obs_df(pd.DataFrame(value))
        except ValueError:
            return None
    return None


def _get_observation_frames() -> tuple[int, pd.DataFrame, pd.DataFrame]:
    """Return the editor counter, initial editor frame, and current status frame."""
    counter = int(st.session_state.get("sb_editor_counter", 0))
    applied = int(st.session_state.get("_obs_counter_applied", 0))

    # We must maintain a stable 'obs_init' for st.data_editor to prevent resets.
    # We only update this stable base when the counter increments (e.g. Fill Example).
    if "sb_obs_base" not in st.session_state or counter > applied:
        if counter > applied and "sb_obs_data" not in st.session_state:
            # Explicit reset requested (e.g. via _fill_example)
            obs_init = _normalise_obs_df(pd.DataFrame(DEFAULT_OBS_ROWS))
        elif "sb_obs_data" in st.session_state:
            # Re-base on current data
            obs_init = st.session_state["sb_obs_data"].copy()
        else:
            # Initial start
            obs_init = _EMPTY_OBS_DF.copy()

        st.session_state["sb_obs_base"] = obs_init
        st.session_state["_obs_counter_applied"] = counter
    else:
        obs_init = st.session_state["sb_obs_base"]

    # current_obs is used for status LEDs; it should reflect the latest known data.
    # sb_obs_data stores the full DataFrame from the end of the previous run.
    current_obs = st.session_state.get("sb_obs_data", obs_init).copy()

    return counter, obs_init, current_obs


def _normalise_gcs_inputs(
    lon_raw: str | None,
    lat_raw: str | None,
    tilt_raw: str | None,
    half_angle_raw: str | None,
    kappa_raw: str | None,
) -> tuple[float | None, float | None, float | None, float | None, float | None]:
    """Parse and clamp GCS inputs using the existing sidebar rules."""
    gcs_lon = _parse_float(lon_raw)
    gcs_lat = _parse_float(lat_raw)
    gcs_tilt = _parse_float(tilt_raw)
    gcs_half_angle = _parse_float(half_angle_raw)
    gcs_kappa = _parse_float(kappa_raw)

    if gcs_lon is not None and not -180.0 <= gcs_lon <= 180.0:
        gcs_lon = (gcs_lon + 180.0) % 360.0 - 180.0
    if gcs_lat is not None and not -90.0 <= gcs_lat <= 90.0:
        gcs_lat = max(-90.0, min(90.0, gcs_lat))
    if gcs_tilt is not None and not -90.0 <= gcs_tilt <= 90.0:
        gcs_tilt = max(-90.0, min(90.0, gcs_tilt))

    if gcs_half_angle is not None:
        if gcs_half_angle <= 0.0:
            gcs_half_angle = 1.0
        elif gcs_half_angle >= 90.0:
            gcs_half_angle = 89.99

    if gcs_kappa is not None:
        if gcs_kappa >= 1.0:
            gcs_kappa = 0.99
        elif gcs_kappa <= 0.0:
            gcs_kappa = 0.01

    return gcs_lon, gcs_lat, gcs_tilt, gcs_half_angle, gcs_kappa


def _compute_task_states(
    *,
    event_str_raw: str | None,
    target_choice: str,
    gcs_values: tuple[float | None, float | None, float | None, float | None, float | None],
    obs_df: pd.DataFrame,
    w: int,
    w_type: str,
    ssn: int,
    sources: dict[str, TaskSource],
) -> TaskStates:
    """Return the status for each sidebar task."""
    has_gcs = all(value is not None for value in gcs_values)
    has_ht = len(_clean_observations(obs_df)) >= 2
    task_states: TaskStates = {
        "event": (
            "ready"
            if (event_str_raw or "").strip() and sources["event"] in {"example", "user"}
            else "default"
        ),
        "target": (
            "default"
            if target_choice == "Earth" and sources["target"] == "system_default"
            else "ready"
        ),
        "gcs": "missing"
        if not has_gcs
        else ("default" if sources["gcs"] == "system_default" else "ready"),
        "ht": "missing"
        if not has_ht
        else ("default" if sources["ht"] == "system_default" else "ready"),
        "drag": (
            "default"
            if w == 420 and w_type == "slow" and ssn == 100 and sources["drag"] == "system_default"
            else "ready"
        ),
    }
    return task_states


def render_sidebar() -> tuple[SimulationConfig, GCSParams, pd.DataFrame, bool, TaskStates]:
    """
    Render the full sidebar and return
    ``(config, gcs_params, obs_df, run_clicked, task_states)``.

    :return: ``(SimulationConfig, GCSParams, pd.DataFrame, bool, TaskStates)``
    """
    _init_sidebar_state()

    preset_names = list(TARGET_PRESETS.keys())
    raw_event_str = str(st.session_state.get("sb_event_str", "") or "")
    target_choice = str(st.session_state.get("sb_target_body", preset_names[0]) or preset_names[0])
    if target_choice not in TARGET_PRESETS:
        target_choice = preset_names[0]
        st.session_state["sb_target_body"] = target_choice
        _mark_section_source("target")

    gcs_values = _normalise_gcs_inputs(
        st.session_state.get("sb_gcs_lon"),
        st.session_state.get("sb_gcs_lat"),
        st.session_state.get("sb_gcs_tilt"),
        st.session_state.get("sb_gcs_half_angle"),
        st.session_state.get("sb_gcs_kappa"),
    )
    counter, obs_init, current_obs_df = _get_observation_frames()
    sources = {section: _get_section_source(section) for section in _TASK_ORDER}
    task_states = _compute_task_states(
        event_str_raw=raw_event_str,
        target_choice=target_choice,
        gcs_values=gcs_values,
        obs_df=current_obs_df,
        w=int(st.session_state.get("sb_w", 390)),
        w_type=str(st.session_state.get("sb_w_type", "slow")),
        ssn=int(st.session_state.get("sb_ssn", 100)),
        sources=sources,
    )
    run_disabled = task_states["gcs"] == "missing" or task_states["ht"] == "missing"
    missing_requirements: list[str] = []
    if task_states["gcs"] == "missing":
        missing_requirements.append(t("sidebar.section_gcs"))
    if task_states["ht"] == "missing":
        missing_requirements.append(t("sidebar.section_ht"))

    if run_disabled:
        missing_str = ", ".join(f'"{item}"' for item in missing_requirements)
        run_tooltip = f"More data needed to run the simulation. Please complete: {missing_str}"
    else:
        run_tooltip = "Ready to run the simulation. Click to start."

    with st.sidebar:
        st.markdown(_SIDEBAR_LAYOUT_CSS, unsafe_allow_html=True)

        with st.container(key="sidebar-run-button"):
            run_clicked = st.button(
                t("sidebar.run_simulation"),
                key="sb_run_button",
                type="primary",
                use_container_width=True,
                disabled=run_disabled,
                help=run_tooltip,
            )

        st.title(t("sidebar.title"))

        with st.container(key="sidebar-example-button"):
            st.button(
                t("sidebar.fill_example"),
                key="sb_fill_example_button",
                type="secondary",
                use_container_width=True,
                help=t("sidebar.fill_example_help"),
                on_click=_fill_example,
            )

        with st.container(key="sidebar-sections"):
            with st.expander(
                _format_section_title(t("sidebar.section_event"), task_states["event"]),
                expanded=False,
            ):
                event_str = st.text_input(
                    t("sidebar.event_label"),
                    key="sb_event_str",
                    placeholder=t("sidebar.event_placeholder"),
                    help=t("sidebar.event_help"),
                    on_change=_mark_section_source,
                    args=("event",),
                )
                event_str_clean = (event_str or "").strip()[:40] or "unknown"

            with st.expander(
                _format_section_title(t("sidebar.section_target"), task_states["target"]),
                expanded=False,
            ):
                preset_choice = st.selectbox(
                    t("sidebar.target_body"),
                    options=preset_names,
                    index=preset_names.index(target_choice),
                    key="sb_target_body",
                    help=t("sidebar.target_body_help"),
                    on_change=_mark_section_source,
                    args=("target",),
                )

                is_custom = TARGET_PRESETS[preset_choice] is None
                preset_vals: dict[str, float] = TARGET_PRESETS.get(preset_choice) or {}  # type: ignore[assignment]

                if is_custom:
                    target_name = st.text_input(
                        t("sidebar.target_name"),
                        value=str(st.session_state.get("sb_target_name", "Custom")),
                        key="sb_target_name",
                        on_change=_mark_section_source,
                        args=("target",),
                    )
                    cc1, cc2 = st.columns(2)
                    target_lon = cc1.number_input(
                        t("sidebar.target_lon"),
                        value=float(st.session_state.get("sb_target_lon", 0.0)),
                        min_value=-180.0,
                        max_value=180.0,
                        step=0.5,
                        format="%.1f",
                        key="sb_target_lon",
                        on_change=_mark_section_source,
                        args=("target",),
                    )
                    target_lat = cc2.number_input(
                        t("sidebar.target_lat"),
                        value=float(st.session_state.get("sb_target_lat", 0.0)),
                        min_value=-90.0,
                        max_value=90.0,
                        step=0.5,
                        format="%.1f",
                        key="sb_target_lat",
                        on_change=_mark_section_source,
                        args=("target",),
                    )
                    target_dist = st.number_input(
                        t("sidebar.target_dist"),
                        value=float(st.session_state.get("sb_target_dist", 1.0)),
                        min_value=0.01,
                        max_value=5.0,
                        step=0.01,
                        format="%.3f",
                        key="sb_target_dist",
                        on_change=_mark_section_source,
                        args=("target",),
                    )
                else:
                    target_name = preset_choice.split(" (")[0]
                    target_lon = preset_vals["lon"]
                    target_lat = preset_vals["lat"]
                    target_dist = preset_vals["distance"]
                    st.caption(
                        t("sidebar.target_caption").format(
                            lon=target_lon,
                            lat=target_lat,
                            dist=target_dist,
                        )
                    )

                target = TargetConfig(
                    name=target_name,
                    lon=float(target_lon),
                    lat=float(target_lat),
                    distance=float(target_dist),
                )

            with st.expander(
                _format_section_title(t("sidebar.section_gcs"), task_states["gcs"]),
                expanded=False,
            ):
                st.caption(t("sidebar.gcs_caption"))
                gcs_lon_str = st.text_input(
                    t("sidebar.gcs_lon"),
                    placeholder=t("sidebar.gcs_lon_placeholder"),
                    key="sb_gcs_lon",
                    help=t("sidebar.gcs_lon_help"),
                    on_change=_mark_section_source,
                    args=("gcs",),
                )
                gcs_lat_str = st.text_input(
                    t("sidebar.gcs_lat"),
                    placeholder=t("sidebar.gcs_lat_placeholder"),
                    key="sb_gcs_lat",
                    help=t("sidebar.gcs_lat_help"),
                    on_change=_mark_section_source,
                    args=("gcs",),
                )
                gcs_tilt_str = st.text_input(
                    t("sidebar.gcs_tilt"),
                    placeholder=t("sidebar.gcs_tilt_placeholder"),
                    key="sb_gcs_tilt",
                    help=t("sidebar.gcs_tilt_help"),
                    on_change=_mark_section_source,
                    args=("gcs",),
                )

                gcs_half_angle_str = st.text_input(
                    t("sidebar.gcs_ha"),
                    placeholder=t("sidebar.gcs_ha_placeholder"),
                    key="sb_gcs_half_angle",
                    help=t("sidebar.gcs_ha_help"),
                    on_change=_mark_section_source,
                    args=("gcs",),
                )
                gcs_kappa_str = st.text_input(
                    t("sidebar.gcs_kappa"),
                    placeholder=t("sidebar.gcs_kappa_placeholder"),
                    key="sb_gcs_kappa",
                    help=t("sidebar.gcs_kappa_help"),
                    on_change=_mark_section_source,
                    args=("gcs",),
                )

                gcs_lon_raw = _parse_float(gcs_lon_str)
                gcs_lat_raw = _parse_float(gcs_lat_str)
                gcs_tilt_raw = _parse_float(gcs_tilt_str)
                gcs_half_angle_raw = _parse_float(gcs_half_angle_str)
                gcs_kappa_raw = _parse_float(gcs_kappa_str)
                gcs_lon, gcs_lat, gcs_tilt, gcs_half_angle, gcs_kappa = _normalise_gcs_inputs(
                    gcs_lon_str,
                    gcs_lat_str,
                    gcs_tilt_str,
                    gcs_half_angle_str,
                    gcs_kappa_str,
                )

                if gcs_lon_raw is not None and not -180.0 <= gcs_lon_raw <= 180.0:
                    wrapped = (gcs_lon_raw + 180.0) % 360.0 - 180.0
                    st.warning(t("sidebar.gcs_lon_warn").format(lon=gcs_lon_raw, wrapped=wrapped))
                if gcs_lat_raw is not None and not -90.0 <= gcs_lat_raw <= 90.0:
                    clamped = max(-90.0, min(90.0, gcs_lat_raw))
                    st.error(t("sidebar.gcs_lat_err").format(lat=gcs_lat_raw, clamped=clamped))
                if gcs_tilt_raw is not None and not -90.0 <= gcs_tilt_raw <= 90.0:
                    clamped = max(-90.0, min(90.0, gcs_tilt_raw))
                    st.warning(
                        t("sidebar.gcs_tilt_warn").format(tilt=gcs_tilt_raw, clamped=clamped)
                    )
                if gcs_half_angle_raw is not None:
                    if gcs_half_angle_raw <= 0.0:
                        st.error(t("sidebar.gcs_ha_err_lo"))
                    elif gcs_half_angle_raw >= 90.0:
                        st.error(t("sidebar.gcs_ha_err_hi"))
                if gcs_kappa_raw is not None:
                    if gcs_kappa_raw >= 1.0:
                        st.error(t("sidebar.gcs_kappa_err_hi"))
                    elif gcs_kappa_raw <= 0.0:
                        st.error(t("sidebar.gcs_kappa_err_lo"))

            with st.expander(
                _format_section_title(t("sidebar.section_ht"), task_states["ht"]),
                expanded=False,
            ):
                st.caption(t("sidebar.obs_caption"))
                obs_df: pd.DataFrame = st.data_editor(
                    obs_init,
                    hide_index=True,
                    num_rows="dynamic",
                    width="content",
                    column_config={
                        "datetime": st.column_config.DatetimeColumn(
                            t("sidebar.obs_time_col"),
                            required=True,
                            format="YYYY-MM-DD HH:mm",
                            help=t("sidebar.obs_time_help"),
                        ),
                        "height": st.column_config.NumberColumn(
                            t("sidebar.obs_height_col"),
                            min_value=0.1,
                            max_value=300.0,
                            step=0.1,
                            format="%.2f",
                            help=t("sidebar.obs_height_help"),
                        ),
                    },
                    key=f"obs_editor_{counter}",
                    on_change=_mark_section_source,
                    args=("ht",),
                )
                obs_df = _normalise_obs_df(obs_df)
                st.session_state["sb_obs_data"] = obs_df

                valid_obs = len(_clean_observations(obs_df))
                if valid_obs < 2:
                    st.caption(t("sidebar.obs_need_more").format(n=valid_obs))
                else:
                    st.caption(t("sidebar.obs_valid").format(n=valid_obs))

                with st.expander(t("sidebar.advanced"), expanded=False):
                    height_error_str = st.text_input(
                        t("sidebar.height_error"),
                        key="sb_height_error",
                        help=t("sidebar.height_error_help"),
                        on_change=_mark_section_source,
                        args=("ht",),
                    )
                    _height_error_parsed = _parse_float(height_error_str, default=0.25)
                    if _height_error_parsed is None:
                        st.warning(t("sidebar.height_error_warn"))
                        _height_error_parsed = 0.25
                    elif _height_error_parsed < 0.0:
                        st.warning(
                            t("sidebar.height_error_neg_warn").format(
                                val=_height_error_parsed,
                                abs_val=abs(_height_error_parsed),
                            )
                        )
                        _height_error_parsed = abs(_height_error_parsed)
                    elif _height_error_parsed == 0.0:
                        st.info(t("sidebar.height_error_zero_info"))
                    height_error = _height_error_parsed

            with st.expander(
                _format_section_title(t("sidebar.section_drag"), task_states["drag"]),
                expanded=False,
            ):
                with st.container(border=True):
                    st.markdown(t("sidebar.dbm_only"))
                    w = st.slider(
                        t("sidebar.wind_speed"),
                        min_value=250,
                        max_value=700,
                        step=10,
                        key="sb_w",
                        help=t("sidebar.wind_speed_help"),
                        on_change=_mark_section_source,
                        args=("drag",),
                    )

                with st.container(border=True):
                    st.markdown(t("sidebar.modbm_only"))
                    w_type = st.radio(
                        t("sidebar.wind_regime"),
                        options=["slow", "fast"],
                        key="sb_w_type",
                        horizontal=True,
                        help=t("sidebar.wind_regime_help"),
                        on_change=_mark_section_source,
                        args=("drag",),
                    )
                    ssn = st.slider(
                        t("sidebar.ssn"),
                        min_value=0,
                        max_value=300,
                        step=1,
                        key="sb_ssn",
                        help=t("sidebar.ssn_help"),
                        on_change=_mark_section_source,
                        args=("drag",),
                    )

                with st.expander(t("sidebar.advanced"), expanded=False):
                    st.caption(t("sidebar.drag_settings"))
                    c_d_str = st.text_input(
                        t("sidebar.c_d"),
                        key="sb_c_d",
                        help=t("sidebar.c_d_help"),
                        on_change=_mark_section_source,
                        args=("drag",),
                    )
                    _c_d_parsed = _parse_float(c_d_str, default=1.0)
                    if _c_d_parsed is None:
                        st.warning(t("sidebar.c_d_warn"))
                        _c_d_parsed = 1.0
                    elif _c_d_parsed <= 0.0:
                        st.error(t("sidebar.c_d_err"))
                        _c_d_parsed = 0.01
                    elif _c_d_parsed > 5.0:
                        st.info(t("sidebar.c_d_info").format(val=_c_d_parsed))
                    c_d = _c_d_parsed

                    st.divider()
                    st.caption(t("sidebar.optional_overrides"))
                    toa_raw = (
                        st.text_input(
                            t("sidebar.toa"),
                            key="sb_toa_raw",
                            placeholder=t("sidebar.toa_placeholder"),
                            help=t("sidebar.toa_help"),
                            on_change=_mark_section_source,
                            args=("drag",),
                        )
                        or None
                    )

                    if toa_raw:
                        try:
                            datetime.strptime(toa_raw, "%d/%m/%Y %H:%M:%S")
                            st.success(t("sidebar.toa_valid"))
                        except ValueError:
                            st.warning(t("sidebar.toa_invalid"))
                            toa_raw = None

                    mass_override_value = st.session_state.get("sb_mass_override", "")
                    if mass_override_value == "0":
                        mass_override_value = ""
                        st.session_state["sb_mass_override"] = mass_override_value
                    if not isinstance(mass_override_value, str):
                        mass_override_value = str(mass_override_value)
                        st.session_state["sb_mass_override"] = mass_override_value

                    m_override_str = st.text_input(
                        t("sidebar.mass_override"),
                        value=mass_override_value,
                        placeholder="e.g. 1.2e15",
                        key="sb_mass_override",
                        help=t("sidebar.mass_override_help"),
                        on_change=_mark_section_source,
                        args=("drag",),
                    )
                    m_override_raw = _parse_float(m_override_str)
                    if m_override_raw is None:
                        m_override_g = None
                    elif m_override_raw <= 0.0:
                        st.error(t("sidebar.mass_override_err"))
                        m_override_g = None
                    else:
                        m_override_g = m_override_raw

                    v0_override_str = st.text_input(
                        t("sidebar.v0_override"),
                        key="sb_v0_override",
                        placeholder=t("sidebar.v0_override_placeholder"),
                        help=t("sidebar.v0_override_help"),
                        on_change=_mark_section_source,
                        args=("drag",),
                    )
                    v0_override_kms = _parse_float(v0_override_str)
                    if v0_override_kms is not None:
                        if v0_override_kms <= 0.0:
                            st.error(t("sidebar.v0_override_err"))
                            v0_override_kms = None
                        elif v0_override_kms > 3000.0:
                            st.info(t("sidebar.v0_override_info").format(v0=v0_override_kms))

    config = SimulationConfig(
        event_str=event_str_clean,
        target=target,
        height_error=float(height_error or 0.25),
        w=float(w or 390),
        w_type=str(w_type or "slow"),
        ssn=float(ssn or 100),
        c_d=float(c_d or 1.0),
        toa_raw=toa_raw,
        m_override_g=m_override_g,
        v0_override_kms=v0_override_kms,
    )

    gcs_params = GCSParams(
        lon_deg=float(gcs_lon) if gcs_lon is not None else _GCS_FALLBACKS["lon_deg"],
        lat_deg=float(gcs_lat) if gcs_lat is not None else _GCS_FALLBACKS["lat_deg"],
        tilt_deg=float(gcs_tilt) if gcs_tilt is not None else _GCS_FALLBACKS["tilt_deg"],
        half_angle_deg=(
            float(gcs_half_angle)
            if gcs_half_angle is not None
            else _GCS_FALLBACKS["half_angle_deg"]
        ),
        kappa=float(gcs_kappa) if gcs_kappa is not None else _GCS_FALLBACKS["kappa"],
    )

    return config, gcs_params, obs_df, run_clicked, task_states
