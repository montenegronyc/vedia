"""Main synthesis engine for combining chart factors into readings.

This module is the heart of the Vedia interpretation engine. It takes
calculated chart data -- planet positions, dashas, yogas, and transits --
and weaves them into coherent, human-readable astrological consultations.
"""
from datetime import datetime
from typing import Optional

from ..models import (
    SIGNS, NAKSHATRA_NAMES, SIGN_LORDS, DASHA_YEARS,
    EXALTATION, DEBILITATION, OWN_SIGNS,
    PlanetPosition, ChartData, DashaPeriod, YogaResult, ShadbalaResult,
)
from .planets import (
    PLANET_SIGNIFICATIONS,
    interpret_planet_in_sign,
    interpret_planet_in_house,
)
from .houses import (
    HOUSE_SIGNIFICATIONS,
    interpret_house_lord_placement,
)


# ---------------------------------------------------------------------------
# Small formatting helpers
# ---------------------------------------------------------------------------

def _format_degree(longitude: float) -> str:
    """Format a longitude as degree-minute notation.

    Example: 15.383 -> "15°22'"
    """
    degrees = int(longitude)
    minutes = int((longitude - degrees) * 60)
    return f"{degrees}°{minutes:02d}'"


def _format_sign_degree(sign: int, degree: float) -> str:
    """Format as '15°22' Taurus'."""
    return f"{_format_degree(degree)} {SIGNS[sign]}"


def _ordinal(n: int) -> str:
    """Return the English ordinal for an integer (1st, 2nd, 3rd ...)."""
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


# ---------------------------------------------------------------------------
# Internal look-up helpers
# ---------------------------------------------------------------------------

def _get_house_sign(asc_sign: int, house: int) -> int:
    """Return the zodiac sign number (1-12) on the cusp of *house*."""
    return ((asc_sign - 1 + house - 1) % 12) + 1


def _get_house_lord(asc_sign: int, house: int) -> str:
    """Return the ruling planet of the given house."""
    return SIGN_LORDS[_get_house_sign(asc_sign, house)]


def _planets_in_house(planets: list[PlanetPosition], house: int) -> list[PlanetPosition]:
    """Filter the planet list to those occupying *house*."""
    return [p for p in planets if p.house == house]


def _find_planet(planets: list[PlanetPosition], name: str) -> Optional[PlanetPosition]:
    """Find a single planet by name, or return None."""
    for p in planets:
        if p.planet == name:
            return p
    return None


def _planet_lord_of(planet: str) -> list[int]:
    """Return the sign numbers this planet rules."""
    return [s for s, lord in SIGN_LORDS.items() if lord == planet]


def _dignity_phrase(p: PlanetPosition) -> str:
    """Return a short human-readable dignity phrase for a planet."""
    if not p.dignity:
        return ""
    phrases = {
        'exalted': "exalted and operating at peak strength",
        'moolatrikona': "in moolatrikona, functioning powerfully",
        'own': "in its own sign, comfortable and authoritative",
        'friendly': "in a friendly sign, well-supported",
        'neutral': "in a neutral sign",
        'enemy': "in an enemy sign, facing friction",
        'debilitated': "debilitated and needing support from other factors",
    }
    return phrases.get(p.dignity.lower(), "")


def _retro_phrase(p: PlanetPosition) -> str:
    """Return a brief retrograde note, or empty string."""
    if not p.is_retrograde:
        return ""
    return (
        f"{p.planet} is retrograde, suggesting an inward turning of its energy "
        "and the revisiting of past themes connected to its significations."
    )


def _combust_phrase(p: PlanetPosition) -> str:
    """Return a brief combustion note, or empty string."""
    if not p.is_combust:
        return ""
    return (
        f"{p.planet} is combust (too close to the Sun), which can dim the "
        "expression of its natural qualities and require conscious effort to "
        "activate its significations."
    )


# ---------------------------------------------------------------------------
# Nakshatra interpretation blurbs
# ---------------------------------------------------------------------------

