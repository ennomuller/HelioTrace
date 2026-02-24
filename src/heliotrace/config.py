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
# ---------------------------------------------------------------------------
TARGET_PRESETS: dict[str, dict[str, float] | None] = {
    "Earth": {"lon": 0.0, "lat": 0.0, "distance": 1.0},
    "Parker Solar Probe (example)": {"lon": -62.484, "lat": 2.834, "distance": 0.08},
    "Custom": None,  # sentinel — user fills in the fields manually
}

# ---------------------------------------------------------------------------
# Default GCS rows loaded into the data editor on first visit
# ---------------------------------------------------------------------------
DEFAULT_GCS_ROWS: list[dict] = [
    {
        "datetime":   datetime(2023, 10, 28, 14, 0),
        "lon":        5.5,
        "lat":        -20.1,
        "tilt":       -7.5,
        "half_angle": 30.0,
        "height":     10.0,
        "kappa":      0.42,
    },
    {
        "datetime":   datetime(2023, 10, 28, 14, 30),
        "lon":        5.5,
        "lat":        -20.1,
        "tilt":       -7.5,
        "half_angle": 30.0,
        "height":     12.1,
        "kappa":      0.42,
    },
    {
        "datetime":   datetime(2023, 10, 28, 15, 0),
        "lon":        5.5,
        "lat":        -20.1,
        "tilt":       -7.5,
        "half_angle": 30.0,
        "height":     14.0,
        "kappa":      0.42,
    },
]
