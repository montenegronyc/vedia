"""Divisional chart (varga) calculations for Vedic astrology.

Divisional charts map each planet's rashi (D1) position into a new sign
by mathematically dividing the 30-degree sign into smaller segments. Each
division scheme reveals a different life domain:

    D2  (Hora)        - Wealth
    D3  (Drekkana)    - Siblings, courage
    D7  (Saptamsha)   - Children, progeny
    D9  (Navamsha)    - Spouse, dharma, overall strength
    D10 (Dashamsha)   - Career, profession
    D12 (Dwadashamsha)- Parents
    D30 (Trimsamsha)  - Misfortune, inauspiciousness
"""

from ..models import PlanetPosition
from .houses import get_house


# ---------------------------------------------------------------------------
# Helper: element lookup
# ---------------------------------------------------------------------------

_FIRE_SIGNS = {1, 5, 9}        # Aries, Leo, Sagittarius
_EARTH_SIGNS = {2, 6, 10}      # Taurus, Virgo, Capricorn
_AIR_SIGNS = {3, 7, 11}        # Gemini, Libra, Aquarius
_WATER_SIGNS = {4, 8, 12}      # Cancer, Scorpio, Pisces

# Navamsha starting signs by element
_NAVAMSHA_STARTS = {
    1: 1,  5: 1,  9: 1,    # Fire  -> Aries
    2: 10, 6: 10, 10: 10,  # Earth -> Capricorn
    3: 7,  7: 7,  11: 7,   # Air   -> Libra
    4: 4,  8: 4,  12: 4,   # Water -> Cancer
}

# Supported divisional chart types
SUPPORTED_VARGAS = ('D2', 'D3', 'D7', 'D9', 'D10', 'D12', 'D30')


def _clamp_degree(sign_degree: float) -> float:
    """Clamp sign_degree into [0, 30), handling exact 30.0 boundary.

    A degree of exactly 30.0 means the planet has crossed into the next sign,
    but if we receive it we treat it as the very end of the current sign
    (i.e. the last pada) to avoid out-of-range results.
    """
    if sign_degree < 0.0:
        return 0.0
    if sign_degree >= 30.0:
        return 29.999999
    return sign_degree


def _is_odd_sign(sign: int) -> bool:
    return sign % 2 == 1


# ---------------------------------------------------------------------------
# D2 - Hora
# ---------------------------------------------------------------------------

def calculate_d2_position(sign: int, sign_degree: float) -> int:
    """Hora (D-2): Divide each sign into two halves of 15 degrees.

    First 15 degrees:
        Odd signs  -> Leo (5) [Sun's hora]
        Even signs -> Cancer (4) [Moon's hora]
    Second 15 degrees:
        Odd signs  -> Cancer (4) [Moon's hora]
        Even signs -> Leo (5) [Sun's hora]

    Args:
        sign: Rashi sign number (1-12).
        sign_degree: Degree within the sign (0-30).

    Returns:
        Hora sign number: 4 (Cancer) or 5 (Leo).
    """
    deg = _clamp_degree(sign_degree)
    odd = _is_odd_sign(sign)

    if deg < 15.0:
        return 5 if odd else 4
    else:
        return 4 if odd else 5


# ---------------------------------------------------------------------------
# D3 - Drekkana
# ---------------------------------------------------------------------------

def calculate_d3_position(sign: int, sign_degree: float) -> int:
    """Drekkana (D-3): Divide each sign into three parts of 10 degrees.

    First decanate  (0-10):  same sign
    Second decanate (10-20): 5th sign from the sign
    Third decanate  (20-30): 9th sign from the sign

    Args:
        sign: Rashi sign number (1-12).
        sign_degree: Degree within the sign (0-30).

    Returns:
        Drekkana sign number (1-12).
    """
    deg = _clamp_degree(sign_degree)
    pada = int(deg / 10.0)  # 0, 1, or 2
    if pada > 2:
        pada = 2

    if pada == 0:
        offset = 0  # same sign
    elif pada == 1:
        offset = 4  # 5th from sign (count 4 forward)
    else:
        offset = 8  # 9th from sign (count 8 forward)

    return ((sign - 1 + offset) % 12) + 1


# ---------------------------------------------------------------------------
# D7 - Saptamsha
# ---------------------------------------------------------------------------

