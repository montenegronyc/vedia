"""Muhurta (auspicious timing) evaluation module.

Evaluates the auspiciousness of a specific date for a person based on their
natal chart, considering:
  - Gochara (Moon's transit from natal Moon)
  - Vara (day-of-week planetary ruler alignment)
  - Nakshatra quality for the event type
  - Transit-natal interactions (aspects from benefics/malefics)
  - Sarvashtakavarga score of Moon's transit sign

Reference: classical muhurta principles from Brihat Samhita and
Muhurta Chintamani.
"""

from datetime import datetime

from ..models import PlanetPosition, NAKSHATRA_NAMES


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Day-of-week planetary rulers (Python weekday: Monday=0 ... Sunday=6)
VARA_LORDS: dict[int, str] = {
    0: 'Moon',      # Monday
    1: 'Mars',      # Tuesday
    2: 'Mercury',   # Wednesday
    3: 'Jupiter',   # Thursday
    4: 'Venus',     # Friday
    5: 'Saturn',    # Saturday
    6: 'Sun',       # Sunday
}

# Gochara: Moon's transit house from natal Moon
_FAVORABLE_GOCHARA_HOUSES = frozenset({1, 3, 6, 7, 10, 11})
_UNFAVORABLE_GOCHARA_HOUSES = frozenset({2, 4, 5, 8, 9, 12})

# Event type -> planets that favor this kind of activity
EVENT_FAVORABLE_PLANETS: dict[str, list[str]] = {
    'court': ['Jupiter', 'Sun', 'Mars'],
    'business': ['Mercury', 'Jupiter', 'Venus'],
    'travel': ['Moon', 'Mercury', 'Jupiter'],
    'ceremony': ['Jupiter', 'Venus', 'Moon'],
    'medical': ['Sun', 'Mars', 'Jupiter'],
    'general': ['Jupiter', 'Venus', 'Mercury'],
}

# Nakshatra groupings by quality (1-indexed nakshatra numbers)
_FIXED_NAKSHATRAS = frozenset({
    4,   # Rohini
    12,  # Uttara Phalguni
    21,  # Uttara Ashadha
    26,  # Uttara Bhadrapada
})

_MOVABLE_NAKSHATRAS = frozenset({
    1,   # Ashwini
    8,   # Pushya
    13,  # Hasta
    22,  # Shravana
    7,   # Punarvasu
    15,  # Swati
    17,  # Anuradha
    5,   # Mrigashira
    27,  # Revati
})

_SHARP_NAKSHATRAS = frozenset({
    6,   # Ardra
    9,   # Ashlesha
    18,  # Jyeshtha
    19,  # Mula
})

_SOFT_NAKSHATRAS = frozenset({
    5,   # Mrigashira
    14,  # Chitra
    17,  # Anuradha
    27,  # Revati
})

# Which nakshatra groups are best for which event types
_NAKSHATRA_EVENT_AFFINITY: dict[str, list[frozenset[int]]] = {
    'court': [_SHARP_NAKSHATRAS, _MOVABLE_NAKSHATRAS],
    'business': [_MOVABLE_NAKSHATRAS, _FIXED_NAKSHATRAS],
    'travel': [_MOVABLE_NAKSHATRAS],
    'ceremony': [_FIXED_NAKSHATRAS, _SOFT_NAKSHATRAS],
    'medical': [_SHARP_NAKSHATRAS, _MOVABLE_NAKSHATRAS],
    'general': [_MOVABLE_NAKSHATRAS, _FIXED_NAKSHATRAS, _SOFT_NAKSHATRAS],
}

# Benefic and malefic planets for transit scoring
_BENEFICS = frozenset({'Jupiter', 'Venus', 'Mercury', 'Moon'})
_MALEFICS = frozenset({'Saturn', 'Rahu', 'Ketu', 'Mars'})

# Vedic special aspects: planet -> list of additional houses aspected (beyond 7th)
_SPECIAL_ASPECTS: dict[str, list[int]] = {
    'Mars': [4, 8],
    'Jupiter': [5, 9],
    'Saturn': [3, 10],
}

# Auspiciousness labels mapped to score ranges
_AUSPICIOUSNESS_LABELS: list[tuple[float, str]] = [
    (80.0, 'Highly Auspicious'),
    (60.0, 'Auspicious'),
    (40.0, 'Moderate'),
    (25.0, 'Challenging'),
    (0.0, 'Inauspicious'),
]

