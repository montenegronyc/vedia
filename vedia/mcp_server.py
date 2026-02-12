"""Vedia MCP Server — 6 tools for Vedic astrology via Claude.

Usage:
    python vedia/mcp_server.py          # stdio transport (for Claude Code)
    claude mcp add --transport stdio vedia -- python /path/to/vedia/mcp_server.py
"""

import json
import sys
import os
from datetime import datetime

# Ensure vedia package is importable when run as a script
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP

from vedia.db import (
    get_connection, init_db, save_person, save_chart, save_dasha_periods,
    save_yogas, save_ashtakavarga, save_shadbala,
    get_person_by_name, get_chart as db_get_chart, get_planet_positions,
    get_dasha_periods, get_yogas, get_all_persons, get_shadbala,
    get_ashtakavarga,
)
from vedia.models import SIGNS, NAKSHATRA_NAMES, ChartData, PlanetPosition, SIGN_LORDS
from vedia.geo import geocode_location, local_to_utc, get_utc_offset
from vedia.calc.ayanamsha import calculate_julian_day, get_ayanamsha_value, calculate_ascendant
from vedia.calc.ephemeris import calculate_planet_positions
from vedia.calc.dashas import calculate_full_dashas, get_current_dasha
from vedia.calc.yogas import detect_all_yogas
from vedia.calc.ashtakavarga import calculate_ashtakavarga
from vedia.calc.shadbala import calculate_shadbala
from vedia.calc.divisional import calculate_divisional_chart, get_divisional_sign
from vedia.calc.houses import get_aspects_with_strength
from vedia.calc.muhurta import evaluate_muhurta, compare_dates
from vedia.transit.current import get_current_positions
from vedia.transit.overlay import overlay_transits, get_transit_summary
from vedia.transit.vedha import analyze_all_vedha
from vedia.interpret.synastry import analyze_synastry

mcp = FastMCP("Vedia")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _db_planets_to_model(planet_rows: list[dict]) -> list[PlanetPosition]:
    """Convert DB planet dicts back into PlanetPosition dataclass instances."""
    return [
        PlanetPosition(
            planet=row['planet'],
            longitude=row['longitude'],
            sign=row['sign'],
            sign_degree=row['sign_degree'],
            nakshatra=row['nakshatra'],
            nakshatra_pada=row['nakshatra_pada'],
            nakshatra_lord=row['nakshatra_lord'],
            house=row['house'],
            is_retrograde=bool(row['is_retrograde']),
            speed=row.get('speed', 0.0) or 0.0,
            dignity=row.get('dignity', '') or '',
            is_combust=bool(row.get('is_combust', False)),
        )
        for row in planet_rows
    ]


def _sign_name(sign: int) -> str:
    return SIGNS[sign] if 1 <= sign <= 12 else f"Sign-{sign}"


def _nak_name(nak: int) -> str:
    return NAKSHATRA_NAMES[nak - 1] if 1 <= nak <= 27 else f"Nak-{nak}"


def _planet_to_dict(p, include_aspects: bool = False, asc_sign: int = 0) -> dict:
    """Serialize a PlanetPosition (dataclass or DB row) to dict."""
    if isinstance(p, PlanetPosition):
        d = {
            'planet': p.planet,
            'sign': p.sign,
            'sign_name': _sign_name(p.sign),
            'degree': round(p.sign_degree, 2),
            'longitude': round(p.longitude, 2),
            'house': p.house,
            'nakshatra': _nak_name(p.nakshatra),
            'nakshatra_num': p.nakshatra,
            'nakshatra_pada': p.nakshatra_pada,
            'nakshatra_lord': p.nakshatra_lord,
            'dignity': p.dignity or None,
            'is_retrograde': p.is_retrograde,
            'is_combust': p.is_combust,
        }
        if include_aspects:
            d['aspects'] = [
                {'sign': s, 'sign_name': _sign_name(s), 'house': ((s - asc_sign) % 12) + 1, 'strength': st}
                for s, st in get_aspects_with_strength(p.planet, p.sign)
            ]
        return d
    # DB row (dict)
    d = {
        'planet': p['planet'],
        'sign': p['sign'],
        'sign_name': _sign_name(p['sign']),
        'degree': round(p['sign_degree'], 2),
        'longitude': round(p['longitude'], 2),
        'house': p['house'],
        'nakshatra': _nak_name(p['nakshatra']),
        'nakshatra_num': p['nakshatra'],
        'nakshatra_pada': p['nakshatra_pada'],
        'nakshatra_lord': p['nakshatra_lord'],
        'dignity': p.get('dignity') or None,
        'is_retrograde': bool(p['is_retrograde']),
        'is_combust': bool(p.get('is_combust', False)),
    }
    if include_aspects:
        d['aspects'] = [
            {'sign': s, 'sign_name': _sign_name(s), 'house': ((s - asc_sign) % 12) + 1, 'strength': st}
            for s, st in get_aspects_with_strength(p['planet'], p['sign'])
        ]
    return d