def calculate_d7_position(sign: int, sign_degree: float) -> int:
    """Saptamsha (D-7): Divide each sign into 7 parts of ~4.2857 degrees.

    Each part spans 4 degrees 17 minutes 8.57 seconds (30/7 degrees).

    For odd signs:  count from the same sign.
    For even signs: count from the 7th sign from it.

    Args:
        sign: Rashi sign number (1-12).
        sign_degree: Degree within the sign (0-30).

    Returns:
        Saptamsha sign number (1-12).
    """
    deg = _clamp_degree(sign_degree)
    part_size = 30.0 / 7.0  # 4.285714...
    pada = int(deg / part_size)  # 0-6
    if pada > 6:
        pada = 6

    if _is_odd_sign(sign):
        start = sign
    else:
        # 7th sign from the current sign
        start = ((sign - 1 + 6) % 12) + 1

    return ((start - 1 + pada) % 12) + 1


# ---------------------------------------------------------------------------
# D9 - Navamsha
# ---------------------------------------------------------------------------

def calculate_d9_position(sign: int, sign_degree: float) -> int:
    """Navamsha (D-9): Divide each sign into 9 parts of 3 degrees 20 minutes.

    Each navamsha pada spans 3.3333 degrees (3 deg 20 min).

    The starting navamsha sign depends on the element of the rashi:
        Fire signs  (1, 5, 9)  -> start from Aries (1)
        Earth signs (2, 6, 10) -> start from Capricorn (10)
        Air signs   (3, 7, 11) -> start from Libra (7)
        Water signs (4, 8, 12) -> start from Cancer (4)

    Args:
        sign: Rashi sign number (1-12).
        sign_degree: Degree within the sign (0-30).

    Returns:
        Navamsha sign number (1-12).
    """
    deg = _clamp_degree(sign_degree)
    part_size = 30.0 / 9.0  # 3.3333...
    pada = int(deg / part_size)  # 0-8
    if pada > 8:
        pada = 8

    starting_sign = _NAVAMSHA_STARTS[sign]
    return ((starting_sign - 1 + pada) % 12) + 1


# ---------------------------------------------------------------------------
# D10 - Dashamsha
# ---------------------------------------------------------------------------

def calculate_d10_position(sign: int, sign_degree: float) -> int:
    """Dashamsha (D-10): Divide each sign into 10 parts of 3 degrees each.

    For odd signs:  count from the same sign.
    For even signs: count from the 9th sign from it.

    Args:
        sign: Rashi sign number (1-12).
        sign_degree: Degree within the sign (0-30).

    Returns:
        Dashamsha sign number (1-12).
    """
    deg = _clamp_degree(sign_degree)
    pada = int(deg / 3.0)  # 0-9
    if pada > 9:
        pada = 9

    if _is_odd_sign(sign):
        start = sign
    else:
        # 9th sign from the current sign
        start = ((sign - 1 + 8) % 12) + 1

    return ((start - 1 + pada) % 12) + 1


# ---------------------------------------------------------------------------
# D12 - Dwadashamsha
# ---------------------------------------------------------------------------

def calculate_d12_position(sign: int, sign_degree: float) -> int:
    """Dwadashamsha (D-12): Divide each sign into 12 parts of 2.5 degrees.

    Always count from the same sign.

    Args:
        sign: Rashi sign number (1-12).
        sign_degree: Degree within the sign (0-30).

    Returns:
        Dwadashamsha sign number (1-12).
    """
    deg = _clamp_degree(sign_degree)
    pada = int(deg / 2.5)  # 0-11
    if pada > 11:
        pada = 11

    return ((sign - 1 + pada) % 12) + 1


# ---------------------------------------------------------------------------
# D30 - Trimsamsha
# ---------------------------------------------------------------------------

def calculate_d30_position(sign: int, sign_degree: float) -> int:
    """Trimsamsha (D-30): Unequal division governed by classical lords.

    Odd signs:
        0-5   -> Mars     -> Aries   (1)
        5-10  -> Saturn   -> Aquarius (11)
        10-18 -> Jupiter  -> Sagittarius (9)
        18-25 -> Mercury  -> Gemini  (3)
        25-30 -> Venus    -> Taurus  (2)

    Even signs:
        0-5   -> Venus    -> Taurus  (2)
        5-12  -> Mercury  -> Gemini  (3)
        12-20 -> Jupiter  -> Sagittarius (9)
        20-25 -> Saturn   -> Aquarius (11)
        25-30 -> Mars     -> Scorpio (8)

    The returned sign is the sign ruled by the trimsamsha lord.

    Args:
        sign: Rashi sign number (1-12).
        sign_degree: Degree within the sign (0-30).

    Returns:
        Trimsamsha sign number (1-12).
    """
    deg = _clamp_degree(sign_degree)

    if _is_odd_sign(sign):
        if deg < 5.0:
            return 1    # Mars -> Aries
        elif deg < 10.0:
            return 11   # Saturn -> Aquarius
        elif deg < 18.0:
            return 9    # Jupiter -> Sagittarius
        elif deg < 25.0:
            return 3    # Mercury -> Gemini
        else:
            return 2    # Venus -> Taurus
    else:
        if deg < 5.0:
            return 2    # Venus -> Taurus
        elif deg < 12.0:
            return 3    # Mercury -> Gemini
        elif deg < 20.0:
            return 9    # Jupiter -> Sagittarius
        elif deg < 25.0:
            return 11   # Saturn -> Aquarius
        else:
            return 8    # Mars -> Scorpio


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_VARGA_FUNCTIONS = {
    'D2':  calculate_d2_position,
    'D3':  calculate_d3_position,
    'D7':  calculate_d7_position,
    'D9':  calculate_d9_position,
    'D10': calculate_d10_position,
    'D12': calculate_d12_position,
    'D30': calculate_d30_position,
}