_NAKSHATRA_DESCRIPTIONS: dict[int, str] = {
    1: (
        "Ashwini nakshatra, ruled by the Ashwini Kumaras (the celestial healers), "
        "endows a swift, healing, and pioneering temperament. The mind moves quickly, "
        "with an instinct for fresh starts and the courage to act on inspiration. "
        "There is a natural gift for medicine, speed, and rejuvenation."
    ),
    2: (
        "Bharani nakshatra, ruled by Yama (the lord of dharma and death), gives a "
        "transformative, intense, and creative emotional nature. The mind processes "
        "life through cycles of creation and dissolution, bearing heavy "
        "responsibilities with quiet strength. Sensuality and artistic depth are pronounced."
    ),
    3: (
        "Krittika nakshatra, ruled by Agni (the god of fire), bestows a sharp, "
        "purifying intellect and a forthright personality. The mind cuts through "
        "illusion with clarity and determination, sometimes at the cost of diplomacy. "
        "Nourishment, cooking, and protective instincts are strong."
    ),
    4: (
        "Rohini nakshatra, ruled by Brahma (the creator), gives a fertile, sensual, "
        "and aesthetically refined emotional nature. The mind is drawn to beauty, "
        "growth, and material abundance, with strong powers of attraction. "
        "Creativity, agriculture, and romantic expression flourish here."
    ),
    5: (
        "Mrigashira nakshatra, ruled by Soma (the Moon god), produces a searching, "
        "curious, and gentle temperament that is always exploring new horizons. "
        "The mind seeks knowledge through travel, conversation, and subtle perception. "
        "There is grace, charm, and a perpetual sense of quest."
    ),
    6: (
        "Ardra nakshatra, ruled by Rudra (the storm god), imparts an emotionally "
        "intense and intellectually penetrating nature. The mind processes life "
        "through storms of change, destruction, and renewal. Research ability, "
        "compassion born of suffering, and technological aptitude are characteristic."
    ),
    7: (
        "Punarvasu nakshatra, ruled by Aditi (the mother of gods), gives a "
        "resilient, optimistic, and nurturing emotional nature. The mind bounces "
        "back from setbacks with renewed faith and generosity. Teaching, counseling, "
        "and the ability to find home wherever one goes define this nakshatra."
    ),
    8: (
        "Pushya nakshatra, ruled by Brihaspati (Jupiter), is considered among the "
        "most auspicious, bestowing a nourishing, wise, and dharmic temperament. "
        "The mind is inclined toward service, spiritual practice, and the patient "
        "cultivation of what is good. Generosity and protective instincts are strong."
    ),
    9: (
        "Ashlesha nakshatra, ruled by the Nagas (serpent deities), imparts a "
        "hypnotic, psychologically astute, and deeply intuitive nature. The mind "
        "is perceptive about hidden motivations and excels in strategy. There is "
        "a capacity for healing through kundalini or tantric practices."
    ),
    10: (
        "Magha nakshatra, ruled by the Pitris (ancestral fathers), confers a regal, "
        "traditional, and authoritative emotional nature rooted in lineage and "
        "ancestral merit. The mind is drawn to tradition, ceremony, and positions "
        "of honor. Leadership comes naturally, carrying the weight of the past."
    ),
    11: (
        "Purva Phalguni nakshatra, ruled by Bhaga (the god of delight), gives a "
        "creative, romantic, and pleasure-seeking emotional nature. The mind is "
        "drawn to the arts, romance, and the enjoyment of life's pleasures. "
        "Generosity, warmth, and a talent for celebration are characteristic."
    ),
    12: (
        "Uttara Phalguni nakshatra, ruled by Aryaman (the god of patronage), "
        "imparts a steady, helpful, and socially responsible temperament. The mind "
        "finds fulfillment through service, friendship, and the establishment of "
        "lasting alliances. Leadership combined with kindness defines this nakshatra."
    ),
    13: (
        "Hasta nakshatra, ruled by Savitar (the vivifying sun god), gives a "
        "skillful, clever, and dexterous emotional nature. The mind excels at "
        "craftsmanship, healing through the hands, and adaptable problem-solving. "
        "There is a lightness and humor that masks considerable depth."
    ),
    14: (
        "Chitra nakshatra, ruled by Tvashtar (the celestial architect), bestows a "
        "creative, visionary, and aesthetically driven temperament. The mind is "
        "drawn to design, architecture, and the creation of beautiful, lasting "
        "things. Charisma and a magnetic personality are pronounced."
    ),
    15: (
        "Swati nakshatra, ruled by Vayu (the wind god), produces an independent, "
        "flexible, and diplomatically skilled emotional nature. The mind values "
        "freedom and self-determination, adapting to circumstances like a blade "
        "of grass in the wind. Business acumen and social refinement are notable."
    ),
    16: (
        "Vishakha nakshatra, ruled by Indra and Agni, gives a determined, "
        "goal-oriented, and intensely focused temperament. The mind pursues its "
        "objectives with single-pointed concentration and competitive fire. "
        "Transformation through ambition and the capacity for sustained effort define this star."
    ),
    17: (
        "Anuradha nakshatra, ruled by Mitra (the god of friendship), confers a "
        "devoted, disciplined, and socially connective emotional nature. The mind "
        "excels at building alliances, maintaining friendships, and succeeding in "
        "foreign environments. Loyalty and organizational skill are hallmarks."
    ),
    18: (
        "Jyeshtha nakshatra, ruled by Indra (the king of gods), imparts a "
        "protective, senior, and authoritative temperament with a keen sense of "
        "responsibility. The mind is drawn to leadership, though lessons about "
        "the responsible use of power are central. Resourcefulness under pressure is strong."
    ),
    19: (
        "Mula nakshatra, ruled by Nirriti (the goddess of dissolution), gives a "
        "probing, philosophical, and sometimes destructive-then-rebuilding emotional "
        "nature. The mind digs to the root of things, seeking truth beneath surface "
        "appearances. Spiritual transformation and research ability are pronounced."
    ),
    20: (
        "Purva Ashadha nakshatra, ruled by Apas (the water deity), bestows an "
        "invincible, purifying, and eloquent emotional nature. The mind is "
        "enthusiastic, philosophical, and naturally persuasive, with the ability "
        "to rally others to a cause. Confidence and regenerative ability are strong."
    ),
    21: (
        "Uttara Ashadha nakshatra, ruled by the Vishvadevas (universal gods), "
        "gives a principled, patient, and ultimately victorious temperament. "
        "The mind achieves its aims through steady, dharmic effort rather than "
        "impulsive action. Leadership that endures and universal values define this star."
    ),
    22: (
        "Shravana nakshatra, ruled by Vishnu (the preserver), confers a "
        "learning-oriented, perceptive, and connective emotional nature. The mind "
        "absorbs knowledge through listening and connects disparate ideas into "
        "coherent understanding. Teaching, counseling, and media work are favored."
    ),
    23: (
        "Dhanishta nakshatra, ruled by the Vasus (the elemental gods), gives a "
        "rhythmic, wealthy, and socially prominent temperament. The mind is drawn "
        "to music, group leadership, and the accumulation of resources. Ambition "
        "is supported by a natural sense of timing and rhythm."
    ),
    24: (
        "Shatabhisha nakshatra, ruled by Varuna (the cosmic lawkeeper), imparts a "
        "secretive, healing, and intellectually independent emotional nature. The "
        "mind seeks hidden knowledge and excels in research, astrology, and "
        "alternative medicine. A need for solitude balances the desire to heal others."
    ),
    25: (
        "Purva Bhadrapada nakshatra, ruled by Aja Ekapada (the one-footed goat), "
        "gives an intense, transformative, and philosophically fiery temperament. "
        "The mind oscillates between worldly ambition and spiritual transcendence. "
        "There is a capacity for dramatic personal reinvention and occult insight."
    ),
    26: (
        "Uttara Bhadrapada nakshatra, ruled by Ahir Budhnya (the serpent of the "
        "deep), confers a wise, contemplative, and deeply compassionate emotional "
        "nature. The mind finds peace through meditation, selfless service, and "
        "the quiet depths of spiritual practice. Kundalini awakening and wisdom "
        "through renunciation are indicated."
    ),
    27: (
        "Revati nakshatra, ruled by Pushan (the nourishing shepherd god), bestows "
        "a gentle, nurturing, and imaginatively rich emotional nature. The mind is "
        "compassionate, artistic, and drawn to caring for the vulnerable. Safe "
        "passage, completion of journeys, and spiritual contentment are its gifts."
    ),
}


# ---------------------------------------------------------------------------
# Ascendant personality sketches
# ---------------------------------------------------------------------------

_ASCENDANT_OVERVIEW: dict[int, str] = {
    1: (
        "With Aries rising, the personality is bold, pioneering, and action-oriented. "
        "You meet the world with directness and courage, preferring to lead rather "
        "than follow. Physical vitality tends to be strong, and there is a natural "
        "competitive edge that seeks to be first."
    ),
    2: (
        "With Taurus rising, the personality projects stability, sensuality, and "
        "quiet determination. You approach life methodically, valuing security, "
        "beauty, and material comfort. Patience and persistence define your "
        "engagement with the world."
    ),
    3: (
        "With Gemini rising, the personality is curious, communicative, and mentally "
        "agile. You engage the world through ideas, conversation, and a restless "
        "desire to learn. Versatility is a hallmark, though sustained focus may "
        "need cultivating."
    ),
    4: (
        "With Cancer rising, the personality is nurturing, emotionally perceptive, "
        "and deeply connected to home and family. You meet the world through "
        "feeling, and your instinct to protect those you love shapes every "
        "dimension of life."
    ),
    5: (
        "With Leo rising, the personality radiates confidence, warmth, and creative "
        "authority. You naturally command attention and carry yourself with dignity. "
        "Generosity of spirit and a dramatic flair colour your interactions."
    ),
    6: (
        "With Virgo rising, the personality is analytical, service-minded, and "
        "attentive to detail. You approach the world with a desire to improve, "
        "heal, and perfect, bringing practical intelligence to every endeavour."
    ),
    7: (
        "With Libra rising, the personality is diplomatic, aesthetically refined, "
        "and oriented toward harmony in relationships. You seek balance and "
        "fairness, approaching the world through partnership and social grace."
    ),
    8: (
        "With Scorpio rising, the personality is intense, psychologically perceptive, "
        "and drawn to the hidden dimensions of life. You engage the world with "
        "depth, determination, and a transformative power that others sense intuitively."
    ),
    9: (
        "With Sagittarius rising, the personality is expansive, philosophical, and "
        "oriented toward meaning and adventure. You meet the world with optimism "
        "and a desire to understand life's deeper truths through experience and study."
    ),
    10: (
        "With Capricorn rising, the personality is ambitious, disciplined, and "
        "acutely aware of responsibility and structure. You approach life as a "
        "long-term project, building steadily toward lasting achievement."
    ),
    11: (
        "With Aquarius rising, the personality is independent, humanitarian, and "
        "drawn to innovation and social ideals. You meet the world through the "
        "lens of progress, valuing intellectual freedom and collective well-being."
    ),
    12: (
        "With Pisces rising, the personality is compassionate, imaginative, and "
        "attuned to the subtler currents of existence. You engage the world "
        "through intuition and empathy, with a natural inclination toward "
        "spiritual and creative expression."
    ),
}


