"""Vedic astrology synastry / compatibility analysis.

Implements Guna Milan (Ashtakoot matching -- 36 point system) and
cross-chart analysis including Venus axis, 7th lord exchange,
ascendant compatibility, and Mangal Dosha comparison.
"""

from ..models import (
    PlanetPosition,
    SIGNS,
    SIGN_LORDS,
    NAKSHATRA_NAMES,
    NATURAL_FRIENDS,
    NATURAL_ENEMIES,
    EXALTATION,
    DEBILITATION,
    OWN_SIGNS,
)


# ---------------------------------------------------------------------------
# Nakshatra classification tables  (1-indexed, nakshatras 1-27)
# ---------------------------------------------------------------------------

# Varna: Brahmin=4, Kshatriya=3, Vaishya=2, Shudra=1
_VARNA_MAP: dict[int, int] = {}
for _n in (1, 5, 8, 14, 16, 19, 23, 26):
    _VARNA_MAP[_n] = 4   # Brahmin
for _n in (3, 6, 10, 13, 17, 21, 24, 27):
    _VARNA_MAP[_n] = 3   # Kshatriya
for _n in (2, 7, 9, 15, 18, 22, 25):
    _VARNA_MAP[_n] = 2   # Vaishya
for _n in (4, 11, 12, 20):
    _VARNA_MAP[_n] = 1   # Shudra

# Gana classification
_DEVA_NAKSHATRAS = {1, 5, 7, 8, 13, 15, 17, 22, 27}
_MANUSHYA_NAKSHATRAS = {2, 4, 6, 11, 12, 20, 21, 25, 26}
_RAKSHASA_NAKSHATRAS = {3, 9, 10, 14, 16, 18, 19, 23, 24}


def _gana_of(nakshatra: int) -> str:
    if nakshatra in _DEVA_NAKSHATRAS:
        return 'Deva'
    if nakshatra in _MANUSHYA_NAKSHATRAS:
        return 'Manushya'
    return 'Rakshasa'


# Yoni (animal) assignment per nakshatra  (1-27)
_YONI_ANIMAL: dict[int, str] = {
    1: 'Horse', 2: 'Elephant', 3: 'Sheep', 4: 'Serpent', 5: 'Dog',
    6: 'Dog', 7: 'Cat', 8: 'Sheep', 9: 'Cat', 10: 'Rat',
    11: 'Rat', 12: 'Cow', 13: 'Buffalo', 14: 'Tiger', 15: 'Buffalo',
    16: 'Tiger', 17: 'Deer', 18: 'Deer', 19: 'Dog', 20: 'Monkey',
    21: 'Mongoose', 22: 'Monkey', 23: 'Lion', 24: 'Horse', 25: 'Lion',
    26: 'Cow', 27: 'Elephant',
}

# Yoni compatibility groups  (enemy/very-enemy pairings)
_YONI_ENEMIES: dict[str, str] = {
    'Horse': 'Buffalo', 'Buffalo': 'Horse',
    'Elephant': 'Lion', 'Lion': 'Elephant',
    'Sheep': 'Monkey', 'Monkey': 'Sheep',
    'Serpent': 'Mongoose', 'Mongoose': 'Serpent',
    'Dog': 'Deer', 'Deer': 'Dog',
    'Cat': 'Rat', 'Rat': 'Cat',
    'Cow': 'Tiger', 'Tiger': 'Cow',
}

_YONI_FRIENDLY: set[tuple[str, str]] = {
    ('Horse', 'Horse'), ('Elephant', 'Elephant'), ('Sheep', 'Sheep'),
    ('Serpent', 'Serpent'), ('Dog', 'Dog'), ('Cat', 'Cat'),
    ('Rat', 'Rat'), ('Cow', 'Cow'), ('Buffalo', 'Buffalo'),
    ('Tiger', 'Tiger'), ('Deer', 'Deer'), ('Monkey', 'Monkey'),
    ('Lion', 'Lion'), ('Mongoose', 'Mongoose'),
}

