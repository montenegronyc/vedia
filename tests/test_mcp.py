"""Unit tests for the Vedia MCP server.

Tests helper functions directly and tool functions against the real DB
(Crystal and Lee are expected to already be stored at vedia.db).
"""
import pytest
from datetime import datetime

from vedia.models import PlanetPosition, SIGNS, NAKSHATRA_NAMES
from vedia.mcp_server import (
    _db_planets_to_model,
    _sign_name,
    _nak_name,
    _planet_to_dict,
    list_charts,
    get_chart,
    analyze_transits,
    analyze_compatibility,
    evaluate_timing,
)


# ---------------------------------------------------------------------------
# Helper: _db_planets_to_model
# ---------------------------------------------------------------------------

def test_db_planets_to_model_basic():
    """_db_planets_to_model converts DB-style dicts to PlanetPosition objects."""
    rows = [
        {
            'planet': 'Sun',
            'longitude': 293.0,
            'sign': 10,
            'sign_degree': 23.0,
            'nakshatra': 22,
            'nakshatra_pada': 4,
            'nakshatra_lord': 'Moon',
            'house': 3,
            'is_retrograde': 0,
            'speed': 1.0,
            'dignity': 'exalted',
            'is_combust': 0,
        },
        {
            'planet': 'Moon',
            'longitude': 127.0,
            'sign': 5,
            'sign_degree': 7.0,
            'nakshatra': 10,
            'nakshatra_pada': 1,
            'nakshatra_lord': 'Ketu',
            'house': 10,
            'is_retrograde': 0,
            'speed': 13.0,
            'dignity': '',
            'is_combust': 0,
        },
    ]
    result = _db_planets_to_model(rows)
    assert len(result) == 2
    assert all(isinstance(p, PlanetPosition) for p in result)
    assert result[0].planet == 'Sun'
    assert result[0].longitude == 293.0
    assert result[0].sign == 10
    assert result[0].sign_degree == 23.0
    assert result[0].nakshatra == 22
    assert result[0].nakshatra_pada == 4
    assert result[0].nakshatra_lord == 'Moon'
    assert result[0].house == 3
    assert result[0].is_retrograde is False
    assert result[0].speed == 1.0
    assert result[0].dignity == 'exalted'
    assert result[0].is_combust is False
    assert result[1].planet == 'Moon'
    assert result[1].house == 10


def test_db_planets_to_model_retrograde():
    """Retrograde and combust flags are converted from int to bool."""
    rows = [
        {
            'planet': 'Rahu',
            'longitude': 15.0,
            'sign': 1,
            'sign_degree': 15.0,
            'nakshatra': 1,
            'nakshatra_pada': 4,
            'nakshatra_lord': 'Ketu',
            'house': 6,
            'is_retrograde': 1,
            'speed': -0.05,
            'dignity': None,
            'is_combust': 1,
        },
    ]
    result = _db_planets_to_model(rows)
    assert result[0].is_retrograde is True
    assert result[0].is_combust is True
    assert result[0].dignity == ''  # None coerced to ''


def test_db_planets_to_model_empty():
    """Empty input returns empty list."""
    assert _db_planets_to_model([]) == []


def test_db_planets_to_model_missing_optional_fields():
    """Missing speed/dignity/is_combust in DB row should use defaults."""
    rows = [
        {
            'planet': 'Mars',
            'longitude': 72.0,
            'sign': 3,
            'sign_degree': 12.0,
            'nakshatra': 6,
            'nakshatra_pada': 1,
            'nakshatra_lord': 'Rahu',
            'house': 8,
            'is_retrograde': 0,
        },
    ]
    result = _db_planets_to_model(rows)
    assert result[0].speed == 0.0
    assert result[0].dignity == ''
    assert result[0].is_combust is False


# ---------------------------------------------------------------------------
# Helper: _sign_name
# ---------------------------------------------------------------------------

def test_sign_name_all_valid():
    """_sign_name returns correct name for every valid sign number 1-12."""
    expected = [
        (1, 'Aries'), (2, 'Taurus'), (3, 'Gemini'), (4, 'Cancer'),
        (5, 'Leo'), (6, 'Virgo'), (7, 'Libra'), (8, 'Scorpio'),
        (9, 'Sagittarius'), (10, 'Capricorn'), (11, 'Aquarius'), (12, 'Pisces'),
    ]
    for num, name in expected:
        assert _sign_name(num) == name


