"""Remedial measures module for Vedic astrology.

Recommends traditional Vedic remedies for weak, afflicted, or
otherwise stressed planets based on shadbala strength, dignity,
combustion status, active dasha lords, and dosha indicators.
"""

from ..models import PlanetPosition, SIGNS, DEBILITATION, SIGN_LORDS


# ---------------------------------------------------------------------------
# Comprehensive remedy data for each planet
# ---------------------------------------------------------------------------

PLANET_REMEDIES = {
    'Sun': {
        'gemstone': 'Ruby (Manikya)',
        'metal': 'Gold',
        'mantra': 'Om Suryaya Namaha',
        'mantra_count': 7000,
        'day': 'Sunday',
        'color': 'Red, orange, copper',
        'charity': 'Donate wheat, jaggery, or copper on Sunday',
        'fasting': 'Fast on Sundays',
        'deity': 'Lord Surya (Sun God)',
        'direction': 'East',
    },
    'Moon': {
        'gemstone': 'Pearl (Moti)',
        'metal': 'Silver',
        'mantra': 'Om Chandraya Namaha',
        'mantra_count': 11000,
        'day': 'Monday',
        'color': 'White, silver, cream',
        'charity': 'Donate rice, white cloth, or silver on Monday',
        'fasting': 'Fast on Mondays',
        'deity': 'Lord Shiva / Goddess Parvati',
        'direction': 'Northwest',
    },
    'Mars': {
        'gemstone': 'Red Coral (Moonga)',
        'metal': 'Copper',
        'mantra': 'Om Mangalaya Namaha',
        'mantra_count': 7000,
        'day': 'Tuesday',
        'color': 'Red, scarlet, coral',
        'charity': 'Donate red lentils, jaggery, or copper on Tuesday',
        'fasting': 'Fast on Tuesdays',
        'deity': 'Lord Hanuman / Lord Kartikeya',
        'direction': 'South',
    },
    'Mercury': {
        'gemstone': 'Emerald (Panna)',
        'metal': 'Bronze',
        'mantra': 'Om Budhaya Namaha',
        'mantra_count': 9000,
        'day': 'Wednesday',
        'color': 'Green',
        'charity': 'Donate green moong dal, green cloth on Wednesday',
        'fasting': 'Fast on Wednesdays',
        'deity': 'Lord Vishnu',
        'direction': 'North',
    },
    'Jupiter': {
        'gemstone': 'Yellow Sapphire (Pukhraj)',
        'metal': 'Gold',
        'mantra': 'Om Gurave Namaha',
        'mantra_count': 19000,
        'day': 'Thursday',
        'color': 'Yellow, gold, saffron',
        'charity': 'Donate turmeric, yellow cloth, bananas on Thursday',
        'fasting': 'Fast on Thursdays',
        'deity': 'Lord Brihaspati / Lord Vishnu',
        'direction': 'Northeast',
    },
    'Venus': {
        'gemstone': 'Diamond (Heera) or White Sapphire',
        'metal': 'Silver',
        'mantra': 'Om Shukraya Namaha',
        'mantra_count': 16000,
        'day': 'Friday',
        'color': 'White, pink, pastel',
        'charity': 'Donate white rice, sugar, white cloth on Friday',
        'fasting': 'Fast on Fridays',
        'deity': 'Goddess Lakshmi',
        'direction': 'Southeast',
    },
    'Saturn': {
        'gemstone': 'Blue Sapphire (Neelam) -- use with caution',
        'metal': 'Iron',
        'mantra': 'Om Shanicharaya Namaha',
        'mantra_count': 23000,
        'day': 'Saturday',
        'color': 'Black, dark blue, indigo',
        'charity': 'Donate black sesame, iron, mustard oil on Saturday',
        'fasting': 'Fast on Saturdays',
        'deity': 'Lord Shani / Lord Hanuman',
        'direction': 'West',
    },
    'Rahu': {
        'gemstone': 'Hessonite Garnet (Gomed)',
        'metal': 'Lead or mixed metals',
        'mantra': 'Om Rahave Namaha',
        'mantra_count': 18000,
        'day': 'Saturday',
        'color': 'Smoky, dark blue',
        'charity': 'Donate black blanket, coconut, or sesame on Saturday',
        'fasting': 'Fast on Saturdays',
        'deity': 'Goddess Durga',
        'direction': 'Southwest',
    },
    'Ketu': {
        'gemstone': "Cat's Eye (Lehsunia)",
        'metal': 'Mixed metals',
        'mantra': 'Om Ketave Namaha',
        'mantra_count': 7000,
        'day': 'Tuesday or Saturday',
        'color': 'Grey, smoky brown',
        'charity': 'Donate blanket, sesame, or bananas on Tuesday',
        'fasting': 'Fast on Tuesdays',
        'deity': 'Lord Ganesha',
        'direction': 'Southwest',
    },
}

