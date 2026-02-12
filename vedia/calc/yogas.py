"""Yoga detection module for Vedic astrology.

Detects major planetary combinations (yogas) in a birth chart, including
benefic yogas (raja, dhana, pancha mahapurusha) and doshas (kemadruma,
kaal sarpa, mangal dosha).
"""

from ..models import (
    YogaResult,
    PlanetPosition,
    SIGN_LORDS,
    OWN_SIGNS,
    EXALTATION,
    DEBILITATION,
    NATURAL_FRIENDS,
)
from .divisional import calculate_d9_position


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _get_planet(planets: list[PlanetPosition], name: str) -> PlanetPosition | None:
    """Find a PlanetPosition by planet name (case-insensitive)."""
    name_lower = name.lower()
    for p in planets:
        if p.planet.lower() == name_lower:
            return p
    return None


def _are_in_kendra(planet1: PlanetPosition, planet2: PlanetPosition) -> bool:
    """Check if two planets are in kendra (1/4/7/10) from each other.

    Kendra relationship means the sign distance between the two planets
    is 0, 3, 6, or 9 signs (corresponding to houses 1, 4, 7, 10).
    """
    house_diff = abs(planet1.sign - planet2.sign) % 12
    return house_diff in (0, 3, 6, 9)


def _is_kendra_house(house: int) -> bool:
    """Check if a house number is a kendra (angular) house."""
    return house in (1, 4, 7, 10)


def _is_trikona_house(house: int) -> bool:
    """Check if a house number is a trikona (trinal) house."""
    return house in (1, 5, 9)


def _is_dusthana_house(house: int) -> bool:
    """Check if a house number is a dusthana (evil) house."""
    return house in (6, 8, 12)


def _get_house_lord(house: int, asc_sign: int) -> str:
    """Return the planetary lord of a given house for a given ascendant sign.

    The sign on the cusp of a house is determined by offsetting from the
    ascendant sign, and then looking up the lord of that sign.
    """
    sign = ((asc_sign - 1 + house - 1) % 12) + 1
    return SIGN_LORDS[sign]


def _get_house_of_planet(planet: PlanetPosition, asc_sign: int) -> int:
    """Derive the house number (1-12) a planet occupies from the ascendant sign.

    This uses the sign-based house system: the ascendant sign is house 1,
    the next sign is house 2, etc.  Falls back to the stored ``planet.house``
    when available.
    """
    return ((planet.sign - asc_sign) % 12) + 1


def _is_in_own_sign(planet: PlanetPosition) -> bool:
    """Check if a planet is in one of its own signs."""
    return planet.sign in OWN_SIGNS.get(planet.planet, [])


def _is_exalted(planet: PlanetPosition) -> bool:
    """Check if a planet is in its sign of exaltation."""
    return EXALTATION.get(planet.planet) == planet.sign


def _is_debilitated(planet: PlanetPosition) -> bool:
    """Check if a planet is in its sign of debilitation."""
    return DEBILITATION.get(planet.planet) == planet.sign


def _same_sign(p1: PlanetPosition, p2: PlanetPosition) -> bool:
    """Check if two planets occupy the same sign (conjunction)."""
    return p1.sign == p2.sign


def _signs_adjacent(sign1: int, sign2: int) -> bool:
    """Check if two signs are adjacent (one sign apart in either direction)."""
    diff = abs(sign1 - sign2) % 12
    return diff in (1, 11)


# ---------------------------------------------------------------------------
# 1. Gaja Kesari Yoga
# ---------------------------------------------------------------------------

def detect_gaja_kesari(
    planets: list[PlanetPosition], asc_sign: int
) -> list[YogaResult]:
    """Detect Gaja Kesari Yoga.

    Formed when Jupiter is in a kendra (1, 4, 7, 10) from the Moon, and
    Jupiter is neither debilitated nor combust.  This yoga bestows
    intelligence, eloquence, lasting fame, and a virtuous character.
    """
    results: list[YogaResult] = []

    jupiter = _get_planet(planets, 'Jupiter')
    moon = _get_planet(planets, 'Moon')
    if jupiter is None or moon is None:
        return results

    if not _are_in_kendra(jupiter, moon):
        return results

    # Jupiter must not be debilitated or combust
    if _is_debilitated(jupiter) or jupiter.is_combust:
        return results

    # Strength assessment
    if _is_exalted(jupiter) or _is_in_own_sign(jupiter):
        strength = 'strong'
    else:
        strength = 'moderate'

    jup_house = _get_house_of_planet(jupiter, asc_sign)
    moon_house = _get_house_of_planet(moon, asc_sign)

    results.append(YogaResult(
        yoga_name='Gaja Kesari Yoga',
        yoga_type='benefic',
        planets_involved=['Jupiter', 'Moon'],
        houses_involved=sorted({jup_house, moon_house}),
        strength=strength,
        description=(
            'Jupiter is in a kendra from the Moon, forming Gaja Kesari Yoga. '
            'The native is blessed with wisdom, a magnetic personality, lasting '
            'reputation, and prosperity. They are likely to hold positions of '
            'authority and enjoy the respect of learned people.'
            + (' Jupiter is in an exalted or own sign, making this yoga '
               'exceptionally powerful.' if strength == 'strong' else '')
        ),
    ))
    return results


# ---------------------------------------------------------------------------
# 2. Raja Yogas
# ---------------------------------------------------------------------------