# Nadi assignment:  Vata / Pitta / Kapha  (repeating pattern across nakshatras)
_NADI_MAP: dict[int, str] = {}
_nadi_cycle = ['Vata', 'Pitta', 'Kapha']
for _i in range(1, 28):
    _NADI_MAP[_i] = _nadi_cycle[(_i - 1) % 3]


# Vashya -- simplified Moon-sign based groupings
# Sign categories for vashya:
#   Chatushpada (quadruped): Aries, Taurus, 2nd half Sagittarius, 1st half Capricorn
#   Manava (human): Gemini, Virgo, Libra, 1st half Sagittarius, Aquarius
#   Jalachara (water): Cancer, Pisces, 2nd half Capricorn
#   Vanachara (wild): Leo
#   Keeta (insect): Scorpio
_VASHYA_GROUP: dict[int, str] = {
    1: 'Chatushpada',   # Aries
    2: 'Chatushpada',   # Taurus
    3: 'Manava',        # Gemini
    4: 'Jalachara',     # Cancer
    5: 'Vanachara',     # Leo
    6: 'Manava',        # Virgo
    7: 'Manava',        # Libra
    8: 'Keeta',         # Scorpio
    9: 'Manava',        # Sagittarius  (simplified)
    10: 'Chatushpada',  # Capricorn    (simplified)
    11: 'Manava',       # Aquarius
    12: 'Jalachara',    # Pisces
}

# Vashya scoring:  same group or compatible pairs => 2, partial => 1, else 0
_VASHYA_COMPAT: dict[tuple[str, str], float] = {
    ('Chatushpada', 'Chatushpada'): 2,
    ('Manava', 'Manava'): 2,
    ('Jalachara', 'Jalachara'): 2,
    ('Vanachara', 'Vanachara'): 2,
    ('Keeta', 'Keeta'): 2,
    ('Manava', 'Chatushpada'): 1,
    ('Chatushpada', 'Manava'): 1,
    ('Jalachara', 'Manava'): 1,
    ('Manava', 'Jalachara'): 1,
    ('Vanachara', 'Chatushpada'): 0.5,
    ('Chatushpada', 'Vanachara'): 0.5,
    ('Vanachara', 'Manava'): 0.5,
    ('Manava', 'Vanachara'): 0.5,
}


# ---------------------------------------------------------------------------
# Nakshatra -> Moon sign helper  (nakshatra 1-27 -> sign 1-12)
# ---------------------------------------------------------------------------

def _nakshatra_to_sign(nakshatra: int) -> int:
    """Return the zodiac sign (1-12) that a nakshatra falls in.

    Each sign spans 2.25 nakshatras (30 deg / 13.333 deg).
    Nak 1 (Ashwini) starts at 0 deg Aries (sign 1).
    """
    # Each nakshatra spans 13d20m = 13.3333 deg
    # Midpoint longitude of nakshatra n (1-based): (n - 1) * 13.3333 + 6.6667
    mid_long = (nakshatra - 1) * (360 / 27) + (180 / 27)
    return int(mid_long / 30) % 12 + 1


# ---------------------------------------------------------------------------
# 1. GUNA MILAN -- eight kutas
# ---------------------------------------------------------------------------

def _kuta_varna(nak1: int, nak2: int) -> dict:
    """Varna kuta (1 point max). Boy's varna >= girl's varna => 1."""
    v1 = _VARNA_MAP.get(nak1, 1)
    v2 = _VARNA_MAP.get(nak2, 1)
    # Traditionally: person1 = boy, person2 = girl
    score = 1 if v1 >= v2 else 0
    varna_names = {4: 'Brahmin', 3: 'Kshatriya', 2: 'Vaishya', 1: 'Shudra'}
    return {
        'name': 'Varna',
        'max': 1,
        'score': score,
        'person1_varna': varna_names.get(v1, '?'),
        'person2_varna': varna_names.get(v2, '?'),
        'description': 'Spiritual / ego compatibility',
    }


