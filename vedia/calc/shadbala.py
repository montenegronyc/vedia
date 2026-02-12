"""Shadbala (six-fold planetary strength) calculation module.

Shadbala quantifies planetary strength through six components:
1. Sthana Bala - Positional strength (dignity + uchcha bala)
2. Dig Bala - Directional strength (house placement)
3. Kala Bala - Temporal strength (day/night, hora)
4. Chesta Bala - Motional strength (retrograde, speed)
5. Naisargika Bala - Natural strength (fixed per planet)
6. Drik Bala - Aspectual strength (benefic/malefic aspects)

Reference: Brihat Parashara Hora Shastra, chapters on Shadbala.
"""

from ..models import (
    ShadbalaResult,
    PlanetPosition,
    EXALTATION,
    DEBILITATION,
    OWN_SIGNS,
    MOOLATRIKONA,
    SIGN_LORDS,
    NATURAL_FRIENDS,
    NATURAL_ENEMIES,
)


# Deep exaltation degrees as absolute longitude (sign_start + degree_in_sign).
# Sun: Aries 10 = 10, Moon: Taurus 3 = 33, Mars: Cap 28 = 298,
# Mercury: Virgo 15 = 165, Jupiter: Cancer 5 = 95, Venus: Pisces 27 = 357,
# Saturn: Libra 20 = 200.
_DEEP_EXALTATION_LONGITUDE = {
    'Sun': 10.0,       # Aries 10
    'Moon': 33.0,      # Taurus 3
    'Mars': 298.0,     # Capricorn 28
    'Mercury': 165.0,  # Virgo 15
    'Jupiter': 95.0,   # Cancer 5
    'Venus': 357.0,    # Pisces 27
    'Saturn': 200.0,   # Libra 20
}

# Deep debilitation is exactly 180 degrees from deep exaltation.
_DEEP_DEBILITATION_LONGITUDE = {
    planet: (deg + 180.0) % 360.0
    for planet, deg in _DEEP_EXALTATION_LONGITUDE.items()
}

# Dignity scores
_DIGNITY_SCORES = {
    'exalted': 60.0,
    'moolatrikona': 45.0,
    'own': 30.0,
    'friendly': 22.5,
    'neutral': 15.0,
    'enemy': 7.5,
    'debilitated': 0.0,
}

# Dig bala: planet -> house where it is strongest
_DIG_BALA_STRONG_HOUSE = {
    'Sun': 10,
    'Mars': 10,
    'Moon': 4,
    'Venus': 4,
    'Jupiter': 1,
    'Mercury': 1,
    'Saturn': 7,
    'Rahu': 10,   # Treated like Saturn by some, we use 10th
    'Ketu': 4,    # Treated like Mars by some, we use 4th
}

# Naisargika bala: fixed natural strength values (in virupas)
_NAISARGIKA_BALA = {
    'Sun': 60.0,
    'Moon': 51.43,
    'Mars': 17.14,
    'Mercury': 25.71,
    'Jupiter': 34.29,
    'Venus': 42.86,
    'Saturn': 8.57,
    'Rahu': 30.0,
    'Ketu': 30.0,
}

# Required minimum shadbala (in virupas) for each planet
_REQUIRED_MINIMUM = {
    'Sun': 390.0,
    'Moon': 360.0,
    'Mars': 300.0,
    'Mercury': 420.0,
    'Jupiter': 390.0,
    'Venus': 330.0,
    'Saturn': 300.0,
    'Rahu': 300.0,
    'Ketu': 300.0,
}

# Benefic and malefic classification for drik bala
_BENEFICS = {'Jupiter', 'Venus', 'Mercury', 'Moon'}
_MALEFICS = {'Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu'}

# Diurnal planets (stronger during the day)
_DIURNAL_PLANETS = {'Sun', 'Jupiter', 'Venus'}
# Nocturnal planets (stronger during the night)
_NOCTURNAL_PLANETS = {'Moon', 'Mars', 'Saturn'}

# Average daily speeds (degrees per day)
_AVG_SPEED = {
    'Sun': 1.0,
    'Moon': 13.0,
}

# Special Vedic aspects: planet -> list of additional houses aspected (beyond 7th)
_SPECIAL_ASPECTS = {
    'Mars': [4, 8],
    'Jupiter': [5, 9],
    'Saturn': [3, 10],
}


def _house_distance(from_house: int, to_house: int) -> int:
    """Calculate minimum circular distance between two houses (1-12).

    Returns a value from 0 to 6 (half the wheel).
    """
    diff = abs(from_house - to_house) % 12
    return min(diff, 12 - diff)


def _angular_distance(lon1: float, lon2: float) -> float:
    """Calculate the shortest angular distance between two longitudes.

    Returns a value in degrees from 0 to 180.
    """
    diff = abs(lon1 - lon2) % 360.0
    return min(diff, 360.0 - diff)


