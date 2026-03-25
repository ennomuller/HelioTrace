"""
Sidebar input panel for HelioTrace.

Renders all user-controllable parameters and returns a
``(SimulationConfig, GCSParams, obs_df, run_clicked)`` tuple.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from heliotrace.config import DEFAULT_OBS_ROWS, TARGET_PRESETS
from heliotrace.i18n import t
from heliotrace.models.schemas import GCSParams, SimulationConfig, TargetConfig

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


def _parse_float(text: str | None, default: float | None = None) -> float | None:
    """Parse a text-input string to float; returns ``default`` on empty or invalid input."""
    if not text or not text.strip():
        return default
    try:
        return float(text.strip())
    except ValueError:
        return default


def _fill_example() -> None:
    """Populate session state with the 2023-10-28 example event and trigger a rerun."""
    for key, val in _EXAMPLE.items():
        st.session_state[key] = val
    # Increment the editor counter so the data_editor re-initialises from DEFAULT_OBS_ROWS
    st.session_state["sb_editor_counter"] = st.session_state.get("sb_editor_counter", 0) + 1
    st.session_state.pop("sb_obs_data", None)
    st.rerun()


def render_sidebar() -> tuple[SimulationConfig, GCSParams, pd.DataFrame, bool, bool]:
    """
    Render the full sidebar and return
    ``(config, gcs_params, obs_df, run_clicked, gcs_params_entered)``.

    - ``config``             — :class:`~heliotrace.models.schemas.SimulationConfig` with
                               every widget value.
    - ``gcs_params``         — :class:`~heliotrace.models.schemas.GCSParams` with the five
                               fixed geometrical GCS inputs.
    - ``obs_df``             — :class:`~pandas.DataFrame` with columns ``datetime`` and
                               ``height`` from the compact observation table.
    - ``run_clicked``        — ``True`` only on the frame the user pressed **\u25b6 Run**.
    - ``gcs_params_entered`` — ``True`` when all five GCS geometry fields have a value.

    :return: ``(SimulationConfig, GCSParams, pd.DataFrame, bool, bool)``
    """
    with st.sidebar:
        st.title(t("sidebar.title"))

        # ---- Fill with example ------------------------------------------ #
        if st.button(
            t("sidebar.fill_example"),
            type="primary",
            width="content",
            help=t("sidebar.fill_example_help"),
        ):
            _fill_example()

        st.divider()
        # ------------------------------------------------------------------ #
        # 1. Event Information
        # ------------------------------------------------------------------ #
        st.subheader(t("sidebar.event_title"))

        event_str = st.text_input(
            t("sidebar.event_label"),
            key="sb_event_str",
            placeholder=t("sidebar.event_placeholder"),
            help=t("sidebar.event_help"),
        )
        event_str_clean = (event_str or "").strip()[:40] or "unknown"

        st.divider()
        # ------------------------------------------------------------------ #
        # 2. Target Configuration
        # ------------------------------------------------------------------ #
        st.subheader(t("sidebar.target_title"))

        preset_names = list(TARGET_PRESETS.keys())
        preset_choice = st.selectbox(
            t("sidebar.target_body"),
            options=preset_names,
            index=0,
            key="sb_target_body",
            help=t("sidebar.target_body_help"),
        )

        is_custom = TARGET_PRESETS[preset_choice] is None
        preset_vals: dict[str, float] = TARGET_PRESETS.get(preset_choice) or {}  # type: ignore[assignment]

        if is_custom:
            target_name = st.text_input(
                t("sidebar.target_name"), value="Custom", key="sb_target_name"
            )
            cc1, cc2 = st.columns(2)
            target_lon = cc1.number_input(
                t("sidebar.target_lon"),
                value=0.0,
                min_value=-180.0,
                max_value=180.0,
                step=0.5,
                format="%.1f",
                key="sb_target_lon",
            )
            target_lat = cc2.number_input(
                t("sidebar.target_lat"),
                value=0.0,
                min_value=-90.0,
                max_value=90.0,
                step=0.5,
                format="%.1f",
                key="sb_target_lat",
            )
            target_dist = st.number_input(
                t("sidebar.target_dist"),
                value=1.0,
                min_value=0.01,
                max_value=5.0,
                step=0.01,
                format="%.3f",
                key="sb_target_dist",
            )
        else:
            target_name = preset_choice.split(" (")[0]
            target_lon = preset_vals["lon"]
            target_lat = preset_vals["lat"]
            target_dist = preset_vals["distance"]
            st.caption(
                t("sidebar.target_caption").format(lon=target_lon, lat=target_lat, dist=target_dist)
            )

        target = TargetConfig(
            name=target_name,
            lon=float(target_lon),
            lat=float(target_lat),
            distance=float(target_dist),
        )

        st.divider()
        # ------------------------------------------------------------------ #
        # 3. GCS Geometrical Parameters
        # ------------------------------------------------------------------ #
        st.subheader(t("sidebar.gcs_title"))

        c_lon, c_lat, c_tilt = st.columns(3)
        gcs_lon_str = c_lon.text_input(
            t("sidebar.gcs_lon"),
            placeholder=t("sidebar.gcs_lon_placeholder"),
            key="sb_gcs_lon",
            help=t("sidebar.gcs_lon_help"),
        )
        gcs_lat_str = c_lat.text_input(
            t("sidebar.gcs_lat"),
            placeholder=t("sidebar.gcs_lat_placeholder"),
            key="sb_gcs_lat",
            help=t("sidebar.gcs_lat_help"),
        )
        gcs_tilt_str = c_tilt.text_input(
            t("sidebar.gcs_tilt"),
            placeholder=t("sidebar.gcs_tilt_placeholder"),
            key="sb_gcs_tilt",
            help=t("sidebar.gcs_tilt_help"),
        )
        gcs_lon = _parse_float(gcs_lon_str)
        gcs_lat = _parse_float(gcs_lat_str)
        gcs_tilt = _parse_float(gcs_tilt_str)

        if gcs_lon is not None and not -180.0 <= gcs_lon <= 180.0:
            wrapped = (gcs_lon + 180.0) % 360.0 - 180.0
            st.warning(t("sidebar.gcs_lon_warn").format(lon=gcs_lon, wrapped=wrapped))
            gcs_lon = wrapped
        if gcs_lat is not None and not -90.0 <= gcs_lat <= 90.0:
            clamped = max(-90.0, min(90.0, gcs_lat))
            st.error(t("sidebar.gcs_lat_err").format(lat=gcs_lat, clamped=clamped))
            gcs_lat = clamped
        if gcs_tilt is not None and not -90.0 <= gcs_tilt <= 90.0:
            clamped = max(-90.0, min(90.0, gcs_tilt))
            st.warning(t("sidebar.gcs_tilt_warn").format(tilt=gcs_tilt, clamped=clamped))
            gcs_tilt = clamped

        c_ha, c_kp = st.columns(2)
        gcs_half_angle_str = c_ha.text_input(
            t("sidebar.gcs_ha"),
            placeholder=t("sidebar.gcs_ha_placeholder"),
            key="sb_gcs_half_angle",
            help=t("sidebar.gcs_ha_help"),
        )
        gcs_kappa_str = c_kp.text_input(
            t("sidebar.gcs_kappa"),
            placeholder=t("sidebar.gcs_kappa_placeholder"),
            key="sb_gcs_kappa",
            help=t("sidebar.gcs_kappa_help"),
        )
        gcs_half_angle = _parse_float(gcs_half_angle_str)
        gcs_kappa = _parse_float(gcs_kappa_str)

        if gcs_half_angle is not None:
            if gcs_half_angle <= 0.0:
                st.error(t("sidebar.gcs_ha_err_lo"))
                gcs_half_angle = 1.0
            elif gcs_half_angle >= 90.0:
                st.error(t("sidebar.gcs_ha_err_hi"))
                gcs_half_angle = 89.99
        if gcs_kappa is not None:
            if gcs_kappa >= 1.0:
                st.error(t("sidebar.gcs_kappa_err_hi"))
                gcs_kappa = 0.99
            elif gcs_kappa <= 0.0:
                st.error(t("sidebar.gcs_kappa_err_lo"))
                gcs_kappa = 0.01

        st.divider()
        # ------------------------------------------------------------------ #
        # 4. Observation Table
        # ------------------------------------------------------------------ #
        st.subheader(t("sidebar.obs_title"))
        st.caption(t("sidebar.obs_caption"))

        counter = st.session_state.get("sb_editor_counter", 0)
        _prev = st.session_state.get("_obs_counter_applied", 0)

        if counter > _prev:
            obs_init = pd.DataFrame(DEFAULT_OBS_ROWS)
            st.session_state["_obs_counter_applied"] = counter
        elif "sb_obs_data" in st.session_state:
            obs_init = st.session_state["sb_obs_data"]
        else:
            obs_init = _EMPTY_OBS_DF

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
        )
        st.session_state["sb_obs_data"] = obs_df

        valid_obs = len(obs_df.dropna(subset=["datetime", "height"]))
        if valid_obs < 2:
            st.caption(t("sidebar.obs_need_more").format(n=valid_obs))
        else:
            st.caption(t("sidebar.obs_valid").format(n=valid_obs))

        with st.expander(t("sidebar.advanced")):
            height_error_str: str = st.text_input(
                t("sidebar.height_error"),
                value="0.25",
                key="sb_height_error",
                help=t("sidebar.height_error_help"),
            )
            _height_error_parsed = _parse_float(height_error_str, default=0.25)
            if _height_error_parsed is None:
                st.warning(t("sidebar.height_error_warn"))
                _height_error_parsed = 0.25
            elif _height_error_parsed < 0.0:
                st.warning(
                    t("sidebar.height_error_neg_warn").format(
                        val=_height_error_parsed, abs_val=abs(_height_error_parsed)
                    )
                )
                _height_error_parsed = abs(_height_error_parsed)
            elif _height_error_parsed == 0.0:
                st.info(t("sidebar.height_error_zero_info"))
            height_error: float = _height_error_parsed

        st.divider()
        # ------------------------------------------------------------------ #
        # 5. Drag Model Parameters
        # ------------------------------------------------------------------ #
        st.subheader(t("sidebar.drag_title"))

        st.markdown(t("sidebar.dbm_only"))
        st.session_state.setdefault("sb_w", 390)
        w = st.slider(
            t("sidebar.wind_speed"),
            min_value=250,
            max_value=700,
            key="sb_w",
            step=10,
            help=t("sidebar.wind_speed_help"),
        )

        st.markdown(t("sidebar.modbm_only"))
        w_type = st.radio(
            t("sidebar.wind_regime"),
            options=["slow", "fast"],
            key="sb_w_type",
            horizontal=True,
            help=t("sidebar.wind_regime_help"),
        )
        st.session_state.setdefault("sb_ssn", 100)
        ssn = st.slider(
            t("sidebar.ssn"),
            min_value=0,
            max_value=300,
            key="sb_ssn",
            step=1,
            help=t("sidebar.ssn_help"),
        )

        # ------------------------------------------------------------------ #
        # 6. Advanced / Optional
        # ------------------------------------------------------------------ #
        with st.expander(t("sidebar.advanced")):
            st.caption(t("sidebar.drag_settings"))
            c_d_str: str = st.text_input(
                t("sidebar.c_d"),
                value="1.0",
                key="sb_c_d",
                help=t("sidebar.c_d_help"),
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
            c_d: float = _c_d_parsed

            st.divider()
            st.caption(t("sidebar.optional_overrides"))
            toa_raw: str | None = (
                st.text_input(
                    t("sidebar.toa"),
                    key="sb_toa_raw",
                    placeholder=t("sidebar.toa_placeholder"),
                    help=t("sidebar.toa_help"),
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

            m_override_raw: float = st.number_input(
                t("sidebar.mass_override"),
                value=0.0,
                min_value=0.0,
                format="%.2e",
                key="sb_mass_override",
                help=t("sidebar.mass_override_help"),
            )
            m_override_g: float | None = m_override_raw if m_override_raw > 0.0 else None

            v0_override_str: str = st.text_input(
                t("sidebar.v0_override"),
                key="sb_v0_override",
                placeholder=t("sidebar.v0_override_placeholder"),
                help=t("sidebar.v0_override_help"),
            )
            v0_override_kms: float | None = _parse_float(v0_override_str)
            if v0_override_kms is not None:
                if v0_override_kms <= 0.0:
                    st.error(t("sidebar.v0_override_err"))
                    v0_override_kms = None
                elif v0_override_kms > 3000.0:
                    st.info(t("sidebar.v0_override_info").format(v0=v0_override_kms))

        st.divider()

        # ------------------------------------------------------------------ #
        # 7. Run button
        # ------------------------------------------------------------------ #
        run_clicked: bool = st.button(
            t("sidebar.run_simulation"),
            type="primary",
            width="content",
        )

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

    gcs_params_entered: bool = all(
        v is not None for v in [gcs_lon, gcs_lat, gcs_tilt, gcs_half_angle, gcs_kappa]
    )
    gcs_params = GCSParams(
        lon_deg=float(gcs_lon) if gcs_lon is not None else 0.0,
        lat_deg=float(gcs_lat) if gcs_lat is not None else 0.0,
        tilt_deg=float(gcs_tilt) if gcs_tilt is not None else 0.0,
        half_angle_deg=float(gcs_half_angle) if gcs_half_angle is not None else 20.0,
        kappa=float(gcs_kappa) if gcs_kappa is not None else 0.4,
    )

    return config, gcs_params, obs_df, run_clicked, gcs_params_entered