def _kuta_vashya(nak1: int, nak2: int) -> dict:
    """Vashya kuta (2 points max). Based on Moon sign groupings."""
    sign1 = _nakshatra_to_sign(nak1)
    sign2 = _nakshatra_to_sign(nak2)
    grp1 = _VASHYA_GROUP.get(sign1, 'Manava')
    grp2 = _VASHYA_GROUP.get(sign2, 'Manava')
    score = _VASHYA_COMPAT.get((grp1, grp2), 0)
    return {
        'name': 'Vashya',
        'max': 2,
        'score': score,
        'person1_group': grp1,
        'person2_group': grp2,
        'description': 'Power / control dynamics',
    }


def _kuta_tara(nak1: int, nak2: int) -> dict:
    """Tara kuta (3 points max). Birth-star compatibility."""
    count = ((nak2 - nak1) % 27) or 27
    remainder = count % 9
    if remainder in (1, 2, 4, 6, 8):
        score = 3.0
        quality = 'Favorable'
    elif remainder in (0, 9):
        score = 1.5
        quality = 'Neutral'
    else:
        score = 0.0
        quality = 'Unfavorable'
    return {
        'name': 'Tara',
        'max': 3,
        'score': score,
        'remainder': remainder,
        'quality': quality,
        'description': 'Birth star compatibility / destiny alignment',
    }


def _kuta_yoni(nak1: int, nak2: int) -> dict:
    """Yoni kuta (4 points max). Physical / sexual compatibility."""
    a1 = _YONI_ANIMAL.get(nak1, 'Horse')
    a2 = _YONI_ANIMAL.get(nak2, 'Horse')

    if a1 == a2:
        score = 4
        quality = 'Same animal -- excellent'
    elif (a1, a2) in _YONI_FRIENDLY or (a2, a1) in _YONI_FRIENDLY:
        # same-animal pairs already handled above; this catches leftover friendly
        score = 3
        quality = 'Friendly'
    elif _YONI_ENEMIES.get(a1) == a2:
        score = 0
        quality = 'Enemies -- very challenging'
    elif a1 in _YONI_ENEMIES and a2 in _YONI_ENEMIES:
        score = 1
        quality = 'Somewhat hostile'
    else:
        score = 2
        quality = 'Neutral'
    return {
        'name': 'Yoni',
        'max': 4,
        'score': score,
        'person1_animal': a1,
        'person2_animal': a2,
        'quality': quality,
        'description': 'Physical / sexual compatibility',
    }


def _kuta_graha_maitri(nak1: int, nak2: int) -> dict:
    """Graha Maitri kuta (5 points max). Moon sign lords' friendship."""
    sign1 = _nakshatra_to_sign(nak1)
    sign2 = _nakshatra_to_sign(nak2)
    lord1 = SIGN_LORDS.get(sign1, 'Sun')
    lord2 = SIGN_LORDS.get(sign2, 'Sun')

    if lord1 == lord2:
        score = 5
        quality = 'Same lord'
    else:
        l1_friends = NATURAL_FRIENDS.get(lord1, [])
        l1_enemies = NATURAL_ENEMIES.get(lord1, [])
        l2_friends = NATURAL_FRIENDS.get(lord2, [])
        l2_enemies = NATURAL_ENEMIES.get(lord2, [])

        is_1_friend_of_2 = lord2 in l1_friends
        is_2_friend_of_1 = lord1 in l2_friends
        is_1_enemy_of_2 = lord2 in l1_enemies
        is_2_enemy_of_1 = lord1 in l2_enemies

        if is_1_friend_of_2 and is_2_friend_of_1:
            score = 5
            quality = 'Mutual friends'
        elif (is_1_friend_of_2 and not is_2_enemy_of_1) or \
             (is_2_friend_of_1 and not is_1_enemy_of_2):
            score = 4
            quality = 'One friend, one neutral'
        elif not is_1_enemy_of_2 and not is_2_enemy_of_1 and \
             not is_1_friend_of_2 and not is_2_friend_of_1:
            score = 3
            quality = 'Both neutral'
        elif is_1_enemy_of_2 and is_2_enemy_of_1:
            score = 0
            quality = 'Mutual enemies'
        else:
            score = 1
            quality = 'One enemy'
    return {
        'name': 'Graha Maitri',
        'max': 5,
        'score': score,
        'person1_lord': lord1,
        'person2_lord': lord2,
        'quality': quality,
        'description': 'Mental / intellectual compatibility',
    }