def _get_dignity_score(planet: PlanetPosition) -> float:
    """Return the dignity-based score for a planet's current position."""
    dignity = planet.dignity.lower() if planet.dignity else ''
    return _DIGNITY_SCORES.get(dignity, 15.0)  # Default to neutral


def _get_uchcha_bala(planet: PlanetPosition) -> float:
    """Calculate uchcha bala (exaltation strength).

    Based on distance from the deep debilitation point.
    Maximum 60 when at exact exaltation, 0 at exact debilitation.
    Formula: (180 - |distance_from_exaltation|) / 3
    """
    name = planet.planet
    if name not in _DEEP_EXALTATION_LONGITUDE:
        # Rahu/Ketu: use a simplified calculation based on sign
        if name == 'Rahu':
            # Rahu exalted in Gemini (sign 3)
            if planet.sign == EXALTATION.get('Rahu', 3):
                return 60.0
            elif planet.sign == DEBILITATION.get('Rahu', 9):
                return 0.0
            else:
                return 30.0
        elif name == 'Ketu':
            if planet.sign == EXALTATION.get('Ketu', 9):
                return 60.0
            elif planet.sign == DEBILITATION.get('Ketu', 3):
                return 0.0
            else:
                return 30.0
        return 30.0

    exalt_lon = _DEEP_EXALTATION_LONGITUDE[name]
    distance_from_exaltation = _angular_distance(planet.longitude, exalt_lon)
    uchcha = (180.0 - distance_from_exaltation) / 3.0
    return max(0.0, min(60.0, uchcha))


def calculate_sthana_bala(planet: PlanetPosition) -> float:
    """Calculate Sthana Bala (positional strength).

    Combines dignity-based strength with uchcha bala (exaltation strength).

    Args:
        planet: PlanetPosition with sign, longitude, and dignity info.

    Returns:
        Sthana bala score (normalized, roughly 0-60 range).
    """
    dignity_score = _get_dignity_score(planet)
    uchcha_score = _get_uchcha_bala(planet)
    return (dignity_score + uchcha_score) / 2.0


def calculate_dig_bala(planet: PlanetPosition) -> float:
    """Calculate Dig Bala (directional strength).

    Based on how close the planet is to its house of directional strength.
    Maximum 60 when in the strongest house, decreasing by 10 per house away.

    Args:
        planet: PlanetPosition with house placement.

    Returns:
        Dig bala score (0-60 range).
    """
    name = planet.planet
    strong_house = _DIG_BALA_STRONG_HOUSE.get(name, 1)
    houses_away = _house_distance(planet.house, strong_house)
    dig_bala = max(0.0, 60.0 - (houses_away * 10.0))
    return dig_bala


def calculate_kala_bala(planet: PlanetPosition, julian_day: float,
                        sun_house: int = 0) -> float:
    """Calculate Kala Bala (temporal strength).

    Simplified temporal strength based on day/night birth and hora.

    Args:
        planet: PlanetPosition for the planet being evaluated.
        julian_day: Julian day number of the birth moment.
        sun_house: House position of the Sun (1-12). If the Sun is in
                   houses 7-12, it is above the horizon (daytime).
                   If 0, we attempt to determine from the planet list context.

    Returns:
        Kala bala score (roughly 15-45 range).
    """
    name = planet.planet

    # Determine if it is daytime: Sun in houses 7-12 means above horizon
    is_daytime = 7 <= sun_house <= 12 if sun_house else True

    # Diurnal/nocturnal points
    diurnal_points = 0.0
    if name == 'Mercury':
        # Mercury is always considered diurnal
        diurnal_points = 30.0
    elif name in _DIURNAL_PLANETS:
        diurnal_points = 30.0 if is_daytime else 0.0
    elif name in _NOCTURNAL_PLANETS:
        diurnal_points = 30.0 if not is_daytime else 0.0
    elif name in ('Rahu', 'Ketu'):
        # Rahu/Ketu: nocturnal by nature
        diurnal_points = 30.0 if not is_daytime else 0.0
    else:
        diurnal_points = 15.0

    # Hora bala: simplified base allocation
    hora_bala = 15.0

    return diurnal_points + hora_bala