# Scoring weights (must sum to 1.0)
_WEIGHT_GOCHARA = 0.25
_WEIGHT_VARA = 0.15
_WEIGHT_NAKSHATRA = 0.20
_WEIGHT_TRANSIT = 0.25
_WEIGHT_ASHTAKAVARGA = 0.15


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _house_from(reference_sign: int, target_sign: int) -> int:
    """Compute 1-based house number of *target_sign* from *reference_sign*."""
    return ((target_sign - reference_sign) % 12) + 1


def _get_planet(planets: list[PlanetPosition], name: str) -> PlanetPosition | None:
    """Find a planet by name in a positions list."""
    for p in planets:
        if p.planet == name:
            return p
    return None


def _aspected_signs(planet: PlanetPosition) -> list[int]:
    """Return list of signs (1-12) that a planet aspects from its current sign."""
    offsets = [7]
    if planet.planet in _SPECIAL_ASPECTS:
        offsets.extend(_SPECIAL_ASPECTS[planet.planet])
    return [((planet.sign - 1 + offset) % 12) + 1 for offset in offsets]


def _angular_distance(lon1: float, lon2: float) -> float:
    """Shortest angular distance between two longitudes on a 360-degree circle."""
    diff = abs((lon1 % 360.0) - (lon2 % 360.0))
    return min(diff, 360.0 - diff)


def _auspiciousness_label(score: float) -> str:
    """Map a 0-100 total score to a descriptive label."""
    for threshold, label in _AUSPICIOUSNESS_LABELS:
        if score >= threshold:
            return label
    return 'Inauspicious'


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def _score_gochara(
    transit_moon_sign: int,
    natal_moon_sign: int,
) -> tuple[float, int, bool, list[str]]:
    """Score based on Moon's transit house from natal Moon.

    Returns (score_0_10, house_from_moon, favorable, factors).
    """
    house = _house_from(natal_moon_sign, transit_moon_sign)
    favorable = house in _FAVORABLE_GOCHARA_HOUSES
    factors = []

    if favorable:
        # Best houses get top scores
        if house in (1, 3, 6, 11):
            score = 9.0
            factors.append(f"Moon transits H{house} from natal Moon -- strongly favorable gochara")
        else:
            score = 7.5
            factors.append(f"Moon transits H{house} from natal Moon -- favorable gochara")
    else:
        if house in (8, 12):
            score = 2.0
            factors.append(f"Moon transits H{house} from natal Moon -- difficult gochara house")
        else:
            score = 3.5
            factors.append(f"Moon transits H{house} from natal Moon -- unfavorable gochara")

    return score, house, favorable, factors


def _score_vara(
    day_lord: str,
    event_type: str,
    dasha_lord: str | None,
) -> tuple[float, list[str]]:
    """Score based on the day's ruling planet and its alignment with the event.

    Returns (score_0_10, factors).
    """
    favorable_planets = EVENT_FAVORABLE_PLANETS.get(event_type, EVENT_FAVORABLE_PLANETS['general'])
    factors = []
    score = 5.0  # neutral baseline

    if day_lord in favorable_planets:
        idx = favorable_planets.index(day_lord)
        # First in list is best match
        if idx == 0:
            score = 9.0
            factors.append(f"Vara lord {day_lord} is the ideal day for {event_type} events")
        else:
            score = 7.5
            factors.append(f"Vara lord {day_lord} is favorable for {event_type} events")
    else:
        # Check for negative pairings
        if event_type == 'court' and day_lord == 'Saturn':
            score = 3.0
            factors.append(f"Saturn day may bring delays in court matters")
        elif event_type == 'travel' and day_lord == 'Saturn':
            score = 3.0
            factors.append(f"Saturn day is not ideal for travel")
        elif event_type == 'ceremony' and day_lord in ('Saturn', 'Mars'):
            score = 3.0
            factors.append(f"{day_lord} day is inauspicious for ceremonies")
        else:
            factors.append(f"Vara lord {day_lord} is neutral for {event_type} events")

    # Bonus if day lord matches active dasha lord
    if dasha_lord and day_lord == dasha_lord:
        score = min(10.0, score + 1.5)
        factors.append(f"Vara lord matches current dasha lord ({dasha_lord}) -- amplified day energy")

    return score, factors