def _find_current_dashas(conn, person_id: int, target_dt: datetime = None) -> dict:
    """Find current maha/antar/pratyantar dasha periods."""
    now_str = (target_dt or datetime.now()).isoformat()
    maha_rows = get_dasha_periods(conn, person_id, level='maha')
    antar_rows = get_dasha_periods(conn, person_id, level='antar')
    pratyantar_rows = get_dasha_periods(conn, person_id, level='pratyantar')

    result = {'current_maha': None, 'current_antar': None, 'current_pratyantar': None}

    for m in maha_rows:
        if m['start_date'] <= now_str <= m['end_date']:
            result['current_maha'] = {
                'planet': m['planet'],
                'start': m['start_date'][:10],
                'end': m['end_date'][:10],
            }
            # Find antar
            for a in antar_rows:
                if a['parent_id'] == m['id'] and a['start_date'] <= now_str <= a['end_date']:
                    result['current_antar'] = {
                        'planet': a['planet'],
                        'start': a['start_date'][:10],
                        'end': a['end_date'][:10],
                    }
                    # Find pratyantar
                    for p in pratyantar_rows:
                        if p['parent_id'] == a['id'] and p['start_date'] <= now_str <= p['end_date']:
                            result['current_pratyantar'] = {
                                'planet': p['planet'],
                                'start': p['start_date'][:10],
                                'end': p['end_date'][:10],
                            }
                            break
                    break
            break

    return result


def _build_chart_payload(conn, person: dict, chart: dict, planet_rows: list[dict]) -> dict:
    """Build the fat chart payload dict shared by calculate_chart and get_chart."""
    asc_sign = chart['ascendant_sign']
    chart_id = chart['id']

    # Planets with aspects
    planets = [_planet_to_dict(row, include_aspects=True, asc_sign=asc_sign) for row in planet_rows]

    # Yogas
    yogas_rows = get_yogas(conn, chart_id)
    yogas = []
    for y in yogas_rows:
        try:
            pi = json.loads(y['planets_involved']) if isinstance(y['planets_involved'], str) else y['planets_involved']
        except (json.JSONDecodeError, TypeError):
            pi = [str(y['planets_involved'])]
        try:
            hi = json.loads(y['houses_involved']) if isinstance(y['houses_involved'], str) else y['houses_involved']
        except (json.JSONDecodeError, TypeError):
            hi = [str(y['houses_involved'])]
        yogas.append({
            'name': y['yoga_name'],
            'type': y['yoga_type'],
            'strength': y.get('strength', 'moderate'),
            'planets': pi,
            'houses': hi,
            'description': y['description'],
        })

    # Current dashas
    dashas = _find_current_dashas(conn, person['id'])

    # Shadbala
    shadbala_rows = get_shadbala(conn, chart_id)
    shadbala = [
        {
            'planet': sb['planet'],
            'total': round(sb['total_shadbala'], 1),
            'ratio': round(sb['shadbala_ratio'], 2),
            'sthana': round(sb['sthana_bala'], 1),
            'dig': round(sb['dig_bala'], 1),
            'kala': round(sb['kala_bala'], 1),
            'chesta': round(sb['chesta_bala'], 1),
            'naisargika': round(sb['naisargika_bala'], 1),
            'drik': round(sb['drik_bala'], 1),
        }
        for sb in shadbala_rows
    ]

    # Sarvashtakavarga
    sarva_rows = get_ashtakavarga(conn, chart_id, 'sarva')
    sarva = {row['sign']: row['points'] for row in sarva_rows}

    # D9 chart
    d9_chart = db_get_chart(conn, person['id'], chart_type='D9')
    d9 = []
    if d9_chart:
        d9_planet_rows = get_planet_positions(conn, d9_chart['id'])
        d9 = [
            {
                'planet': row['planet'],
                'sign': row['sign'],
                'sign_name': _sign_name(row['sign']),
                'house': row['house'],
            }
            for row in d9_planet_rows
        ]

    return {
        'person': {
            'name': person['name'],
            'birth_date': person['birth_date'],
            'birth_time': person['birth_time'],
            'birth_timezone': person['birth_timezone'],
            'birth_location': person['birth_location'],
            'latitude': person['latitude'],
            'longitude': person['longitude'],
        },
        'ascendant': {
            'sign': asc_sign,
            'sign_name': _sign_name(asc_sign),
            'degree': round(chart['ascendant_degree'], 2),
        },
        'planets': planets,
        'yogas': yogas,
        'dashas': dashas,
        'shadbala': shadbala,
        'ashtakavarga': {'sarva': sarva},
        'd9': d9,
    }


