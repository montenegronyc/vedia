"""Ayanamsha, Julian Day, and Ascendant calculations.

Provides helper functions for:
- Lahiri ayanamsha value lookup
- Julian Day conversion from calendar date/time
- Sidereal ascendant computation using whole-sign houses
"""

import swisseph as swe


def get_ayanamsha_value(julian_day: float) -> float:
    """Return the Lahiri ayanamsha value for a given Julian Day.

    The ayanamsha is the angular difference between the tropical and
    sidereal zodiacs. Lahiri (Chitrapaksha) is the Indian government
    standard.

    Args:
        julian_day: Julian Day number in Universal Time.

    Returns:
        Ayanamsha in degrees (typically ~23-25 degrees for modern dates).
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    return swe.get_ayanamsa_ut(julian_day)


def calculate_julian_day(
    year: int,
    month: int,
    day: int,
    hour_decimal: float,
    utc_offset: float = 0.0,
) -> float:
    """Convert a calendar date and time to Julian Day number.

    Converts local time to UTC before calling Swiss Ephemeris, which
    expects UT (Universal Time).

    Args:
        year: Calendar year (e.g. 1990).
        month: Month number 1-12.
        day: Day of month 1-31.
        hour_decimal: Local time as a decimal hour (e.g. 14.5 for 2:30 PM).
        utc_offset: Hours east of UTC (e.g. 5.5 for IST, -5 for EST).
            Defaults to 0 (already UTC).

    Returns:
        Julian Day number in Universal Time.
    """
    # Convert local time to UTC by subtracting the UTC offset
    ut_hour = hour_decimal - utc_offset

    # Handle day rollover from timezone conversion.
    # If ut_hour goes below 0 or above 24 we need to adjust the date.
    # We let swe.julday handle fractional hours outside 0-24 correctly,
    # but for clarity we normalise explicitly.
    extra_days = 0
    if ut_hour < 0.0:
        # Rolled back to previous day(s)
        while ut_hour < 0.0:
            ut_hour += 24.0
            extra_days -= 1
    elif ut_hour >= 24.0:
        # Rolled forward to next day(s)
        while ut_hour >= 24.0:
            ut_hour -= 24.0
            extra_days += 1

    # Apply day adjustment using Julian Day arithmetic for correctness
    # across month/year boundaries.
    if extra_days != 0:
        # Get JD for the base date at 0h UT, then add/subtract days
        jd_base = swe.julday(year, month, day, 0.0)
        jd_adjusted = jd_base + extra_days
        # Convert back to calendar to get the corrected year/month/day
        adjusted = swe.revjul(jd_adjusted)
        year, month, day = int(adjusted[0]), int(adjusted[1]), int(adjusted[2])

    return swe.julday(year, month, day, ut_hour)


def calculate_ascendant(
    julian_day: float,
    latitude: float,
    longitude: float,
) -> tuple[float, float]:
    """Compute the sidereal ascendant (lagna) for a given time and place.

    Uses whole-sign houses (system 'W') in sidereal mode with Lahiri
    ayanamsha.

    Args:
        julian_day: Julian Day number in Universal Time.
        latitude: Geographic latitude in decimal degrees (north positive).
        longitude: Geographic longitude in decimal degrees (east positive).

    Returns:
        Tuple of (ascendant_longitude, sidereal_time) where:
        - ascendant_longitude is the sidereal longitude of the ascendant
          in degrees (0-360).
        - sidereal_time is the local sidereal time in hours.

    To derive the ascendant sign and degree::

        ascendant_sign = int(ascendant_longitude / 30) + 1   # 1-12
        ascendant_degree = ascendant_longitude % 30           # 0-30
    """
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    # swe.houses_ex returns (cusps_tuple, ascmc_tuple)
    # cusps_tuple: 13 elements (index 0 unused for some systems; 1-12 are house cusps)
    # ascmc_tuple: [0]=Ascendant, [1]=MC, [2]=ARMC (sidereal time in degrees), ...
    cusps, ascmc = swe.houses_ex(
        julian_day,
        latitude,
        longitude,
        b'W',
        swe.FLG_SIDEREAL,
    )

    ascendant_longitude = ascmc[0] % 360.0

    # ARMC is Right Ascension of the Midheaven in degrees; convert to hours
    sidereal_time = ascmc[2] / 15.0

    return ascendant_longitude, sidereal_time