def detect_raja_yogas(
    planets: list[PlanetPosition], asc_sign: int
) -> list[YogaResult]:
    """Detect Raja Yogas.

    A Raja Yoga forms when the lord of a kendra house (1, 4, 7, 10) and
    the lord of a trikona house (1, 5, 9) are conjunct, in mutual kendra,
    or exchange signs.  A single planet that lords both a kendra and a
    trikona also forms Raja Yoga on its own.

    Raja Yoga confers power, authority, fame, and success in all
    undertakings.
    """
    results: list[YogaResult] = []
    kendra_houses = [1, 4, 7, 10]
    trikona_houses = [1, 5, 9]

    # Build maps: lord -> list of houses it rules (kendra / trikona)
    kendra_lords: dict[str, list[int]] = {}
    trikona_lords: dict[str, list[int]] = {}

    for h in kendra_houses:
        lord = _get_house_lord(h, asc_sign)
        kendra_lords.setdefault(lord, []).append(h)

    for h in trikona_houses:
        lord = _get_house_lord(h, asc_sign)
        trikona_lords.setdefault(lord, []).append(h)

    seen_combos: set[tuple[str, ...]] = set()

    # --- Case 1: A planet lords both a kendra and a trikona ----------------
    for planet_name in set(kendra_lords) & set(trikona_lords):
        p = _get_planet(planets, planet_name)
        if p is None:
            continue

        houses = sorted(set(kendra_lords[planet_name] + trikona_lords[planet_name]))
        combo = (planet_name,)
        if combo in seen_combos:
            continue
        seen_combos.add(combo)

        strength = 'strong' if (_is_exalted(p) or _is_in_own_sign(p)) else 'moderate'
        if _is_debilitated(p):
            strength = 'weak'

        results.append(YogaResult(
            yoga_name='Raja Yoga',
            yoga_type='benefic',
            planets_involved=[planet_name],
            houses_involved=houses,
            strength=strength,
            description=(
                f'{planet_name} is the lord of both kendra house(s) '
                f'{kendra_lords[planet_name]} and trikona house(s) '
                f'{trikona_lords[planet_name]}, forming a potent Raja Yoga '
                f'by itself. The native is destined for leadership, high '
                f'status, and significant accomplishments in life.'
            ),
        ))

    # --- Case 2: Kendra lord + trikona lord connected ----------------------
    for k_lord, k_houses in kendra_lords.items():
        for t_lord, t_houses in trikona_lords.items():
            if k_lord == t_lord:
                continue  # already handled above

            combo = tuple(sorted([k_lord, t_lord]))
            if combo in seen_combos:
                continue

            p_k = _get_planet(planets, k_lord)
            p_t = _get_planet(planets, t_lord)
            if p_k is None or p_t is None:
                continue

            connection = None

            # Conjunction (same sign)
            if _same_sign(p_k, p_t):
                connection = 'conjunct'
            # Mutual kendra
            elif _are_in_kendra(p_k, p_t):
                connection = 'in mutual kendra'
            # Sign exchange (parivartana)
            elif p_k.sign in OWN_SIGNS.get(t_lord, []) and p_t.sign in OWN_SIGNS.get(k_lord, []):
                connection = 'in sign exchange (Parivartana)'

            if connection is None:
                continue

            seen_combos.add(combo)

            # Strength
            if any(_is_debilitated(pp) for pp in (p_k, p_t)):
                strength = 'weak'
            elif any(_is_exalted(pp) or _is_in_own_sign(pp) for pp in (p_k, p_t)):
                strength = 'strong'
            else:
                strength = 'moderate'

            involved_houses = sorted(set(k_houses + t_houses))
            results.append(YogaResult(
                yoga_name='Raja Yoga',
                yoga_type='benefic',
                planets_involved=list(combo),
                houses_involved=involved_houses,
                strength=strength,
                description=(
                    f'{k_lord} (lord of kendra house(s) {k_houses}) and '
                    f'{t_lord} (lord of trikona house(s) {t_houses}) are '
                    f'{connection}, forming Raja Yoga. This powerful combination '
                    f'grants the native authority, recognition, and success in '
                    f'their chosen field.'
                ),
            ))

    return results


# ---------------------------------------------------------------------------
# 3. Dhana Yogas
# ---------------------------------------------------------------------------

