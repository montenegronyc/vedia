"""Overlay transit planets on a natal chart and analyze impacts.

Determines which natal houses transiting planets occupy, identifies
conjunctions with natal planets, evaluates Vedic aspects from transit
planets to natal planets, and produces a structured transit summary
including Sade Sati, Jupiter transits, and Rahu/Ketu axis analysis.
"""

from ..models import PlanetPosition, SIGNS


# ---------------------------------------------------------------------------
# Vedic aspect definitions
# ---------------------------------------------------------------------------
# In Vedic astrology every planet casts a full (100%) aspect on the 7th
# house from its position. Additionally, certain planets have special
# (full-strength) aspects:
#   Mars   -> 4th and 8th houses from itself
#   Jupiter -> 5th and 9th houses from itself
#   Saturn  -> 3rd and 10th houses from itself
#   Rahu/Ketu also cast 5th, 7th, 9th aspects (treated like Jupiter here)
#
# The dict maps planet name to a list of house-offsets that receive
# the planet's full aspect (the offset is counted from the planet's
# occupied house, inclusive: offset 7 means the 7th house from itself).
# ---------------------------------------------------------------------------
_VEDIC_ASPECTS: dict[str, list[int]] = {
    'Sun':     [7],
    'Moon':    [7],
    'Mars':    [4, 7, 8],
    'Mercury': [7],
    'Jupiter': [5, 7, 9],
    'Venus':   [7],
    'Saturn':  [3, 7, 10],
    'Rahu':    [5, 7, 9],
    'Ketu':    [5, 7, 9],
}


def _house_from_reference(planet_sign: int, reference_sign: int) -> int:
    """Compute whole-sign house number of *planet_sign* from *reference_sign*.

    The reference sign is always house 1.  Returns 1-12.
    """
    return ((planet_sign - reference_sign) % 12) + 1


def _sign_at_offset(base_sign: int, offset: int) -> int:
    """Return the sign number that is *offset* houses from *base_sign*.

    ``offset=1`` returns *base_sign* itself (the 1st house from itself).
    ``offset=7`` returns the sign 6 signs ahead, etc.
    """
    return ((base_sign - 1 + offset - 1) % 12) + 1


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def overlay_transits(
    natal_planets: list[PlanetPosition],
    transit_planets: list[PlanetPosition],
    natal_asc_sign: int,
) -> list[dict]:
    """Overlay transit planets onto a natal chart.

    For each transit planet this function determines:

    * Which natal house (whole-sign) the transit planet occupies.
    * Which natal planets it conjuncts (same sign).
    * Which natal planets it aspects via Vedic aspects.

    Args:
        natal_planets: Natal PlanetPosition list (all 9 grahas).
        transit_planets: Current transit PlanetPosition list.
        natal_asc_sign: Sign number (1-12) of the natal ascendant.

    Returns:
        List of dicts, one per transit planet::

            {
                "transit_planet": str,
                "transit_sign": int,
                "transit_sign_name": str,
                "natal_house": int,
                "conjunctions": [
                    {"natal_planet": str, "orb": float}, ...
                ],
                "aspects": [
                    {"natal_planet": str, "aspect_type": int,
                     "natal_sign": int}, ...
                ],
            }
    """
    results: list[dict] = []

    for tp in transit_planets:
        natal_house = _house_from_reference(tp.sign, natal_asc_sign)

        # --- Conjunctions: natal planets in the same sign as this transit ---
        conjunctions: list[dict] = []
        for np in natal_planets:
            if np.sign == tp.sign:
                orb = abs(tp.longitude - np.longitude)
                if orb > 180.0:
                    orb = 360.0 - orb
                conjunctions.append({
                    'natal_planet': np.planet,
                    'orb': round(orb, 4),
                })

        # --- Vedic aspects from this transit planet to natal planets --------
        aspect_offsets = _VEDIC_ASPECTS.get(tp.planet, [7])
        aspected_signs = {_sign_at_offset(tp.sign, off) for off in aspect_offsets}

        aspects: list[dict] = []
        for np in natal_planets:
            if np.sign in aspected_signs:
                # Determine which aspect type (offset) hit this natal planet
                for off in aspect_offsets:
                    if _sign_at_offset(tp.sign, off) == np.sign:
                        aspects.append({
                            'natal_planet': np.planet,
                            'aspect_type': off,
                            'natal_sign': np.sign,
                        })
                        break

        results.append({
            'transit_planet': tp.planet,
            'transit_sign': tp.sign,
            'transit_sign_name': SIGNS[tp.sign] if tp.sign < len(SIGNS) else '',
            'natal_house': natal_house,
            'conjunctions': conjunctions,
            'aspects': aspects,
        })

    return results


