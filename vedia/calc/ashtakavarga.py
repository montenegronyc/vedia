"""Ashtakavarga calculation engine.

Ashtakavarga is a transit/strength scoring system in Vedic astrology. Each of
the seven classical planets (Sun through Saturn, excluding Rahu and Ketu)
contributes "bindus" (benefic points) to all twelve signs, based on its
position relative to every other planet, itself, and the ascendant.

Two levels of output are produced:

  - Bhinnashtakavarga (BAV): Per-planet tables showing bindus in each sign.
    Each sign receives 0 or 1 bindu from each of the 8 reference points
    (7 planets + ascendant), yielding a range of 0-8 per sign per planet.

  - Sarvashtakavarga (SAV): The aggregate of all seven BAV tables. Each sign
    gets a total score in the range 0-56 (7 planets * 8 max each).
"""

from ..models import PlanetPosition

# The seven classical planets used in Ashtakavarga (no Rahu/Ketu)
_ASHTAKAVARGA_PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']

# Reference points: the 7 planets plus the ascendant
_REFERENCE_POINTS = _ASHTAKAVARGA_PLANETS + ['Ascendant']

# ---------------------------------------------------------------------------
# Benefic-point tables
#
# For each contributing planet, this table lists the house numbers (counted
# from each reference point) where the contributing planet gives a bindu (1).
# House numbering is 1-based: house 1 = same sign as reference, house 2 = the
# next sign, and so on.
# ---------------------------------------------------------------------------

