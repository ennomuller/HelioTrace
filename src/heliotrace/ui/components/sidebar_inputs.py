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


def render_sidebar() -> tuple[SimulationConfig, GCSParams, pd.DataFrame, bool]:
    """
    Render the full sidebar and return ``(config, gcs_params, obs_df, run_clicked)``.

    - ``config``      — :class:`~heliotrace.models.schemas.SimulationConfig` with
                        every widget value.
    - ``gcs_params``  — :class:`~heliotrace.models.schemas.GCSParams` with the five
                        fixed geometrical GCS inputs.
    - ``obs_df``      — :class:`~pandas.DataFrame` with columns ``datetime`` and
                        ``height`` from the compact observation table.
    - ``run_clicked`` — ``True`` only on the frame the user pressed **▶ Run**.

    :return: ``(SimulationConfig, GCSParams, pd.DataFrame, bool)``
    """
    with st.sidebar:
        st.title("⚙️ Configuration")

        # ------------------------------------------------------------------ #
        # 1. Event Information
        # ------------------------------------------------------------------ #
        st.header("📅 Event Info")

        event_str = st.text_input(
            "Event Date (YYYYMMDD)",
            value="20231028",
            help="Used as an identifier in titles and file names.",
        )
        try:
            cme_launch_day = datetime.strptime(event_str, "%Y%m%d")
            st.caption(f"📆 {cme_launch_day.strftime('%d %B %Y')}")
        except ValueError:
            st.warning("Invalid date format — expected YYYYMMDD.")
            cme_launch_day = datetime(2023, 10, 28)

        st.divider()

        # ------------------------------------------------------------------ #
        # 2. Target Configuration
        # ------------------------------------------------------------------ #
        st.header("🎯 Target")

        preset_names  = list(TARGET_PRESETS.keys())
        preset_choice = st.selectbox(
            "Target body",
            options=preset_names,
            index=0,
            help="Select a preconfigured target, or choose 'Custom' to enter coordinates manually.",
        )

        is_custom  = TARGET_PRESETS[preset_choice] is None
        preset_vals: dict[str, float] = TARGET_PRESETS.get(preset_choice) or {}  # type: ignore[assignment]

        if is_custom:
            target_name = st.text_input("Target name", value="Custom")
            target_lon  = st.number_input("Longitude [deg]", value=0.0,  min_value=-180.0, max_value=180.0, step=0.5, format="%.1f")
            target_lat  = st.number_input("Latitude [deg]",  value=0.0,  min_value=-90.0,  max_value=90.0,  step=0.5, format="%.1f")
            target_dist = st.number_input("Distance [AU]",   value=1.0,  min_value=0.01,   max_value=5.0,   step=0.01, format="%.3f")
        else:
            target_name = preset_choice.split(" (")[0]
            target_lon  = preset_vals["lon"]
            target_lat  = preset_vals["lat"]
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
        st.header("🔭 GCS Parameters")

        gcs_lon = st.number_input(
            "Longitude [deg]",
            value=5.5,
            min_value=-180.0,
            max_value=180.0,
            step=0.5,
            format="%.1f",
            key="gcs_lon",
            help=(
                "Stonyhurst heliographic longitude of the CME source region [deg]. "
                "0° corresponds to the Earth direction."
            ),
        )

        gcs_lat = st.number_input(
            "Latitude [deg]",
            value=-20.1,
            min_value=-90.0,
            max_value=90.0,
            step=0.5,
            format="%.1f",
            key="gcs_lat",
            help=(
                "Stonyhurst heliographic latitude of the CME source [deg]. "
                "Positive values indicate the northern hemisphere."
            ),
        )

        gcs_tilt = st.number_input(
            "Tilt [deg]",
            value=-7.5,
            min_value=-90.0,
            max_value=90.0,
            step=0.5,
            format="%.1f",
            key="gcs_tilt",
            help=(
                "Tilt of the CME flux-rope axis relative to the solar equatorial plane [deg]. "
                "Positive = counter-clockwise rotation."
            ),
        )

        gcs_half_angle = st.number_input(
            "Half-angle α [deg]",
            value=30.0,
            min_value=0.1,
            max_value=89.9,
            step=0.5,
            format="%.1f",
            key="gcs_half_angle",
            help=(
                "GCS half-angle α: angular half-width of the CME shell at the apex [deg]. "
                "Typical range: 15–45°."
            ),
        )
        if not 5.0 <= gcs_half_angle <= 60.0:
            st.warning("⚠️ Half-angle outside typical range 5–60°. Unusual geometry.")

        gcs_kappa = st.number_input(
            "Aspect ratio κ",
            value=0.42,
            min_value=0.01,
            max_value=0.99,
            step=0.01,
            format="%.2f",
            key="gcs_kappa",
            help=(
                "GCS aspect ratio κ: ratio of cross-section radius to apex distance. "
                "Controls CME 'fatness'. Typical range: 0.2–0.6."
            ),
        )
        if not 0.1 <= gcs_kappa <= 0.8:
            st.warning("⚠️ κ outside typical range 0.1–0.8. Unusual geometry.")

        with st.expander("🔧 Advanced"):
            height_error = st.number_input(
                "Height error ± [R☉]",
                value=0.25,
                min_value=0.01,
                max_value=5.0,
                step=0.05,
                format="%.2f",
                help=(
                    "Symmetric ± uncertainty applied to every height measurement "
                    "used in the weighted linear H-T fit [R☉]."
                ),
            )

        st.divider()

        # ------------------------------------------------------------------ #
        # 4. Observation Table
        # ------------------------------------------------------------------ #
        st.header("📋 Observations")
        st.caption("CME apex height measurements from coronagraph images.")

        obs_df: pd.DataFrame = st.data_editor(
            pd.DataFrame(DEFAULT_OBS_ROWS),
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
            key="obs_editor",
        )

        valid_obs = len(obs_df.dropna(subset=["datetime", "height"]))
        if valid_obs < 2:
            st.info(f"ℹ️ At least **2** observations required for the H-T fit. ({valid_obs} so far)")
        else:
            st.caption(f"✓ {valid_obs} valid observations.")

        st.divider()

        # ------------------------------------------------------------------ #
        # 5. Drag Model Parameters
        # ------------------------------------------------------------------ #
        st.header("🌬️ Drag Model Parameters")

        w = st.slider(
            "Solar wind speed w [km/s]  (DBM)",
            min_value=250,
            max_value=700,
            value=390,
            step=10,
            help="Constant ambient solar wind speed used by the standard DBM.",
        )

        w_type = st.radio(
            "Solar wind regime  (MODBM)",
            options=["slow", "fast"],
            index=0,
            horizontal=True,
            help="Venzmer & Bothmer (2018) background wind profile.",
        )

        ssn = st.slider(
            "Smoothed sunspot number (SSN)  (MODBM)",
            min_value=0,
            max_value=300,
            value=100,
            step=5,
            help="Monthly smoothed total sunspot number for the MODBM density profile.",
        )

        c_d = st.number_input(
            "Drag coefficient c_d",
            value=1.0,
            min_value=0.1,
            max_value=5.0,
            step=0.1,
            format="%.1f",
            help="Dimensionless drag coefficient (converges to ~1 beyond ~12 R☉, Cargill 2004).",
        )

        st.divider()

        # ------------------------------------------------------------------ #
        # 6. Optional / Advanced settings
        # ------------------------------------------------------------------ #
        with st.expander("⚙️ Advanced / Optional"):
            toa_raw: Optional[str] = st.text_input(
                "Expected arrival time (optional)",
                value="",
                placeholder="DD/MM/YYYY HH:MM:SS",
                help="Observed/predicted arrival for comparison. Leave blank to skip.",
            ) or None

            if toa_raw:
                try:
                    datetime.strptime(toa_raw, "%d/%m/%Y %H:%M:%S")
                    st.success("✓ Valid arrival time format")
                except ValueError:
                    st.warning("⚠ Expected format: DD/MM/YYYY HH:MM:SS")
                    toa_raw = None

            m_override_raw: float = st.number_input(
                "CME mass override [g]  (0 = use Pluta formula)",
                value=0.0,
                min_value=0.0,
                format="%.2e",
                help="Override the Pluta (2018) mass formula. Enter 0 to keep the formula.",
            )
            m_override_g: Optional[float] = m_override_raw if m_override_raw > 0.0 else None

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
        event_str=event_str,
        cme_launch_day=cme_launch_day,
        target=target,
        height_error=float(height_error),
        w=float(w),
        w_type=str(w_type),
        ssn=float(ssn),
        c_d=float(c_d),
        toa_raw=toa_raw,
        m_override_g=m_override_g,
    )

    gcs_params = GCSParams(
        lon_deg=float(gcs_lon),
        lat_deg=float(gcs_lat),
        tilt_deg=float(gcs_tilt),
        half_angle_deg=float(gcs_half_angle),
        kappa=float(gcs_kappa),
    )

    return config, gcs_params, obs_df, run_clicked

    """
    Render the full sidebar and return ``(config, run_clicked)``.

    The returned :class:`~heliotrace.models.schemas.SimulationConfig` holds the
    current value of every widget.  ``run_clicked`` is ``True`` only on the
    exact frame when the user pressed the Run button.

    :return: ``(SimulationConfig, bool)``
    """
    with st.sidebar:
        st.title("⚙️ Configuration")

        # ------------------------------------------------------------------ #
        # 1. Event Information
        # ------------------------------------------------------------------ #
        st.header("📅 Event Info")

        event_str = st.text_input(
            "Event Date (YYYYMMDD)",
            value="20231028",
            help="Used as an identifier in titles and file names.",
        )
        try:
            cme_launch_day = datetime.strptime(event_str, "%Y%m%d")
            st.caption(f"📆 {cme_launch_day.strftime('%d %B %Y')}")
        except ValueError:
            st.warning("Invalid date format — expected YYYYMMDD.")
            cme_launch_day = datetime(2023, 10, 28)

        st.divider()

        # ------------------------------------------------------------------ #
        # 2. Target Configuration
        # ------------------------------------------------------------------ #
        st.header("🎯 Target")

        preset_names  = list(TARGET_PRESETS.keys())
        preset_choice = st.selectbox(
            "Target body",
            options=preset_names,
            index=0,
            help="Select a preconfigured target, or choose 'Custom' to enter coordinates manually.",
        )

        is_custom  = TARGET_PRESETS[preset_choice] is None
        preset_vals: dict[str, float] = TARGET_PRESETS.get(preset_choice) or {}  # type: ignore[assignment]

        if is_custom:
            target_name = st.text_input("Target name", value="Custom")
            target_lon  = st.number_input("Longitude [deg]", value=0.0,  min_value=-180.0, max_value=180.0, step=0.5, format="%.1f")
            target_lat  = st.number_input("Latitude [deg]",  value=0.0,  min_value=-90.0,  max_value=90.0,  step=0.5, format="%.1f")
            target_dist = st.number_input("Distance [AU]",   value=1.0,  min_value=0.01,   max_value=5.0,   step=0.01, format="%.3f")
        else:
            target_name = preset_choice.split(" (")[0]
            target_lon  = preset_vals["lon"]
            target_lat  = preset_vals["lat"]
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
        # 3. GCS Uncertainty
        # ------------------------------------------------------------------ #
        st.header("📏 Height Measurement")

        height_error = st.number_input(
            "Height error ± [R☉]",
            value=0.25,
            min_value=0.01,
            max_value=5.0,
            step=0.05,
            format="%.2f",
            help="Symmetric ±uncertainty applied to every GCS height measurement.",
        )

        st.divider()

        # ------------------------------------------------------------------ #
        # 4. Drag Model Parameters
        # ------------------------------------------------------------------ #
        st.header("🌬️ Drag Model Parameters")

        w = st.slider(
            "Solar wind speed w [km/s]  (DBM)",
            min_value=250,
            max_value=700,
            value=390,
            step=10,
            help="Constant ambient solar wind speed used by the standard DBM.",
        )

        w_type = st.radio(
            "Solar wind regime  (MODBM)",
            options=["slow", "fast"],
            index=0,
            horizontal=True,
            help="Venzmer & Bothmer (2018) background wind profile.",
        )

        ssn = st.slider(
            "Smoothed sunspot number (SSN)  (MODBM)",
            min_value=0,
            max_value=300,
            value=100,
            step=5,
            help="Monthly smoothed total sunspot number for the MODBM density profile.",
        )

        c_d = st.number_input(
            "Drag coefficient c_d",
            value=1.0,
            min_value=0.1,
            max_value=5.0,
            step=0.1,
            format="%.1f",
            help="Dimensionless drag coefficient (converges to ~1 beyond ~12 R☉, Cargill 2004).",
        )

        st.divider()

        # ------------------------------------------------------------------ #
        # 5. Optional / Advanced settings
        # ------------------------------------------------------------------ #
        with st.expander("⚙️ Advanced / Optional"):
            toa_raw: Optional[str] = st.text_input(
                "Expected arrival time (optional)",
                value="",
                placeholder="DD/MM/YYYY HH:MM:SS",
                help="Observed/predicted arrival for comparison. Leave blank to skip.",
            ) or None

            if toa_raw:
                try:
                    datetime.strptime(toa_raw, "%d/%m/%Y %H:%M:%S")
                    st.success("✓ Valid arrival time format")
                except ValueError:
                    st.warning("⚠ Expected format: DD/MM/YYYY HH:MM:SS")
                    toa_raw = None

            m_override_raw: float = st.number_input(
                "CME mass override [g]  (0 = use Pluta formula)",
                value=0.0,
                min_value=0.0,
                format="%.2e",
                help="Override the Pluta (2018) mass formula. Enter 0 to keep the formula.",
            )
            m_override_g: Optional[float] = m_override_raw if m_override_raw > 0.0 else None

        st.divider()

        # ------------------------------------------------------------------ #
        # 6. Run button
        # ------------------------------------------------------------------ #
        run_clicked: bool = st.button(
            "▶ Run Simulation",
            type="primary",
            use_container_width=True,
        )

    config = SimulationConfig(
        event_str=event_str,
        cme_launch_day=cme_launch_day,
        target=target,
        height_error=float(height_error),
        w=float(w),
        w_type=str(w_type),
        ssn=float(ssn),
        c_d=float(c_d),
        toa_raw=toa_raw,
        m_override_g=m_override_g,
    )

    return config, run_clicked
