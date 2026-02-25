"""
Sidebar input panel for HelioTrace.

Renders all user-controllable parameters and returns a ``(SimulationConfig, run_clicked)`` tuple.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

import streamlit as st

from heliotrace.config import TARGET_PRESETS
from heliotrace.models.schemas import SimulationConfig, TargetConfig


def render_sidebar(show_run_button: bool = True) -> tuple[SimulationConfig, bool]:
    """
    Render the full sidebar and return ``(config, run_clicked)``.

    The returned :class:`~heliotrace.models.schemas.SimulationConfig` holds the
    current value of every widget.  ``run_clicked`` is ``True`` only on the
    exact frame when the user pressed the Run button (only possible when
    ``show_run_button=True``).

    :param show_run_button: When ``False`` the **▶ Run Simulation** button is
        suppressed.  Set to ``False`` on the GCS Observations page so the
        button only appears on the Propagation page.
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
            target_lon  = st.number_input("Longitude [deg]", value=0.0,  min_value=-180.0, max_value=180.0, step=0.5)
            target_lat  = st.number_input("Latitude [deg]",  value=0.0,  min_value=-90.0,  max_value=90.0,  step=0.5)
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
        # 6. Run button  (propagation page only)
        # ------------------------------------------------------------------ #
        if show_run_button:
            run_clicked: bool = st.button(
                "▶ Run Simulation",
                type="primary",
                use_container_width=True,
            )
        else:
            run_clicked = False

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