_BENEFIC_POINTS: dict[str, dict[str, list[int]]] = {
    'Sun': {
        'Sun':       [1, 2, 4, 7, 8, 9, 10, 11],
        'Moon':      [3, 6, 10, 11],
        'Mars':      [1, 2, 4, 7, 8, 9, 10, 11],
        'Mercury':   [3, 5, 6, 9, 10, 11, 12],
        'Jupiter':   [5, 6, 9, 11],
        'Venus':     [6, 7, 12],
        'Saturn':    [1, 2, 4, 7, 8, 9, 10, 11],
        'Ascendant': [3, 4, 6, 10, 11, 12],
    },
    'Moon': {
        'Sun':       [3, 6, 7, 8, 10, 11],
        'Moon':      [1, 3, 6, 7, 10, 11],
        'Mars':      [2, 3, 5, 6, 9, 10, 11],
        'Mercury':   [1, 3, 4, 5, 7, 8, 10, 11],
        'Jupiter':   [1, 4, 7, 8, 10, 11, 12],
        'Venus':     [3, 4, 5, 7, 9, 10, 11],
        'Saturn':    [3, 5, 6, 11],
        'Ascendant': [3, 6, 10, 11],
    },
    'Mars': {
        'Sun':       [3, 5, 6, 10, 11],
        'Moon':      [3, 6, 11],
        'Mars':      [1, 2, 4, 7, 8, 10, 11],
        'Mercury':   [3, 5, 6, 11],
        'Jupiter':   [6, 10, 11, 12],
        'Venus':     [6, 8, 11, 12],
        'Saturn':    [1, 4, 7, 8, 9, 10, 11],
        'Ascendant': [1, 3, 6, 10, 11],
    },
    'Mercury': {
        'Sun':       [5, 6, 9, 11, 12],
        'Moon':      [2, 4, 6, 8, 10, 11],
        'Mars':      [1, 2, 4, 7, 8, 9, 10, 11],
        'Mercury':   [1, 3, 5, 6, 9, 10, 11, 12],
        'Jupiter':   [6, 8, 11, 12],
        'Venus':     [1, 2, 3, 4, 5, 8, 9, 11],
        'Saturn':    [1, 2, 4, 7, 8, 9, 10, 11],
        'Ascendant': [1, 2, 4, 6, 8, 10, 11],
    },
    'Jupiter': {
        'Sun':       [1, 2, 3, 4, 7, 8, 9, 10, 11],
        'Moon':      [2, 5, 7, 9, 11],
        'Mars':      [1, 2, 4, 7, 8, 10, 11],
        'Mercury':   [1, 2, 4, 5, 6, 9, 10, 11],
        'Jupiter':   [1, 2, 3, 4, 7, 8, 10, 11],
        'Venus':     [2, 5, 6, 9, 10, 11],
        'Saturn':    [3, 5, 6, 12],
        'Ascendant': [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    'Venus': {
        'Sun':       [8, 11, 12],
        'Moon':      [1, 2, 3, 4, 5, 8, 9, 11, 12],
        'Mars':      [3, 5, 6, 9, 11, 12],
        'Mercury':   [3, 5, 6, 9, 11],
        'Jupiter':   [5, 8, 9, 10, 11],
        'Venus':     [1, 2, 3, 4, 5, 8, 9, 10, 11],
        'Saturn':    [3, 4, 5, 8, 9, 10, 11],
        'Ascendant': [1, 2, 3, 4, 5, 8, 9, 11],
    },
    'Saturn': {
        'Sun':       [1, 2, 4, 7, 8, 10, 11],
        'Moon':      [3, 6, 11],
        'Mars':      [3, 5, 6, 10, 11, 12],
        'Mercury':   [6, 8, 9, 10, 11, 12],
        'Jupiter':   [5, 6, 11, 12],
        'Venus':     [6, 11, 12],
        'Saturn':    [3, 5, 6, 11],
        'Ascendant': [1, 3, 4, 6, 10, 11],
    },
}

# Pre-compute set-based lookups for faster membership testing.  The nested
# dict maps contributing_planet -> reference_point -> frozenset of house
# numbers where a bindu is granted.
_BENEFIC_SETS: dict[str, dict[str, frozenset[int]]] = {
    planet: {
        ref: frozenset(houses)
        for ref, houses in ref_table.items()
    }
    for planet, ref_table in _BENEFIC_POINTS.items()
}


def _house_from(reference_sign: int, target_sign: int) -> int:
    """Compute the 1-based house number of *target_sign* from *reference_sign*.

    Both signs are numbered 1-12. House 1 means the target is the same sign
    as the reference; house 2 is the next sign, etc.

    Args:
        reference_sign: Sign number (1-12) of the reference point.
        target_sign: Sign number (1-12) whose house position we want.

    Returns:
        House number (1-12).
    """
    return ((target_sign - reference_sign) % 12) + 1


def _get_planet_sign(planets: list[PlanetPosition], planet_name: str) -> int:
    """Look up the sign of a planet from the list of positions.

    Args:
        planets: List of PlanetPosition objects for the chart.
        planet_name: Name of the planet to find.

    Returns:
        Sign number (1-12).

    Raises:
        ValueError: If the planet is not found in the positions list.
    """
    for p in planets:
        if p.planet == planet_name:
            return p.sign
    raise ValueError(
        f"Planet '{planet_name}' not found in positions. "
        f"Available: {[p.planet for p in planets]}"
    )


def calculate_bhinnashtakavarga(
    planets: list[PlanetPosition],
    ascendant_sign: int,
) -> dict[str, dict[int, int]]:
    """Calculate the Bhinnashtakavarga (individual planet) tables.

    For each of the seven planets (Sun through Saturn), this function
    computes how many bindus (benefic points) each of the twelve signs
    receives.  A sign can receive 0 or 1 bindu from each of the 8
    reference points (7 planets + ascendant), so scores range from 0 to 8.

    The algorithm for each (contributing_planet, reference_point, sign)
    combination:
      1. Find the sign occupied by the reference point.
      2. Compute the house number of the target sign from the reference.
      3. If that house is in the benefic-point list for
         (contributing_planet, reference_point), add 1 bindu.

    Args:
        planets: List of PlanetPosition objects. Must include at least
            the seven classical planets (Sun, Moon, Mars, Mercury,
            Jupiter, Venus, Saturn).
        ascendant_sign: Sign number (1-12) of the ascendant/lagna.

    Returns:
        Dict keyed by planet name, whose values are dicts mapping each
        sign number (1-12) to its bindu count (0-8).

    Raises:
        ValueError: If a required planet is missing from the positions.
    """
    # Build a quick lookup of planet name -> sign
    planet_signs: dict[str, int] = {}
    for p in planets:
        planet_signs[p.planet] = p.sign

    for name in _ASHTAKAVARGA_PLANETS:
        if name not in planet_signs:
            raise ValueError(
                f"Required planet '{name}' not found in positions. "
                f"Available: {list(planet_signs.keys())}"
            )

    # Include the ascendant as a reference point
    reference_signs: dict[str, int] = {
        name: planet_signs[name] for name in _ASHTAKAVARGA_PLANETS
    }
    reference_signs['Ascendant'] = ascendant_sign

    bhinna: dict[str, dict[int, int]] = {}

    for planet in _ASHTAKAVARGA_PLANETS:
        benefic_table = _BENEFIC_SETS[planet]
        sign_scores: dict[int, int] = {}

        for sign in range(1, 13):
            score = 0
            for ref_name in _REFERENCE_POINTS:
                ref_sign = reference_signs[ref_name]
                house = _house_from(ref_sign, sign)
                if house in benefic_table[ref_name]:
                    score += 1
            sign_scores[sign] = score

        bhinna[planet] = sign_scores

    return bhinna


def calculate_sarvashtakavarga(
    bhinna: dict[str, dict[int, int]],
) -> dict[int, int]:
    """Calculate the Sarvashtakavarga (aggregate) table.

    Sums the Bhinnashtakavarga scores of all seven planets for each sign.
    The resulting per-sign total ranges from 0 to 56 (7 planets * max 8
    each).

    Signs scoring above the average of ~28 are considered strong for
    transits; those below are considered weak.

    Args:
        bhinna: Bhinnashtakavarga dict as returned by
            calculate_bhinnashtakavarga.

    Returns:
        Dict mapping each sign number (1-12) to its total Sarvashtakavarga
        score.
    """
    sarva: dict[int, int] = {}

    for sign in range(1, 13):
        total = 0
        for planet in _ASHTAKAVARGA_PLANETS:
            total += bhinna[planet][sign]
        sarva[sign] = total

    return sarva


def calculate_ashtakavarga(
    planets: list[PlanetPosition],
    ascendant_sign: int,
) -> tuple[dict[str, dict[int, int]], dict[int, int]]:
    """Calculate both Bhinnashtakavarga and Sarvashtakavarga.

    Convenience function that computes the full Ashtakavarga system in a
    single call.

    Args:
        planets: List of PlanetPosition objects (must include the seven
            classical planets).
        ascendant_sign: Sign number (1-12) of the ascendant/lagna.

    Returns:
        Tuple of (bhinna, sarva) where:
          - bhinna is the Bhinnashtakavarga dict (planet -> {sign: score})
          - sarva is the Sarvashtakavarga dict ({sign: total_score})

    Raises:
        ValueError: If a required planet is missing from the positions.
    """
    bhinna = calculate_bhinnashtakavarga(planets, ascendant_sign)
    sarva = calculate_sarvashtakavarga(bhinna)
    return (bhinna, sarva)