def _kuta_gana(nak1: int, nak2: int) -> dict:
    """Gana kuta (6 points max). Temperament compatibility."""
    g1 = _gana_of(nak1)
    g2 = _gana_of(nak2)

    if g1 == g2:
        score = 6
    elif {g1, g2} == {'Deva', 'Manushya'}:
        score = 5
    elif {g1, g2} == {'Manushya', 'Rakshasa'}:
        score = 1
    else:
        # Deva + Rakshasa
        score = 0

    return {
        'name': 'Gana',
        'max': 6,
        'score': score,
        'person1_gana': g1,
        'person2_gana': g2,
        'description': 'Temperament compatibility',
    }


def _kuta_bhakoot(nak1: int, nak2: int) -> dict:
    """Bhakoot kuta (7 points max). Emotional compatibility via Moon sign distance."""
    sign1 = _nakshatra_to_sign(nak1)
    sign2 = _nakshatra_to_sign(nak2)

    dist = ((sign2 - sign1) % 12) or 12
    reverse_dist = ((sign1 - sign2) % 12) or 12

    # Favorable pairs: 1-1, 1-7, 3-11, 4-10, 5-9
    favorable = {(1, 1), (1, 7), (7, 1), (3, 11), (11, 3), (4, 10), (10, 4), (5, 9), (9, 5)}
    # Unfavorable: 2-12, 6-8
    unfavorable = {(2, 12), (12, 2), (6, 8), (8, 6)}

    pair = (dist, reverse_dist)
    if dist == reverse_dist == 1:
        # same sign
        score = 7
        quality = 'Same sign'
    elif (dist, reverse_dist) in favorable or (reverse_dist, dist) in favorable:
        score = 7
        quality = 'Favorable'
    elif (dist, reverse_dist) in unfavorable or (reverse_dist, dist) in unfavorable:
        score = 0
        quality = 'Unfavorable'
    else:
        score = 7
        quality = 'Favorable'

    return {
        'name': 'Bhakoot',
        'max': 7,
        'score': score,
        'person1_sign': SIGNS[sign1],
        'person2_sign': SIGNS[sign2],
        'distance': dist,
        'quality': quality,
        'description': 'Emotional compatibility / prosperity',
    }


def _kuta_nadi(nak1: int, nak2: int) -> dict:
    """Nadi kuta (8 points max). Health / genetic compatibility."""
    n1 = _NADI_MAP.get(nak1, 'Vata')
    n2 = _NADI_MAP.get(nak2, 'Vata')
    score = 0 if n1 == n2 else 8
    return {
        'name': 'Nadi',
        'max': 8,
        'score': score,
        'person1_nadi': n1,
        'person2_nadi': n2,
        'quality': 'Same nadi -- caution' if n1 == n2 else 'Different nadi -- excellent',
        'description': 'Health / genetic compatibility',
    }


def calculate_guna_milan(nak1: int, nak2: int) -> dict:
    """Calculate all eight Ashtakoot kutas and return a summary dict.

    Parameters
    ----------
    nak1 : int
        Moon nakshatra of person 1 (1-27).
    nak2 : int
        Moon nakshatra of person 2 (1-27).

    Returns
    -------
    dict with keys: kutas (list of 8 dicts), total, max_total, percentage, assessment.
    """
    kutas = [
        _kuta_varna(nak1, nak2),
        _kuta_vashya(nak1, nak2),
        _kuta_tara(nak1, nak2),
        _kuta_yoni(nak1, nak2),
        _kuta_graha_maitri(nak1, nak2),
        _kuta_gana(nak1, nak2),
        _kuta_bhakoot(nak1, nak2),
        _kuta_nadi(nak1, nak2),
    ]
    total = sum(k['score'] for k in kutas)
    pct = (total / 36) * 100

    if total >= 28:
        assessment = 'Excellent'
    elif total >= 24:
        assessment = 'Very Good'
    elif total >= 18:
        assessment = 'Good'
    elif total >= 12:
        assessment = 'Average'
    else:
        assessment = 'Challenging'

    return {
        'kutas': kutas,
        'total': total,
        'max_total': 36,
        'percentage': round(pct, 1),
        'assessment': assessment,
    }