def calculate_chesta_bala(planet: PlanetPosition) -> float:
    """Calculate Chesta Bala (motional strength).

    Based on the planet's motion: retrograde, stationary, direct speed.

    Args:
        planet: PlanetPosition with speed and retrograde info.

    Returns:
        Chesta bala score (0-60 range).
    """
    name = planet.planet

    # Sun and Moon never go retrograde
    if name in ('Sun', 'Moon'):
        avg = _AVG_SPEED.get(name, 1.0)
        actual_speed = abs(planet.speed)
        if actual_speed > avg:
            return 45.0
        else:
            return 30.0

    # Rahu and Ketu always move retrograde in mean motion
    if name in ('Rahu', 'Ketu'):
        return 30.0

    # For true planets: Mars, Mercury, Jupiter, Venus, Saturn
    speed = planet.speed  # Negative means retrograde in most ephemeris systems

    if planet.is_retrograde:
        # Check if nearly stationary (very slow retrograde)
        if abs(speed) < 0.05:
            return 60.0  # Stationary
        return 60.0  # Retrograde

    # Direct motion
    if abs(speed) < 0.05:
        return 60.0  # Stationary (about to turn retrograde or just turned direct)

    # Classify by speed relative to rough averages
    # Rough average daily motions for direct planets:
    _direct_avg_speed = {
        'Mars': 0.52,
        'Mercury': 1.38,
        'Jupiter': 0.08,
        'Venus': 1.18,
        'Saturn': 0.03,
    }
    avg = _direct_avg_speed.get(name, 0.5)

    if abs(speed) > avg * 1.2:
        return 45.0  # Fast
    elif abs(speed) < avg * 0.5:
        return 30.0  # Slow
    else:
        return 15.0  # Normal direct


def calculate_naisargika_bala(planet: str) -> float:
    """Calculate Naisargika Bala (natural strength).

    Fixed values based on the intrinsic luminosity/strength of each planet.
    These values are constant and do not change with chart specifics.

    Args:
        planet: Planet name string.

    Returns:
        Naisargika bala score (fixed value per planet).
    """
    return _NAISARGIKA_BALA.get(planet, 15.0)


def _get_aspected_signs(planet: PlanetPosition) -> list[int]:
    """Return list of signs (1-12) that a planet aspects from its current sign.

    All planets aspect the 7th sign from their position.
    Mars additionally aspects the 4th and 8th.
    Jupiter additionally aspects the 5th and 9th.
    Saturn additionally aspects the 3rd and 10th.
    """
    aspects = [7]  # All planets aspect 7th from their sign
    if planet.planet in _SPECIAL_ASPECTS:
        aspects.extend(_SPECIAL_ASPECTS[planet.planet])

    aspected_signs = []
    for offset in aspects:
        target_sign = ((planet.sign - 1 + offset) % 12) + 1
        aspected_signs.append(target_sign)

    return aspected_signs


def calculate_drik_bala(planet: PlanetPosition,
                        all_planets: list[PlanetPosition]) -> float:
    """Calculate Drik Bala (aspectual strength).

    Strength gained or lost from aspects of other planets.
    Benefic aspects add strength, malefic aspects reduce it.

    Args:
        planet: The planet whose drik bala is being calculated.
        all_planets: All planet positions in the chart.

    Returns:
        Drik bala score (clamped to 0-60 range).
    """
    aspect_sum = 0.0

    for other in all_planets:
        if other.planet == planet.planet:
            continue

        # Check if 'other' aspects the sign where 'planet' is placed
        aspected_signs = _get_aspected_signs(other)
        if planet.sign in aspected_signs:
            if other.planet in _BENEFICS:
                aspect_sum += 15.0
            elif other.planet in _MALEFICS:
                aspect_sum -= 15.0

    # Base of 30 + aspect effects, clamped to 0-60
    drik_bala = 30.0 + aspect_sum
    return max(0.0, min(60.0, drik_bala))


def calculate_shadbala(planets: list[PlanetPosition],
                       julian_day: float) -> list[ShadbalaResult]:
    """Calculate complete Shadbala for all planets in a chart.

    Computes all six strength components for each planet and derives
    the total shadbala and shadbala ratio (total / required minimum).

    Args:
        planets: List of PlanetPosition objects for all planets.
        julian_day: Julian day number of the birth moment.

    Returns:
        List of ShadbalaResult, one per planet, with all components filled.
    """
    # Find Sun's house for kala bala day/night determination
    sun_house = 0
    for p in planets:
        if p.planet == 'Sun':
            sun_house = p.house
            break

    results = []

    for planet in planets:
        name = planet.planet

        sthana = calculate_sthana_bala(planet)
        dig = calculate_dig_bala(planet)
        kala = calculate_kala_bala(planet, julian_day, sun_house=sun_house)
        chesta = calculate_chesta_bala(planet)
        naisargika = calculate_naisargika_bala(name)
        drik = calculate_drik_bala(planet, planets)

        total = sthana + dig + kala + chesta + naisargika + drik
        required = _REQUIRED_MINIMUM.get(name, 300.0)
        ratio = total / required if required > 0 else 0.0

        result = ShadbalaResult(
            planet=name,
            sthana_bala=round(sthana, 2),
            dig_bala=round(dig, 2),
            kala_bala=round(kala, 2),
            chesta_bala=round(chesta, 2),
            naisargika_bala=round(naisargika, 2),
            drik_bala=round(drik, 2),
            total_shadbala=round(total, 2),
            shadbala_ratio=round(ratio, 4),
        )
        results.append(result)

    return results
