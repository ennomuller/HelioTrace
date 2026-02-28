"""
Multi-target selector component for the HelioTrace sidebar.

Responsibilities:
- Render Earth (fixed, always present) with editable lon / lat / distance inputs
  displayed side-by-side in three columns.
- Render any additional targets the user has added (celestial bodies or spacecraft)
  with the same three-column layout plus an auto-calculate button and a remove button.
- Provide per-target "Fetch position" buttons that call sunpy to compute the actual
  Heliographic Stonyhurst position for the configured event date.
- Expose a radio widget when there are multiple targets so the user can select the
  one that is fed to the simulation.
- Return a :class:`~heliotrace.models.schemas.TargetConfig` for the selected target.

Session-state keys used (defined in heliotrace.config):
- ``KEY_TARGET_LIST``     — list of target dicts, each with id/name/type/key/lon/lat/distance/fixed
- ``KEY_NEXT_TARGET_ID``  — monotonically increasing counter for stable unique IDs
- ``KEY_SELECTED_TARGET`` — id of the currently selected (simulation) target
"""

from __future__ import annotations

import re
from datetime import datetime

import streamlit as st

from heliotrace.config import (
    CELESTIAL_BODIES,
    KEY_NEXT_TARGET_ID,
    KEY_SELECTED_TARGET,
    KEY_TARGET_LIST,
    SPACECRAFT,
)
from heliotrace.models.schemas import TargetConfig

# ---------------------------------------------------------------------------
# Slug helper
# ---------------------------------------------------------------------------


def _make_slug(name: str, target_id: int) -> str:
    """
    Build a stable, filesystem-safe slug used as the base for widget keys.

    Example: ("Parker Solar Probe", 3) → "parker_solar_probe_3"
    """
    base = name.lower().replace(" ", "_").replace("-", "_")
    base = re.sub(r"[^a-z0-9_]", "", base)
    return f"{base}_{target_id}"


# ---------------------------------------------------------------------------
# Position fetch helpers
# ---------------------------------------------------------------------------


def _fetch_body_position(
    body_name: str,
    obs_time: datetime,
) -> tuple[float, float, float] | None:
    """
    Retrieve Heliographic Stonyhurst position via
    ``sunpy.coordinates.get_body_heliographic_stonyhurst``.

    :param body_name: Lower-case body name accepted by sunpy (e.g. ``"mars"``).
    :param obs_time: Observation datetime used to evaluate the ephemeris.
    :returns: ``(lon_deg, lat_deg, dist_AU)`` on success, ``None`` on failure.
    """
    try:
        import astropy.units as u
        from astropy.time import Time
        from sunpy.coordinates import get_body_heliographic_stonyhurst

        coord = get_body_heliographic_stonyhurst(body_name, time=Time(obs_time))
        return (
            float(coord.lon.deg),
            float(coord.lat.deg),
            float(coord.radius.to(u.AU).value),
        )
    except Exception as exc:
        st.error(f"Could not fetch position for '{body_name}': {exc}")
        return None


def _fetch_spacecraft_position(
    horizons_id: str,
    obs_time: datetime,
) -> tuple[float, float, float] | None:
    """
    Retrieve Heliographic Stonyhurst position via
    ``sunpy.coordinates.get_horizons_coord`` (queries JPL Horizons; requires
    internet and *astroquery*).

    :param horizons_id: JPL Horizons target ID string, e.g. ``"-96"`` for PSP.
    :param obs_time: Observation datetime.
    :returns: ``(lon_deg, lat_deg, dist_AU)`` on success, ``None`` on failure.
    """
    try:
        import astropy.units as u
        from astropy.time import Time
        from sunpy.coordinates import get_horizons_coord

        coord = get_horizons_coord(horizons_id, time=Time(obs_time))
        hgs = coord.heliographic_stonyhurst
        return (
            float(hgs.lon.deg),
            float(hgs.lat.deg),
            float(hgs.radius.to(u.AU).value),
        )
    except Exception as exc:
        st.error(
            f"JPL Horizons lookup failed for ID '{horizons_id}': {exc}. "
            "Check your internet connection or try a different date."
        )
        return None


# ---------------------------------------------------------------------------
# Session-state helpers
# ---------------------------------------------------------------------------


def _get_targets() -> list[dict]:
    return st.session_state[KEY_TARGET_LIST]


def _set_targets(targets: list[dict]) -> None:
    st.session_state[KEY_TARGET_LIST] = targets


# ---------------------------------------------------------------------------
# Internal renderers
# ---------------------------------------------------------------------------