# ---------------------------------------------------------------------------
# Section builders -- used by the main reading generators
# ---------------------------------------------------------------------------

def _section(title: str, body: str) -> str:
    """Wrap a reading section with a visual header."""
    return f"\n{'=' * 3} {title} {'=' * 3}\n\n{body.strip()}\n"


def _describe_planet_brief(p: PlanetPosition) -> str:
    """One-liner summary: planet, sign, house, dignity, retro/combust flags."""
    parts = [f"{p.planet} at {_format_sign_degree(p.sign, p.sign_degree)} in the {_ordinal(p.house)} house"]
    dig = _dignity_phrase(p)
    if dig:
        parts.append(f"({dig})")
    if p.is_retrograde:
        parts.append("[R]")
    if p.is_combust:
        parts.append("[combust]")
    return " ".join(parts)


def _house_section(
    house: int,
    asc_sign: int,
    planets: list[PlanetPosition],
    extra_lines: list[str] | None = None,
) -> str:
    """Build a paragraph for a given house covering sign, lord, and occupants."""
    lines: list[str] = []
    sign = _get_house_sign(asc_sign, house)
    lord = SIGN_LORDS[sign]
    lord_planet = _find_planet(planets, lord)

    lines.append(
        f"The {_ordinal(house)} house carries the sign {SIGNS[sign]}, "
        f"ruled by {lord}."
    )

    # Planets occupying this house
    occupants = _planets_in_house(planets, house)
    if occupants:
        names = ", ".join(p.planet for p in occupants)
        lines.append(f"This house is occupied by {names}.")
        for occ in occupants:
            lines.append(interpret_planet_in_house(occ.planet, house))
            note = _retro_phrase(occ)
            if note:
                lines.append(note)
            note = _combust_phrase(occ)
            if note:
                lines.append(note)
    else:
        lines.append(
            "No planets occupy this house at birth, so its results flow "
            "primarily through its lord's condition and any aspects received."
        )

    # Lord placement
    if lord_planet:
        lines.append(
            interpret_house_lord_placement(house, lord, lord_planet.house)
        )
        dig = _dignity_phrase(lord_planet)
        if dig:
            lines.append(
                f"As lord of the {_ordinal(house)} house, {lord} is {dig}, "
                "which colours the quality of results this house can deliver."
            )
    else:
        lines.append(
            f"{lord} rules this house and its placement in the chart "
            "determines the direction of these life themes."
        )

    if extra_lines:
        lines.extend(extra_lines)

    return " ".join(lines)


# ---------------------------------------------------------------------------
# 1. BIRTH CHART READING
# ---------------------------------------------------------------------------