# Houses that trigger Mangal Dosha when Mars occupies them
_MANGAL_DOSHA_HOUSES = {1, 2, 4, 7, 8, 12}

# Planets whose gemstones require an explicit caution note
_CAUTION_GEMSTONE_PLANETS = {'Saturn', 'Rahu', 'Ketu'}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_shadbala_map(shadbala: list[dict] | None) -> dict[str, float]:
    """Return a {planet_name: shadbala_ratio} mapping.

    Accepts either a list of dicts (DB row style) or a list of
    ShadbalaResult-like objects (duck-typed via ``.planet`` /
    ``.shadbala_ratio`` attributes).
    """
    result: dict[str, float] = {}
    if not shadbala:
        return result
    for entry in shadbala:
        if isinstance(entry, dict):
            name = entry.get('planet', '')
            ratio = entry.get('shadbala_ratio', 1.0)
        else:
            # Support ShadbalaResult dataclass instances
            name = getattr(entry, 'planet', '')
            ratio = getattr(entry, 'shadbala_ratio', 1.0)
        if name:
            result[name] = float(ratio)
    return result


def _planet_by_name(planets: list[PlanetPosition], name: str) -> PlanetPosition | None:
    """Find a planet by name, or return None."""
    for p in planets:
        if p.planet == name:
            return p
    return None


def _caution_text(planet_name: str) -> str | None:
    """Return a caution string for planets whose gemstones need care."""
    if planet_name == 'Saturn':
        return (
            "Blue Sapphire is extremely powerful and can produce adverse "
            "effects if Saturn is not supportive in the chart. Always consult "
            "a qualified astrologer and trial-wear the stone before committing."
        )
    if planet_name == 'Rahu':
        return (
            "Hessonite should only be worn after careful assessment of Rahu's "
            "role in the chart. Consult a qualified astrologer before wearing."
        )
    if planet_name == 'Ketu':
        return (
            "Cat's Eye is a potent stone that can amplify Ketu's detaching "
            "influence. Consult a qualified astrologer before wearing."
        )
    return None


def _priority_rank(priority: str) -> int:
    """Numeric rank for sorting: lower number = higher priority."""
    return {'high': 0, 'medium': 1, 'low': 2}.get(priority, 3)


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def get_remedies(
    planets: list[PlanetPosition],
    asc_sign: int,
    shadbala: list[dict] | None = None,
    active_dasha_lords: list[str] | None = None,
) -> list[dict]:
    """Identify planets that need strengthening and return remedy recommendations.

    Logic
    -----
    1. Identify weak planets (shadbala_ratio < 0.7 when shadbala provided).
    2. Identify debilitated planets (from ``PlanetPosition.dignity``).
    3. Identify combust planets.
    4. For active dasha lords, always include their remedies (even if strong).
    5. Check for doshas: Mangal Dosha (Mars in houses 1, 2, 4, 7, 8, 12)
       and Sade Sati indicators (Saturn in 12th, 1st, or 2nd from Moon).
    6. Prioritise: active dasha lords > debilitated > combust > weak shadbala.

    Parameters
    ----------
    planets : list[PlanetPosition]
        All nine Vedic planet positions for the chart.
    asc_sign : int
        Ascendant zodiac sign (1-12).
    shadbala : list[dict] | None
        Shadbala results -- either DB row dicts or ShadbalaResult instances.
    active_dasha_lords : list[str] | None
        Planet names currently running as maha/antar dasha lords.

    Returns
    -------
    list[dict]
        Sorted list of remedy dicts, highest priority first.
    """
    shadbala_map = _build_shadbala_map(shadbala)
    dasha_lords = set(active_dasha_lords) if active_dasha_lords else set()

    # Collect remedy candidates as {planet_name: (reason, priority)}
    # If a planet qualifies for multiple reasons, keep the highest priority.
    candidates: dict[str, tuple[str, str]] = {}

    def _register(name: str, reason: str, priority: str) -> None:
        """Register a candidate, keeping the higher-priority entry."""
        if name not in candidates or _priority_rank(priority) < _priority_rank(candidates[name][1]):
            candidates[name] = (reason, priority)

    # 1. Active dasha lords -- always included at high priority
    for lord in dasha_lords:
        p = _planet_by_name(planets, lord)
        if p is not None:
            _register(lord, 'Active dasha lord', 'high')

    # 2. Debilitated planets
    for p in planets:
        if p.dignity and p.dignity.lower() == 'debilitated':
            sign_name = SIGNS[p.sign] if 1 <= p.sign <= 12 else str(p.sign)
            _register(p.planet, f'Debilitated in {sign_name}', 'high')

    # 3. Combust planets
    for p in planets:
        if p.is_combust:
            _register(p.planet, 'Combust (too close to Sun)', 'medium')

    # 4. Weak shadbala
    for name, ratio in shadbala_map.items():
        if ratio < 0.7:
            _register(name, f'Weak shadbala ({ratio:.2f})', 'medium')

    # 5. Dosha checks
    # 5a. Mangal Dosha
    mars = _planet_by_name(planets, 'Mars')
    if mars and mars.house in _MANGAL_DOSHA_HOUSES:
        _register(
            'Mars',
            f'Mangal Dosha (Mars in {_ordinal(mars.house)} house)',
            'medium',
        )

    # 5b. Sade Sati indicator
    moon = _planet_by_name(planets, 'Moon')
    saturn = _planet_by_name(planets, 'Saturn')
    if moon and saturn:
        diff = ((saturn.sign - moon.sign) % 12)
        if diff in (0, 1, 11):
            phase_map = {11: 'rising phase', 0: 'peak phase', 1: 'setting phase'}
            phase = phase_map[diff]
            _register(
                'Saturn',
                f'Sade Sati indicator ({phase}, natal Saturn {_ordinal(saturn.house)} house)',
                'medium',
            )

    # Build final remedy list
    remedies: list[dict] = []
    for planet_name, (reason, priority) in candidates.items():
        data = PLANET_REMEDIES.get(planet_name)
        if data is None:
            continue

        remedy: dict = {
            'planet': planet_name,
            'reason': reason,
            'priority': priority,
            'gemstone': data['gemstone'],
            'mantra': data['mantra'],
            'mantra_count': data['mantra_count'],
            'day': data['day'],
            'charity': data['charity'],
            'fasting': data['fasting'],
            'color': data['color'],
            'deity': data['deity'],
            'caution': _caution_text(planet_name),
        }
        remedies.append(remedy)

    # Sort by priority rank, then alphabetically by planet name
    remedies.sort(key=lambda r: (_priority_rank(r['priority']), r['planet']))

    return remedies