def _render_coord_inputs(target: dict) -> tuple[float, float, float]:
    """
    Render three-column lon / lat / distance number inputs for one target.

    Widget keys are ``target_lon_{slug}``, ``target_lat_{slug}``,
    ``target_dist_{slug}``.  The keys are pre-populated from the target dict
    on first render so that auto-calculate can later update them via
    ``st.session_state[key] = new_value; st.rerun()``.

    :returns: Current ``(lon_deg, lat_deg, distance_AU)`` values.
    """
    slug = target["key"]
    lon_key = f"target_lon_{slug}"
    lat_key = f"target_lat_{slug}"
    dist_key = f"target_dist_{slug}"

    # Pre-populate only on first render
    if lon_key not in st.session_state:
        st.session_state[lon_key] = target["lon"]
    if lat_key not in st.session_state:
        st.session_state[lat_key] = target["lat"]
    if dist_key not in st.session_state:
        st.session_state[dist_key] = target["distance"]

    col_lon, col_lat, col_dist = st.columns(3)
    lon = col_lon.number_input(
        "Lon [°]",
        min_value=-180.0,
        max_value=180.0,
        step=0.5,
        format="%.1f",
        key=lon_key,
        help="Stonyhurst heliographic longitude [deg].",
    )
    lat = col_lat.number_input(
        "Lat [°]",
        min_value=-90.0,
        max_value=90.0,
        step=0.5,
        format="%.1f",
        key=lat_key,
        help="Stonyhurst heliographic latitude [deg].",
    )
    dist = col_dist.number_input(
        "Dist [AU]",
        min_value=0.001,
        max_value=50.0,
        step=0.01,
        format="%.3f",
        key=dist_key,
        help="Radial distance from the Sun [AU].",
    )
    return float(lon), float(lat), float(dist)


def _auto_calculate(target: dict, obs_time: datetime) -> None:
    """
    Fetch the target's position from sunpy and write values into the Streamlit
    session state driving the number_input widgets, then call ``st.rerun()``.

    This is the correct Streamlit pattern for programmatically updating
    ``number_input`` widgets: set ``st.session_state[key]`` directly, then
    rerun — never rely on passing a new ``value=`` argument.
    """
    result: tuple[float, float, float] | None = None
    slug = target["key"]

    with st.spinner(f"Fetching {target['name']} position…"):
        if target["type"] == "body":
            result = _fetch_body_position(target["name"].lower(), obs_time)
        else:  # spacecraft
            horizons_id = SPACECRAFT.get(target["name"], target["name"])
            result = _fetch_spacecraft_position(horizons_id, obs_time)

    if result is None:
        return  # error already displayed by helper

    lon, lat, dist = result

    # Update widget state so number_inputs re-render with new values
    st.session_state[f"target_lon_{slug}"] = lon
    st.session_state[f"target_lat_{slug}"] = lat
    st.session_state[f"target_dist_{slug}"] = dist

    # Mirror into the targets list so defaults survive future reruns
    for t in _get_targets():
        if t["id"] == target["id"]:
            t["lon"] = lon
            t["lat"] = lat
            t["distance"] = dist
            break

    st.success(f"{target['name']}: lon={lon:.2f}°, lat={lat:.2f}°, dist={dist:.4f} AU")
    st.rerun()


def _remove_target(target_id: int) -> None:
    """
    Remove a target by id, clean up its widget state keys, and fall back
    the simulation selection to Earth (id=0) if needed.
    """
    targets = _get_targets()
    removed = next((t for t in targets if t["id"] == target_id), None)
    if removed:
        slug = removed["key"]
        for wkey in (
            f"target_lon_{slug}",
            f"target_lat_{slug}",
            f"target_dist_{slug}",
            f"autocalc_{slug}",
            f"remove_{slug}",
        ):
            st.session_state.pop(wkey, None)

    _set_targets([t for t in targets if t["id"] != target_id])

    if st.session_state[KEY_SELECTED_TARGET] == target_id:
        st.session_state[KEY_SELECTED_TARGET] = 0


def _add_target(name: str, target_type: str) -> None:
    """
    Append a new target to the session-state targets list with zero-value
    coordinates (the user is expected to hit 'Fetch position' to populate
    them, or enter values manually).
    """
    next_id: int = st.session_state[KEY_NEXT_TARGET_ID]
    slug = _make_slug(name, next_id)
    new_target: dict = {
        "id": next_id,
        "name": name,
        "type": target_type,
        "key": slug,
        "lon": 0.0,
        "lat": 0.0,
        "distance": 1.0,
        "fixed": False,
    }
    _get_targets().append(new_target)
    st.session_state[KEY_NEXT_TARGET_ID] = next_id + 1