def _load_person_and_chart(conn, name: str):
    """Load person + D1 chart + planets from DB. Returns (person, chart, planet_rows) or raises."""
    person = get_person_by_name(conn, name)
    if person is None:
        return None, None, None
    chart = db_get_chart(conn, person['id'])
    if chart is None:
        return person, None, None
    planet_rows = get_planet_positions(conn, chart['id'])
    return person, chart, planet_rows


# ---------------------------------------------------------------------------
# Tool 1: calculate_chart
# ---------------------------------------------------------------------------

@mcp.tool()
def calculate_chart(name: str, birth_date: str, birth_time: str, birth_location: str) -> dict:
    """Calculate a complete Vedic birth chart. Runs the full pipeline: geocode, ephemeris,
    houses, nakshatras, yogas, dashas, ashtakavarga, shadbala, D9, and saves to DB.
    birth_date: YYYY-MM-DD, birth_time: HH:MM or HH:MM:SS (24h), birth_location: city/country string.
    Returns the complete chart data including planets, yogas, dashas, shadbala, ashtakavarga, and D9."""
    try:
        # Step 1: Geocode
        geo = geocode_location(birth_location)
        lat, lon, tz_str = geo.latitude, geo.longitude, geo.timezone

        # Step 2: Parse date/time
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                dt_parts = datetime.strptime(f"{birth_date} {birth_time}", fmt)
                break
            except ValueError:
                continue
        else:
            return {"error": "Invalid date/time format. Use YYYY-MM-DD and HH:MM:SS or HH:MM."}

        utc_offset = get_utc_offset(tz_str, dt_parts)
        utc_dt = local_to_utc(
            dt_parts.year, dt_parts.month, dt_parts.day,
            dt_parts.hour, dt_parts.minute, dt_parts.second,
            tz_str,
        )

        # Step 3: Julian Day
        hour_decimal = dt_parts.hour + dt_parts.minute / 60.0 + dt_parts.second / 3600.0
        jd = calculate_julian_day(dt_parts.year, dt_parts.month, dt_parts.day, hour_decimal, utc_offset)

        # Step 4: Ayanamsha + Ascendant
        ayanamsha_val = get_ayanamsha_value(jd)
        asc_longitude, sidereal_time = calculate_ascendant(jd, lat, lon)
        asc_sign = int(asc_longitude / 30) + 1
        asc_degree = asc_longitude % 30

        # Step 5: Planet positions
        planet_positions = calculate_planet_positions(jd, asc_sign)

        # Step 6: Build ChartData
        chart_data = ChartData(
            person_name=name,
            birth_date=birth_date,
            birth_time=birth_time,
            birth_timezone=tz_str,
            birth_location=birth_location,
            latitude=lat,
            longitude=lon,
            chart_type='D1',
            ayanamsha='lahiri',
            ayanamsha_value=ayanamsha_val,
            ascendant_sign=asc_sign,
            ascendant_degree=asc_degree,
            julian_day=jd,
            sidereal_time=sidereal_time,
            planets=planet_positions,
        )

        # Step 7: Dashas
        moon_pos = next((p for p in planet_positions if p.planet == 'Moon'), None)
        if moon_pos is None:
            return {"error": "Moon position not found in calculations."}
        dashas = calculate_full_dashas(moon_pos.longitude, dt_parts)

        # Step 8: Yogas
        yogas = detect_all_yogas(planet_positions, asc_sign)

        # Step 9: Ashtakavarga
        bhinna, sarva = calculate_ashtakavarga(planet_positions, asc_sign)

        # Step 10: Shadbala
        shadbala_results = calculate_shadbala(planet_positions, jd)

        # Step 11: Save to DB
        conn = get_connection()
        init_db(conn)
        person_id = save_person(conn, name, birth_date, birth_time, tz_str, birth_location, lat, lon)
        chart_id = save_chart(conn, person_id, chart_data)

        # Save D9
        d9_planets = calculate_divisional_chart(planet_positions, 'D9', asc_sign, asc_degree)
        d9_asc_sign = get_divisional_sign(asc_sign, asc_degree, 'D9')
        d9_chart_data = ChartData(
            person_name=name,
            birth_date=birth_date,
            birth_time=birth_time,
            birth_timezone=tz_str,
            birth_location=birth_location,
            latitude=lat,
            longitude=lon,
            chart_type='D9',
            ayanamsha='lahiri',
            ayanamsha_value=ayanamsha_val,
            ascendant_sign=d9_asc_sign,
            ascendant_degree=asc_degree,
            julian_day=jd,
            sidereal_time=sidereal_time,
            planets=d9_planets,
        )
        save_chart(conn, person_id, d9_chart_data)
        save_dasha_periods(conn, person_id, dashas)
        save_yogas(conn, chart_id, yogas)
        save_ashtakavarga(conn, chart_id, bhinna, sarva)
        save_shadbala(conn, chart_id, shadbala_results)

        # Step 12: Return fat payload
        person = get_person_by_name(conn, name)
        chart = db_get_chart(conn, person['id'])
        planet_rows = get_planet_positions(conn, chart['id'])
        result = _build_chart_payload(conn, person, chart, planet_rows)
        conn.close()
        return result

    except (ValueError, ConnectionError) as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Chart calculation failed: {e}"}