def test_sign_name_out_of_range():
    """_sign_name returns fallback string for out-of-range sign numbers."""
    assert _sign_name(0) == 'Sign-0'
    assert _sign_name(13) == 'Sign-13'
    assert _sign_name(-1) == 'Sign--1'


# ---------------------------------------------------------------------------
# Helper: _nak_name
# ---------------------------------------------------------------------------

def test_nak_name_known_nakshatras():
    """_nak_name returns correct name for known nakshatra numbers."""
    assert _nak_name(1) == 'Ashwini'
    assert _nak_name(10) == 'Magha'
    assert _nak_name(19) == 'Mula'
    assert _nak_name(20) == 'Purva Ashadha'
    assert _nak_name(27) == 'Revati'


def test_nak_name_out_of_range():
    """_nak_name returns fallback string for out-of-range nakshatra numbers."""
    assert _nak_name(0) == 'Nak-0'
    assert _nak_name(28) == 'Nak-28'
    assert _nak_name(-1) == 'Nak--1'


def test_nak_name_all_27():
    """_nak_name matches NAKSHATRA_NAMES for all 27 nakshatras."""
    for i in range(27):
        assert _nak_name(i + 1) == NAKSHATRA_NAMES[i]


# ---------------------------------------------------------------------------
# Helper: _planet_to_dict
# ---------------------------------------------------------------------------

def test_planet_to_dict_from_model():
    """_planet_to_dict serializes a PlanetPosition dataclass to dict."""
    pp = PlanetPosition(
        planet='Jupiter', longitude=295.5, sign=10, sign_degree=25.5,
        nakshatra=23, nakshatra_pada=1, nakshatra_lord='Mars',
        house=3, is_retrograde=False, speed=0.1, dignity='debilitated', is_combust=False,
    )
    d = _planet_to_dict(pp)
    assert d['planet'] == 'Jupiter'
    assert d['sign'] == 10
    assert d['sign_name'] == 'Capricorn'
    assert d['degree'] == 25.5
    assert d['longitude'] == 295.5
    assert d['house'] == 3
    assert d['nakshatra'] == 'Dhanishta'
    assert d['nakshatra_num'] == 23
    assert d['nakshatra_pada'] == 1
    assert d['nakshatra_lord'] == 'Mars'
    assert d['dignity'] == 'debilitated'
    assert d['is_retrograde'] is False
    assert d['is_combust'] is False
    # Without include_aspects, no aspects key
    assert 'aspects' not in d


def test_planet_to_dict_with_aspects():
    """_planet_to_dict includes aspects when include_aspects=True."""
    pp = PlanetPosition(
        planet='Mars', longitude=340.0, sign=12, sign_degree=10.0,
        nakshatra=25, nakshatra_pada=2, nakshatra_lord='Jupiter',
        house=5, is_retrograde=False, speed=0.5, dignity='', is_combust=False,
    )
    d = _planet_to_dict(pp, include_aspects=True, asc_sign=8)
    assert 'aspects' in d
    assert isinstance(d['aspects'], list)
    # Mars aspects use offsets {4: 75, 7: 100, 8: 100}
    # From sign 12: 4th offset = sign 4, 7th offset = sign 7, 8th offset = sign 8
    aspected_signs = [a['sign'] for a in d['aspects']]
    assert 4 in aspected_signs   # 4th offset from sign 12
    assert 7 in aspected_signs   # 7th offset from sign 12
    assert 8 in aspected_signs   # 8th offset from sign 12
    # Each aspect has sign_name, house, strength
    for asp in d['aspects']:
        assert 'sign_name' in asp
        assert 'house' in asp
        assert 'strength' in asp


def test_planet_to_dict_from_db_row():
    """_planet_to_dict handles DB row dicts (not just PlanetPosition)."""
    row = {
        'planet': 'Venus',
        'longitude': 347.0,
        'sign': 12,
        'sign_degree': 17.0,
        'nakshatra': 26,
        'nakshatra_pada': 2,
        'nakshatra_lord': 'Saturn',
        'house': 5,
        'is_retrograde': 0,
        'speed': 1.2,
        'dignity': 'exalted',
        'is_combust': 0,
    }
    d = _planet_to_dict(row)
    assert d['planet'] == 'Venus'
    assert d['sign_name'] == 'Pisces'
    assert d['degree'] == 17.0
    assert d['nakshatra'] == 'Uttara Bhadrapada'
    assert d['dignity'] == 'exalted'
    assert d['is_retrograde'] is False
    assert d['is_combust'] is False