def generate_birth_chart_reading(
    planets: list[PlanetPosition],
    asc_sign: int,
    asc_degree: float,
    yogas: list[YogaResult],
    current_dasha: dict,
    moon_nakshatra: int,
) -> str:
    """Produce a comprehensive, multi-section natal chart reading.

    Parameters
    ----------
    planets : list[PlanetPosition]
        All nine Vedic planet positions calculated for the birth chart.
    asc_sign : int
        Ascendant zodiac sign (1-12).
    asc_degree : float
        Degree of the ascendant within its sign (0-30).
    yogas : list[YogaResult]
        Active yogas detected in the chart.
    current_dasha : dict
        Keys expected: ``maha`` (str planet), ``antar`` (str planet),
        ``maha_start`` (str ISO date), ``maha_end`` (str ISO date),
        ``antar_start`` (str ISO date), ``antar_end`` (str ISO date).
    moon_nakshatra : int
        Moon's birth nakshatra (1-27).

    Returns
    -------
    str
        A formatted, multi-section astrological reading.
    """
    sections: list[str] = []

    # -- Overview --
    chart_lord = SIGN_LORDS[asc_sign]
    chart_lord_planet = _find_planet(planets, chart_lord)

    overview_lines = [
        f"Ascendant: {_format_sign_degree(asc_sign, asc_degree)}.",
        "",
        _ASCENDANT_OVERVIEW.get(asc_sign, ""),
        "",
    ]
    if chart_lord_planet:
        overview_lines.append(
            f"The chart ruler is {chart_lord}, lord of {SIGNS[asc_sign]}. "
            f"It is placed in the {_ordinal(chart_lord_planet.house)} house "
            f"in {SIGNS[chart_lord_planet.sign]}. "
            f"The condition and placement of this planet colour the entire "
            f"life trajectory, setting the tone for how opportunities unfold "
            f"and challenges are met."
        )
        dig = _dignity_phrase(chart_lord_planet)
        if dig:
            overview_lines.append(
                f"Here, {chart_lord} is {dig}, which has a significant "
                "bearing on overall vitality and life direction."
            )
    sections.append(_section("BIRTH CHART OVERVIEW", "\n".join(overview_lines)))

    # -- 1st House: Personality & Self --
    first_extra: list[str] = []
    if chart_lord_planet:
        first_extra.append(
            f"Since {chart_lord} (your ascendant lord) resides in the "
            f"{_ordinal(chart_lord_planet.house)} house, your sense of self "
            "is channelled through the themes of that house, drawing your "
            "attention and life energy in that direction."
        )
    sections.append(_section(
        "PERSONALITY & SELF (1st House)",
        _house_section(1, asc_sign, planets, first_extra),
    ))

    # -- Moon: Mind & Emotions --
    moon = _find_planet(planets, 'Moon')
    moon_lines: list[str] = []
    if moon:
        moon_lines.append(
            f"The Moon, the significator of mind and emotional life, is placed "
            f"at {_format_sign_degree(moon.sign, moon.sign_degree)} in the "
            f"{_ordinal(moon.house)} house."
        )
        moon_lines.append(interpret_planet_in_sign('Moon', moon.sign, moon.dignity))
        moon_lines.append(interpret_planet_in_house('Moon', moon.house))
        moon_lines.append("")

        # Janma Nakshatra
        if 1 <= moon_nakshatra <= 27:
            nak_name = NAKSHATRA_NAMES[moon_nakshatra - 1]
            nak_desc = _NAKSHATRA_DESCRIPTIONS.get(moon_nakshatra, "")
            moon_lines.append(
                f"Your Janma Nakshatra (birth star) is {nak_name}. "
                f"This is the lunar mansion that most intimately shapes your "
                f"emotional temperament and inner world."
            )
            if nak_desc:
                moon_lines.append(nak_desc)
            moon_lines.append("")

        # Extra Moon notes
        note = _retro_phrase(moon)
        if note:
            moon_lines.append(note)
        note = _combust_phrase(moon)
        if note:
            moon_lines.append(note)

        moon_lines.append(
            "The Moon's condition is arguably the most important single factor "
            "in Vedic astrology, as it governs the subjective experience of "
            "life -- your emotional resilience, mental patterns, and the lens "
            "through which all other planetary results are felt."
        )
    else:
        moon_lines.append("Moon data is not available for this chart.")

    sections.append(_section("MIND & EMOTIONS (Moon)", "\n".join(moon_lines)))

    # -- 10th House: Career & Public Life --
    sun = _find_planet(planets, 'Sun')
    career_extra: list[str] = []
    if sun:
        career_extra.append(
            f"The Sun, natural karaka of authority and public recognition, is "
            f"in the {_ordinal(sun.house)} house in {SIGNS[sun.sign]}. "
            f"{interpret_planet_in_house('Sun', sun.house)}"
        )
    sections.append(_section(
        "CAREER & PUBLIC LIFE (10th House)",
        _house_section(10, asc_sign, planets, career_extra),
    ))

    # -- 7th House: Relationships & Marriage --
    venus = _find_planet(planets, 'Venus')
    rel_extra: list[str] = []
    if venus:
        rel_extra.append(
            f"Venus, the natural karaka of love and marriage, is in the "
            f"{_ordinal(venus.house)} house in {SIGNS[venus.sign]}. "
            f"{interpret_planet_in_house('Venus', venus.house)}"
        )
    sections.append(_section(
        "RELATIONSHIPS & MARRIAGE (7th House)",
        _house_section(7, asc_sign, planets, rel_extra),
    ))

    # -- 2nd & 11th Houses: Wealth & Finances --
    jupiter = _find_planet(planets, 'Jupiter')
    wealth_lines: list[str] = [
        "--- 2nd House (Accumulated Wealth & Family Resources) ---",
        _house_section(2, asc_sign, planets),
        "",
        "--- 11th House (Gains & Income Streams) ---",
        _house_section(11, asc_sign, planets),
        "",
    ]
    if jupiter:
        wealth_lines.append(
            f"Jupiter, the great benefic and natural karaka of wealth and "
            f"expansion, is in the {_ordinal(jupiter.house)} house in "
            f"{SIGNS[jupiter.sign]}. {interpret_planet_in_house('Jupiter', jupiter.house)}"
        )
    sections.append(_section(
        "WEALTH & FINANCES (2nd & 11th Houses)",
        "\n".join(wealth_lines),
    ))

    # -- 9th & 12th Houses: Spirituality & Dharma --
    ketu = _find_planet(planets, 'Ketu')
    spirit_lines: list[str] = [
        "--- 9th House (Dharma, Fortune & Higher Purpose) ---",
        _house_section(9, asc_sign, planets),
        "",
        "--- 12th House (Liberation, Foreign Lands & the Unseen) ---",
        _house_section(12, asc_sign, planets),
        "",
    ]
    if jupiter:
        spirit_lines.append(
            f"Jupiter's placement in the {_ordinal(jupiter.house)} house "
            f"shapes the spiritual and philosophical orientation of the chart."
        )
    if ketu:
        spirit_lines.append(
            f"Ketu, the moksha-karaka, sits in the {_ordinal(ketu.house)} house "
            f"in {SIGNS[ketu.sign]}, pointing toward where detachment and "
            f"spiritual insight develop most naturally."
        )
    sections.append(_section(
        "SPIRITUALITY & DHARMA (9th & 12th Houses)",
        "\n".join(spirit_lines),
    ))

    # -- Active Yogas --
    if yogas:
        yoga_lines: list[str] = [
            "Yogas are special planetary combinations that amplify or redirect "
            "the chart's potential. The following yogas are active in your chart:",
            "",
        ]
        for y in yogas:
            strength_label = f" [{y.strength}]" if y.strength else ""
            yoga_lines.append(f"  * {y.yoga_name} ({y.yoga_type}){strength_label}")
            if y.description:
                yoga_lines.append(f"    {y.description}")
            if y.planets_involved:
                yoga_lines.append(
                    f"    Formed by: {', '.join(y.planets_involved)}"
                )
            yoga_lines.append("")
    else:
        yoga_lines = [
            "No classical yogas were detected with the current analysis "
            "parameters. This does not diminish the chart -- many meaningful "
            "patterns express through the individual house and planet "
            "placements described above."
        ]
    sections.append(_section("ACTIVE YOGAS", "\n".join(yoga_lines)))

    # -- Current Dasha Period --
    dasha_lines: list[str] = []
    maha_lord = current_dasha.get('maha', '')
    antar_lord = current_dasha.get('antar', '')

    if maha_lord:
        maha_planet = _find_planet(planets, maha_lord)
        dasha_lines.append(
            f"You are currently running the Maha Dasha (major period) of "
            f"{maha_lord}"
        )
        maha_start = current_dasha.get('maha_start', '')
        maha_end = current_dasha.get('maha_end', '')
        if maha_start and maha_end:
            dasha_lines[-1] += f" ({maha_start} to {maha_end})."
        else:
            dasha_lines[-1] += "."

        dasha_lines.append(
            f"The {maha_lord} Maha Dasha lasts {DASHA_YEARS.get(maha_lord, '?')} "
            f"years and activates the houses that {maha_lord} rules and occupies "
            f"in the natal chart."
        )

        if maha_planet:
            dasha_lines.append(
                f"In your chart, {maha_lord} is placed in the "
                f"{_ordinal(maha_planet.house)} house in {SIGNS[maha_planet.sign]}. "
                f"During this period, the themes of the {_ordinal(maha_planet.house)} "
                f"house come to the foreground of life experience."
            )
            ruled_signs = _planet_lord_of(maha_lord)
            ruled_houses = []
            for s in ruled_signs:
                for h in range(1, 13):
                    if _get_house_sign(asc_sign, h) == s:
                        ruled_houses.append(h)
            if ruled_houses:
                house_str = " and ".join(_ordinal(h) for h in sorted(ruled_houses))
                dasha_lines.append(
                    f"As lord of the {house_str} house(s), {maha_lord} channels "
                    f"those life areas into prominence during this period."
                )
            sig = PLANET_SIGNIFICATIONS.get(maha_lord, {})
            strong = sig.get('strong', '')
            if strong:
                dasha_lines.append(
                    f"When well-placed, {maha_lord} brings: {strong}."
                )
        dasha_lines.append("")

    if antar_lord:
        antar_planet = _find_planet(planets, antar_lord)
        dasha_lines.append(
            f"Within the {maha_lord} Maha Dasha, the current Antar Dasha "
            f"(sub-period) belongs to {antar_lord}"
        )
        antar_start = current_dasha.get('antar_start', '')
        antar_end = current_dasha.get('antar_end', '')
        if antar_start and antar_end:
            dasha_lines[-1] += f" ({antar_start} to {antar_end})."
        else:
            dasha_lines[-1] += "."

        dasha_lines.append(
            f"The Antar Dasha adds a secondary layer of influence, blending "
            f"{antar_lord}'s significations with the overarching {maha_lord} theme."
        )

        if antar_planet:
            dasha_lines.append(
                f"{antar_lord} occupies the {_ordinal(antar_planet.house)} house "
                f"in {SIGNS[antar_planet.sign]}, so this sub-period spotlights "
                f"those natal themes."
            )

        # Maha-Antar relationship note
        if maha_lord and antar_lord and maha_lord != antar_lord:
            from ..models import NATURAL_FRIENDS, NATURAL_ENEMIES
            if antar_lord in NATURAL_FRIENDS.get(maha_lord, []):
                dasha_lines.append(
                    f"{maha_lord} and {antar_lord} are natural friends, suggesting "
                    f"this sub-period flows with relative ease and mutual support "
                    f"between their respective life themes."
                )
            elif antar_lord in NATURAL_ENEMIES.get(maha_lord, []):
                dasha_lines.append(
                    f"{maha_lord} and {antar_lord} are natural enemies, suggesting "
                    f"this sub-period may bring some tension or conflicting "
                    f"priorities between the life themes they govern."
                )
            else:
                dasha_lines.append(
                    f"{maha_lord} and {antar_lord} hold a neutral relationship, "
                    f"suggesting a moderately balanced sub-period where results "
                    f"depend significantly on their natal dignities and house placements."
                )

    if not dasha_lines:
        dasha_lines.append(
            "Dasha information was not provided for this reading. "
            "The Vimshottari dasha system is a cornerstone of Vedic timing, "
            "and incorporating it would add a vital temporal dimension."
        )

    sections.append(_section("CURRENT DASHA PERIOD", "\n".join(dasha_lines)))

    # -- Closing --
    closing = (
        "This reading synthesizes the major factors of your birth chart. "
        "Vedic astrology illuminates tendencies and timing, not fixed fate. "
        "Every planetary placement carries both a challenge and a gift, and "
        "conscious awareness of these patterns is the first step toward "
        "working with them wisely. The planets impel; they do not compel."
    )
    sections.append(_section("GUIDANCE NOTE", closing))

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# 2. TRANSIT READING
# ---------------------------------------------------------------------------

