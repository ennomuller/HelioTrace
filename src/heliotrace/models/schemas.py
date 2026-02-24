"""
Pure data model definitions for the CME Explorer simulation pipeline.

Design principles:
- All dataclasses are plain Python — zero Streamlit coupling.
- All inputs live in SimulationConfig; all outputs live in SimulationResults.
- This module is safely importable in test and non-Streamlit contexts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------

@dataclass
class TargetConfig:
    """Heliographic configuration of the impact target."""

    name:     str
    lon:      float   # Stonyhurst longitude [deg]
    lat:      float   # Stonyhurst latitude [deg]
    distance: float   # Radial distance from Sun [AU]


@dataclass
class SimulationConfig:
    """All user-controlled inputs for one simulation run."""

    event_str:      str               # YYYYMMDD label for display/file naming
    cme_launch_day: datetime          # Parsed from event_str
    target:         TargetConfig

    # GCS uncertainty
    height_error:   float             # ± measurement error on each height [R_sun]

    # DBM parameters
    w:              float             # Ambient solar wind speed [km/s]

    # MODBM parameters
    w_type:         str               # 'slow' | 'fast'
    ssn:            float             # Monthly smoothed total sunspot number

    # Shared drag parameters
    c_d:            float             # Drag coefficient (dimensionless)

    # Optional overrides
    toa_raw:        Optional[str]     # Expected arrival "DD/MM/YYYY HH:MM:SS"; None → skip
    m_override_g:   Optional[float]   # CME mass override [g]; None → use Pluta formula


# ---------------------------------------------------------------------------
# Derived / output models
# ---------------------------------------------------------------------------

@dataclass
class DerivedGCSParams:
    """Parameters extracted from the GCS data table and the linear H-T fit."""

    r0_rsun:          float     # Initial height (max of observed) [R_sun]
    t0:               datetime  # Launch reference time (time of max observed height)
    alpha_deg:        float     # Median half-angle [deg]
    kappa:            float     # Median aspect ratio
    lon_deg:          float     # Median Stonyhurst longitude [deg]
    lat_deg:          float     # Median latitude [deg]
    tilt_deg:         float     # Median tilt [deg]
    v_apex_kms:       float     # Apex velocity from linear fit [km/s]
    v_apex_error_kms: float     # 1σ uncertainty on v_apex [km/s]
    fit_chi_squared:  float     # χ² of the linear fit
    fit_slope:        float     # Raw slope [R_sun/s] (needed for plot reconstruction)
    fit_intercept:    float     # Raw intercept [R_sun] (needed for plot reconstruction)


@dataclass
class PropagationSeries:
    """Pre-sampled ODE solution arrays ready for Plotly — avoids storing raw scipy objects."""

    t_hours: list[float]   # Elapsed propagation time [h]
    r_rsun:  list[float]   # CME distance from Sun [R_sun]
    v_kms:   list[float]   # CME radial velocity [km/s]


@dataclass
class SimulationResults:
    """All outputs from one complete simulation run."""

    derived:          DerivedGCSParams
    projection_ratio: float
    v0_kms:           float
    target_hit:       bool

    # DBM
    dbm_series:               Optional[PropagationSeries]
    elapsed_time_DBM_h:       Optional[float]   # Transit time [h]
    velocity_arrival_DBM_kms: Optional[float]   # Impact speed [km/s]
    arrival_time_DBM:         Optional[datetime]

    # MODBM
    modbm_series:               Optional[PropagationSeries]
    elapsed_time_MODBM_h:       Optional[float]
    velocity_arrival_MODBM_kms: Optional[float]
    arrival_time_MODBM:         Optional[datetime]
