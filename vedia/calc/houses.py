"""House calculations for Vedic astrology (whole sign house system)."""

from ..models import SIGN_LORDS


# Special aspects beyond the universal 7th-sign aspect
_SPECIAL_ASPECTS = {
    'Mars': [4, 8],
    'Jupiter': [5, 9],
    'Saturn': [3, 10],
    'Rahu': [5, 9],
    'Ketu': [5, 9],
}

# House significations
_HOUSE_SIGNIFICATIONS = {
    1: 'Self, body, personality, health, appearance',
    2: 'Wealth, family, speech, food, early education',
    3: 'Siblings, courage, communication, short travels, effort',
    4: 'Mother, home, property, vehicles, emotional peace',
    5: 'Children, intelligence, creativity, education, past merit',
    6: 'Enemies, disease, debt, service, daily work, obstacles',
    7: 'Spouse, partnerships, marriage, business relations',
    8: 'Longevity, transformation, hidden matters, inheritance, occult',
    9: 'Father, luck, dharma, higher education, long travel, guru',
    10: 'Career, profession, status, authority, public life',
    11: 'Gains, income, friends, aspirations, elder siblings',
    12: 'Losses, expenses, liberation, foreign lands, sleep, isolation',
}


def get_house(planet_sign: int, ascendant_sign: int) -> int:
    """Determine the house a planet occupies using the whole sign house system.

    Args:
        planet_sign: Sign number (1-12) the planet is in.
        ascendant_sign: Sign number (1-12) of the ascendant.

    Returns:
        House number (1-12).
    """
    return ((planet_sign - ascendant_sign) % 12) + 1


def get_house_lord(house: int, ascendant_sign: int) -> str:
    """Find the lord of a given house based on the ascendant.

    In whole sign houses, the sign of house N is determined by counting
    from the ascendant sign. The lord of that sign is the house lord.

    Args:
        house: House number (1-12).
        ascendant_sign: Sign number (1-12) of the ascendant.

    Returns:
        Name of the planet that lords over the house.
    """
    house_sign = ((ascendant_sign - 1 + house - 1) % 12) + 1
    return SIGN_LORDS[house_sign]


def get_aspects(planet: str, planet_sign: int) -> list[int]:
    """Calculate which signs a planet aspects from its current sign.

    All planets aspect the 7th sign from them. Additionally:
    - Mars aspects the 4th and 8th signs.
    - Jupiter aspects the 5th and 9th signs.
    - Saturn aspects the 3rd and 10th signs.
    - Rahu and Ketu aspect the 5th, 7th, and 9th signs.

    Args:
        planet: Planet name (e.g. 'Mars', 'Jupiter').
        planet_sign: Sign number (1-12) the planet occupies.

    Returns:
        Sorted list of aspected sign numbers (1-12).
    """
    aspect_offsets = set()

    # Rahu and Ketu have 5th, 7th, 9th (7th is included in their special list
    # but we add it universally below, so the set handles deduplication)
    # Universal 7th aspect for all planets
    aspect_offsets.add(7)

    # Add special aspects if applicable
    if planet in _SPECIAL_ASPECTS:
        for offset in _SPECIAL_ASPECTS[planet]:
            aspect_offsets.add(offset)

    aspected_signs = []
    for offset in aspect_offsets:
        # Counting offset signs from planet_sign (inclusive of planet_sign as 1)
        aspected_sign = ((planet_sign - 1 + offset) % 12) + 1
        aspected_signs.append(aspected_sign)

    return sorted(aspected_signs)


# Proportional aspect strengths (traditional weights)
_ASPECT_STRENGTHS = {
    'Mars':    {4: 75, 7: 100, 8: 100},
    'Jupiter': {5: 50, 7: 100, 9: 75},
    'Saturn':  {3: 50, 7: 100, 10: 100},
    'Rahu':    {5: 50, 7: 100, 9: 75},
    'Ketu':    {5: 50, 7: 100, 9: 75},
}


def get_aspects_with_strength(planet: str, planet_sign: int) -> list[tuple[int, int]]:
    """Calculate which signs a planet aspects with proportional strength.

    Returns a list of (aspected_sign, strength_percent) tuples.
    Strength is 100 for full aspects, 75 for three-quarter, 50 for half.

    All planets have a full (100%) 7th-sign aspect. Special aspects
    use traditional proportional weights.

    Args:
        planet: Planet name (e.g. 'Mars', 'Jupiter').
        planet_sign: Sign number (1-12) the planet occupies.

    Returns:
        List of (sign_number, strength_percent) tuples, sorted by sign.
    """
    strengths = _ASPECT_STRENGTHS.get(planet, {7: 100})

    # If planet has no special aspects, just give it the universal 7th
    if planet not in _ASPECT_STRENGTHS:
        strengths = {7: 100}

    result = []
    for offset, strength_pct in strengths.items():
        aspected_sign = ((planet_sign - 1 + offset) % 12) + 1
        result.append((aspected_sign, strength_pct))

    return sorted(result, key=lambda x: x[0])


def get_house_signification(house: int) -> str:
    """Return a brief description of what a house signifies.

    Args:
        house: House number (1-12).

    Returns:
        String describing the house significations.

    Raises:
        ValueError: If house number is not 1-12.
    """
    if house < 1 or house > 12:
        raise ValueError(f"House number must be 1-12, got {house}")
    return _HOUSE_SIGNIFICATIONS[house]