def _is_sade_sati(natal_moon_sign: int, transit_saturn_sign: int) -> tuple[bool, str]:
    """Check whether Saturn is transiting through the Sade Sati zone.

    Sade Sati = Saturn transiting the 12th, 1st, or 2nd house from the
    natal Moon sign (a 7.5-year period of karmic restructuring).

    Returns (is_active, phase_description).
    """
    diff = ((transit_saturn_sign - natal_moon_sign) % 12)
    if diff == 11:  # 12th from Moon
        return True, "rising phase (12th from Moon)"
    if diff == 0:   # over Moon
        return True, "peak phase (transiting over natal Moon)"
    if diff == 1:   # 2nd from Moon
        return True, "setting phase (2nd from Moon)"
    return False, ""


def _transit_house(natal_asc_sign: int, transit_sign: int) -> int:
    """Return the natal house a transit planet is activating."""
    return ((transit_sign - natal_asc_sign) % 12) + 1


def _is_conjunct(p1: PlanetPosition, p2: PlanetPosition, orb: float = 10.0) -> bool:
    """Check if two planets are within orb degrees of longitude."""
    diff = abs(p1.longitude - p2.longitude)
    if diff > 180:
        diff = 360 - diff
    return diff <= orb


def generate_transit_reading(
    natal_planets: list[PlanetPosition],
    natal_asc_sign: int,
    transit_planets: list[PlanetPosition],
    current_dasha: dict,
) -> str:
    """Produce a reading focused on current planetary transits.

    Parameters
    ----------
    natal_planets : list[PlanetPosition]
        Birth chart planet positions.
    natal_asc_sign : int
        Birth ascendant sign (1-12).
    transit_planets : list[PlanetPosition]
        Current planetary positions (transit chart).
    current_dasha : dict
        Same format as in ``generate_birth_chart_reading``.

    Returns
    -------
    str
        Formatted transit analysis.
    """
    sections: list[str] = []
    today = datetime.now().strftime("%d %B %Y")

    header = (
        f"Transit analysis prepared for {today}.\n\n"
        "Transits show the current celestial weather interacting with the "
        "promise of the natal chart. In Vedic astrology, transits are always "
        "read in conjunction with the running dasha period -- a transit can "
        "only activate what the dasha has made ripe."
    )
    sections.append(_section("CURRENT PLANETARY TRANSITS", header))

    natal_moon = _find_planet(natal_planets, 'Moon')

    # ---- Major slow-movers ----
    major_lines: list[str] = []

    # Saturn
    t_saturn = _find_planet(transit_planets, 'Saturn')
    if t_saturn:
        sat_house = _transit_house(natal_asc_sign, t_saturn.sign)
        major_lines.append(f"-- Saturn Transit --")
        major_lines.append(
            f"Saturn is currently transiting {SIGNS[t_saturn.sign]}, "
            f"activating your {_ordinal(sat_house)} house. "
            f"Saturn's transit through a house lasts roughly 2.5 years, "
            f"bringing themes of restructuring, discipline, and karmic "
            f"accountability to the affairs of that house."
        )
        house_sig = HOUSE_SIGNIFICATIONS.get(sat_house, {})
        areas = house_sig.get('areas', '')
        if areas:
            major_lines.append(
                f"The {_ordinal(sat_house)} house governs {areas}. "
                f"Saturn's presence here demands patient effort and maturity "
                f"in these areas, ultimately building lasting foundations."
            )

        # Sade Sati check
        if natal_moon:
            sade_sati, phase = _is_sade_sati(natal_moon.sign, t_saturn.sign)
            if sade_sati:
                major_lines.append(
                    f"Sade Sati is ACTIVE -- {phase}. This is the "
                    f"well-known 7.5-year period when Saturn transits over "
                    f"and around the natal Moon. It brings emotional maturation, "
                    f"restructuring of personal life, and the dissolution of "
                    f"patterns that no longer serve growth. While it can feel "
                    f"heavy, it is one of the most growth-producing transits "
                    f"in Vedic astrology. Patience and self-care are essential."
                )
            else:
                major_lines.append("Sade Sati is not currently active.")

        # Conjunctions with natal planets
        for np in natal_planets:
            if _is_conjunct(t_saturn, np, orb=8.0):
                major_lines.append(
                    f"Saturn is closely transiting over natal {np.planet}, "
                    f"intensifying karmic themes connected to {np.planet}'s "
                    f"significations. This conjunction demands maturity in "
                    f"the areas {np.planet} governs."
                )
        major_lines.append("")

    # Jupiter
    t_jupiter = _find_planet(transit_planets, 'Jupiter')
    if t_jupiter:
        jup_house = _transit_house(natal_asc_sign, t_jupiter.sign)
        major_lines.append(f"-- Jupiter Transit --")
        major_lines.append(
            f"Jupiter is currently transiting {SIGNS[t_jupiter.sign]}, "
            f"activating your {_ordinal(jup_house)} house. "
            f"Jupiter's transit through a house lasts about one year, "
            f"bringing expansion, opportunity, and grace to its affairs."
        )
        house_sig = HOUSE_SIGNIFICATIONS.get(jup_house, {})
        areas = house_sig.get('areas', '')
        if areas:
            major_lines.append(
                f"The {_ordinal(jup_house)} house governs {areas}. "
                f"Jupiter's benevolent gaze here opens doors and encourages "
                f"growth in these domains."
            )
        for np in natal_planets:
            if _is_conjunct(t_jupiter, np, orb=10.0):
                major_lines.append(
                    f"Jupiter is closely transiting over natal {np.planet}, "
                    f"amplifying and blessing the significations of {np.planet}. "
                    f"This is generally a protective and expansive influence."
                )
        major_lines.append("")

    # Rahu-Ketu axis
    t_rahu = _find_planet(transit_planets, 'Rahu')
    t_ketu = _find_planet(transit_planets, 'Ketu')
    if t_rahu and t_ketu:
        rahu_house = _transit_house(natal_asc_sign, t_rahu.sign)
        ketu_house = _transit_house(natal_asc_sign, t_ketu.sign)
        major_lines.append(f"-- Rahu-Ketu Axis --")
        major_lines.append(
            f"Rahu is transiting {SIGNS[t_rahu.sign]} "
            f"(your {_ordinal(rahu_house)} house) while Ketu transits "
            f"{SIGNS[t_ketu.sign]} (your {_ordinal(ketu_house)} house). "
            f"The nodal axis stays in a sign pair for about 18 months, "
            f"creating an evolutionary tension between worldly desire "
            f"(Rahu's house) and spiritual release (Ketu's house)."
        )
        rahu_sig = HOUSE_SIGNIFICATIONS.get(rahu_house, {})
        ketu_sig = HOUSE_SIGNIFICATIONS.get(ketu_house, {})
        rahu_areas = rahu_sig.get('areas', '')
        ketu_areas = ketu_sig.get('areas', '')
        if rahu_areas and ketu_areas:
            major_lines.append(
                f"Rahu is amplifying desire and ambition around {rahu_areas}, "
                f"while Ketu is encouraging detachment and spiritual insight "
                f"in the domain of {ketu_areas}."
            )
        for np in natal_planets:
            if _is_conjunct(t_rahu, np, orb=8.0):
                major_lines.append(
                    f"Rahu is closely transiting natal {np.planet}, "
                    f"which can intensify and sometimes distort "
                    f"{np.planet}'s significations -- amplifying ambition "
                    f"but requiring discernment."
                )
            if _is_conjunct(t_ketu, np, orb=8.0):
                major_lines.append(
                    f"Ketu is closely transiting natal {np.planet}, "
                    f"fostering detachment, spiritual insight, or unexpected "
                    f"shifts connected to {np.planet}'s themes."
                )
        major_lines.append("")

    # Mars (faster but impactful)
    t_mars = _find_planet(transit_planets, 'Mars')
    if t_mars:
        mars_house = _transit_house(natal_asc_sign, t_mars.sign)
        major_lines.append(f"-- Mars Transit --")
        major_lines.append(
            f"Mars is transiting {SIGNS[t_mars.sign]}, activating your "
            f"{_ordinal(mars_house)} house. Mars moves through a sign in "
            f"roughly 45 days, bringing energy, initiative, and sometimes "
            f"friction to the house it occupies."
        )
        house_sig = HOUSE_SIGNIFICATIONS.get(mars_house, {})
        areas = house_sig.get('areas', '')
        if areas:
            major_lines.append(
                f"Short-term action and drive are directed toward {areas}."
            )
        major_lines.append("")

    sections.append(_section("MAJOR TRANSITS", "\n".join(major_lines)))

    # ---- Dasha-Transit Interaction ----
    dasha_lines: list[str] = []
    maha_lord = current_dasha.get('maha', '')
    antar_lord = current_dasha.get('antar', '')

    if maha_lord:
        dasha_lines.append(
            f"The running Maha Dasha of {maha_lord} sets the primary life "
            f"theme. Transits that aspect or conjoin natal {maha_lord} carry "
            f"extra weight during this period."
        )
        maha_planet = _find_planet(natal_planets, maha_lord)
        if maha_planet:
            for tp in transit_planets:
                if tp.planet in ('Saturn', 'Jupiter', 'Rahu', 'Ketu'):
                    if _is_conjunct(tp, maha_planet, orb=10.0):
                        dasha_lines.append(
                            f"Notably, transiting {tp.planet} is closely "
                            f"engaging natal {maha_lord} (the dasha lord), "
                            f"making this a particularly significant period "
                            f"for the themes {maha_lord} governs."
                        )

    if antar_lord:
        dasha_lines.append(
            f"The Antar Dasha of {antar_lord} adds a secondary timing layer. "
            f"Transits touching natal {antar_lord} fine-tune events within "
            f"the broader Maha Dasha framework."
        )

    if not dasha_lines:
        dasha_lines.append(
            "Dasha information was not provided. For the most accurate "
            "transit reading, the running Vimshottari dasha periods should "
            "be considered alongside these transits."
        )
    sections.append(_section("DASHA-TRANSIT INTERACTION", "\n".join(dasha_lines)))

    # ---- Monthly Forecast ----
    forecast_lines: list[str] = []
    forecast_lines.append(
        "Combining the current dasha period with the transit picture above, "
        "the following general guidance applies:"
    )
    forecast_lines.append("")

    # Build guidance from the slowest transit (Saturn) and Jupiter
    if t_saturn:
        sat_house = _transit_house(natal_asc_sign, t_saturn.sign)
        if sat_house in (1, 4, 7, 10):
            forecast_lines.append(
                "Saturn transiting a kendra (angular) house brings significant "
                "structural changes to your public and personal life. This is a "
                "time for patient rebuilding and accepting responsibilities. "
                "Results require sustained effort but are ultimately durable."
            )
        elif sat_house in (1, 5, 9):
            forecast_lines.append(
                "Saturn transiting a trine house is restructuring your "
                "relationship with dharma, creativity, and self-identity. "
                "This is a time for deepening discipline in spiritual or "
                "creative practice."
            )
        elif sat_house in (6, 8, 12):
            forecast_lines.append(
                "Saturn transiting a dusthana house may bring health awareness, "
                "hidden challenges, or expenses that serve a karmic purpose. "
                "Look after your physical well-being and attend to any "
                "lingering obligations."
            )
        else:
            forecast_lines.append(
                "Saturn's transit through your chart is encouraging steady, "
                "methodical progress. Avoid shortcuts and trust the process "
                "of building something lasting."
            )

    if t_jupiter:
        jup_house = _transit_house(natal_asc_sign, t_jupiter.sign)
        if jup_house in (1, 5, 9):
            forecast_lines.append(
                "Jupiter transiting a dharma house is one of the most "
                "auspicious configurations, bringing wisdom, opportunity, "
                "and spiritual growth. Make the most of this window for "
                "learning, teaching, or beginning important ventures."
            )
        elif jup_house in (2, 11):
            forecast_lines.append(
                "Jupiter transiting a wealth house supports financial "
                "growth, new income channels, and the fulfilment of "
                "material desires. Generosity during this time "
                "multiplies returns."
            )
        else:
            forecast_lines.append(
                "Jupiter's transit brings its natural grace and expansion "
                "to the house it occupies. Stay open to opportunities and "
                "maintain an attitude of gratitude and ethical conduct."
            )

    forecast_lines.append("")
    forecast_lines.append(
        "As always, free will is the final arbiter. These celestial currents "
        "indicate the weather, but you choose how to navigate it."
    )
    sections.append(_section("MONTHLY FORECAST", "\n".join(forecast_lines)))

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# 3. TOPIC READING
# ---------------------------------------------------------------------------