def _score_nakshatra(
    transit_moon_nakshatra: int,
    event_type: str,
) -> tuple[float, list[str]]:
    """Score the transit Moon's nakshatra for the event type.

    Returns (score_0_10, factors).
    """
    nak_name = NAKSHATRA_NAMES[transit_moon_nakshatra - 1] if 1 <= transit_moon_nakshatra <= 27 else '?'
    affinity_groups = _NAKSHATRA_EVENT_AFFINITY.get(event_type, _NAKSHATRA_EVENT_AFFINITY['general'])
    factors = []

    # Check primary affinity (first group in list is best match)
    for rank, group in enumerate(affinity_groups):
        if transit_moon_nakshatra in group:
            if rank == 0:
                score = 9.0
                factors.append(f"Nakshatra {nak_name} is highly suitable for {event_type}")
            else:
                score = 7.0
                factors.append(f"Nakshatra {nak_name} is suitable for {event_type}")
            return score, factors

    # Not in any favorable group -- check if it is in an adverse group
    if event_type == 'ceremony' and transit_moon_nakshatra in _SHARP_NAKSHATRAS:
        factors.append(f"Nakshatra {nak_name} (sharp) is inauspicious for ceremonies")
        return 2.5, factors

    if event_type == 'court' and transit_moon_nakshatra in _SOFT_NAKSHATRAS:
        factors.append(f"Nakshatra {nak_name} (soft) is less effective for court proceedings")
        return 4.0, factors

    # Neutral
    factors.append(f"Nakshatra {nak_name} is neutral for {event_type}")
    return 5.0, factors


def _score_transits(
    natal_planets: list[PlanetPosition],
    transit_planets: list[PlanetPosition],
) -> tuple[float, list[str]]:
    """Score transit-natal interactions.

    Jupiter aspects to natal planets are beneficial; Saturn/Rahu aspects
    are problematic. Also checks for tight conjunctions.

    Returns (score_0_10, factors).
    """
    factors = []
    benefic_hits = 0
    malefic_hits = 0

    for tp in transit_planets:
        if tp.planet in ('Ketu',):
            # Ketu aspects are secondary; skip for simplicity
            continue

        aspected = _aspected_signs(tp)

        for np in natal_planets:
            # Check aspects
            if np.sign in aspected:
                if tp.planet in ('Jupiter', 'Venus'):
                    benefic_hits += 1
                    if tp.planet == 'Jupiter':
                        factors.append(
                            f"Transit Jupiter aspects natal {np.planet} -- protective and expansive"
                        )
                elif tp.planet in ('Saturn', 'Rahu'):
                    malefic_hits += 1
                    if tp.planet == 'Saturn':
                        factors.append(
                            f"Transit Saturn aspects natal {np.planet} -- pressure and restriction"
                        )
                    elif tp.planet == 'Rahu':
                        factors.append(
                            f"Transit Rahu aspects natal {np.planet} -- confusion or obsession"
                        )

            # Check tight conjunctions (within 5 degrees)
            if tp.sign == np.sign and _angular_distance(tp.longitude, np.longitude) <= 5.0:
                if tp.planet in _BENEFICS and tp.planet not in ('Moon',):
                    benefic_hits += 1
                    factors.append(
                        f"Transit {tp.planet} conjunct natal {np.planet} ({_angular_distance(tp.longitude, np.longitude):.1f} deg) -- beneficial"
                    )
                elif tp.planet in _MALEFICS and tp.planet not in ('Mars',):
                    malefic_hits += 1
                    factors.append(
                        f"Transit {tp.planet} conjunct natal {np.planet} ({_angular_distance(tp.longitude, np.longitude):.1f} deg) -- challenging"
                    )

    # Cap factor lists to avoid noise
    if len(factors) > 6:
        factors = factors[:6]
        factors.append("(additional transit interactions omitted)")

    # Convert hits to a score
    net = benefic_hits - malefic_hits
    # Baseline 5.0, +0.7 per benefic net, clamped 0-10
    score = max(0.0, min(10.0, 5.0 + net * 0.7))

    return score, factors


