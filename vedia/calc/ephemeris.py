"""Swiss Ephemeris wrapper for Vedic planet position calculations.

Uses pyswisseph (swe) with Lahiri ayanamsha to compute sidereal positions
of the nine Vedic grahas: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn,
Rahu, and Ketu.
"""

import swisseph as swe

from ..models import (
    COMBUSTION_DEGREES,
    PLANETS,
    PlanetPosition,
)
from .nakshatras import get_dignity, get_nakshatra_info


# Swiss Ephemeris planet IDs for the seven visible grahas + Rahu
_SWE_PLANET_IDS: dict[str, int] = {
    'Sun': swe.SUN,          # 0
    'Moon': swe.MOON,        # 1
    'Mars': swe.MARS,        # 4
    'Mercury': swe.MERCURY,  # 2
    'Jupiter': swe.JUPITER,  # 5
    'Venus': swe.VENUS,      # 3
    'Saturn': swe.SATURN,    # 6
    'Rahu': swe.MEAN_NODE,   # 10
}

# Planets that never appear retrograde in Vedic astrology
_NO_RETROGRADE = {'Sun', 'Moon', 'Rahu', 'Ketu'}


def _longitude_to_sign(longitude: float) -> tuple[int, float]:
    """Convert absolute sidereal longitude (0-360) to sign number and degree.

    Returns:
        (sign, sign_degree) where sign is 1-12 and sign_degree is 0-30.
    """
    longitude = longitude % 360.0
    sign = int(longitude / 30.0) + 1
    sign_degree = longitude % 30.0
    return sign, sign_degree


def _whole_sign_house(planet_sign: int, asc_sign: int) -> int:
    """Compute whole-sign house number.

    The ascendant sign is always house 1. Subsequent signs map to
    houses 2 through 12.
    """
    return ((planet_sign - asc_sign) % 12) + 1


def _angular_distance(lon1: float, lon2: float) -> float:
    """Shortest angular distance between two longitudes on a 360-degree circle."""
    diff = abs((lon1 % 360.0) - (lon2 % 360.0))
    return min(diff, 360.0 - diff)


def _is_combust(planet: str, planet_longitude: float, sun_longitude: float) -> bool:
    """Check whether a planet is combust (too close to the Sun).

    Sun, Rahu, and Ketu cannot be combust. Combustion thresholds are
    defined in models.COMBUSTION_DEGREES.
    """
    if planet not in COMBUSTION_DEGREES:
        return False
    threshold = COMBUSTION_DEGREES[planet]
    return _angular_distance(planet_longitude, sun_longitude) <= threshold


def calculate_planet_positions(
    julian_day: float,
    asc_sign: int,
) -> list[PlanetPosition]:
    """Calculate sidereal positions of all nine Vedic grahas.

    Args:
        julian_day: Julian Day number in Universal Time.
        asc_sign: The sign number (1-12) of the ascendant, used for
            whole-sign house computation.

    Returns:
        List of PlanetPosition dataclass instances, one per graha in the
        standard Vedic order (Sun, Moon, Mars, Mercury, Jupiter, Venus,
        Saturn, Rahu, Ketu).
    """
    # Ensure sidereal mode is set for every call (idempotent)
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # ------------------------------------------------------------------
    # First pass: compute raw positions for all planets with swe IDs.
    # We store results keyed by planet name so we can derive Ketu from
    # Rahu and also look up Sun longitude for combustion checks.
    # ------------------------------------------------------------------
    raw: dict[str, tuple[float, float]] = {}  # name -> (longitude, speed_long)

    for name, pid in _SWE_PLANET_IDS.items():
        result, retflag = swe.calc_ut(
            julian_day,
            pid,
            swe.FLG_SIDEREAL | swe.FLG_SPEED,
        )
        # result is (longitude, latitude, distance, speed_long, speed_lat, speed_dist)
        longitude = result[0] % 360.0
        speed_long = result[3]
        raw[name] = (longitude, speed_long)

    # Ketu is always exactly opposite Rahu
    rahu_lon, rahu_speed = raw['Rahu']
    ketu_lon = (rahu_lon + 180.0) % 360.0
    ketu_speed = -rahu_speed  # speed is mirrored
    raw['Ketu'] = (ketu_lon, ketu_speed)

    sun_longitude = raw['Sun'][0]

    # ------------------------------------------------------------------
    # Second pass: build PlanetPosition objects in standard order
    # ------------------------------------------------------------------
    positions: list[PlanetPosition] = []

    for name in PLANETS:
        longitude, speed_long = raw[name]
        sign, sign_degree = _longitude_to_sign(longitude)
        house = _whole_sign_house(sign, asc_sign)

        # Nakshatra
        nakshatra_index, pada, nakshatra_lord = get_nakshatra_info(longitude)

        # Retrograde: negative speed, but not for bodies that never retrograde
        is_retrograde = (speed_long < 0.0) and (name not in _NO_RETROGRADE)

        # Dignity
        dignity = get_dignity(name, sign, sign_degree)

        # Combustion
        is_combust = _is_combust(name, longitude, sun_longitude)

        positions.append(
            PlanetPosition(
                planet=name,
                longitude=round(longitude, 6),
                sign=sign,
                sign_degree=round(sign_degree, 4),
                nakshatra=nakshatra_index,
                nakshatra_pada=pada,
                nakshatra_lord=nakshatra_lord,
                house=house,
                is_retrograde=is_retrograde,
                speed=round(speed_long, 6),
                dignity=dignity,
                is_combust=is_combust,
            )
        )

    return positions