# Topic -> relevant houses, relevant planets, relevant lord houses
_TOPIC_MAP: dict[str, dict] = {
    'career': {
        'houses': [10, 6, 2],
        'karakas': ['Sun', 'Saturn', 'Mercury'],
        'lord_houses': [10],
        'title': 'CAREER & PROFESSIONAL LIFE',
    },
    'love': {
        'houses': [7, 5, 2],
        'karakas': ['Venus', 'Jupiter'],
        'lord_houses': [7],
        'title': 'LOVE & RELATIONSHIPS',
    },
    'relationship': {
        'houses': [7, 5, 2],
        'karakas': ['Venus', 'Jupiter'],
        'lord_houses': [7],
        'title': 'LOVE & RELATIONSHIPS',
    },
    'marriage': {
        'houses': [7, 5, 2],
        'karakas': ['Venus', 'Jupiter'],
        'lord_houses': [7],
        'title': 'MARRIAGE & PARTNERSHIP',
    },
    'health': {
        'houses': [1, 6, 8],
        'karakas': ['Sun', 'Mars'],
        'lord_houses': [1],
        'title': 'HEALTH & VITALITY',
    },
    'wealth': {
        'houses': [2, 11, 5, 9],
        'karakas': ['Jupiter', 'Venus'],
        'lord_houses': [2, 11],
        'title': 'WEALTH & FINANCIAL PROSPECTS',
    },
    'money': {
        'houses': [2, 11, 5, 9],
        'karakas': ['Jupiter', 'Venus'],
        'lord_houses': [2, 11],
        'title': 'WEALTH & FINANCIAL PROSPECTS',
    },
    'finance': {
        'houses': [2, 11, 5, 9],
        'karakas': ['Jupiter', 'Venus'],
        'lord_houses': [2, 11],
        'title': 'WEALTH & FINANCIAL PROSPECTS',
    },
    'education': {
        'houses': [4, 5, 9],
        'karakas': ['Mercury', 'Jupiter'],
        'lord_houses': [4, 5],
        'title': 'EDUCATION & LEARNING',
    },
    'spirituality': {
        'houses': [9, 12, 5],
        'karakas': ['Jupiter', 'Ketu'],
        'lord_houses': [9, 12],
        'title': 'SPIRITUALITY & INNER GROWTH',
    },
    'family': {
        'houses': [2, 4, 5],
        'karakas': ['Moon', 'Jupiter'],
        'lord_houses': [4],
        'title': 'FAMILY & DOMESTIC LIFE',
    },
}