# ---------------------------------------------------------------------------
# Format function
# ---------------------------------------------------------------------------

def format_remedies_text(remedies: list[dict]) -> str:
    """Format a list of remedy dicts into a readable multi-section string.

    Parameters
    ----------
    remedies : list[dict]
        Output from ``get_remedies()``.

    Returns
    -------
    str
        Human-readable, multi-section remedies text.
    """
    if not remedies:
        return (
            "=== REMEDIAL MEASURES ===\n\n"
            "No planets were identified as requiring specific remedial "
            "measures at this time. The chart's planetary strengths appear "
            "adequate for the current period."
        )

    lines: list[str] = []
    lines.append("=== REMEDIAL MEASURES ===")
    lines.append("")
    lines.append(
        "The following remedies are recommended based on the chart analysis. "
        "Remedies work best when adopted with sincerity and consistency. "
        "Gemstone recommendations should always be confirmed with a qualified "
        "Vedic astrologer before wearing."
    )
    lines.append("")

    for i, remedy in enumerate(remedies, 1):
        priority_label = remedy['priority'].upper()
        lines.append(f"--- {i}. {remedy['planet']} [{priority_label} PRIORITY] ---")
        lines.append(f"  Reason     : {remedy['reason']}")
        lines.append(f"  Gemstone   : {remedy['gemstone']}")
        lines.append(f"  Mantra     : {remedy['mantra']}")
        lines.append(f"  Repetitions: {remedy['mantra_count']:,} times")
        lines.append(f"  Best day   : {remedy['day']}")
        lines.append(f"  Color      : {remedy['color']}")
        lines.append(f"  Deity      : {remedy['deity']}")
        lines.append(f"  Charity    : {remedy['charity']}")
        lines.append(f"  Fasting    : {remedy['fasting']}")
        if remedy.get('caution'):
            lines.append(f"  CAUTION    : {remedy['caution']}")
        lines.append("")

    lines.append(
        "Note: These are traditional Vedic remedies offered as spiritual "
        "guidance. They are not a substitute for professional medical, "
        "legal, or financial advice. Gemstones in particular should be "
        "trialled carefully under the guidance of a knowledgeable astrologer."
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Small utility
# ---------------------------------------------------------------------------

def _ordinal(n: int) -> str:
    """Return the English ordinal for an integer (1st, 2nd, 3rd ...)."""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"