# ---------------------------------------------------------------------------
# 2. CROSS-CHART ANALYSIS
# ---------------------------------------------------------------------------

def _find_planet(planets: list[PlanetPosition], name: str) -> PlanetPosition | None:
    """Return the PlanetPosition for *name*, or None."""
    for p in planets:
        if p.planet == name:
            return p
    return None


def _planet_dignity_label(planet: PlanetPosition) -> str:
    """Return a human-readable dignity label."""
    if planet.dignity:
        return planet.dignity.capitalize()
    name = planet.planet
    if planet.sign == EXALTATION.get(name):
        return 'Exalted'
    if planet.sign == DEBILITATION.get(name):
        return 'Debilitated'
    if planet.sign in OWN_SIGNS.get(name, []):
        return 'Own sign'
    return 'Neutral'


def _lords_are_friends(lord1: str, lord2: str) -> bool:
    return lord2 in NATURAL_FRIENDS.get(lord1, [])


def _lords_are_enemies(lord1: str, lord2: str) -> bool:
    return lord2 in NATURAL_ENEMIES.get(lord1, [])


def analyze_venus(
    p1_planets: list[PlanetPosition],
    p2_planets: list[PlanetPosition],
) -> dict:
    """Compare Venus positions between two charts."""
    v1 = _find_planet(p1_planets, 'Venus')
    v2 = _find_planet(p2_planets, 'Venus')

    if v1 is None or v2 is None:
        return {'available': False, 'note': 'Venus data missing from one or both charts.'}

    same_sign = v1.sign == v2.sign
    sign_dist = ((v2.sign - v1.sign) % 12) or 12
    # Trine (5, 9) or same sign are harmonious
    harmonious = same_sign or sign_dist in (5, 9)
    # Opposition (7) or square-like (4, 10) can be challenging
    tense = sign_dist in (6, 8)

    if harmonious:
        quality = 'Harmonious'
    elif tense:
        quality = 'Tense'
    else:
        quality = 'Neutral'

    return {
        'available': True,
        'person1_venus_sign': SIGNS[v1.sign],
        'person1_venus_house': v1.house,
        'person1_venus_dignity': _planet_dignity_label(v1),
        'person2_venus_sign': SIGNS[v2.sign],
        'person2_venus_house': v2.house,
        'person2_venus_dignity': _planet_dignity_label(v2),
        'same_sign': same_sign,
        'sign_distance': sign_dist,
        'quality': quality,
    }


