"""
Ephemeris lookups for planets and spacecraft using sunpy.
"""
from datetime import datetime
import streamlit as st
from astropy.time import Time
import astropy.units as u

try:
    from sunpy.coordinates import get_body_heliographic_stonyhurst, get_horizons_coord
except ImportError:
    pass # Handled by dependency management, but keeps type checkers happy if missing during dev

class EphemerisError(Exception):
    """Raised when an ephemeris lookup fails."""
    pass

@st.cache_data(ttl=3600)
def get_target_coordinates(body_name: str, obstime: datetime, is_planet: bool) -> tuple[float, float, float]:
    """
    Fetch coordinates for a given body and time.
    Returns (lon_deg, lat_deg, radius_au).
    """
    time_obj = Time(obstime)
    try:
        if is_planet:
            coord = get_body_heliographic_stonyhurst(body_name.lower(), time=time_obj)
        else:
            coord = get_horizons_coord(body_name, time=time_obj)
            
        lon = coord.lon.to_value(u.deg)
        lat = coord.lat.to_value(u.deg)
        dist = coord.radius.to_value(u.AU)
        
        return lon, lat, dist
    except Exception as e:
        raise EphemerisError(f"Failed to fetch coordinates for {body_name}: {e}") from e