def detect_dhana_yogas(
    planets: list[PlanetPosition], asc_sign: int
) -> list[YogaResult]:
    """Detect Dhana (wealth) Yogas.

    Dhana Yogas are formed through the interaction of the lords of
    wealth-producing houses (2, 5, 9, 11).  They indicate financial
    prosperity, material comforts, and accumulation of assets.
    """
    results: list[YogaResult] = []

    lord_2 = _get_house_lord(2, asc_sign)
    lord_5 = _get_house_lord(5, asc_sign)
    lord_9 = _get_house_lord(9, asc_sign)
    lord_11 = _get_house_lord(11, asc_sign)

    p_lord_2 = _get_planet(planets, lord_2)
    p_lord_5 = _get_planet(planets, lord_5)
    p_lord_9 = _get_planet(planets, lord_9)
    p_lord_11 = _get_planet(planets, lord_11)

    seen: set[str] = set()

    # --- 2nd and 11th lords conjunct or in mutual kendra -------------------
    if p_lord_2 and p_lord_11:
        connected = False
        connection = ''
        if _same_sign(p_lord_2, p_lord_11):
            connected = True
            connection = 'conjunct'
        elif _are_in_kendra(p_lord_2, p_lord_11):
            connected = True
            connection = 'in mutual kendra'

        if connected:
            key = f'2-11-{connection}'
            if key not in seen:
                seen.add(key)
                strength = 'strong' if any(
                    _is_exalted(p) or _is_in_own_sign(p)
                    for p in (p_lord_2, p_lord_11)
                ) else 'moderate'

                results.append(YogaResult(
                    yoga_name='Dhana Yoga',
                    yoga_type='benefic',
                    planets_involved=sorted({lord_2, lord_11}),
                    houses_involved=[2, 11],
                    strength=strength,
                    description=(
                        f'The lord of the 2nd house ({lord_2}) and the lord of '
                        f'the 11th house ({lord_11}) are {connection}, forming '
                        f'Dhana Yoga. The native is likely to accumulate '
                        f'substantial wealth through earned income and '
                        f'investments.'
                    ),
                ))

    # --- 5th/9th lord conjunct with 2nd or 11th lord ----------------------
    for trikona_h, trikona_lord, p_trikona in [
        (5, lord_5, p_lord_5),
        (9, lord_9, p_lord_9),
    ]:
        if p_trikona is None:
            continue
        for wealth_h, wealth_lord, p_wealth in [
            (2, lord_2, p_lord_2),
            (11, lord_11, p_lord_11),
        ]:
            if p_wealth is None:
                continue
            if _same_sign(p_trikona, p_wealth):
                key = f'{trikona_h}-{wealth_h}'
                if key not in seen:
                    seen.add(key)
                    strength = 'strong' if any(
                        _is_exalted(p) or _is_in_own_sign(p)
                        for p in (p_trikona, p_wealth)
                    ) else 'moderate'

                    results.append(YogaResult(
                        yoga_name='Dhana Yoga',
                        yoga_type='benefic',
                        planets_involved=sorted({trikona_lord, wealth_lord}),
                        houses_involved=sorted({trikona_h, wealth_h}),
                        strength=strength,
                        description=(
                            f'The lord of the {trikona_h}th house ({trikona_lord}) '
                            f'is conjunct the lord of the {wealth_h}th house '
                            f'({wealth_lord}), forming Dhana Yoga. This promises '
                            f'wealth through fortune, past-life merit, and '
                            f'speculative gains.'
                        ),
                    ))

    # --- Jupiter as lord of 2nd, 5th, or 11th in strong position -----------
    jupiter = _get_planet(planets, 'Jupiter')
    if jupiter is not None:
        jup_lords_houses = []
        for h, lord in [(2, lord_2), (5, lord_5), (11, lord_11)]:
            if lord == 'Jupiter':
                jup_lords_houses.append(h)

        if jup_lords_houses and (_is_exalted(jupiter) or _is_in_own_sign(jupiter)
                                  or _is_kendra_house(jupiter.house)):
            key = f'jupiter-dhana-{jup_lords_houses}'
            if key not in seen:
                seen.add(key)
                strength = 'strong' if (_is_exalted(jupiter) or _is_in_own_sign(jupiter)) else 'moderate'
                results.append(YogaResult(
                    yoga_name='Dhana Yoga (Jupiter)',
                    yoga_type='benefic',
                    planets_involved=['Jupiter'],
                    houses_involved=jup_lords_houses,
                    strength=strength,
                    description=(
                        f'Jupiter, the great benefic, rules wealth house(s) '
                        f'{jup_lords_houses} and is placed in a strong position '
                        f'({"exalted" if _is_exalted(jupiter) else "own sign" if _is_in_own_sign(jupiter) else "kendra house"}). '
                        f'This Dhana Yoga blesses the native with financial '
                        f'abundance, wise financial decisions, and growth of '
                        f'wealth over time.'
                    ),
                ))

    return results


# ---------------------------------------------------------------------------
# 4. Pancha Mahapurusha Yogas
# ---------------------------------------------------------------------------

_MAHAPURUSHA_NAMES = {
    'Mars': 'Ruchaka',
    'Mercury': 'Bhadra',
    'Jupiter': 'Hamsa',
    'Venus': 'Malavya',
    'Saturn': 'Shasha',
}

_MAHAPURUSHA_DESC = {
    'Mars': (
        'Ruchaka Yoga bestows a strong body, courageous temperament, '
        'leadership qualities, and success in military, police, or '
        'competitive fields. The native commands respect and is fearless.'
    ),
    'Mercury': (
        'Bhadra Yoga grants sharp intellect, oratorical skills, '
        'proficiency in trade and commerce, and a youthful appearance. '
        'The native excels in communication, writing, and business.'
    ),
    'Jupiter': (
        'Hamsa Yoga blesses the native with wisdom, spirituality, '
        'good morals, and a generous disposition. They are learned, '
        'respected by the virtuous, and enjoy a comfortable life.'
    ),
    'Venus': (
        'Malavya Yoga confers beauty, artistic talent, a luxurious '
        'lifestyle, and a happy marriage. The native is charming, '
        'sensual, and surrounded by material comforts.'
    ),
    'Saturn': (
        'Shasha Yoga endows the native with authority over others, '
        'administrative prowess, and a disciplined character. They '
        'rise through perseverance and may hold positions in government '
        'or large organizations.'
    ),
}


def detect_pancha_mahapurusha(
    planets: list[PlanetPosition], asc_sign: int
) -> list[YogaResult]:
    """Detect Pancha Mahapurusha Yogas.

    These five great yogas form when Mars, Mercury, Jupiter, Venus, or
    Saturn occupy their own or exaltation sign while simultaneously
    being in a kendra house (1, 4, 7, 10) from the ascendant.
    """
    results: list[YogaResult] = []

    for planet_name in ('Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'):
        p = _get_planet(planets, planet_name)
        if p is None:
            continue

        in_own_or_exalted = _is_in_own_sign(p) or _is_exalted(p)
        house = _get_house_of_planet(p, asc_sign)
        in_kendra = _is_kendra_house(house)

        if in_own_or_exalted and in_kendra:
            yoga_name = _MAHAPURUSHA_NAMES[planet_name]
            strength = 'strong' if _is_exalted(p) else 'moderate'
            # Combust or retrograde adjustments
            if p.is_combust:
                strength = 'weak'

            results.append(YogaResult(
                yoga_name=f'{yoga_name} Yoga (Pancha Mahapurusha)',
                yoga_type='benefic',
                planets_involved=[planet_name],
                houses_involved=[house],
                strength=strength,
                description=_MAHAPURUSHA_DESC[planet_name],
            ))

    return results