def get_divisional_sign(sign: int, sign_degree: float, chart_type: str) -> int:
    """Calculate the divisional sign for any supported varga.

    A convenience dispatcher that routes to the appropriate D-N function.

    Args:
        sign: Rashi sign number (1-12).
        sign_degree: Degree within the sign (0-30).
        chart_type: One of 'D2', 'D3', 'D7', 'D9', 'D10', 'D12', 'D30'.

    Returns:
        Divisional chart sign number (1-12).

    Raises:
        ValueError: If chart_type is not supported.
    """
    chart_type = chart_type.upper()
    fn = _VARGA_FUNCTIONS.get(chart_type)
    if fn is None:
        raise ValueError(
            f"Unsupported chart type '{chart_type}'. "
            f"Supported types: {', '.join(SUPPORTED_VARGAS)}"
        )
    return fn(sign, sign_degree)


# ---------------------------------------------------------------------------
# Full divisional chart calculation
# ---------------------------------------------------------------------------

def calculate_divisional_chart(
    planets: list[PlanetPosition],
    chart_type: str,
    ascendant_sign: int,
    ascendant_degree: float = 0.0,
) -> list[PlanetPosition]:
    """Calculate a complete divisional chart from D1 planet positions.

    For each planet, the rashi sign is projected into the divisional chart
    using the appropriate varga function. New ``PlanetPosition`` objects are
    created with the divisional sign, while preserving the original longitude,
    nakshatra data, retrograde status, and speed.

    House numbers are recalculated relative to the divisional ascendant.
    The divisional ascendant is determined by projecting the D1 ascendant
    through the same varga function.

    Args:
        planets: List of D1 ``PlanetPosition`` objects.
        chart_type: One of 'D2', 'D3', 'D7', 'D9', 'D10', 'D12', 'D30'.
        ascendant_sign: D1 ascendant sign (1-12).
        ascendant_degree: Degree of ascendant within its D1 sign (0-30).
            Defaults to 0.0.

    Returns:
        New list of ``PlanetPosition`` objects with divisional signs and
        recalculated houses.

    Raises:
        ValueError: If chart_type is not supported.
    """
    chart_type = chart_type.upper()

    # Validate chart type early
    if chart_type not in _VARGA_FUNCTIONS:
        raise ValueError(
            f"Unsupported chart type '{chart_type}'. "
            f"Supported types: {', '.join(SUPPORTED_VARGAS)}"
        )

    # Calculate the divisional ascendant
    div_asc_sign = get_divisional_sign(ascendant_sign, ascendant_degree, chart_type)

    result = []
    for planet in planets:
        div_sign = get_divisional_sign(planet.sign, planet.sign_degree, chart_type)
        div_house = get_house(div_sign, div_asc_sign)

        # Recalculate sign_degree within the divisional sign.
        # In divisional charts the sub-degree within the new sign is not
        # directly meaningful for most purposes, so we carry the original
        # sign_degree for reference.  A more precise sub-degree could be
        # computed per varga, but the sign placement is what matters.
        new_pos = PlanetPosition(
            planet=planet.planet,
            longitude=planet.longitude,
            sign=div_sign,
            sign_degree=planet.sign_degree,
            nakshatra=planet.nakshatra,
            nakshatra_pada=planet.nakshatra_pada,
            nakshatra_lord=planet.nakshatra_lord,
            house=div_house,
            is_retrograde=planet.is_retrograde,
            speed=planet.speed,
            dignity='',           # Dignity must be recomputed for the new sign
            is_combust=planet.is_combust,
        )
        result.append(new_pos)

    return result
