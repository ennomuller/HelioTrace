"""
Sidebar input panel for HelioTrace.

Renders all user-controllable parameters and returns a
``(SimulationConfig, GCSParams, obs_df, run_clicked)`` tuple.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import pandas as pd
import streamlit as st

from heliotrace.config import DEFAULT_OBS_ROWS, TARGET_PRESETS
from heliotrace.models.schemas import GCSParams, SimulationConfig, TargetConfig

# ---------------------------------------------------------------------------
# Example event: 2023-10-28 Halloween CME
# ---------------------------------------------------------------------------
_EXAMPLE: dict = {
    "sb_event_str": "20231028",
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
        st.title("⚙️ Configuration")

        # ---- Fill with example ------------------------------------------ #
        if st.button(
            "⚡ Fill with example",
            type="primary",
            use_container_width=True,
            help="Auto-fill all fields with the 2023-10-28 Halloween CME event.",
        ):
            _fill_example()

        st.divider()
        # ------------------------------------------------------------------ #
        # 1. Event Information
        # ------------------------------------------------------------------ #
        st.subheader("📅 Event Info")

        event_str = st.text_input(
            "Event Date (YYYYMMDD)",
            key="sb_event_str",
            placeholder="e.g. 20231028",
            help="Used as an identifier in titles and file names.",
        )
        try:
            cme_launch_day = datetime.strptime(event_str, "%Y%m%d")
            st.caption(f"📆 {cme_launch_day.strftime('%d %B %Y')}")
        except ValueError:
            if event_str.strip():
                st.warning("Invalid date format — expected YYYYMMDD.")
            cme_launch_day = datetime(2023, 10, 28)

        st.divider()
        # ------------------------------------------------------------------ #
        # 2. Target Configuration
        # ------------------------------------------------------------------ #
        st.subheader("🎯 Target")

        preset_names = list(TARGET_PRESETS.keys())
        preset_choice = st.selectbox(
            "Target body",
            options=preset_names,
            index=0,
            help="Select a preconfigured target, or choose 'Custom' to enter coordinates manually.",
        )

        is_custom = TARGET_PRESETS[preset_choice] is None
        preset_vals: dict[str, float] = TARGET_PRESETS.get(preset_choice) or {}  # type: ignore[assignment]

        if is_custom:
            target_name = st.text_input("Target name", value="Custom")
            cc1, cc2 = st.columns(2)
            target_lon = cc1.number_input(
                "Lon [deg]", value=0.0, min_value=-180.0, max_value=180.0, step=0.5, format="%.1f"
            )
            target_lat = cc2.number_input(
                "Lat [deg]", value=0.0, min_value=-90.0, max_value=90.0, step=0.5, format="%.1f"
            )
            target_dist = st.number_input(
                "Distance [AU]", value=1.0, min_value=0.01, max_value=5.0, step=0.01, format="%.3f"
            )
        else:
            target_name = preset_choice.split(" (")[0]
            target_lon = preset_vals["lon"]
            target_lat = preset_vals["lat"]
            target_dist = preset_vals["distance"]
            st.caption(
                f"Lon: **{target_lon}°** | Lat: **{target_lat}°** | Distance: **{target_dist} AU**"
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
        st.subheader("🐚 GCS Parameters")

        c_lon, c_lat, c_tilt = st.columns(3)
        gcs_lon_str = c_lon.text_input(
            "Lon [deg]",
            placeholder="[-180, 180]",
            key="sb_gcs_lon",
            help="Stonyhurst heliographic longitude of the CME source region [deg].",
        )
        gcs_lat_str = c_lat.text_input(
            "Lat [deg]",
            placeholder="[-90, 90]",
            key="sb_gcs_lat",
            help="Stonyhurst heliographic latitude of the CME source [deg].",
        )
        gcs_tilt_str = c_tilt.text_input(
            "Tilt [deg]",
            placeholder="[-90, 90]",
            key="sb_gcs_tilt",
            help="Tilt of the CME flux-rope axis relative to the solar equatorial plane [deg].",
        )
        gcs_lon = _parse_float(gcs_lon_str)
        gcs_lat = _parse_float(gcs_lat_str)
        gcs_tilt = _parse_float(gcs_tilt_str)

        c_ha, c_kp = st.columns(2)
        gcs_half_angle_str = c_ha.text_input(
            "Half-angle α [deg]",
            placeholder="[0.1, 89.9]",
            key="sb_gcs_half_angle",
            help=(
                "GCS half-angle α: angular half-width of the CME shell [deg]. Valid: [0.1°, 89.9°]."
            ),
        )
        gcs_kappa_str = c_kp.text_input(
            "Aspect ratio κ",
            placeholder="[0.01, 0.99]",
            key="sb_gcs_kappa",
            help="GCS aspect ratio κ: cross-section radius / apex distance. Valid: [0.01, 0.99].",
        )
        gcs_half_angle = _parse_float(gcs_half_angle_str)
        gcs_kappa = _parse_float(gcs_kappa_str)
        if gcs_half_angle and not 5.0 <= gcs_half_angle <= 60.0:
            st.warning("⚠️ Half-angle outside typical range 5–60°.")
        if gcs_kappa and not 0.1 <= gcs_kappa <= 0.8:
            st.warning("⚠️ κ outside typical range 0.1–0.8.")

        st.divider()
        # ------------------------------------------------------------------ #
        # 4. Observation Table
        # ------------------------------------------------------------------ #
        st.subheader("📋 Observations")
        st.caption("CME apex heights from coronagraph images.")

        counter = st.session_state.get("sb_editor_counter", 0)
        obs_init = pd.DataFrame(DEFAULT_OBS_ROWS) if counter > 0 else _EMPTY_OBS_DF

        obs_df: pd.DataFrame = st.data_editor(
            obs_init,
            hide_index=True,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "datetime": st.column_config.DatetimeColumn(
                    "Time (UTC)",
                    required=True,
                    format="YYYY-MM-DD HH:mm",
                    help="UTC observation timestamp from the coronagraph image.",
                ),
                "height": st.column_config.NumberColumn(
                    "Height [R☉]",
                    min_value=0.1,
                    max_value=300.0,
                    step=0.1,
                    format="%.2f",
                    help="CME leading-edge apex height in solar radii [R☉].",
                ),
            },
            key=f"obs_editor_{counter}",
        )

        valid_obs = len(obs_df.dropna(subset=["datetime", "height"]))
        if valid_obs < 2:
            st.caption(f"ℹ️ Need ≥2 observations for H-T fit. ({valid_obs} so far)")
        else:
            st.caption(f"✓ {valid_obs} valid observations.")

        with st.expander("⚙️ Advanced"):
            height_error_str: str = st.text_input(
                "Height error ± [R☉]",
                value="0.25",
                key="sb_height_error",
                help="Symmetric ±uncertainty applied to every height measurement [R☉].",
            )
            height_error: float = _parse_float(height_error_str, default=0.25) or 0.25

        st.divider()
        # ------------------------------------------------------------------ #
        # 5. Drag Model Parameters
        # ------------------------------------------------------------------ #
        st.subheader("🪂 Drag Parameters")

        st.markdown("**DBM only**")
        st.session_state.setdefault("sb_w", 390)
        w = st.slider(
            "Solar wind speed w [km/s]",
            min_value=250,
            max_value=700,
            key="sb_w",
            step=10,
            help="Constant ambient solar wind speed used by the standard DBM.",
        )

        st.markdown("**MoDBM only**")
        w_type = st.radio(
            "Solar wind regime",
            options=["slow", "fast"],
            key="sb_w_type",
            horizontal=True,
            help="Venzmer & Bothmer (2018) background wind profile.",
        )
        st.session_state.setdefault("sb_ssn", 100)
        ssn = st.slider(
            "Smoothed SSN",
            min_value=0,
            max_value=300,
            key="sb_ssn",
            step=1,
            help="Monthly smoothed total sunspot number for the MoDBM density profile.",
        )

        # ------------------------------------------------------------------ #
        # 6. Advanced / Optional
        # ------------------------------------------------------------------ #
        with st.expander("⚙️ Advanced"):
            st.caption("Drag settings")
            c_d_str: str = st.text_input(
                "Drag coefficient c_d",
                value="1.0",
                key="sb_c_d",
                help=(
                    "Dimensionless drag coefficient (converges to ~1 beyond ~12 R☉, Cargill 2004)."
                ),
            )
            c_d: float = _parse_float(c_d_str, default=1.0) or 1.0

            st.divider()
            st.caption("Optional overrides")
            toa_raw: Optional[str] = (
                st.text_input(
                    "Expected arrival time (optional)",
                    key="sb_toa_raw",
                    placeholder="DD/MM/YYYY HH:MM:SS",
                    help="Observed/predicted arrival for comparison. Leave blank to skip.",
                )
                or None
            )

            if toa_raw:
                try:
                    datetime.strptime(toa_raw, "%d/%m/%Y %H:%M:%S")
                    st.success("✓ Valid arrival time format")
                except ValueError:
                    st.warning("⚠ Expected format: DD/MM/YYYY HH:MM:SS")
                    toa_raw = None

            m_override_raw: float = st.number_input(
                "CME mass override [g]  (0 = Pluta formula)",
                value=0.0,
                min_value=0.0,
                format="%.2e",
                help="Override the Pluta (2018) mass formula. Enter 0 to keep the formula.",
            )
            m_override_g: Optional[float] = m_override_raw if m_override_raw > 0.0 else None

            v0_override_str: str = st.text_input(
                "v₀ override [km/s]  (blank = geometry-derived)",
                key="sb_v0_override",
                placeholder="e.g. 600",
                help="Hard override for the CME velocity component directed at the target. "
                "Replaces the geometry-derived v₀ = v_apex × projection ratio.",
            )
            v0_override_kms: Optional[float] = _parse_float(v0_override_str)

        st.divider()

        # ------------------------------------------------------------------ #
        # 7. Run button
        # ------------------------------------------------------------------ #
        run_clicked: bool = st.button(
            "▶ Run Simulation",
            type="primary",
            use_container_width=True,
        )

    config = SimulationConfig(
        event_str=event_str or "unknown",
        cme_launch_day=cme_launch_day,
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