# ---------------------------------------------------------------------------
# 5. Budhaditya Yoga
# ---------------------------------------------------------------------------

def detect_budhaditya(
    planets: list[PlanetPosition], asc_sign: int
) -> list[YogaResult]:
    """Detect Budhaditya Yoga.

    Formed when the Sun and Mercury are conjunct (same sign) in a kendra
    or trikona house.  This yoga sharpens the intellect and confers fame
    through learning.  Its potency is reduced when Mercury is combust.
    """
    results: list[YogaResult] = []

    sun = _get_planet(planets, 'Sun')
    mercury = _get_planet(planets, 'Mercury')
    if sun is None or mercury is None:
        return results

    if not _same_sign(sun, mercury):
        return results

    house = _get_house_of_planet(sun, asc_sign)
    if not (_is_kendra_house(house) or _is_trikona_house(house)):
        return results

    # Mercury combust makes the yoga weaker but it still exists
    if mercury.is_combust:
        strength = 'weak'
        combust_note = (
            ' However, Mercury is combust (too close to the Sun), which '
            'diminishes the clarity of intellect and may cause communication '
            'difficulties until the native matures.'
        )
    else:
        if _is_exalted(mercury) or _is_in_own_sign(mercury):
            strength = 'strong'
        else:
            strength = 'moderate'
        combust_note = ''

    results.append(YogaResult(
        yoga_name='Budhaditya Yoga',
        yoga_type='benefic',
        planets_involved=['Sun', 'Mercury'],
        houses_involved=[house],
        strength=strength,
        description=(
            f'Sun and Mercury are conjunct in house {house}, a '
            f'{"kendra" if _is_kendra_house(house) else "trikona"} house, '
            f'forming Budhaditya Yoga. The native possesses sharp intelligence, '
            f'analytical ability, and can attain fame through education, '
            f'writing, or scholarly pursuits.{combust_note}'
        ),
    ))
    return results


# ---------------------------------------------------------------------------
# 6. Viparita Raja Yoga
# ---------------------------------------------------------------------------

def detect_viparita_raja(
    planets: list[PlanetPosition], asc_sign: int
) -> list[YogaResult]:
    """Detect Viparita Raja Yoga.

    Formed when the lord of a dusthana house (6, 8, 12) is placed in
    another dusthana house.  Paradoxically, this turns misfortune into
    fortune -- the native benefits from the downfall of enemies or
    unexpected reversals of adversity.
    """
    results: list[YogaResult] = []
    dusthana_houses = [6, 8, 12]

    _yoga_names = {
        6: 'Harsha Viparita Raja Yoga',
        8: 'Sarala Viparita Raja Yoga',
        12: 'Vimala Viparita Raja Yoga',
    }

    _yoga_descs = {
        6: (
            'The lord of the 6th house (enemies, debt, disease) is placed in '
            'a dusthana, forming Harsha Viparita Raja Yoga. The native '
            'overcomes enemies and competition effortlessly, enjoys good '
            'health, and turns obstacles into opportunities.'
        ),
        8: (
            'The lord of the 8th house (obstacles, sudden events) is placed in '
            'a dusthana, forming Sarala Viparita Raja Yoga. The native is '
            'fearless, overcomes crises with ease, and may gain through '
            'inheritance, insurance, or the misfortunes of others.'
        ),
        12: (
            'The lord of the 12th house (loss, expenditure) is placed in a '
            'dusthana, forming Vimala Viparita Raja Yoga. The native has '
            'controlled expenditure, gains spiritual merit, and may prosper '
            'in foreign lands or through charitable activities.'
        ),
    }

    for source_house in dusthana_houses:
        lord = _get_house_lord(source_house, asc_sign)
        p = _get_planet(planets, lord)
        if p is None:
            continue

        placed_house = _get_house_of_planet(p, asc_sign)
        if placed_house in dusthana_houses and placed_house != source_house:
            strength = 'moderate'
            # Stronger if the lord is not debilitated
            if _is_debilitated(p):
                strength = 'weak'
            elif _is_exalted(p) or _is_in_own_sign(p):
                strength = 'strong'

            results.append(YogaResult(
                yoga_name=_yoga_names[source_house],
                yoga_type='benefic',
                planets_involved=[lord],
                houses_involved=sorted({source_house, placed_house}),
                strength=strength,
                description=_yoga_descs[source_house],
            ))

    return results


# ---------------------------------------------------------------------------
# 7. Neecha Bhanga Raja Yoga
# ---------------------------------------------------------------------------