def generate_topic_reading(
    topic: str,
    planets: list[PlanetPosition],
    asc_sign: int,
    yogas: list[YogaResult],
    current_dasha: dict,
    transit_planets: list[PlanetPosition] | None = None,
) -> str:
    """Produce a focused reading on a specific life topic.

    Parameters
    ----------
    topic : str
        The topic keyword (e.g. 'career', 'love', 'health').
    planets : list[PlanetPosition]
        Natal planet positions.
    asc_sign : int
        Ascendant sign (1-12).
    yogas : list[YogaResult]
        Active yogas in the chart.
    current_dasha : dict
        Same format as in ``generate_birth_chart_reading``.
    transit_planets : list[PlanetPosition] | None
        Current transit positions (optional).

    Returns
    -------
    str
        Formatted topic-specific reading.
    """
    key = topic.lower().strip()
    config = _TOPIC_MAP.get(key)
    if config is None:
        # Attempt a partial match
        for k, v in _TOPIC_MAP.items():
            if k in key or key in k:
                config = v
                break
    if config is None:
        config = {
            'houses': [1],
            'karakas': ['Sun'],
            'lord_houses': [1],
            'title': f'READING: {topic.upper()}',
        }

    sections: list[str] = []
    title = config['title']
    relevant_houses: list[int] = config['houses']
    karakas: list[str] = config['karakas']
    lord_houses: list[int] = config['lord_houses']

    # -- Natal factors --
    natal_lines: list[str] = []
    natal_lines.append(
        f"This reading focuses on {title.lower()} as indicated by your "
        f"birth chart. The primary houses under consideration are the "
        f"{', '.join(_ordinal(h) for h in relevant_houses)}, along with "
        f"the natural karaka planets {', '.join(karakas)}."
    )
    natal_lines.append("")

    for h in relevant_houses:
        sign = _get_house_sign(asc_sign, h)
        lord = SIGN_LORDS[sign]
        natal_lines.append(f"--- {_ordinal(h)} House ({SIGNS[sign]}, lord {lord}) ---")
        natal_lines.append(_house_section(h, asc_sign, planets))
        natal_lines.append("")

    # Karaka planets
    natal_lines.append("--- Key Significator Planets ---")
    for k_name in karakas:
        kp = _find_planet(planets, k_name)
        if kp:
            natal_lines.append(f"{_describe_planet_brief(kp)}")
            natal_lines.append(interpret_planet_in_house(k_name, kp.house))
            dig = _dignity_phrase(kp)
            if dig:
                natal_lines.append(f"{k_name} is {dig}.")
            natal_lines.append("")
    sections.append(_section(f"{title} -- NATAL INDICATORS", "\n".join(natal_lines)))

    # -- Dasha connection --
    dasha_lines: list[str] = []
    maha_lord = current_dasha.get('maha', '')
    antar_lord = current_dasha.get('antar', '')

    if maha_lord:
        maha_planet = _find_planet(planets, maha_lord)
        dasha_connected = False

        # Does the maha lord rule or occupy a relevant house?
        for lh in lord_houses:
            house_lord = _get_house_lord(asc_sign, lh)
            if maha_lord == house_lord:
                dasha_lines.append(
                    f"The current Maha Dasha lord {maha_lord} rules the "
                    f"{_ordinal(lh)} house, directly activating {title.lower()} "
                    f"themes in this period of your life. This is a time when "
                    f"developments in this area are especially pronounced."
                )
                dasha_connected = True
                break

        if not dasha_connected and maha_planet:
            if maha_planet.house in relevant_houses:
                dasha_lines.append(
                    f"The Maha Dasha lord {maha_lord} occupies the "
                    f"{_ordinal(maha_planet.house)} house, which is directly "
                    f"relevant to {title.lower()}. Expect this topic to feature "
                    f"prominently during this dasha."
                )
                dasha_connected = True

        if not dasha_connected:
            dasha_lines.append(
                f"The current Maha Dasha of {maha_lord} does not directly "
                f"rule or occupy the primary houses for {title.lower()}, "
                f"so developments in this area operate as a background theme "
                f"rather than the central narrative of this period."
            )

        if antar_lord:
            antar_planet = _find_planet(planets, antar_lord)
            antar_relevant = False
            for lh in lord_houses:
                if antar_lord == _get_house_lord(asc_sign, lh):
                    antar_relevant = True
                    break
            if not antar_relevant and antar_planet:
                if antar_planet.house in relevant_houses:
                    antar_relevant = True

            if antar_relevant:
                dasha_lines.append(
                    f"The Antar Dasha of {antar_lord} is actively connected "
                    f"to {title.lower()} themes, making this sub-period "
                    f"particularly significant for this area."
                )
            else:
                dasha_lines.append(
                    f"The Antar Dasha of {antar_lord} operates in a "
                    f"supporting role for {title.lower()} during this sub-period."
                )
    else:
        dasha_lines.append(
            "Dasha timing information was not provided. Incorporating the "
            "Vimshottari dasha would sharpen the timing dimension of this reading."
        )

    sections.append(_section("TIMING (Dasha Connection)", "\n".join(dasha_lines)))

    # -- Relevant yogas --
    relevant_yogas = [
        y for y in yogas
        if any(h in y.houses_involved for h in relevant_houses)
        or any(k in y.planets_involved for k in karakas)
    ]
    if relevant_yogas:
        yoga_lines: list[str] = [
            f"The following yogas bear directly on {title.lower()}:",
            "",
        ]
        for y in relevant_yogas:
            yoga_lines.append(f"  * {y.yoga_name} ({y.yoga_type})")
            if y.description:
                yoga_lines.append(f"    {y.description}")
            yoga_lines.append("")
        sections.append(_section("RELEVANT YOGAS", "\n".join(yoga_lines)))

    # -- Transit overlay (if provided) --
    if transit_planets:
        transit_lines: list[str] = []
        slow_movers = ['Saturn', 'Jupiter', 'Rahu', 'Ketu']
        for sm in slow_movers:
            tp = _find_planet(transit_planets, sm)
            if tp:
                t_house = _transit_house(asc_sign, tp.sign)
                if t_house in relevant_houses:
                    transit_lines.append(
                        f"Transiting {sm} is currently in your "
                        f"{_ordinal(t_house)} house ({SIGNS[tp.sign]}), "
                        f"directly influencing {title.lower()} matters."
                    )
                    sig = PLANET_SIGNIFICATIONS.get(sm, {})
                    if sm == 'Jupiter':
                        transit_lines.append(
                            f"Jupiter's transit here is generally supportive, "
                            f"bringing expansion and opportunity to this area."
                        )
                    elif sm == 'Saturn':
                        transit_lines.append(
                            f"Saturn's transit here demands patience and "
                            f"discipline but builds lasting foundations when "
                            f"the effort is sincere."
                        )
                    elif sm == 'Rahu':
                        transit_lines.append(
                            f"Rahu's transit amplifies desire and ambition in "
                            f"this area but requires careful discernment to "
                            f"avoid illusion."
                        )
                    elif sm == 'Ketu':
                        transit_lines.append(
                            f"Ketu's transit encourages detachment and "
                            f"spiritual perspective, which may feel like "
                            f"loss but ultimately serves liberation."
                        )
                    transit_lines.append("")

                # Check conjunctions with natal karakas
                for k_name in karakas:
                    kp = _find_planet(planets, k_name)
                    if kp and _is_conjunct(tp, kp, orb=10.0):
                        transit_lines.append(
                            f"Transiting {sm} is conjunct natal {k_name} "
                            f"(a key significator for {title.lower()}), "
                            f"making this a pivotal window for developments "
                            f"in this area."
                        )

        if transit_lines:
            sections.append(_section(
                "CURRENT TRANSITS (Topic-Specific)",
                "\n".join(transit_lines),
            ))

    # -- Synthesis --
    synthesis_lines: list[str] = []
    synthesis_lines.append(
        f"Drawing together the natal placements, dasha timing, "
        f"and {'transit influences, ' if transit_planets else ''}"
        f"the following picture emerges for {title.lower()}:"
    )
    synthesis_lines.append("")

    # Summarise the strongest factor
    primary_house = relevant_houses[0]
    primary_sign = _get_house_sign(asc_sign, primary_house)
    primary_lord = SIGN_LORDS[primary_sign]
    primary_lord_planet = _find_planet(planets, primary_lord)

    synthesis_lines.append(
        f"The {_ordinal(primary_house)} house, the principal house for "
        f"{title.lower()}, carries {SIGNS[primary_sign]} and is ruled by "
        f"{primary_lord}."
    )

    occupants = _planets_in_house(planets, primary_house)
    if occupants:
        occ_names = ", ".join(p.planet for p in occupants)
        synthesis_lines.append(
            f"The presence of {occ_names} in this house actively energises "
            f"this life area, for better or more challenging, depending on "
            f"each planet's nature and dignity."
        )

    if primary_lord_planet:
        dig = _dignity_phrase(primary_lord_planet)
        if dig and ('exalted' in dig or 'own' in dig or 'moolatrikona' in dig):
            synthesis_lines.append(
                f"The lord of this house, {primary_lord}, is {dig}, which is a "
                f"genuinely positive indicator -- suggesting that the "
                f"fundamental promise in this area is strong and supportive."
            )
        elif dig and ('debilitated' in dig or 'enemy' in dig):
            synthesis_lines.append(
                f"The lord of this house, {primary_lord}, is {dig}. This "
                f"suggests that results in this area may require extra effort, "
                f"patience, or the support of remedial measures. It is not a "
                f"denial, but an indication that the path may be less direct."
            )
        else:
            synthesis_lines.append(
                f"The lord of this house, {primary_lord}, is {dig or 'in a moderate condition'}, "
                f"indicating that results in this area are achievable with "
                f"steady effort and attention."
            )

    synthesis_lines.append("")
    synthesis_lines.append(
        "Remember that Vedic astrology maps tendencies and timing, not "
        "certainties. Awareness of these patterns empowers you to align "
        "your efforts with the cosmic currents rather than struggle "
        "against them."
    )

    sections.append(_section("SYNTHESIS", "\n".join(synthesis_lines)))

    return "\n".join(sections)