# ---------------------------------------------------------------------------
# Tool 2: get_chart
# ---------------------------------------------------------------------------

@mcp.tool()
def get_chart(name: str) -> dict:
    """Load a previously calculated Vedic birth chart from the database.
    Returns complete chart data: planets with signs/houses/nakshatras/dignity/aspects,
    all yogas, current maha/antar/pratyantar dashas, shadbala scores,
    sarvashtakavarga, and D9 (Navamsha) positions."""
    try:
        conn = get_connection()
        init_db(conn)
        person, chart, planet_rows = _load_person_and_chart(conn, name)
        if person is None:
            conn.close()
            return {"error": f"No person found matching '{name}'. Use list_charts to see available charts."}
        if chart is None:
            conn.close()
            return {"error": f"No chart found for '{person['name']}'. Use calculate_chart to create one."}

        result = _build_chart_payload(conn, person, chart, planet_rows)
        conn.close()
        return result

    except Exception as e:
        return {"error": f"Failed to load chart: {e}"}


# ---------------------------------------------------------------------------
# Tool 3: analyze_transits
# ---------------------------------------------------------------------------

@mcp.tool()
def analyze_transits(name: str, date: str = "") -> dict:
    """Analyze planetary transits overlaid on a natal chart.
    date: YYYY-MM-DD (default: today). Returns transit positions, natal house placements,
    conjunctions, aspects, SAV scores per transit sign, vedha obstructions,
    Sade Sati status, Jupiter transit analysis, and Rahu-Ketu axis."""
    try:
        conn = get_connection()
        init_db(conn)
        person, chart, planet_rows = _load_person_and_chart(conn, name)
        if person is None:
            conn.close()
            return {"error": f"No person found matching '{name}'."}
        if chart is None:
            conn.close()
            return {"error": f"No chart found for '{person['name']}'."}

        natal_planets = _db_planets_to_model(planet_rows)
        asc_sign = chart['ascendant_sign']

        # Calculate transit positions
        if date:
            try:
                target_dt = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                conn.close()
                return {"error": "Invalid date format. Use YYYY-MM-DD."}
            jd = calculate_julian_day(target_dt.year, target_dt.month, target_dt.day, 12.0, 0.0)
            transit_planets = calculate_planet_positions(jd, asc_sign)
            transit_date = date
        else:
            transit_planets = get_current_positions()
            transit_date = datetime.now().strftime('%Y-%m-%d')

        # Overlay
        overlay = overlay_transits(natal_planets, transit_planets, asc_sign)
        summary = get_transit_summary(natal_planets, transit_planets, asc_sign)

        # Vedha
        natal_moon_sign = None
        for p in natal_planets:
            if p.planet == 'Moon':
                natal_moon_sign = p.sign
                break
        vedha = []
        if natal_moon_sign is not None:
            vedha = analyze_all_vedha(transit_planets, natal_moon_sign)

        # SAV scores per transit sign
        sarva_rows = get_ashtakavarga(conn, chart['id'], 'sarva')
        sav_by_sign = {row['sign']: row['points'] for row in sarva_rows}

        conn.close()

        # Build transit entries
        transits = []
        for entry in overlay:
            t = {
                'transit_planet': entry['transit_planet'],
                'transit_sign': entry['transit_sign'],
                'transit_sign_name': _sign_name(entry['transit_sign']),
                'natal_house': entry['natal_house'],
                'sav_score': sav_by_sign.get(entry['transit_sign']),
                'conjunctions': entry.get('conjunctions', []),
                'aspects': entry.get('aspects', []),
            }
            transits.append(t)

        # Extract special transits from summary
        special = summary.get('_special', {})

        return {
            'transit_date': transit_date,
            'transits': transits,
            'special': {
                'sade_sati': special.get('sade_sati', {}),
                'jupiter_transit': special.get('jupiter_transit', {}),
                'rahu_ketu_axis': special.get('rahu_ketu_axis', {}),
            },
            'vedha': vedha,
        }

    except Exception as e:
        return {"error": f"Transit analysis failed: {e}"}