def detect_neecha_bhanga(
    planets: list[PlanetPosition], asc_sign: int
) -> list[YogaResult]:
    """Detect Neecha Bhanga Raja Yoga (cancellation of debilitation).

    A debilitated planet's weakness is cancelled (and turned into
    strength) if:
      - The lord of the sign where the planet is debilitated is in a
        kendra from the lagna or the Moon.
      - OR the planet that is exalted in the debilitation sign is in a
        kendra from the lagna or the Moon.

    The native rises from humble beginnings or overcomes significant
    hardships to achieve great success.
    """
    results: list[YogaResult] = []

    moon = _get_planet(planets, 'Moon')

    # Build a mapping: sign -> planet exalted in that sign
    exaltation_lord_of_sign: dict[int, str] = {}
    for planet_name, exalt_sign in EXALTATION.items():
        exaltation_lord_of_sign[exalt_sign] = planet_name

    for p in planets:
        if not _is_debilitated(p):
            continue
        if p.planet in ('Rahu', 'Ketu'):
            continue  # typically not considered for neecha bhanga

        debilitation_sign = p.sign  # the sign where the planet sits (debilitated)
        sign_lord_name = SIGN_LORDS.get(debilitation_sign)
        cancellation_reasons: list[str] = []

        # Condition 1: Lord of the debilitation sign in kendra from lagna/Moon
        if sign_lord_name:
            sign_lord = _get_planet(planets, sign_lord_name)
            if sign_lord is not None:
                sign_lord_house = _get_house_of_planet(sign_lord, asc_sign)
                in_kendra_from_lagna = _is_kendra_house(sign_lord_house)
                in_kendra_from_moon = (
                    moon is not None and _are_in_kendra(sign_lord, moon)
                )
                if in_kendra_from_lagna or in_kendra_from_moon:
                    loc = []
                    if in_kendra_from_lagna:
                        loc.append('lagna')
                    if in_kendra_from_moon:
                        loc.append('Moon')
                    cancellation_reasons.append(
                        f'{sign_lord_name} (lord of the debilitation sign) is '
                        f'in a kendra from {" and ".join(loc)}'
                    )

        # Condition 2: Planet exalted in the debilitation sign in kendra
        exalt_planet_name = exaltation_lord_of_sign.get(debilitation_sign)
        if exalt_planet_name and exalt_planet_name != p.planet:
            exalt_planet = _get_planet(planets, exalt_planet_name)
            if exalt_planet is not None:
                exalt_house = _get_house_of_planet(exalt_planet, asc_sign)
                in_kendra_from_lagna = _is_kendra_house(exalt_house)
                in_kendra_from_moon = (
                    moon is not None and _are_in_kendra(exalt_planet, moon)
                )
                if in_kendra_from_lagna or in_kendra_from_moon:
                    loc = []
                    if in_kendra_from_lagna:
                        loc.append('lagna')
                    if in_kendra_from_moon:
                        loc.append('Moon')
                    cancellation_reasons.append(
                        f'{exalt_planet_name} (exalted in the debilitation sign) '
                        f'is in a kendra from {" and ".join(loc)}'
                    )

        if cancellation_reasons:
            results.append(YogaResult(
                yoga_name='Neecha Bhanga Raja Yoga',
                yoga_type='benefic',
                planets_involved=[p.planet],
                houses_involved=[_get_house_of_planet(p, asc_sign)],
                strength='moderate',
                description=(
                    f'{p.planet} is debilitated in {_sign_name(p.sign)}, but '
                    f'its debilitation is cancelled because: '
                    f'{"; ".join(cancellation_reasons)}. '
                    f'This Neecha Bhanga Raja Yoga indicates that the native '
                    f'will overcome early-life challenges related to '
                    f'{p.planet}\'s significations and ultimately achieve '
                    f'remarkable success through resilience and determination.'
                ),
            ))

    return results


def _sign_name(sign: int) -> str:
    """Return the name of a sign given its number (1-12)."""
    names = [
        '', 'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces',
    ]
    if 1 <= sign <= 12:
        return names[sign]
    return f'Sign-{sign}'


# ---------------------------------------------------------------------------
# 8. Kemadruma Yoga (Dosha)
# ---------------------------------------------------------------------------

def detect_kemadruma(
    planets: list[PlanetPosition], asc_sign: int
) -> list[YogaResult]:
    """Detect Kemadruma Yoga (a dosha / negative yoga).

    Kemadruma Yoga is formed when no planet (Sun through Saturn,
    excluding Rahu/Ketu) occupies the 2nd or 12th sign from the Moon.
    It can indicate periods of poverty, loneliness, or lack of support,
    though its effects are mitigated if Jupiter aspects the Moon or if
    the Moon is in a kendra.
    """
    results: list[YogaResult] = []

    moon = _get_planet(planets, 'Moon')
    if moon is None:
        return results

    moon_sign = moon.sign
    sign_2nd = (moon_sign % 12) + 1          # next sign
    sign_12th = ((moon_sign - 2) % 12) + 1   # previous sign

    # Check all true planets (not Rahu/Ketu)
    has_adjacent_planet = False
    for p in planets:
        if p.planet in ('Moon', 'Rahu', 'Ketu'):
            continue
        if p.sign in (sign_2nd, sign_12th):
            has_adjacent_planet = True
            break

    if has_adjacent_planet:
        return results

    # Check for cancellation factors
    jupiter = _get_planet(planets, 'Jupiter')
    moon_house = _get_house_of_planet(moon, asc_sign)
    cancellation_notes = []

    if jupiter is not None and _are_in_kendra(jupiter, moon):
        cancellation_notes.append(
            'Jupiter aspects or is in kendra from the Moon, partially '
            'cancelling the negative effects.'
        )
    if _is_kendra_house(moon_house):
        cancellation_notes.append(
            f'The Moon is in kendra house {moon_house}, which mitigates '
            f'the dosha significantly.'
        )

    strength = 'moderate'
    if cancellation_notes:
        strength = 'weak'

    cancel_text = ' '.join(cancellation_notes)

    results.append(YogaResult(
        yoga_name='Kemadruma Yoga',
        yoga_type='dosha',
        planets_involved=['Moon'],
        houses_involved=[moon_house],
        strength=strength,
        description=(
            'No planet occupies the 2nd or 12th sign from the Moon, forming '
            'Kemadruma Yoga. This can indicate periods of financial hardship, '
            'emotional isolation, or a sense of being unsupported. The native '
            'may need to be self-reliant early in life.'
            + (f' {cancel_text}' if cancel_text else '')
        ),
    ))
    return results


# ---------------------------------------------------------------------------
# 9. Kaal Sarpa Yoga (Dosha)
# ---------------------------------------------------------------------------

