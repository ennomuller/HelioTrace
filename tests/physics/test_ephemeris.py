from datetime import datetime
from unittest.mock import patch

import astropy.units as u
import pytest
from astropy.coordinates import SkyCoord

from heliotrace.physics.ephemeris import EphemerisError, get_target_coordinates


@patch("heliotrace.physics.ephemeris.get_body_heliographic_stonyhurst")
def test_get_target_coordinates_planet(mock_get_body):
    mock_get_body.return_value = SkyCoord(
        lon=10 * u.deg, lat=5 * u.deg, radius=0.5 * u.AU, frame="heliographic_stonyhurst"
    )

    lon, lat, dist = get_target_coordinates("Venus", datetime(2024, 1, 1), is_planet=True)

    assert lon == 10.0
    assert lat == 5.0
    assert dist == 0.5
    mock_get_body.assert_called_once()


@patch("heliotrace.physics.ephemeris.get_horizons_coord")
def test_get_target_coordinates_satellite(mock_get_horizons):
    mock_get_horizons.return_value = SkyCoord(
        lon=-10 * u.deg, lat=-5 * u.deg, radius=0.8 * u.AU, frame="heliographic_stonyhurst"
    )

    lon, lat, dist = get_target_coordinates("STEREO-A", datetime(2024, 1, 1), is_planet=False)

    assert lon == -10.0
    assert lat == -5.0
    assert dist == 0.8
    mock_get_horizons.assert_called_once()


@patch("heliotrace.physics.ephemeris.get_horizons_coord")
def test_get_target_coordinates_satellite_error(mock_get_horizons):
    mock_get_horizons.side_effect = Exception("Network error")

    with pytest.raises(EphemerisError, match="Failed to fetch coordinates"):
        get_target_coordinates("STEREO-A", datetime(2024, 1, 2), is_planet=False)