def analyze_seventh_lord(
    p1_planets: list[PlanetPosition],
    p1_asc_sign: int,
    p2_planets: list[PlanetPosition],
    p2_asc_sign: int,
) -> dict:
    """Examine the 7th lord of each chart and where it falls in the partner's chart."""
    seventh_sign_1 = ((p1_asc_sign - 1 + 6) % 12) + 1
    seventh_sign_2 = ((p2_asc_sign - 1 + 6) % 12) + 1
    lord1 = SIGN_LORDS.get(seventh_sign_1, 'Sun')
    lord2 = SIGN_LORDS.get(seventh_sign_2, 'Sun')

    # Find these lords in the charts
    lord1_in_p1 = _find_planet(p1_planets, lord1)
    lord2_in_p2 = _find_planet(p2_planets, lord2)

    result: dict = {
        'person1_7th_sign': SIGNS[seventh_sign_1],
        'person1_7th_lord': lord1,
        'person2_7th_sign': SIGNS[seventh_sign_2],
        'person2_7th_lord': lord2,
    }

    if lord1_in_p1:
        # Where is person1's 7th lord by sign -- check in person2's chart by sign
        p1_lord_sign = lord1_in_p1.sign
        # House in person2's frame = distance from person2's ascendant
        house_in_p2 = ((p1_lord_sign - p2_asc_sign) % 12) + 1
        result['person1_7th_lord_sign'] = SIGNS[p1_lord_sign]
        result['person1_7th_lord_in_p2_house'] = house_in_p2

    if lord2_in_p2:
        p2_lord_sign = lord2_in_p2.sign
        house_in_p1 = ((p2_lord_sign - p1_asc_sign) % 12) + 1
        result['person2_7th_lord_sign'] = SIGNS[p2_lord_sign]
        result['person2_7th_lord_in_p1_house'] = house_in_p1

    # Is there a lord exchange (mutual reception)?
    if lord1_in_p1 and lord2_in_p2:
        exchange = (lord1_in_p1.sign == seventh_sign_2 and lord2_in_p2.sign == seventh_sign_1)
        result['mutual_exchange'] = exchange
    else:
        result['mutual_exchange'] = False

    return result


def analyze_ascendant_compatibility(p1_asc_sign: int, p2_asc_sign: int) -> dict:
    """Assess ascendant lord relationship."""
    lord1 = SIGN_LORDS.get(p1_asc_sign, 'Sun')
    lord2 = SIGN_LORDS.get(p2_asc_sign, 'Sun')

    same_sign = p1_asc_sign == p2_asc_sign
    dist = ((p2_asc_sign - p1_asc_sign) % 12) or 12

    if lord1 == lord2 or same_sign:
        quality = 'Excellent -- same or same-lord ascendants'
    elif _lords_are_friends(lord1, lord2) and _lords_are_friends(lord2, lord1):
        quality = 'Good -- mutual friendly lords'
    elif _lords_are_friends(lord1, lord2) or _lords_are_friends(lord2, lord1):
        quality = 'Moderate -- partially friendly lords'
    elif _lords_are_enemies(lord1, lord2) or _lords_are_enemies(lord2, lord1):
        quality = 'Challenging -- enemy ascendant lords'
    else:
        quality = 'Neutral'

    return {
        'person1_asc': SIGNS[p1_asc_sign],
        'person1_asc_lord': lord1,
        'person2_asc': SIGNS[p2_asc_sign],
        'person2_asc_lord': lord2,
        'sign_distance': dist,
        'quality': quality,
    }


def check_mangal_dosha(planets: list[PlanetPosition], asc_sign: int) -> dict:
    """Check for Mangal Dosha (Kuja Dosha) in a single chart.

    Mars in houses 1, 2, 4, 7, 8, or 12 from ascendant *or* Moon *or* Venus
    is traditionally considered Manglik.  We check from Ascendant here.
    """
    mars = _find_planet(planets, 'Mars')
    if mars is None:
        return {'manglik': False, 'note': 'Mars not found in chart.'}

    mars_house = ((mars.sign - asc_sign) % 12) + 1
    manglik_houses = {1, 2, 4, 7, 8, 12}
    is_manglik = mars_house in manglik_houses

    # Check for common cancellations
    cancellations = []
    if mars.sign in (1, 8, 10):
        # Mars in own sign or exaltation -- reduced effect
        cancellations.append(f'Mars in own/exalted sign ({SIGNS[mars.sign]})')
    jupiter = _find_planet(planets, 'Jupiter')
    if jupiter and ((jupiter.sign - asc_sign) % 12) + 1 in (1, 4, 7):
        cancellations.append('Jupiter in kendra mitigates Mangal Dosha')

    return {
        'manglik': is_manglik,
        'mars_house': mars_house,
        'mars_sign': SIGNS[mars.sign],
        'cancellations': cancellations,
        'effective': is_manglik and len(cancellations) == 0,
    }