def detect_kaal_sarp(
    planets: list[PlanetPosition], asc_sign: int
) -> list[YogaResult]:
    """Detect Kaal Sarpa Yoga / Dosha.

    Formed when all seven visible planets (Sun through Saturn) are
    hemmed between the Rahu-Ketu axis -- i.e. all fall within the arc
    from Rahu to Ketu in one direction around the zodiac.

    This yoga can indicate karmic restrictions, sudden upheavals, and
    delays in success, but also deep spiritual evolution.
    """
    results: list[YogaResult] = []

    rahu = _get_planet(planets, 'Rahu')
    ketu = _get_planet(planets, 'Ketu')
    if rahu is None or ketu is None:
        return results

    rahu_long = rahu.longitude
    ketu_long = ketu.longitude

    # Collect longitudes of the seven planets
    seven_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
    planet_longs: list[float] = []
    for name in seven_planets:
        p = _get_planet(planets, name)
        if p is None:
            return results  # incomplete data
        planet_longs.append(p.longitude)

    # Check if all planets are on one side of the Rahu-Ketu axis.
    # Direction 1: arc from Rahu to Ketu going forward (increasing longitude)
    # Direction 2: arc from Ketu to Rahu going forward

    def _all_in_arc(start: float, end: float, longs: list[float]) -> bool:
        """Check if all longitudes fall within the arc from start to end
        going in the forward (increasing) direction around the circle."""
        for lng in longs:
            if start < end:
                if not (start <= lng <= end):
                    return False
            else:  # arc wraps around 360
                if not (lng >= start or lng <= end):
                    return False
        return True

    is_kaal_sarp = (
        _all_in_arc(rahu_long, ketu_long, planet_longs)
        or _all_in_arc(ketu_long, rahu_long, planet_longs)
    )

    if not is_kaal_sarp:
        return results

    # Determine partial vs full: if any planet is exactly conjunct Rahu/Ketu
    # (same sign), it is sometimes considered a "partial" Kaal Sarpa
    partial = False
    for lng in planet_longs:
        # Within ~1 degree of Rahu or Ketu
        for node_long in (rahu_long, ketu_long):
            diff = abs(lng - node_long) % 360
            if diff > 180:
                diff = 360 - diff
            if diff < 1.0:
                partial = True
                break

    strength = 'moderate' if not partial else 'weak'

    results.append(YogaResult(
        yoga_name='Kaal Sarpa Yoga',
        yoga_type='dosha',
        planets_involved=['Rahu', 'Ketu'] + seven_planets,
        houses_involved=[rahu.house, ketu.house],
        strength=strength,
        description=(
            'All seven planets are hemmed between the Rahu-Ketu axis, forming '
            'Kaal Sarpa Yoga. This indicates a strong karmic pattern in this '
            'lifetime. The native may experience sudden reversals of fortune, '
            'obstacles in worldly pursuits, and recurring themes of restriction. '
            'However, this yoga also confers deep spiritual insight and the '
            'potential for extraordinary achievements once the karmic lessons '
            'are integrated.'
            + (' This is a partial Kaal Sarpa as a planet is closely conjunct '
               'a node, reducing the intensity.' if partial else '')
        ),
    ))
    return results


# ---------------------------------------------------------------------------
# 10. Mangal Dosha (Kuja Dosha)
# ---------------------------------------------------------------------------

def detect_mangal_dosha(
    planets: list[PlanetPosition], asc_sign: int
) -> list[YogaResult]:
    """Detect Mangal Dosha (Mars Dosha / Kuja Dosha).

    Formed when Mars occupies the 1st, 2nd, 4th, 7th, 8th, or 12th
    house from the ascendant.  This dosha is primarily considered in
    the context of marriage compatibility and can indicate challenges
    in partnerships.
    """
    results: list[YogaResult] = []

    mars = _get_planet(planets, 'Mars')
    if mars is None:
        return results

    house = _get_house_of_planet(mars, asc_sign)
    manglik_houses = (1, 2, 4, 7, 8, 12)

    if house not in manglik_houses:
        return results

    # 7th and 8th are considered strongest placements for the dosha
    if house in (7, 8):
        strength = 'strong'
    else:
        strength = 'moderate'

    # Check for cancellation conditions
    cancellations: list[str] = []
    if _is_in_own_sign(mars) or _is_exalted(mars):
        cancellations.append(
            f'Mars is in {"its own" if _is_in_own_sign(mars) else "its exaltation"} '
            f'sign, which significantly reduces the dosha.'
        )
        strength = 'weak'

    jupiter = _get_planet(planets, 'Jupiter')
    if jupiter is not None and (jupiter.house == 1 or _are_in_kendra(jupiter, mars)):
        cancellations.append(
            'Jupiter\'s aspect or kendra placement mitigates the dosha.'
        )
        if strength != 'weak':
            strength = 'moderate'

    cancel_text = ' '.join(cancellations)

    _house_effects = {
        1: 'in the 1st house, affecting temperament and causing aggression in relationships',
        2: 'in the 2nd house, affecting family harmony and financial stability in marriage',
        4: 'in the 4th house, affecting domestic peace and property matters',
        7: 'in the 7th house, directly impacting marriage and partnerships with potential for conflict',
        8: 'in the 8th house, indicating sudden disruptions and challenges to marital longevity',
        12: 'in the 12th house, affecting the intimate life and potentially causing separation',
    }

    results.append(YogaResult(
        yoga_name='Mangal Dosha',
        yoga_type='dosha',
        planets_involved=['Mars'],
        houses_involved=[house],
        strength=strength,
        description=(
            f'Mars is placed {_house_effects[house]}, forming Mangal Dosha. '
            f'This dosha is primarily assessed for marriage compatibility. '
            f'The native may experience delays or friction in partnerships.'
            + (f' {cancel_text}' if cancel_text else '')
        ),
    ))
    return results