# ---------------------------------------------------------------------------
# Tool 4: analyze_compatibility
# ---------------------------------------------------------------------------

@mcp.tool()
def analyze_compatibility(name1: str, name2: str) -> dict:
    """Full synastry/compatibility analysis between two saved persons.
    Returns Guna Milan (Ashtakoot) 36-point breakdown, Venus axis analysis,
    7th lord exchange, ascendant compatibility, Mangal Dosha comparison,
    overall score (0-100), and assessment."""
    try:
        conn = get_connection()
        init_db(conn)

        person1, chart1, planet_rows1 = _load_person_and_chart(conn, name1)
        if person1 is None:
            conn.close()
            return {"error": f"No person found matching '{name1}'."}
        if chart1 is None:
            conn.close()
            return {"error": f"No chart found for '{person1['name']}'."}

        person2, chart2, planet_rows2 = _load_person_and_chart(conn, name2)
        if person2 is None:
            conn.close()
            return {"error": f"No person found matching '{name2}'."}
        if chart2 is None:
            conn.close()
            return {"error": f"No chart found for '{person2['name']}'."}

        conn.close()

        planets1 = _db_planets_to_model(planet_rows1)
        planets2 = _db_planets_to_model(planet_rows2)
        asc1 = chart1['ascendant_sign']
        asc2 = chart2['ascendant_sign']

        moon1 = next((p for p in planets1 if p.planet == 'Moon'), None)
        moon2 = next((p for p in planets2 if p.planet == 'Moon'), None)
        if moon1 is None or moon2 is None:
            return {"error": "Moon position missing from one or both charts."}

        result = analyze_synastry(
            person1_planets=planets1,
            person1_asc_sign=asc1,
            person1_moon_nakshatra=moon1.nakshatra,
            person2_planets=planets2,
            person2_asc_sign=asc2,
            person2_moon_nakshatra=moon2.nakshatra,
        )

        result['person1'] = person1['name']
        result['person2'] = person2['name']
        return result

    except Exception as e:
        return {"error": f"Compatibility analysis failed: {e}"}


# ---------------------------------------------------------------------------
# Tool 5: evaluate_timing
# ---------------------------------------------------------------------------