# ---------------------------------------------------------------------------
# 3. SUMMARY GENERATION
# ---------------------------------------------------------------------------

def _generate_summary(
    guna: dict,
    venus: dict,
    seventh: dict,
    asc_compat: dict,
    mangal1: dict,
    mangal2: dict,
    overall_score: float,
    assessment: str,
) -> str:
    """Compose a multi-paragraph interpretive summary."""
    paragraphs: list[str] = []

    # Guna Milan overview
    total = guna['total']
    paragraphs.append(
        f"The Ashtakoot (Guna Milan) score is {total}/36 ({guna['percentage']}%), "
        f"which is considered {guna['assessment'].lower()}. "
        + (
            "This is a strong foundation for compatibility, indicating natural "
            "harmony across most dimensions of the relationship."
            if total >= 24
            else
            "While some areas show natural alignment, others will require "
            "conscious effort and mutual understanding."
            if total >= 18
            else
            "Several areas of friction are indicated. Success in this "
            "partnership will depend on maturity, communication, and willingness "
            "to work through differences."
        )
    )

    # Nadi & health
    nadi = next(k for k in guna['kutas'] if k['name'] == 'Nadi')
    if nadi['score'] == 0:
        paragraphs.append(
            "The Nadi kuta scores zero (Nadi Dosha), traditionally the most "
            "significant compatibility concern. Both partners share the same "
            f"nadi ({nadi['person1_nadi']}), which Vedic tradition associates "
            "with potential health challenges for progeny. Remedial measures "
            "such as Nadi Dosha Nivaran Puja are sometimes recommended."
        )

    # Gana compatibility
    gana_k = next(k for k in guna['kutas'] if k['name'] == 'Gana')
    if gana_k['score'] <= 1:
        paragraphs.append(
            f"Temperament-wise, the pairing of {gana_k['person1_gana']} and "
            f"{gana_k['person2_gana']} gana suggests distinctly different "
            "temperaments. Understanding and respecting each other's emotional "
            "nature will be essential."
        )

    # Venus
    if venus.get('available'):
        paragraphs.append(
            f"Venus comparison shows Person 1's Venus in {venus['person1_venus_sign']} "
            f"({venus['person1_venus_dignity']}) and Person 2's Venus in "
            f"{venus['person2_venus_sign']} ({venus['person2_venus_dignity']}). "
            f"The overall Venus axis quality is {venus['quality'].lower()}, "
            + (
                "suggesting natural romantic resonance and shared aesthetic values."
                if venus['quality'] == 'Harmonious'
                else
                "which may require effort to align romantic expectations and love languages."
                if venus['quality'] == 'Tense'
                else
                "indicating a workable but not inherently charged romantic dynamic."
            )
        )

    # 7th lord exchange
    if seventh.get('mutual_exchange'):
        paragraphs.append(
            "A rare and highly auspicious mutual exchange of 7th lords is present, "
            "suggesting a deep karmic bond specifically related to partnership."
        )

    # Ascendant
    paragraphs.append(
        f"Ascendant compatibility: {asc_compat['quality']}. "
        f"Person 1 rising in {asc_compat['person1_asc']} (lord {asc_compat['person1_asc_lord']}) "
        f"and Person 2 rising in {asc_compat['person2_asc']} (lord {asc_compat['person2_asc_lord']})."
    )

    # Mangal Dosha
    both_manglik = mangal1.get('effective') and mangal2.get('effective')
    one_manglik = mangal1.get('effective') != mangal2.get('effective')
    if both_manglik:
        paragraphs.append(
            "Both charts carry effective Mangal Dosha, which in Vedic tradition "
            "cancels out -- a favorable indication for this pairing."
        )
    elif one_manglik:
        who = 'Person 1' if mangal1.get('effective') else 'Person 2'
        paragraphs.append(
            f"Only {who} has effective Mangal Dosha (Mars in house "
            f"{mangal1['mars_house'] if mangal1.get('effective') else mangal2['mars_house']}). "
            "This mismatch is traditionally considered a concern for marital "
            "harmony. Remedial measures may be recommended."
        )

    # Overall
    paragraphs.append(
        f"Overall compatibility score: {overall_score:.0f}/100 -- {assessment}."
    )

    return "\n\n".join(paragraphs)


