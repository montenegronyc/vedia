"""Calculate current (real-time) planetary positions in sidereal zodiac.

Provides functions to get the sidereal longitude of all nine Vedic grahas
for the current moment or for an arbitrary Julian Day. Positions use Lahiri
ayanamsha and are suitable for transit analysis against a natal chart.
"""

import swisseph as swe
from datetime import datetime, timezone

from ..models import PLANETS, PlanetPosition
from ..calc.nakshatras import get_nakshatra_info


# Swiss Ephemeris planet IDs for the seven visible grahas + Rahu (mean node)
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


def get_current_positions() -> list[PlanetPosition]:
    """Get current sidereal positions of all 9 Vedic planets.

    Uses the system clock in UTC to compute the Julian Day, then delegates
    to :func:`get_positions_for_date`.

    Returns:
        List of PlanetPosition instances in standard Vedic order.
        The ``house`` field is set to 0 because there is no natal ascendant
        context for a standalone transit snapshot.
    """
    now = datetime.now(timezone.utc)
    jd = swe.julday(
        now.year, now.month, now.day,
        now.hour + now.minute / 60.0 + now.second / 3600.0,
    )
    return get_positions_for_date(jd)


def get_positions_for_date(julian_day: float) -> list[PlanetPosition]:
    """Get sidereal positions for a given Julian Day.

    Calculates longitude, speed, nakshatra, retrograde status, and sign
    for every planet in :data:`~vedia.models.PLANETS`. Ketu is derived
    as 180 degrees opposite Rahu.

    Args:
        julian_day: Julian Day number in Universal Time.

    Returns:
        List of PlanetPosition instances in standard Vedic order.
        The ``house`` field is 0 (no natal context).
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # ------------------------------------------------------------------
    # First pass: compute raw sidereal longitudes and speeds
    # ------------------------------------------------------------------
    raw: dict[str, tuple[float, float]] = {}  # name -> (longitude, speed)

    for name, pid in _SWE_PLANET_IDS.items():
        result, _retflag = swe.calc_ut(
            julian_day, pid,
            swe.FLG_SIDEREAL | swe.FLG_SPEED,
        )
        longitude = result[0] % 360.0
        speed = result[3]
        raw[name] = (longitude, speed)

    # Ketu is always exactly opposite Rahu
    rahu_lon, rahu_speed = raw['Rahu']
    raw['Ketu'] = ((rahu_lon + 180.0) % 360.0, -rahu_speed)

    # ------------------------------------------------------------------
    # Second pass: build PlanetPosition objects in standard order
    # ------------------------------------------------------------------
    positions: list[PlanetPosition] = []

    for name in PLANETS:
        lon, speed = raw[name]

        sign = int(lon / 30.0) + 1
        sign_deg = lon % 30.0

        is_retro = (speed < 0.0) and (name not in _NO_RETROGRADE)

        nak_num, nak_pada, nak_lord = get_nakshatra_info(lon)

        positions.append(PlanetPosition(
            planet=name,
            longitude=round(lon, 6),
            sign=sign,
            sign_degree=round(sign_deg, 4),
            nakshatra=nak_num,
            nakshatra_pada=nak_pada,
            nakshatra_lord=nak_lord,
            house=0,  # no natal context for standalone transits
            is_retrograde=is_retro,
            speed=round(speed, 6),
        ))

    return positions
