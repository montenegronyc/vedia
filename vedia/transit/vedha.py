"""Vedha (obstruction) analysis for transits.

In Vedic transit analysis, vedha is the principle that a benefic transit
result can be blocked (obstructed) when a malefic planet simultaneously
transits the corresponding vedha point. Each planet has a defined set of
benefic transit houses (from the Moon) paired with vedha houses. If any
other planet occupies the vedha house, the good results of the benefic
transit are considered nullified or weakened.

Sun and Moon do not cause vedha on each other (they are exempt from
mutual vedha). This module implements that exception.
"""

from ..models import PlanetPosition

# ---------------------------------------------------------------------------
# Vedha pairs for each planet's transit houses (counted from the Moon).
# Format: {benefic_house: vedha_house}
#
# When a planet transits a benefic house (the key), its good results are
# obstructed if ANY other planet (with exceptions) transits the
# corresponding vedha house (the value).
# ---------------------------------------------------------------------------
VEDHA_POINTS: dict[str, dict[int, int]] = {
    'Sun':     {1: 4, 3: 9, 4: 10, 6: 5, 7: 1, 10: 8, 11: 12},
    'Moon':    {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8},
    'Mars':    {1: 5, 3: 12, 6: 9, 10: 7, 11: 8},
    'Mercury': {1: 5, 2: 3, 4: 12, 6: 8, 8: 1, 10: 9, 11: 12},
    'Jupiter': {2: 12, 5: 4, 7: 3, 9: 10, 11: 8},
    'Venus':   {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3},
    'Saturn':  {3: 12, 6: 9, 11: 5},
}

# Sun and Moon are exempt from causing vedha on each other
_VEDHA_EXEMPT_PAIRS: set[frozenset[str]] = {
    frozenset({'Sun', 'Moon'}),
}


def _house_from_moon(planet_sign: int, moon_sign: int) -> int:
    """Compute the house number of *planet_sign* counted from *moon_sign*.

    The Moon's sign is house 1.  Returns 1-12.
    """
    return ((planet_sign - moon_sign) % 12) + 1


def check_vedha(
    transit_planet: str,
    transit_house_from_moon: int,
    all_transit_houses: dict[str, int],
) -> dict:
    """Check if a specific transit planet has its vedha point obstructed.

    Looks up whether the planet's current house from Moon is one of its
    benefic transit houses, and if so, whether any other planet currently
    sits at the corresponding vedha house.

    Args:
        transit_planet: Name of the planet being checked (e.g. ``'Jupiter'``).
        transit_house_from_moon: House number (1-12) of this planet counted
            from the natal Moon sign.
        all_transit_houses: Dict mapping every transit planet name to its
            current house from Moon (e.g. ``{'Sun': 3, 'Moon': 7, ...}``).

    Returns:
        Dict with keys:

        * ``has_vedha`` (bool): ``True`` if the benefic transit is obstructed.
        * ``blocking_planet`` (str or None): Name of the planet causing vedha.
        * ``vedha_house`` (int or None): The house number that is obstructed.
        * ``benefic_house`` (int or None): The benefic house that was being
          transited (same as *transit_house_from_moon* when vedha applies).
    """
    vedha_map = VEDHA_POINTS.get(transit_planet)

    # If this planet has no vedha table or is not in a benefic house, no vedha
    if vedha_map is None or transit_house_from_moon not in vedha_map:
        return {
            'has_vedha': False,
            'blocking_planet': None,
            'vedha_house': None,
            'benefic_house': None,
        }

    vedha_house = vedha_map[transit_house_from_moon]

    # Check if any OTHER planet occupies the vedha house
    for other_planet, other_house in all_transit_houses.items():
        if other_planet == transit_planet:
            continue

        if other_house != vedha_house:
            continue

        # Check Sun-Moon mutual exemption
        pair = frozenset({transit_planet, other_planet})
        if pair in _VEDHA_EXEMPT_PAIRS:
            continue

        # Vedha is active: this planet's benefic transit is obstructed
        return {
            'has_vedha': True,
            'blocking_planet': other_planet,
            'vedha_house': vedha_house,
            'benefic_house': transit_house_from_moon,
        }

    # No planet at the vedha point -- benefic transit is unobstructed
    return {
        'has_vedha': False,
        'blocking_planet': None,
        'vedha_house': vedha_house,
        'benefic_house': transit_house_from_moon,
    }


def analyze_all_vedha(
    transit_planets: list[PlanetPosition],
    natal_moon_sign: int,
) -> list[dict]:
    """Analyze vedha for every transit planet relative to the natal Moon.

    Computes each planet's house from the Moon, then checks whether any
    vedha obstruction applies.

    Args:
        transit_planets: List of current transit PlanetPosition instances.
        natal_moon_sign: Sign number (1-12) of the natal Moon.

    Returns:
        List of dicts, one per transit planet::

            {
                "planet": str,
                "house_from_moon": int,
                "transit_sign": int,
                "has_vedha": bool,
                "blocking_planet": str or None,
                "vedha_house": int or None,
                "benefic_house": int or None,
                "is_benefic_transit": bool,
            }

        ``is_benefic_transit`` is ``True`` when the planet's current house
        from Moon is listed as a benefic transit house in ``VEDHA_POINTS``.
    """
    # Build house-from-Moon lookup for all transit planets
    all_transit_houses: dict[str, int] = {}
    for tp in transit_planets:
        all_transit_houses[tp.planet] = _house_from_moon(tp.sign, natal_moon_sign)

    results: list[dict] = []

    for tp in transit_planets:
        house_from_moon = all_transit_houses[tp.planet]
        vedha_map = VEDHA_POINTS.get(tp.planet, {})
        is_benefic = house_from_moon in vedha_map

        vedha_result = check_vedha(
            tp.planet, house_from_moon, all_transit_houses,
        )

        results.append({
            'planet': tp.planet,
            'house_from_moon': house_from_moon,
            'transit_sign': tp.sign,
            'has_vedha': vedha_result['has_vedha'],
            'blocking_planet': vedha_result['blocking_planet'],
            'vedha_house': vedha_result['vedha_house'],
            'benefic_house': vedha_result['benefic_house'],
            'is_benefic_transit': is_benefic,
        })

    return results