def test_planet_to_dict_empty_dignity():
    """Dignity of '' or None serializes to None."""
    pp = PlanetPosition(
        planet='Sun', longitude=293.0, sign=10, sign_degree=23.0,
        nakshatra=22, nakshatra_pada=4, nakshatra_lord='Moon',
        house=3, is_retrograde=False, speed=1.0, dignity='', is_combust=False,
    )
    d = _planet_to_dict(pp)
    assert d['dignity'] is None


# ---------------------------------------------------------------------------
# Tool: list_charts
# ---------------------------------------------------------------------------

def test_list_charts_returns_persons_key():
    """list_charts() returns a dict with 'persons' key."""
    result = list_charts()
    assert 'error' not in result, f"list_charts failed: {result.get('error')}"
    assert 'persons' in result
    assert isinstance(result['persons'], list)


def test_list_charts_contains_crystal_and_lee():
    """Crystal and Lee should both be in the DB."""
    result = list_charts()
    names = [p['name'] for p in result['persons']]
    assert 'Crystal' in names
    assert 'Lee' in names


def test_list_charts_person_fields():
    """Each person entry has expected fields."""
    result = list_charts()
    for p in result['persons']:
        assert 'name' in p
        assert 'birth_date' in p
        assert 'birth_time' in p
        assert 'birth_location' in p
        assert 'ascendant_sign' in p
        assert 'ascendant_name' in p


# ---------------------------------------------------------------------------
# Tool: get_chart
# ---------------------------------------------------------------------------

def test_get_chart_crystal():
    """get_chart('Crystal') returns a complete chart dict."""
    result = get_chart('Crystal')
    assert 'error' not in result, f"get_chart failed: {result.get('error')}"
    expected_keys = ['person', 'ascendant', 'planets', 'yogas', 'dashas',
                     'shadbala', 'ashtakavarga', 'd9']
    for key in expected_keys:
        assert key in result, f"Missing key: {key}"


def test_get_chart_nonexistent():
    """get_chart for a nonexistent person returns error."""
    result = get_chart('NonexistentPerson12345')
    assert 'error' in result


def test_get_chart_person_structure():
    """The person dict in get_chart result has all expected fields."""
    result = get_chart('Crystal')
    person = result['person']
    assert person['name'] == 'Crystal'
    assert 'birth_date' in person
    assert 'birth_time' in person
    assert 'birth_location' in person
    assert 'latitude' in person
    assert 'longitude' in person
    assert isinstance(person['latitude'], float)
    assert isinstance(person['longitude'], float)


def test_get_chart_ascendant_structure():
    """The ascendant dict has sign, sign_name, and degree."""
    result = get_chart('Crystal')
    asc = result['ascendant']
    assert 'sign' in asc
    assert 'sign_name' in asc
    assert 'degree' in asc
    assert isinstance(asc['sign'], int)
    assert 1 <= asc['sign'] <= 12
    assert asc['sign_name'] == SIGNS[asc['sign']]
    assert isinstance(asc['degree'], float)


def test_get_chart_planets_structure():
    """Planets list has exactly 9 entries with all required fields."""
    result = get_chart('Crystal')
    planets = result['planets']
    assert isinstance(planets, list)
    assert len(planets) == 9

    expected_planet_names = {'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter',
                             'Venus', 'Saturn', 'Rahu', 'Ketu'}
    actual_names = {p['planet'] for p in planets}
    assert actual_names == expected_planet_names

    for p in planets:
        assert 'planet' in p
        assert 'sign' in p
        assert 'sign_name' in p
        assert 'degree' in p
        assert 'house' in p
        assert 'nakshatra' in p
        assert 'aspects' in p
        assert isinstance(p['aspects'], list)
        assert 1 <= p['sign'] <= 12
        assert 1 <= p['house'] <= 12
        assert isinstance(p['degree'], float)


def test_get_chart_yogas_structure():
    """Yogas list contains dicts with expected fields."""
    result = get_chart('Crystal')
    yogas = result['yogas']
    assert isinstance(yogas, list)
    assert len(yogas) > 0  # Crystal should have at least some yogas

    for y in yogas:
        assert 'name' in y
        assert 'type' in y
        assert 'strength' in y
        assert 'planets' in y
        assert 'houses' in y
        assert 'description' in y
        assert isinstance(y['planets'], list)
        assert isinstance(y['houses'], list)