# ---------------------------------------------------------------------------
# 4. MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def analyze_synastry(
    person1_planets: list[PlanetPosition],
    person1_asc_sign: int,
    person1_moon_nakshatra: int,
    person2_planets: list[PlanetPosition],
    person2_asc_sign: int,
    person2_moon_nakshatra: int,
) -> dict:
    """Run full synastry analysis between two birth charts.

    Parameters
    ----------
    person1_planets : list[PlanetPosition]
        Planetary positions for person 1.
    person1_asc_sign : int
        Ascendant sign (1-12) for person 1.
    person1_moon_nakshatra : int
        Moon nakshatra (1-27) for person 1.
    person2_planets : list[PlanetPosition]
        Planetary positions for person 2.
    person2_asc_sign : int
        Ascendant sign (1-12) for person 2.
    person2_moon_nakshatra : int
        Moon nakshatra (1-27) for person 2.

    Returns
    -------
    dict
        guna_milan, venus_analysis, seventh_lord, ascendant_compatibility,
        mangal_dosha, overall_score (0-100), assessment, summary.
    """
    # 1. Guna Milan
    guna = calculate_guna_milan(person1_moon_nakshatra, person2_moon_nakshatra)

    # 2. Cross-chart analyses
    venus = analyze_venus(person1_planets, person2_planets)
    seventh = analyze_seventh_lord(person1_planets, person1_asc_sign,
                                   person2_planets, person2_asc_sign)
    asc_compat = analyze_ascendant_compatibility(person1_asc_sign, person2_asc_sign)
    mangal1 = check_mangal_dosha(person1_planets, person1_asc_sign)
    mangal2 = check_mangal_dosha(person2_planets, person2_asc_sign)

    # 3. Composite overall score  (weighted blend)
    # Guna Milan: 60% weight  (score out of 36 -> 0-100)
    guna_pct = (guna['total'] / 36) * 100
    # Venus: 10%
    venus_score = 100 if venus.get('quality') == 'Harmonious' else (
        50 if venus.get('quality') == 'Neutral' else 25
    )
    if not venus.get('available'):
        venus_score = 50  # unknown -> neutral
    # Ascendant: 10%
    asc_quality = asc_compat['quality']
    asc_score = 100 if 'Excellent' in asc_quality else (
        75 if 'Good' in asc_quality else (
        50 if 'Moderate' in asc_quality or 'Neutral' in asc_quality else 25
    ))
    # Mangal match: 10%
    both_manglik = mangal1.get('effective') and mangal2.get('effective')
    neither_manglik = not mangal1.get('effective') and not mangal2.get('effective')
    mangal_score = 100 if (both_manglik or neither_manglik) else 30
    # 7th lord bonus: 10%
    seventh_score = 100 if seventh.get('mutual_exchange') else 60

    overall = (
        guna_pct * 0.60 +
        venus_score * 0.10 +
        asc_score * 0.10 +
        mangal_score * 0.10 +
        seventh_score * 0.10
    )
    overall = min(100, max(0, overall))

    if overall >= 80:
        assessment = 'Excellent'
    elif overall >= 65:
        assessment = 'Good'
    elif overall >= 45:
        assessment = 'Average'
    else:
        assessment = 'Challenging'

    summary = _generate_summary(
        guna, venus, seventh, asc_compat, mangal1, mangal2, overall, assessment,
    )

    return {
        'guna_milan': guna,
        'venus_analysis': venus,
        'seventh_lord': seventh,
        'ascendant_compatibility': asc_compat,
        'mangal_dosha': {
            'person1': mangal1,
            'person2': mangal2,
            'both_manglik': both_manglik,
            'cancels_out': both_manglik,
        },
        'overall_score': round(overall, 1),
        'assessment': assessment,
        'summary': summary,
    }