# ---------------------------------------------------------------------------
# 11. Vargottama Detection
# ---------------------------------------------------------------------------

_PLANET_NAMES_ALL = [
    'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter',
    'Venus', 'Saturn', 'Rahu', 'Ketu',
]

_VARGOTTAMA_DESCRIPTIONS = {
    'Sun': (
        'The Sun occupies the same sign in both the D1 and D9 charts, '
        'greatly strengthening the native\'s sense of self, authority, '
        'and vitality. Leadership abilities and confidence are amplified.'
    ),
    'Moon': (
        'The Moon is Vargottama, reinforcing emotional stability and '
        'mental strength. The native enjoys a steady mind, good '
        'intuition, and strong public connection.'
    ),
    'Mars': (
        'Mars in Vargottama position intensifies courage, determination, '
        'and physical energy. The native possesses unwavering drive and '
        'the ability to overcome obstacles decisively.'
    ),
    'Mercury': (
        'Mercury is Vargottama, sharpening intellect, communication, '
        'and analytical skills. The native excels in learning, trade, '
        'and diplomatic expression.'
    ),
    'Jupiter': (
        'Jupiter in Vargottama amplifies wisdom, spiritual growth, and '
        'fortune. The native benefits from strong dharmic inclinations '
        'and the favour of teachers and mentors.'
    ),
    'Venus': (
        'Venus is Vargottama, enhancing artistic talent, romantic '
        'fulfilment, and material comforts. Relationships and creative '
        'pursuits flourish under this placement.'
    ),
    'Saturn': (
        'Saturn in Vargottama solidifies discipline, perseverance, and '
        'long-term success. The native builds enduring structures and '
        'earns respect through sustained effort.'
    ),
    'Rahu': (
        'Rahu in Vargottama strengthens the native\'s capacity for '
        'unconventional achievement and worldly ambition. Material '
        'gains through innovation are indicated.'
    ),
    'Ketu': (
        'Ketu in Vargottama deepens spiritual insight and detachment. '
        'The native has a powerful intuitive sense and may attain '
        'liberation-oriented wisdom.'
    ),
}


def detect_vargottama(
    planets: list[PlanetPosition], asc_sign: int
) -> list[YogaResult]:
    """Detect Vargottama planets (same sign in D1 and D9 charts).

    A planet is Vargottama when it occupies the same zodiacal sign in
    the rashi (D1) chart and the navamsha (D9) chart.  This is a
    significant indicator of inherent strength for that planet.

    Parameters
    ----------
    planets : list[PlanetPosition]
        All nine planetary positions in the D1 chart.
    asc_sign : int
        The sign number (1-12) of the ascendant (unused but kept for
        a consistent API with other detection functions).

    Returns
    -------
    list[YogaResult]
        One result per Vargottama planet found.
    """
    results: list[YogaResult] = []

    for name in _PLANET_NAMES_ALL:
        p = _get_planet(planets, name)
        if p is None:
            continue

        d9_sign = calculate_d9_position(p.sign, p.sign_degree)
        if d9_sign != p.sign:
            continue

        # Determine strength: "strong" if also exalted or in own sign
        is_exalted = (p.sign == EXALTATION.get(name))
        is_own = (p.sign in OWN_SIGNS.get(name, []))
        strength = 'strong' if (is_exalted or is_own) else 'moderate'

        description = _VARGOTTAMA_DESCRIPTIONS.get(name, (
            f'{name} is Vargottama, occupying the same sign in both '
            f'the rashi and navamsha charts, indicating inherent strength.'
        ))

        results.append(YogaResult(
            yoga_name=f'Vargottama ({name})',
            yoga_type='benefic',
            planets_involved=[name],
            houses_involved=[p.house],
            strength=strength,
            description=description,
        ))

    return results


# ---------------------------------------------------------------------------
# 12. Graha Yuddha (Planetary War)
# ---------------------------------------------------------------------------

_WAR_PLANETS = ['Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']

_WAR_EFFECTS = {
    'Mars': 'courage, initiative, and physical vitality are diminished',
    'Mercury': 'intellect, communication, and commercial acumen suffer',
    'Jupiter': 'wisdom, fortune, and spiritual guidance are weakened',
    'Venus': 'relationships, comforts, and artistic expression are harmed',
    'Saturn': 'discipline, endurance, and long-term prospects are undermined',
}


def detect_graha_yuddha(
    planets: list[PlanetPosition], asc_sign: int
) -> list[YogaResult]:
    """Detect Graha Yuddha (planetary war) between the five tara planets.

    Planetary war occurs when two planets (excluding Sun, Moon, Rahu,
    and Ketu) are within 1 degree of absolute longitude of each other.
    The planet with the higher longitude is considered the winner;
    the loser is significantly weakened.

    Parameters
    ----------
    planets : list[PlanetPosition]
        All planetary positions in the chart.
    asc_sign : int
        The sign number (1-12) of the ascendant (unused but kept for
        a consistent API with other detection functions).

    Returns
    -------
    list[YogaResult]
        One result per planetary war detected.
    """
    results: list[YogaResult] = []

    # Collect war-eligible planets that exist in the chart
    war_planets: list[PlanetPosition] = []
    for name in _WAR_PLANETS:
        p = _get_planet(planets, name)
        if p is not None:
            war_planets.append(p)

    # Check every pair
    for i in range(len(war_planets)):
        for j in range(i + 1, len(war_planets)):
            p1 = war_planets[i]
            p2 = war_planets[j]

            # Absolute longitude difference, handling 360° wrap
            diff = abs(p1.longitude - p2.longitude)
            if diff > 180.0:
                diff = 360.0 - diff

            if diff > 1.0:
                continue

            # Winner has higher longitude (traditional rule)
            if p1.longitude >= p2.longitude:
                winner, loser = p1, p2
            else:
                winner, loser = p2, p1

            strength = 'strong' if diff < 0.5 else 'moderate'
            loser_effect = _WAR_EFFECTS.get(loser.planet, 'significations are weakened')

            results.append(YogaResult(
                yoga_name=f'Graha Yuddha ({winner.planet} defeats {loser.planet})',
                yoga_type='dosha',
                planets_involved=[winner.planet, loser.planet],
                houses_involved=[winner.house, loser.house],
                strength=strength,
                description=(
                    f'{winner.planet} and {loser.planet} are in planetary war, '
                    f'separated by only {diff:.2f}°. {winner.planet} emerges '
                    f'victorious with higher longitude, while {loser.planet}\'s '
                    f'{loser_effect}. The houses ruled and occupied by '
                    f'{loser.planet} may experience setbacks.'
                ),
            ))

    return results


