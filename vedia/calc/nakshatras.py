"""Nakshatra calculations and planetary dignity assessment."""

from ..models import (
    NAKSHATRA_NAMES,
    NAKSHATRA_LORDS,
    EXALTATION,
    DEBILITATION,
    OWN_SIGNS,
    MOOLATRIKONA,
    NATURAL_FRIENDS,
    NATURAL_ENEMIES,
    SIGN_LORDS,
)

# Each nakshatra spans 13 degrees 20 minutes = 13.333... degrees
NAKSHATRA_SPAN = 13.333333
# Each pada spans 3 degrees 20 minutes = 3.333... degrees
PADA_SPAN = 3.333333


def get_nakshatra_info(longitude: float) -> tuple[int, int, str]:
    """Determine nakshatra number, pada, and nakshatra lord from sidereal longitude.

    Args:
        longitude: Sidereal longitude in degrees (0-360).

    Returns:
        Tuple of (nakshatra_number, pada, nakshatra_lord).
        nakshatra_number is 1-27, pada is 1-4.
    """
    nakshatra_number = int(longitude / NAKSHATRA_SPAN) + 1
    # Clamp to valid range (handles exactly 360.0)
    if nakshatra_number > 27:
        nakshatra_number = 27

    offset_in_nakshatra = longitude % NAKSHATRA_SPAN
    pada = int(offset_in_nakshatra / PADA_SPAN) + 1
    # Clamp pada to valid range
    if pada > 4:
        pada = 4

    # NAKSHATRA_LORDS is 0-indexed, nakshatra_number is 1-indexed
    nakshatra_lord = NAKSHATRA_LORDS[nakshatra_number - 1]

    return (nakshatra_number, pada, nakshatra_lord)


def get_nakshatra_name(nakshatra_num: int) -> str:
    """Return the name of a nakshatra given its number (1-27).

    Args:
        nakshatra_num: Nakshatra number from 1 to 27.

    Returns:
        Name of the nakshatra.

    Raises:
        IndexError: If nakshatra_num is out of range.
    """
    if nakshatra_num < 1 or nakshatra_num > 27:
        raise IndexError(f"Nakshatra number must be 1-27, got {nakshatra_num}")
    return NAKSHATRA_NAMES[nakshatra_num - 1]


def get_dignity(planet: str, sign: int, sign_degree: float) -> str:
    """Determine the dignity of a planet in a given sign and degree.

    Checks in priority order: exalted, moolatrikona, own, debilitated,
    then friendly/neutral/enemy based on natural relationships.

    Args:
        planet: Planet name (e.g. 'Sun', 'Moon', 'Mars').
        sign: Sign number 1-12.
        sign_degree: Degree within the sign (0-30).

    Returns:
        One of: 'exalted', 'moolatrikona', 'own', 'debilitated',
        'friendly', 'neutral', 'enemy'.
    """
    # 1. Exalted
    if planet in EXALTATION and EXALTATION[planet] == sign:
        return 'exalted'

    # 2. Moolatrikona (only some planets have this defined, and it has degree ranges)
    if planet in MOOLATRIKONA:
        mt_sign, mt_start, mt_end = MOOLATRIKONA[planet]
        if sign == mt_sign and mt_start <= sign_degree <= mt_end:
            return 'moolatrikona'

    # 3. Own sign
    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        return 'own'

    # 4. Debilitated
    if planet in DEBILITATION and DEBILITATION[planet] == sign:
        return 'debilitated'

    # 5. Friendly / Neutral / Enemy based on natural relationships
    sign_lord = SIGN_LORDS.get(sign)
    if sign_lord is None:
        return 'neutral'

    # A planet cannot be a friend/enemy of itself
    if sign_lord == planet:
        return 'own'

    friends = NATURAL_FRIENDS.get(planet, [])
    enemies = NATURAL_ENEMIES.get(planet, [])

    if sign_lord in friends:
        return 'friendly'
    elif sign_lord in enemies:
        return 'enemy'
    else:
        return 'neutral'