@mcp.tool()
def evaluate_timing(name: str, dates: str, event_type: str = "general") -> dict:
    """Muhurta: evaluate one or more dates for auspiciousness.
    dates: comma-separated YYYY-MM-DD (e.g. '2026-04-30' or '2026-04-28,2026-04-30,2026-05-02').
    event_type: general, court, business, travel, ceremony, medical.
    Returns per-date scores (gochara, vara, nakshatra, transits, SAV), total auspiciousness,
    factors, and recommendations. Multiple dates are ranked best-first."""
    try:
        conn = get_connection()
        init_db(conn)
        person, chart, planet_rows = _load_person_and_chart(conn, name)
        if person is None:
            conn.close()
            return {"error": f"No person found matching '{name}'."}
        if chart is None:
            conn.close()
            return {"error": f"No chart found for '{person['name']}'."}

        natal_planets = _db_planets_to_model(planet_rows)
        natal_asc_sign = chart['ascendant_sign']

        # Find natal Moon sign
        natal_moon_sign = None
        for p in natal_planets:
            if p.planet == 'Moon':
                natal_moon_sign = p.sign
                break
        if natal_moon_sign is None:
            conn.close()
            return {"error": "Natal Moon not found in chart data."}

        # Parse dates
        date_list = [d.strip() for d in dates.split(',') if d.strip()]
        if not date_list:
            conn.close()
            return {"error": "No dates provided. Use comma-separated YYYY-MM-DD."}

        parsed_dates = []
        for d in date_list:
            try:
                parsed_dates.append(datetime.strptime(d, '%Y-%m-%d'))
            except ValueError:
                conn.close()
                return {"error": f"Invalid date format: '{d}'. Use YYYY-MM-DD."}

        # Get dasha lord for each date
        maha_rows = get_dasha_periods(conn, person['id'], level='maha')

        # Get shadbala and SAV
        shadbala_rows = get_shadbala(conn, chart['id'])
        sarva_rows = get_ashtakavarga(conn, chart['id'], 'sarva')
        sarvashtakavarga = {row['sign']: row['points'] for row in sarva_rows} if sarva_rows else None

        conn.close()

        # Build transit data for each date
        transit_data = []
        for target_dt in parsed_dates:
            jd = calculate_julian_day(target_dt.year, target_dt.month, target_dt.day, 12.0, 0.0)
            transit_planets = calculate_planet_positions(jd, natal_asc_sign)
            transit_data.append((target_dt, transit_planets))

        # Find dasha lord for first date (used for all evaluations)
        dasha_lord = None
        if maha_rows and parsed_dates:
            target_str = parsed_dates[0].isoformat()
            for m in maha_rows:
                if m['start_date'] <= target_str <= m['end_date']:
                    dasha_lord = m['planet']
                    break

        kwargs = {
            'dasha_lord': dasha_lord,
            'shadbala': shadbala_rows if shadbala_rows else None,
            'sarvashtakavarga': sarvashtakavarga,
        }

        if len(transit_data) == 1:
            result = evaluate_muhurta(
                natal_planets=natal_planets,
                natal_asc_sign=natal_asc_sign,
                natal_moon_sign=natal_moon_sign,
                transit_planets=transit_data[0][1],
                target_date=transit_data[0][0],
                event_type=event_type,
                **kwargs,
            )
            return {'evaluations': [result]}
        else:
            results = compare_dates(
                natal_planets=natal_planets,
                natal_asc_sign=natal_asc_sign,
                natal_moon_sign=natal_moon_sign,
                transit_data=transit_data,
                event_type=event_type,
                **kwargs,
            )
            return {'evaluations': results}

    except Exception as e:
        return {"error": f"Timing evaluation failed: {e}"}


# ---------------------------------------------------------------------------
# Tool 6: list_charts
# ---------------------------------------------------------------------------

@mcp.tool()
def list_charts() -> dict:
    """List all saved persons with birth data and ascendant sign.
    Use this to see who has charts in the database before calling get_chart."""
    try:
        conn = get_connection()
        init_db(conn)
        persons = get_all_persons(conn)

        result = []
        for p in persons:
            entry = {
                'name': p['name'],
                'birth_date': p['birth_date'],
                'birth_time': p['birth_time'],
                'birth_location': p['birth_location'],
            }
            chart = db_get_chart(conn, p['id'])
            if chart:
                entry['ascendant_sign'] = chart['ascendant_sign']
                entry['ascendant_name'] = _sign_name(chart['ascendant_sign'])
            result.append(entry)

        conn.close()
        return {'persons': result}

    except Exception as e:
        return {"error": f"Failed to list charts: {e}"}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