def _score_ashtakavarga(
    transit_moon_sign: int,
    sarvashtakavarga: dict | None,
) -> tuple[float, list[str]]:
    """Score based on SAV value for the Moon's transit sign.

    Returns (score_0_10, factors).
    """
    if sarvashtakavarga is None:
        return 5.0, []  # Neutral if no data

    sav_value = sarvashtakavarga.get(transit_moon_sign, 28)  # default to average
    factors = []

    # SAV ranges: 0-56, average ~28 per sign
    if sav_value >= 34:
        score = 9.0
        factors.append(f"SAV score {sav_value} in Moon's transit sign -- strongly supportive")
    elif sav_value >= 30:
        score = 7.5
        factors.append(f"SAV score {sav_value} in Moon's transit sign -- above average")
    elif sav_value >= 25:
        score = 5.0
        factors.append(f"SAV score {sav_value} in Moon's transit sign -- average")
    elif sav_value >= 20:
        score = 3.5
        factors.append(f"SAV score {sav_value} in Moon's transit sign -- below average")
    else:
        score = 2.0
        factors.append(f"SAV score {sav_value} in Moon's transit sign -- weak support")

    return score, factors


# ---------------------------------------------------------------------------
# Recommendation engine
# ---------------------------------------------------------------------------

def _generate_recommendations(
    total_score: float,
    auspiciousness: str,
    event_type: str,
    vara_lord: str,
    gochara_favorable: bool,
    transit_moon_nakshatra: int,
    factors: list[str],
) -> list[str]:
    """Generate practical recommendations based on the evaluation."""
    recs = []
    nak_name = NAKSHATRA_NAMES[transit_moon_nakshatra - 1] if 1 <= transit_moon_nakshatra <= 27 else '?'

    if auspiciousness == 'Highly Auspicious':
        recs.append(f"Excellent date for {event_type} activities -- proceed with confidence")
    elif auspiciousness == 'Auspicious':
        recs.append(f"Good date for {event_type} -- favorable conditions overall")
    elif auspiciousness == 'Moderate':
        recs.append(f"Acceptable date for {event_type} but consider alternatives if possible")
    elif auspiciousness == 'Challenging':
        recs.append(f"This date has significant challenges for {event_type} -- consider postponing")
    else:
        recs.append(f"Strongly recommend choosing a different date for {event_type}")

    if not gochara_favorable:
        recs.append("Moon's transit position is unfavorable -- if possible, wait for Moon to move to a better house")

    favorable_planets = EVENT_FAVORABLE_PLANETS.get(event_type, EVENT_FAVORABLE_PLANETS['general'])
    if vara_lord not in favorable_planets:
        # Suggest better days
        best_days = []
        for weekday, lord in VARA_LORDS.items():
            if lord == favorable_planets[0]:
                day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                best_days.append(day_names[weekday])
        if best_days:
            recs.append(f"For {event_type}, {', '.join(best_days)} ({favorable_planets[0]} day) would be ideal")

    # Check for specific nakshatra advice
    affinity_groups = _NAKSHATRA_EVENT_AFFINITY.get(event_type, _NAKSHATRA_EVENT_AFFINITY['general'])
    in_affinity = any(transit_moon_nakshatra in g for g in affinity_groups)
    if not in_affinity:
        if event_type == 'ceremony':
            recs.append("Look for dates when Moon transits Rohini, Uttara Phalguni, or Uttara Ashadha for ceremonies")
        elif event_type == 'court':
            recs.append("Look for dates when Moon transits Ardra, Jyeshtha, or Mula for court proceedings")
        elif event_type == 'travel':
            recs.append("Look for dates when Moon transits Ashwini, Pushya, or Hasta for travel")

    return recs


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def evaluate_muhurta(
    natal_planets: list[PlanetPosition],
    natal_asc_sign: int,
    natal_moon_sign: int,
    transit_planets: list[PlanetPosition],
    target_date: datetime,
    event_type: str = 'general',
    dasha_lord: str | None = None,
    shadbala: list[dict] | None = None,
    sarvashtakavarga: dict | None = None,
) -> dict:
    """Evaluate the auspiciousness of a specific date for a person.

    Args:
        natal_planets: List of PlanetPosition for the natal chart.
        natal_asc_sign: Sign number (1-12) of the natal ascendant.
        natal_moon_sign: Sign number (1-12) of the natal Moon.
        transit_planets: List of PlanetPosition for the target date.
        target_date: The date being evaluated.
        event_type: Type of event ('court', 'business', 'travel',
            'ceremony', 'medical', 'general').
        dasha_lord: Currently active maha dasha lord (planet name), if known.
        shadbala: Shadbala results (list of dicts), if available.
        sarvashtakavarga: SAV dict mapping sign (1-12) to score, if available.

    Returns:
        Dict with scoring breakdown, auspiciousness label, factors, and
        recommendations.
    """
    all_factors: list[str] = []

    # --- Transit Moon info ---
    transit_moon = _get_planet(transit_planets, 'Moon')
    if transit_moon is None:
        raise ValueError("Transit Moon not found in transit_planets")

    transit_moon_sign = transit_moon.sign
    transit_moon_nak = transit_moon.nakshatra
    transit_moon_nak_name = (
        NAKSHATRA_NAMES[transit_moon_nak - 1] if 1 <= transit_moon_nak <= 27 else '?'
    )

    # --- Vara (day lord) ---
    weekday = target_date.weekday()  # Monday=0 ... Sunday=6
    vara_lord = VARA_LORDS[weekday]
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_of_week = day_names[weekday]

    # --- 1. Gochara score ---
    gochara_score, house_from_moon, gochara_favorable, gochara_factors = _score_gochara(
        transit_moon_sign, natal_moon_sign,
    )
    all_factors.extend(gochara_factors)

    # --- 2. Vara score ---
    vara_score, vara_factors = _score_vara(vara_lord, event_type, dasha_lord)
    all_factors.extend(vara_factors)

    # --- 3. Nakshatra score ---
    nakshatra_score, nak_factors = _score_nakshatra(transit_moon_nak, event_type)
    all_factors.extend(nak_factors)

    # --- 4. Transit interactions score ---
    transit_score, transit_factors = _score_transits(natal_planets, transit_planets)
    all_factors.extend(transit_factors)

    # --- 5. Ashtakavarga score ---
    ashtakavarga_score, sav_factors = _score_ashtakavarga(transit_moon_sign, sarvashtakavarga)
    all_factors.extend(sav_factors)

    # --- Total weighted score (0-100) ---
    total_score = (
        gochara_score * _WEIGHT_GOCHARA
        + vara_score * _WEIGHT_VARA
        + nakshatra_score * _WEIGHT_NAKSHATRA
        + transit_score * _WEIGHT_TRANSIT
        + ashtakavarga_score * _WEIGHT_ASHTAKAVARGA
    ) * 10.0  # scale from 0-10 weighted sum to 0-100

    total_score = round(max(0.0, min(100.0, total_score)), 1)

    auspiciousness = _auspiciousness_label(total_score)

    # --- Recommendations ---
    recommendations = _generate_recommendations(
        total_score, auspiciousness, event_type, vara_lord,
        gochara_favorable, transit_moon_nak, all_factors,
    )

    # --- Moon transit info ---
    moon_transit = {
        'sign': transit_moon_sign,
        'nakshatra': transit_moon_nak_name,
        'nakshatra_num': transit_moon_nak,
        'house_from_natal_moon': house_from_moon,
        'favorable': gochara_favorable,
    }

    return {
        'date': target_date.strftime('%Y-%m-%d'),
        'day_of_week': day_of_week,
        'vara_lord': vara_lord,
        'moon_transit': moon_transit,
        'gochara_score': round(gochara_score, 1),
        'vara_score': round(vara_score, 1),
        'nakshatra_score': round(nakshatra_score, 1),
        'transit_score': round(transit_score, 1),
        'ashtakavarga_score': round(ashtakavarga_score, 1),
        'total_score': total_score,
        'auspiciousness': auspiciousness,
        'factors': all_factors,
        'recommendations': recommendations,
    }


def compare_dates(
    natal_planets: list[PlanetPosition],
    natal_asc_sign: int,
    natal_moon_sign: int,
    transit_data: list[tuple[datetime, list[PlanetPosition]]],
    event_type: str = 'general',
    **kwargs,
) -> list[dict]:
    """Evaluate multiple dates and return results sorted best-first.

    Args:
        natal_planets: Natal chart planet positions.
        natal_asc_sign: Natal ascendant sign (1-12).
        natal_moon_sign: Natal Moon sign (1-12).
        transit_data: List of (date, transit_planets) pairs to evaluate.
        event_type: Event type for scoring context.
        **kwargs: Additional keyword arguments passed to evaluate_muhurta
            (dasha_lord, shadbala, sarvashtakavarga).

    Returns:
        List of evaluation dicts sorted by total_score descending (best first).
    """
    results = []
    for target_date, transit_planets in transit_data:
        result = evaluate_muhurta(
            natal_planets=natal_planets,
            natal_asc_sign=natal_asc_sign,
            natal_moon_sign=natal_moon_sign,
            transit_planets=transit_planets,
            target_date=target_date,
            event_type=event_type,
            **kwargs,
        )
        results.append(result)

    results.sort(key=lambda r: r['total_score'], reverse=True)
    return results