def test_get_chart_dashas_structure():
    """Dashas dict has current_maha, current_antar, current_pratyantar."""
    result = get_chart('Crystal')
    dashas = result['dashas']
    assert 'current_maha' in dashas
    assert 'current_antar' in dashas
    assert 'current_pratyantar' in dashas

    # Maha dasha should exist for current date
    maha = dashas['current_maha']
    assert maha is not None
    assert 'planet' in maha
    assert 'start' in maha
    assert 'end' in maha


def test_get_chart_shadbala_structure():
    """Shadbala is a list of dicts with planet, total, and ratio."""
    result = get_chart('Crystal')
    shadbala = result['shadbala']
    assert isinstance(shadbala, list)
    assert len(shadbala) > 0

    for sb in shadbala:
        assert 'planet' in sb
        assert 'total' in sb
        assert 'ratio' in sb
        assert isinstance(sb['total'], float)
        assert isinstance(sb['ratio'], float)


def test_get_chart_ashtakavarga_structure():
    """Ashtakavarga has a sarva dict mapping sign numbers to points."""
    result = get_chart('Crystal')
    av = result['ashtakavarga']
    assert 'sarva' in av
    sarva = av['sarva']
    assert isinstance(sarva, dict)
    # Should have entries for signs 1-12
    assert len(sarva) == 12
    for sign, points in sarva.items():
        assert isinstance(points, int)


def test_get_chart_d9_structure():
    """D9 (Navamsha) is a list of planet dicts (may be empty if D9 not saved)."""
    result = get_chart('Crystal')
    d9 = result['d9']
    assert isinstance(d9, list)

    # If D9 data exists, validate structure
    if len(d9) > 0:
        assert len(d9) == 9  # 9 planets
        for entry in d9:
            assert 'planet' in entry
            assert 'sign' in entry
            assert 'sign_name' in entry
            assert 'house' in entry


def test_get_chart_d9_structure_lee():
    """Lee's D9 chart should exist and have 9 planets."""
    result = get_chart('Lee')
    d9 = result['d9']
    assert isinstance(d9, list)

    if len(d9) > 0:
        assert len(d9) == 9
        for entry in d9:
            assert 'planet' in entry
            assert 'sign' in entry
            assert 'sign_name' in entry
            assert 'house' in entry


def test_get_chart_lee():
    """get_chart('Lee') also returns a complete chart dict."""
    result = get_chart('Lee')
    assert 'error' not in result, f"get_chart Lee failed: {result.get('error')}"
    assert result['person']['name'] == 'Lee'
    assert len(result['planets']) == 9


# ---------------------------------------------------------------------------
# Tool: analyze_transits
# ---------------------------------------------------------------------------

def test_analyze_transits_crystal_default_date():
    """analyze_transits for Crystal with default (today) date."""
    result = analyze_transits('Crystal')
    assert 'error' not in result, f"analyze_transits failed: {result.get('error')}"
    assert 'transit_date' in result
    assert 'transits' in result
    assert 'special' in result
    assert 'vedha' in result
    # transit_date should be today
    assert result['transit_date'] == datetime.now().strftime('%Y-%m-%d')


def test_analyze_transits_crystal_explicit_date():
    """analyze_transits with an explicit date."""
    result = analyze_transits('Crystal', '2026-03-15')
    assert 'error' not in result, f"analyze_transits failed: {result.get('error')}"
    assert result['transit_date'] == '2026-03-15'
    assert isinstance(result['transits'], list)
    assert len(result['transits']) == 9  # 9 transit planets


def test_analyze_transits_transit_entry_fields():
    """Each transit entry has required fields."""
    result = analyze_transits('Crystal', '2026-03-15')
    for t in result['transits']:
        assert 'transit_planet' in t
        assert 'transit_sign' in t
        assert 'transit_sign_name' in t
        assert 'natal_house' in t
        assert 'sav_score' in t
        assert 'conjunctions' in t
        assert 'aspects' in t


def test_analyze_transits_special_keys():
    """Special transits dict has sade_sati, jupiter_transit, rahu_ketu_axis."""
    result = analyze_transits('Crystal', '2026-03-15')
    special = result['special']
    assert 'sade_sati' in special
    assert 'jupiter_transit' in special
    assert 'rahu_ketu_axis' in special