def _render_single_target(target: dict, obs_time: datetime) -> None:
    """Render one target block: header, coord inputs, fetch button, remove button."""
    slug = target["key"]
    name = target["name"]

    if target["fixed"]:
        st.markdown(f"**{name}** *(default)*")
    else:
        hdr_col, rm_col = st.columns([5, 1])
        hdr_col.markdown(f"**{name}**")
        if rm_col.button("✕", key=f"remove_{slug}", help=f"Remove {name}"):
            _remove_target(target["id"])
            st.rerun()
            return

    _render_coord_inputs(target)

    if st.button(
        "🔄 Fetch position for event date",
        key=f"autocalc_{slug}",
        use_container_width=True,
        help=f"Query sunpy/JPL Horizons for {name}'s position on the event date.",
    ):
        _auto_calculate(target, obs_time)


def _render_add_target_controls() -> None:
    """Render the two dropdowns and Add buttons for adding new targets."""
    st.markdown("**Add target**")

    body_options = ["— select body —"] + list(CELESTIAL_BODIES.keys())
    sc_options = ["— select spacecraft —"] + list(SPACECRAFT.keys())

    body_col, sc_col = st.columns(2)

    with body_col:
        body_choice = st.selectbox(
            "Celestial body",
            options=body_options,
            index=0,
            key="add_body_select",
        )
        if st.button("+ Add body", key="add_body_btn", use_container_width=True):
            if body_choice != body_options[0]:
                existing_names = {t["name"] for t in _get_targets()}
                if body_choice in existing_names:
                    st.warning(f"'{body_choice}' is already in the target list.")
                else:
                    _add_target(name=body_choice, target_type="body")
                    st.session_state["add_body_select"] = body_options[0]
                    st.rerun()

    with sc_col:
        sc_choice = st.selectbox(
            "Spacecraft / probe",
            options=sc_options,
            index=0,
            key="add_sc_select",
        )
        if st.button("+ Add spacecraft", key="add_sc_btn", use_container_width=True):
            if sc_choice != sc_options[0]:
                existing_names = {t["name"] for t in _get_targets()}
                if sc_choice in existing_names:
                    st.warning(f"'{sc_choice}' is already in the target list.")
                else:
                    _add_target(name=sc_choice, target_type="spacecraft")
                    st.session_state["add_sc_select"] = sc_options[0]
                    st.rerun()


def _get_selected_target(targets: list[dict], selected_id: int) -> dict:
    """
    Return the target dict matching ``selected_id``, falling back to Earth
    (id=0) if not found.
    """
    result = next((t for t in targets if t["id"] == selected_id), None)
    if result is None:
        result = targets[0]
        st.session_state[KEY_SELECTED_TARGET] = result["id"]
    return result


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def render_target_selector(obs_time: datetime) -> TargetConfig:
    """
    Render the full multi-target section inside the sidebar and return the
    :class:`~heliotrace.models.schemas.TargetConfig` for the selected target.

    Must be called from within a ``with st.sidebar:`` block.

    :param obs_time: CME event datetime forwarded to sunpy for auto-calculation.
    :returns: :class:`~heliotrace.models.schemas.TargetConfig` ready for
              :class:`~heliotrace.models.schemas.SimulationConfig`.
    """
    st.subheader("🎯 Targets")

    targets: list[dict] = _get_targets()
    selected_id: int = st.session_state[KEY_SELECTED_TARGET]

    # ---- Per-target blocks -------------------------------------------------
    for target in targets:
        _render_single_target(target, obs_time)
        st.divider()

    # ---- Simulation target radio (only when >1 target) ---------------------
    if len(targets) > 1:
        st.markdown("**Select for simulation**")
        target_names = [t["name"] for t in targets]
        target_ids = [t["id"] for t in targets]

        current_idx = next((i for i, t in enumerate(targets) if t["id"] == selected_id), 0)
        chosen_name = st.radio(
            "Simulation target",
            options=target_names,
            index=current_idx,
            horizontal=True,
            label_visibility="collapsed",
            help="Select which target the CME propagation is computed toward.",
        )
        chosen_idx = target_names.index(chosen_name)
        selected_id = target_ids[chosen_idx]
        st.session_state[KEY_SELECTED_TARGET] = selected_id

        st.divider()

    # ---- Add-target controls -----------------------------------------------
    _render_add_target_controls()

    # ---- Build TargetConfig for the selected target ------------------------
    sel = _get_selected_target(targets, selected_id)
    slug = sel["key"]

    return TargetConfig(
        name=sel["name"],
        lon=float(st.session_state.get(f"target_lon_{slug}", sel["lon"])),
        lat=float(st.session_state.get(f"target_lat_{slug}", sel["lat"])),
        distance=float(st.session_state.get(f"target_dist_{slug}", sel["distance"])),
    )