# ---------------------------------------------------------------------------
# 13. Sade Sati
# ---------------------------------------------------------------------------

def detect_sade_sati(
    planets: list[PlanetPosition],
    asc_sign: int,
    transit_saturn_sign: int | None = None,
) -> list[YogaResult]:
    """Detect Sade Sati (Saturn's 7.5 year transit over Moon).

    Saturn transiting the 12th, 1st, or 2nd house from the natal Moon
    sign constitutes the three phases of Sade Sati.  If
    ``transit_saturn_sign`` is not provided, the natal Saturn position
    is used as a proxy.
    """
    results: list[YogaResult] = []

    moon = _get_planet(planets, 'Moon')
    if moon is None:
        return results

    moon_sign = moon.sign

    if transit_saturn_sign is None:
        saturn = _get_planet(planets, 'Saturn')
        if saturn is None:
            return results
        saturn_sign = saturn.sign
    else:
        saturn_sign = transit_saturn_sign

    # The three phases:
    # Phase 1 (rising): Saturn in 12th from Moon
    # Phase 2 (peak):   Saturn in same sign as Moon (1st from Moon)
    # Phase 3 (setting): Saturn in 2nd from Moon
    sign_12th = ((moon_sign - 2) % 12) + 1
    sign_1st = moon_sign
    sign_2nd = (moon_sign % 12) + 1

    phase = None
    if saturn_sign == sign_12th:
        phase = 'first (rising)'
        strength = 'moderate'
    elif saturn_sign == sign_1st:
        phase = 'second (peak)'
        strength = 'strong'
    elif saturn_sign == sign_2nd:
        phase = 'third (setting)'
        strength = 'moderate'

    if phase is None:
        return results

    results.append(YogaResult(
        yoga_name='Sade Sati',
        yoga_type='transit_dosha',
        planets_involved=['Saturn', 'Moon'],
        houses_involved=[moon.house],
        strength=strength,
        description=(
            f'Saturn is transiting the {phase} phase of Sade Sati relative to '
            f'the natal Moon in {_sign_name(moon_sign)}. This 7.5-year transit '
            f'brings karmic lessons, emotional maturation, and restructuring of '
            f'life foundations. The native may face delays, increased '
            f'responsibilities, and periods of introspection.'
            + (' The peak phase is the most intense, demanding patience and '
               'inner resilience.' if 'peak' in phase else '')
        ),
    ))
    return results


# ---------------------------------------------------------------------------
# 12. Master detection function
# ---------------------------------------------------------------------------

def detect_all_yogas(
    planets: list[PlanetPosition],
    asc_sign: int,
    transit_saturn_sign: int | None = None,
) -> list[YogaResult]:
    """Run all yoga detection functions and return combined results.

    Parameters
    ----------
    planets : list[PlanetPosition]
        List of planetary positions in the chart.
    asc_sign : int
        The sign number (1-12) of the ascendant.
    transit_saturn_sign : int | None
        Optional current transit sign of Saturn (1-12) for Sade Sati
        detection.  If not provided, the natal Saturn position is used.

    Returns
    -------
    list[YogaResult]
        All detected yogas and doshas, sorted by type then strength.
    """
    all_yogas: list[YogaResult] = []

    all_yogas.extend(detect_gaja_kesari(planets, asc_sign))
    all_yogas.extend(detect_raja_yogas(planets, asc_sign))
    all_yogas.extend(detect_dhana_yogas(planets, asc_sign))
    all_yogas.extend(detect_pancha_mahapurusha(planets, asc_sign))
    all_yogas.extend(detect_budhaditya(planets, asc_sign))
    all_yogas.extend(detect_viparita_raja(planets, asc_sign))
    all_yogas.extend(detect_neecha_bhanga(planets, asc_sign))
    all_yogas.extend(detect_kemadruma(planets, asc_sign))
    all_yogas.extend(detect_kaal_sarp(planets, asc_sign))
    all_yogas.extend(detect_mangal_dosha(planets, asc_sign))
    all_yogas.extend(detect_vargottama(planets, asc_sign))
    all_yogas.extend(detect_graha_yuddha(planets, asc_sign))
    all_yogas.extend(detect_sade_sati(planets, asc_sign, transit_saturn_sign))

    # Sort: benefic yogas first, then doshas; within each group strongest first
    _type_order = {'benefic': 0, 'dosha': 1, 'transit_dosha': 2}
    _strength_order = {'strong': 0, 'moderate': 1, 'weak': 2}

    all_yogas.sort(
        key=lambda y: (
            _type_order.get(y.yoga_type, 9),
            _strength_order.get(y.strength, 9),
        )
    )

    return all_yogas