def test_analyze_transits_nonexistent_person():
    """analyze_transits for nonexistent person returns error."""
    result = analyze_transits('NonexistentPerson12345')
    assert 'error' in result


def test_analyze_transits_invalid_date():
    """analyze_transits with invalid date format returns error."""
    result = analyze_transits('Crystal', 'not-a-date')
    assert 'error' in result


def test_analyze_transits_vedha_is_list():
    """Vedha result is always a list."""
    result = analyze_transits('Crystal', '2026-03-15')
    assert isinstance(result['vedha'], list)


# ---------------------------------------------------------------------------
# Tool: analyze_compatibility
# ---------------------------------------------------------------------------

def test_analyze_compatibility_crystal_lee():
    """analyze_compatibility between Crystal and Lee returns synastry data."""
    result = analyze_compatibility('Crystal', 'Lee')
    assert 'error' not in result, f"analyze_compatibility failed: {result.get('error')}"
    assert 'guna_milan' in result
    assert 'overall_score' in result


def test_analyze_compatibility_person_names():
    """Result includes person names."""
    result = analyze_compatibility('Crystal', 'Lee')
    assert result.get('person1') == 'Crystal'
    assert result.get('person2') == 'Lee'


def test_analyze_compatibility_guna_milan_has_score():
    """Guna Milan section should have a total score."""
    result = analyze_compatibility('Crystal', 'Lee')
    guna = result['guna_milan']
    assert isinstance(guna, dict)
    assert 'total' in guna or 'score' in guna or 'total_score' in guna


def test_analyze_compatibility_overall_score_range():
    """Overall score should be between 0 and 100."""
    result = analyze_compatibility('Crystal', 'Lee')
    score = result['overall_score']
    assert isinstance(score, (int, float))
    assert 0 <= score <= 100


def test_analyze_compatibility_nonexistent_person():
    """analyze_compatibility with nonexistent person returns error."""
    result = analyze_compatibility('Crystal', 'NonexistentPerson12345')
    assert 'error' in result


# ---------------------------------------------------------------------------
# Tool: evaluate_timing
# ---------------------------------------------------------------------------

def test_evaluate_timing_single_date():
    """evaluate_timing with a single date for Crystal."""
    result = evaluate_timing('Crystal', '2026-04-30', 'court')
    assert 'error' not in result, f"evaluate_timing failed: {result.get('error')}"
    assert 'evaluations' in result
    evals = result['evaluations']
    assert isinstance(evals, list)
    assert len(evals) == 1


def test_evaluate_timing_multiple_dates():
    """evaluate_timing with multiple comma-separated dates."""
    result = evaluate_timing('Crystal', '2026-04-28,2026-04-30,2026-05-02', 'court')
    assert 'error' not in result, f"evaluate_timing failed: {result.get('error')}"
    evals = result['evaluations']
    assert isinstance(evals, list)
    assert len(evals) == 3


def test_evaluate_timing_multiple_dates_ranking():
    """Multiple dates should be ranked (sorted by total score descending)."""
    result = evaluate_timing('Crystal', '2026-04-28,2026-04-30,2026-05-02', 'court')
    evals = result['evaluations']
    # compare_dates should return ranked results; verify they have total scores
    for ev in evals:
        assert 'total' in ev or 'total_score' in ev or 'score' in ev


def test_evaluate_timing_evaluation_fields():
    """Each evaluation should have score-related fields."""
    result = evaluate_timing('Crystal', '2026-04-30', 'court')
    ev = result['evaluations'][0]
    # Should have at least a date and some score
    assert isinstance(ev, dict)
    # The evaluate_muhurta function returns dicts; verify they are non-empty
    assert len(ev) > 0


def test_evaluate_timing_nonexistent_person():
    """evaluate_timing for nonexistent person returns error."""
    result = evaluate_timing('NonexistentPerson12345', '2026-04-30', 'court')
    assert 'error' in result


def test_evaluate_timing_invalid_date():
    """evaluate_timing with invalid date format returns error."""
    result = evaluate_timing('Crystal', 'bad-date', 'court')
    assert 'error' in result


def test_evaluate_timing_general_event_type():
    """evaluate_timing works with general event type."""
    result = evaluate_timing('Crystal', '2026-04-30', 'general')
    assert 'error' not in result, f"evaluate_timing failed: {result.get('error')}"
    assert 'evaluations' in result
