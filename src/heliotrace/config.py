"""
Application-level configuration: event presets and default GCS table rows.

This is the single source of truth for static data.  Add new preset events here.
"""

from __future__ import annotations

from datetime import datetime

# ---------------------------------------------------------------------------
# Session-state key constants — shared across UI and tests
# ---------------------------------------------------------------------------
KEY_SIM_RESULTS: str = "simulation_results"
KEY_SIM_CONFIG: str = "simulation_config"

# ---------------------------------------------------------------------------
# Target presets  (name → {lon_deg, lat_deg, distance_au} | None for Custom)
# Kept for legacy compatibility with tests.
# ---------------------------------------------------------------------------
TARGET_PRESETS: dict[str, dict[str, float] | None] = {
    "Earth": {"lon": 0.0, "lat": 0.0, "distance": 1.0},
    "Parker Solar Probe (example)": {"lon": -62.484, "lat": 2.834, "distance": 0.08},
    "Custom": None,  # sentinel — user fills in the fields manually
}

# ---------------------------------------------------------------------------
# Celestial bodies — supported by sunpy.coordinates.get_body_heliographic_stonyhurst
# Keys = display name, values = body name passed to sunpy (Astropy ERFA/DE ephemeris)
# ---------------------------------------------------------------------------
CELESTIAL_BODIES: dict[str, str] = {
    "Mercury": "mercury",
    "Venus": "venus",
    "Mars": "mars",
    "Jupiter": "jupiter",
    "Saturn": "saturn",
    "Uranus": "uranus",
    "Neptune": "neptune",
    "Moon": "moon",
    "Pluto": "pluto",
}

# ---------------------------------------------------------------------------
# Spacecraft — supported by sunpy.coordinates.get_horizons_coord (JPL Horizons)
# Keys = display name, values = JPL Horizons ID string (negative = spacecraft)
# ---------------------------------------------------------------------------
SPACECRAFT: dict[str, str] = {
    "Parker Solar Probe": "-96",
    "Solar Orbiter": "-144",
    "STEREO-A": "-234",
    "STEREO-B": "-235",
    "Solar Dynamics Observatory": "-82",
    "SOHO": "-21",
    "BepiColombo": "-121",
    "MAVEN": "-202",
    "Juno": "-61",
    "Wind": "-8",
    "ACE": "-92",
    "DSCOVR": "-25",
}

# ---------------------------------------------------------------------------
# Session-state key constants for the multi-target selector
# ---------------------------------------------------------------------------
KEY_TARGET_LIST: str = "targets"
KEY_NEXT_TARGET_ID: str = "next_target_id"
KEY_SELECTED_TARGET: str = "selected_target_id"

# ---------------------------------------------------------------------------
# Default GCS rows loaded into the data editor on first visit
# ---------------------------------------------------------------------------

# Compact observation rows for the sidebar table (time + height only)
DEFAULT_OBS_ROWS: list[dict] = [
    {"datetime": datetime(2023, 10, 28, 14, 0), "height": 10.0},
    {"datetime": datetime(2023, 10, 28, 14, 30), "height": 12.1},
    {"datetime": datetime(2023, 10, 28, 15, 0), "height": 14.0},
]

# Full 7-column rows (kept for tests and legacy compatibility)
DEFAULT_GCS_ROWS: list[dict] = [
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