def get_transit_summary(
    natal_planets: list[PlanetPosition],
    transit_planets: list[PlanetPosition],
    natal_asc_sign: int,
) -> dict:
    """Produce a high-level transit summary keyed by transit planet.

    Includes the house being transited, key conjunctions/aspects, and
    special annotations for:

    * **Sade Sati**: Saturn transiting the 12th, 1st, or 2nd house from
      the natal Moon sign (7.5-year Saturn transit over the Moon).
    * **Jupiter transits**: Jupiter's house from the Moon and from the
      ascendant, highlighting auspicious positions (2, 5, 7, 9, 11).
    * **Rahu/Ketu axis**: Which pair of natal houses the nodal axis passes
      through.

    Args:
        natal_planets: Natal PlanetPosition list.
        transit_planets: Current transit PlanetPosition list.
        natal_asc_sign: Sign number (1-12) of the natal ascendant.

    Returns:
        Dict keyed by planet name::

            {
                "Sun": {
                    "natal_house": int,
                    "transit_sign": int,
                    "conjunctions": [...],
                    "aspects": [...],
                    "notes": [str, ...],
                },
                ...
                "_special": {
                    "sade_sati": {...} or None,
                    "jupiter_transit": {...},
                    "rahu_ketu_axis": {...},
                },
            }
    """
    overlay = overlay_transits(natal_planets, transit_planets, natal_asc_sign)

    # Build quick lookup: transit planet name -> overlay entry
    overlay_map: dict[str, dict] = {}
    for entry in overlay:
        overlay_map[entry['transit_planet']] = entry

    # Find natal Moon sign for house-from-Moon calculations
    natal_moon_sign = _get_planet_sign(natal_planets, 'Moon')

    # Build per-planet summary
    summary: dict = {}

    for entry in overlay:
        planet = entry['transit_planet']
        house_from_moon = _house_from_reference(entry['transit_sign'], natal_moon_sign)

        notes: list[str] = []

        # Conjunction notes
        if entry['conjunctions']:
            conj_names = [c['natal_planet'] for c in entry['conjunctions']]
            notes.append(f"Conjunct natal {', '.join(conj_names)}")

        # Aspect notes
        if entry['aspects']:
            for asp in entry['aspects']:
                notes.append(
                    f"Aspects natal {asp['natal_planet']} "
                    f"(house {asp['aspect_type']} aspect)"
                )

        summary[planet] = {
            'natal_house': entry['natal_house'],
            'transit_sign': entry['transit_sign'],
            'house_from_moon': house_from_moon,
            'conjunctions': entry['conjunctions'],
            'aspects': entry['aspects'],
            'notes': notes,
        }

    # ------------------------------------------------------------------
    # Special transit annotations
    # ------------------------------------------------------------------
    special: dict = {}

    # --- Sade Sati check (Saturn from Moon) ---
    saturn_entry = overlay_map.get('Saturn')
    if saturn_entry is not None:
        saturn_house_from_moon = _house_from_reference(
            saturn_entry['transit_sign'], natal_moon_sign,
        )
        if saturn_house_from_moon in (12, 1, 2):
            phase_map = {12: 'rising (12th from Moon)', 1: 'peak (over Moon)',
                         2: 'setting (2nd from Moon)'}
            special['sade_sati'] = {
                'active': True,
                'phase': phase_map[saturn_house_from_moon],
                'saturn_house_from_moon': saturn_house_from_moon,
                'saturn_transit_sign': saturn_entry['transit_sign'],
            }
        else:
            special['sade_sati'] = {
                'active': False,
                'saturn_house_from_moon': saturn_house_from_moon,
            }

    # --- Jupiter transit ---
    jupiter_entry = overlay_map.get('Jupiter')
    if jupiter_entry is not None:
        jup_house_from_moon = _house_from_reference(
            jupiter_entry['transit_sign'], natal_moon_sign,
        )
        jup_house_from_asc = jupiter_entry['natal_house']
        auspicious_houses = {2, 5, 7, 9, 11}
        special['jupiter_transit'] = {
            'house_from_moon': jup_house_from_moon,
            'house_from_ascendant': jup_house_from_asc,
            'favorable_from_moon': jup_house_from_moon in auspicious_houses,
            'favorable_from_asc': jup_house_from_asc in auspicious_houses,
        }

    # --- Rahu / Ketu axis ---
    rahu_entry = overlay_map.get('Rahu')
    ketu_entry = overlay_map.get('Ketu')
    if rahu_entry is not None and ketu_entry is not None:
        special['rahu_ketu_axis'] = {
            'rahu_natal_house': rahu_entry['natal_house'],
            'ketu_natal_house': ketu_entry['natal_house'],
            'rahu_house_from_moon': _house_from_reference(
                rahu_entry['transit_sign'], natal_moon_sign,
            ),
            'ketu_house_from_moon': _house_from_reference(
                ketu_entry['transit_sign'], natal_moon_sign,
            ),
            'axis_houses': sorted([
                rahu_entry['natal_house'], ketu_entry['natal_house'],
            ]),
        }

    summary['_special'] = special
    return summary


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_planet_sign(planets: list[PlanetPosition], planet_name: str) -> int:
    """Return the sign number for *planet_name* from a list of positions.

    Raises ``ValueError`` if the planet is not found.
    """
    for p in planets:
        if p.planet == planet_name:
            return p.sign
    raise ValueError(f"Planet '{planet_name}' not found in positions list")
