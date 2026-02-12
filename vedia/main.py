"""CLI entry point for Vedia -- Vedic astrology engine.

Usage:
    python -m vedia new --name "Crystal" --date 1985-02-06 --time 03:45:00 --location "Detroit, Michigan"
    python -m vedia chart "Crystal"
    python -m vedia transit "Crystal"
    python -m vedia dasha "Crystal"
    python -m vedia ask "Crystal" "How is my career looking?"
    python -m vedia list
"""

import argparse
import json
import sys
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich import box

from .db import (
    get_connection, init_db, save_person, save_chart, save_dasha_periods,
    save_yogas, save_ashtakavarga, save_shadbala, save_reading,
    get_person_by_name, get_chart, get_planet_positions, get_dasha_periods,
    get_yogas, get_all_persons, get_shadbala, get_ashtakavarga,
)
from .models import SIGNS, NAKSHATRA_NAMES, ChartData, PlanetPosition, SIGN_LORDS
from .calc.houses import get_aspects

try:
    from .geo import geocode_location, local_to_utc, get_utc_offset, format_location_info
except ImportError:
    geocode_location = None

try:
    from .calc.ayanamsha import calculate_julian_day, get_ayanamsha_value, calculate_ascendant
except ImportError:
    calculate_julian_day = None

try:
    from .calc.ephemeris import calculate_planet_positions
except ImportError:
    calculate_planet_positions = None

try:
    from .calc.dashas import calculate_full_dashas, get_current_dasha
except ImportError:
    calculate_full_dashas = None
    get_current_dasha = None

try:
    from .calc.yogas import detect_all_yogas
except ImportError:
    detect_all_yogas = None

try:
    from .calc.ashtakavarga import calculate_ashtakavarga
except ImportError:
    calculate_ashtakavarga = None

try:
    from .calc.shadbala import calculate_shadbala
except ImportError:
    calculate_shadbala = None

try:
    from .calc.divisional import calculate_divisional_chart, get_divisional_sign
except ImportError:
    calculate_divisional_chart = None
    get_divisional_sign = None

try:
    from .transit.current import get_current_positions
except ImportError:
    get_current_positions = None

try:
    from .transit.overlay import overlay_transits, get_transit_summary
except ImportError:
    overlay_transits = None
    get_transit_summary = None

try:
    from .transit.vedha import analyze_all_vedha
except ImportError:
    analyze_all_vedha = None

try:
    from .interpret.synastry import analyze_synastry
except ImportError:
    analyze_synastry = None

try:
    from .calc.muhurta import evaluate_muhurta, compare_dates
except ImportError:
    evaluate_muhurta = None


console = Console()

# ---------------------------------------------------------------------------
# Planet display colors
# ---------------------------------------------------------------------------
PLANET_COLORS = {
    'Sun': 'gold1',
    'Moon': 'grey82',
    'Mars': 'red',
    'Mercury': 'green',
    'Jupiter': 'yellow',
    'Venus': 'magenta',
    'Saturn': 'blue',
    'Rahu': 'grey50',
    'Ketu': 'grey50',
}

# Strength/yoga type styling
STRENGTH_COLORS = {
    'strong': 'bold green',
    'moderate': 'yellow',
    'weak': 'dim',
}

YOGA_TYPE_COLORS = {
    'benefic': 'green',
    'dosha': 'red',
    'transit_dosha': 'dark_orange',
}

# Dignity styling
DIGNITY_COLORS = {
    'exalted': 'bold green',
    'moolatrikona': 'green',
    'own': 'cyan',
    'friendly': 'blue',
    'neutral': 'white',
    'enemy': 'dark_orange',
    'debilitated': 'bold red',
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def format_degree(deg: float) -> str:
    """Format a degree value as DD*MM' (e.g. 15*23')."""
    d = int(deg)
    m = int((deg - d) * 60)
    return f"{d}\u00b0{m:02d}'"


def format_sign_degree(sign: int, degree: float) -> str:
    """Format as 'DD*MM' SignName' (e.g. 15*23' Taurus)."""
    sign_name = SIGNS[sign] if 1 <= sign <= 12 else f"Sign-{sign}"
    return f"{format_degree(degree)} {sign_name}"


def _colored_planet(name: str) -> Text:
    """Return a rich Text object with the planet name colored."""
    color = PLANET_COLORS.get(name, 'white')
    return Text(name, style=color)


def _colored_planet_str(name: str) -> str:
    """Return a rich markup string for the planet name."""
    color = PLANET_COLORS.get(name, 'white')
    return f"[{color}]{name}[/{color}]"


def _load_person(name: str, conn):
    """Load a person from the database by name. Exit with error if not found."""
    person = get_person_by_name(conn, name)
    if person is None:
        console.print(f"[red]Error:[/red] No person found matching '{name}'")
        console.print("Run [cyan]python -m vedia list[/cyan] to see stored charts.")
        sys.exit(1)
    return person


def _load_chart_data(person_id: int, conn):
    """Load chart + planet positions from DB. Exit with error if missing."""
    chart = get_chart(conn, person_id)
    if chart is None:
        console.print("[red]Error:[/red] No chart found for this person.")
        console.print("Run [cyan]python -m vedia new ...[/cyan] to create a chart first.")
        sys.exit(1)
    planets = get_planet_positions(conn, chart['id'])
    return chart, planets


def _db_planets_to_model(planet_rows: list[dict]) -> list[PlanetPosition]:
    """Convert DB planet dicts back into PlanetPosition dataclass instances."""
    positions = []
    for row in planet_rows:
        positions.append(PlanetPosition(
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
        ))
    return positions


# ---------------------------------------------------------------------------
# Command: new
# ---------------------------------------------------------------------------

def cmd_new(args):
    """Create a new birth chart and save to database."""
    # Validate required modules
    for mod_name, mod in [('geo', geocode_location), ('ayanamsha', calculate_julian_day),
                          ('ephemeris', calculate_planet_positions), ('dashas', calculate_full_dashas),
                          ('yogas', detect_all_yogas), ('ashtakavarga', calculate_ashtakavarga),
                          ('shadbala', calculate_shadbala)]:
        if mod is None:
            console.print(f"[red]Error:[/red] Required module '{mod_name}' is not available.")
            sys.exit(1)

    name = args.name
    date_str = args.date
    time_str = args.time
    location = args.location

    console.print()
    console.print(Panel(
        f"[bold]Creating chart for [cyan]{name}[/cyan][/bold]\n"
        f"Born: {date_str} at {time_str}\n"
        f"Location: {location}",
        title="[bold gold1]Vedia[/bold gold1]",
        border_style="gold1",
    ))

    # Step 1: Geocode the location
    with console.status("[bold cyan]Geocoding location..."):
        try:
            geo = geocode_location(location)
        except (ValueError, ConnectionError) as e:
            console.print(f"[red]Geocoding error:[/red] {e}")
            sys.exit(1)

    lat, lon, tz_str = geo.latitude, geo.longitude, geo.timezone
    location_info = format_location_info(location, lat, lon, tz_str)
    console.print(f"  [dim]Location resolved:[/dim] {location_info}")

    # Step 2: Parse birth date/time and convert to UTC
    try:
        dt_parts = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            dt_parts = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            console.print("[red]Error:[/red] Invalid date/time format. Use YYYY-MM-DD and HH:MM:SS or HH:MM.")
            sys.exit(1)

    utc_offset = get_utc_offset(tz_str, dt_parts)
    utc_dt = local_to_utc(
        dt_parts.year, dt_parts.month, dt_parts.day,
        dt_parts.hour, dt_parts.minute, dt_parts.second,
        tz_str,
    )
    console.print(f"  [dim]UTC offset:[/dim] {utc_offset:+.1f}h  |  [dim]UTC time:[/dim] {utc_dt.strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 3: Calculate Julian Day
    hour_decimal = dt_parts.hour + dt_parts.minute / 60.0 + dt_parts.second / 3600.0
    jd = calculate_julian_day(dt_parts.year, dt_parts.month, dt_parts.day, hour_decimal, utc_offset)
    console.print(f"  [dim]Julian Day:[/dim] {jd:.6f}")

    # Step 4: Calculate ayanamsha and ascendant
    ayanamsha_val = get_ayanamsha_value(jd)
    asc_longitude, sidereal_time = calculate_ascendant(jd, lat, lon)
    asc_sign = int(asc_longitude / 30) + 1
    asc_degree = asc_longitude % 30
    console.print(f"  [dim]Ayanamsha (Lahiri):[/dim] {format_degree(ayanamsha_val)}")
    console.print(f"  [dim]Ascendant:[/dim] {format_sign_degree(asc_sign, asc_degree)}")

    # Step 5: Calculate planet positions
    with console.status("[bold cyan]Calculating planetary positions..."):
        planet_positions = calculate_planet_positions(jd, asc_sign)

    # Step 6: Build ChartData
    chart_data = ChartData(
        person_name=name,
        birth_date=date_str,
        birth_time=time_str,
        birth_timezone=tz_str,
        birth_location=location,
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

    # Step 7: Calculate dashas from Moon position
    moon_pos = next((p for p in planet_positions if p.planet == 'Moon'), None)
    if moon_pos is None:
        console.print("[red]Error:[/red] Moon position not found in calculations.")
        sys.exit(1)

    with console.status("[bold cyan]Computing Vimshottari dashas..."):
        dashas = calculate_full_dashas(moon_pos.longitude, dt_parts)

    # Step 8: Calculate yogas
    with console.status("[bold cyan]Detecting yogas..."):
        yogas = detect_all_yogas(planet_positions, asc_sign)

    # Step 9: Calculate ashtakavarga
    with console.status("[bold cyan]Computing Ashtakavarga..."):
        bhinna, sarva = calculate_ashtakavarga(planet_positions, asc_sign)

    # Step 10: Calculate shadbala
    with console.status("[bold cyan]Computing Shadbala..."):
        shadbala_results = calculate_shadbala(planet_positions, jd)

    # Step 11: Save everything to database
    with console.status("[bold cyan]Saving to database..."):
        conn = get_connection()
        init_db(conn)
        person_id = save_person(conn, name, date_str, time_str, tz_str, location, lat, lon)
        chart_id = save_chart(conn, person_id, chart_data)

        # Save D9 (Navamsha) chart
        if calculate_divisional_chart is not None:
            d9_planets = calculate_divisional_chart(planet_positions, 'D9', asc_sign, asc_degree)
            d9_chart_data = ChartData(
                person_name=name,
                birth_date=date_str,
                birth_time=time_str,
                birth_timezone=tz_str,
                birth_location=location,
                latitude=lat,
                longitude=lon,
                chart_type='D9',
                ayanamsha='lahiri',
                ayanamsha_value=ayanamsha_val,
                ascendant_sign=get_divisional_sign(asc_sign, asc_degree, 'D9'),
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
        conn.close()

    # Step 12: Display summary
    console.print()

    # Quick planet summary table
    summary_table = Table(
        title="Planetary Positions",
        box=box.ROUNDED,
        border_style="gold1",
        header_style="bold white",
        show_lines=False,
    )
    summary_table.add_column("Planet", style="bold", min_width=8)
    summary_table.add_column("Sign", min_width=12)
    summary_table.add_column("Degree", justify="right")
    summary_table.add_column("Nakshatra")
    summary_table.add_column("House", justify="center")

    for p in planet_positions:
        color = PLANET_COLORS.get(p.planet, 'white')
        sign_name = SIGNS[p.sign] if 1 <= p.sign <= 12 else '?'
        nak_name = NAKSHATRA_NAMES[p.nakshatra - 1] if 1 <= p.nakshatra <= 27 else '?'
        retro = " (R)" if p.is_retrograde else ""
        summary_table.add_row(
            f"[{color}]{p.planet}[/{color}]",
            sign_name,
            format_degree(p.sign_degree),
            f"{nak_name} P{p.nakshatra_pada}",
            str(p.house),
        )

    console.print(summary_table)

    # Yoga count summary
    if yogas:
        benefic_count = sum(1 for y in yogas if y.yoga_type == 'benefic')
        dosha_count = sum(1 for y in yogas if y.yoga_type in ('dosha', 'transit_dosha'))
        console.print(
            f"\n  [green]{benefic_count} benefic yoga(s)[/green] and "
            f"[red]{dosha_count} dosha(s)[/red] detected."
        )

    console.print(
        f"\n[bold green]Chart saved successfully.[/bold green] "
        f"Use [cyan]python -m vedia chart \"{name}\"[/cyan] to view the full chart."
    )
    console.print()


# ---------------------------------------------------------------------------
# Command: chart
# ---------------------------------------------------------------------------

def cmd_chart(args):
    """Display a birth chart with full detail."""
    conn = get_connection()
    init_db(conn)
    person = _load_person(args.name, conn)
    chart, planet_rows = _load_chart_data(person['id'], conn)
    yogas_rows = get_yogas(conn, chart['id'])
    shadbala_rows = get_shadbala(conn, chart['id'])
    conn.close()

    # Header panel
    asc_sign = chart['ascendant_sign']
    asc_degree = chart['ascendant_degree']
    asc_name = SIGNS[asc_sign] if 1 <= asc_sign <= 12 else '?'

    header_text = (
        f"[bold cyan]{person['name']}[/bold cyan]\n"
        f"Born: {person['birth_date']} at {person['birth_time']}\n"
        f"Location: {person['birth_location']}\n"
        f"Coordinates: {person['latitude']:.4f}, {person['longitude']:.4f}  |  "
        f"TZ: {person['birth_timezone']}\n"
        f"Ayanamsha (Lahiri): {format_degree(chart['ayanamsha_value'])}\n"
        f"[bold]Ascendant (Lagna):[/bold] {format_sign_degree(asc_sign, asc_degree)}"
    )

    console.print()
    console.print(Panel(
        header_text,
        title="[bold gold1]Birth Chart (D1 - Rashi)[/bold gold1]",
        border_style="gold1",
        padding=(1, 2),
    ))

    # Main planet positions table
    planet_table = Table(
        box=box.ROUNDED,
        border_style="gold1",
        header_style="bold white",
        show_lines=True,
        title="Planetary Positions",
    )
    planet_table.add_column("Planet", style="bold", min_width=9)
    planet_table.add_column("Sign", min_width=12)
    planet_table.add_column("Degree", justify="right", min_width=8)
    planet_table.add_column("Nakshatra", min_width=18)
    planet_table.add_column("Pada", justify="center")
    planet_table.add_column("House", justify="center")
    planet_table.add_column("Dignity", min_width=12)
    planet_table.add_column("Retro", justify="center")

    for row in planet_rows:
        color = PLANET_COLORS.get(row['planet'], 'white')
        sign_name = SIGNS[row['sign']] if 1 <= row['sign'] <= 12 else '?'
        nak_name = NAKSHATRA_NAMES[row['nakshatra'] - 1] if 1 <= row['nakshatra'] <= 27 else '?'

        # Dignity styling
        dignity_raw = row.get('dignity', '') or ''
        dignity_color = DIGNITY_COLORS.get(dignity_raw.lower(), 'white')
        dignity_display = f"[{dignity_color}]{dignity_raw.capitalize()}[/{dignity_color}]" if dignity_raw else "[dim]-[/dim]"

        # Retrograde indicator
        retro = "[bold red]R[/bold red]" if row['is_retrograde'] else "[dim]-[/dim]"

        # Combust indicator appended to planet name
        combust_flag = " [dim red](C)[/dim red]" if row.get('is_combust') else ""

        planet_table.add_row(
            f"[{color}]{row['planet']}[/{color}]{combust_flag}",
            sign_name,
            format_degree(row['sign_degree']),
            nak_name,
            str(row['nakshatra_pada']),
            str(row['house']),
            dignity_display,
            retro,
        )

    console.print(planet_table)

    # Planetary Aspects (Drishti) table
    # Build a lookup: sign -> list of planet names in that sign
    sign_to_planets: dict[int, list[str]] = {}
    for row in planet_rows:
        sign_to_planets.setdefault(row['sign'], []).append(row['planet'])

    aspect_table = Table(
        box=box.ROUNDED,
        border_style="gold1",
        header_style="bold white",
        show_lines=True,
        title="Planetary Aspects (Drishti)",
    )
    aspect_table.add_column("Planet", style="bold", min_width=9)
    aspect_table.add_column("Aspected Signs", min_width=18)
    aspect_table.add_column("Houses", justify="center", min_width=8)
    aspect_table.add_column("Planets Aspected", min_width=18)

    for row in planet_rows:
        planet_name = row['planet']
        planet_sign = row['sign']
        color = PLANET_COLORS.get(planet_name, 'white')

        aspected_signs = get_aspects(planet_name, planet_sign)

        sign_names = []
        house_nums = []
        aspected_planets = []

        for s in aspected_signs:
            sign_names.append(SIGNS[s] if 1 <= s <= 12 else '?')
            house_nums.append(str(((s - asc_sign) % 12) + 1))
            for p in sign_to_planets.get(s, []):
                if p != planet_name:
                    p_color = PLANET_COLORS.get(p, 'white')
                    aspected_planets.append(f"[{p_color}]{p}[/{p_color}]")

        aspect_table.add_row(
            f"[{color}]{planet_name}[/{color}]",
            ", ".join(sign_names),
            ", ".join(house_nums),
            ", ".join(aspected_planets) if aspected_planets else "[dim]-[/dim]",
        )

    console.print()
    console.print(aspect_table)

    # Shadbala table
    if shadbala_rows:
        sb_table = Table(
            title="Shadbala (Planetary Strength)",
            box=box.SIMPLE_HEAVY,
            border_style="blue",
            header_style="bold white",
        )
        sb_table.add_column("Planet", style="bold", min_width=9)
        sb_table.add_column("Sthana", justify="right")
        sb_table.add_column("Dig", justify="right")
        sb_table.add_column("Kala", justify="right")
        sb_table.add_column("Chesta", justify="right")
        sb_table.add_column("Naisargika", justify="right")
        sb_table.add_column("Drik", justify="right")
        sb_table.add_column("Total", justify="right", style="bold")
        sb_table.add_column("Ratio", justify="right")

        for sb in shadbala_rows:
            color = PLANET_COLORS.get(sb['planet'], 'white')
            ratio = sb['shadbala_ratio']
            ratio_style = "bold green" if ratio >= 1.0 else "bold red" if ratio < 0.7 else "yellow"
            sb_table.add_row(
                f"[{color}]{sb['planet']}[/{color}]",
                f"{sb['sthana_bala']:.1f}",
                f"{sb['dig_bala']:.1f}",
                f"{sb['kala_bala']:.1f}",
                f"{sb['chesta_bala']:.1f}",
                f"{sb['naisargika_bala']:.1f}",
                f"{sb['drik_bala']:.1f}",
                f"{sb['total_shadbala']:.1f}",
                f"[{ratio_style}]{ratio:.2f}[/{ratio_style}]",
            )

        console.print()
        console.print(sb_table)

    # Yogas table
    if yogas_rows:
        console.print()
        yoga_table = Table(
            title="Yogas Detected",
            box=box.ROUNDED,
            border_style="green",
            header_style="bold white",
            show_lines=True,
        )
        yoga_table.add_column("Yoga", style="bold", min_width=28)
        yoga_table.add_column("Type", min_width=8)
        yoga_table.add_column("Strength", min_width=10)
        yoga_table.add_column("Planets")
        yoga_table.add_column("Houses")

        for y in yogas_rows:
            type_color = YOGA_TYPE_COLORS.get(y['yoga_type'], 'white')
            strength_color = STRENGTH_COLORS.get(y.get('strength', ''), 'white')

            # Parse JSON fields
            try:
                planets_list = json.loads(y['planets_involved']) if isinstance(y['planets_involved'], str) else y['planets_involved']
            except (json.JSONDecodeError, TypeError):
                planets_list = [str(y['planets_involved'])]

            try:
                houses_list = json.loads(y['houses_involved']) if isinstance(y['houses_involved'], str) else y['houses_involved']
            except (json.JSONDecodeError, TypeError):
                houses_list = [str(y['houses_involved'])]

            # Color each planet name
            planets_display = ", ".join(
                f"[{PLANET_COLORS.get(p, 'white')}]{p}[/{PLANET_COLORS.get(p, 'white')}]"
                for p in planets_list
            )

            yoga_table.add_row(
                y['yoga_name'],
                f"[{type_color}]{y['yoga_type'].capitalize()}[/{type_color}]",
                f"[{strength_color}]{(y.get('strength') or 'moderate').capitalize()}[/{strength_color}]",
                planets_display,
                ", ".join(str(h) for h in houses_list),
            )

        console.print(yoga_table)

        # Yoga descriptions
        console.print()
        for y in yogas_rows:
            type_color = YOGA_TYPE_COLORS.get(y['yoga_type'], 'white')
            console.print(Panel(
                y['description'],
                title=f"[bold {type_color}]{y['yoga_name']}[/bold {type_color}]",
                border_style=type_color,
                padding=(0, 2),
            ))
    else:
        console.print("\n[dim]No yogas detected in this chart.[/dim]")

    console.print()


# ---------------------------------------------------------------------------
# Command: d9
# ---------------------------------------------------------------------------

def cmd_d9(args):
    """Display the Navamsha (D9) chart."""
    conn = get_connection()
    init_db(conn)
    person = _load_person(args.name, conn)
    chart = get_chart(conn, person['id'], chart_type='D9')
    if chart is None:
        console.print("[red]Error:[/red] No D9 chart found. Re-run [cyan]python -m vedia new ...[/cyan] to generate it.")
        sys.exit(1)
    planet_rows = get_planet_positions(conn, chart['id'])
    conn.close()

    asc_sign = chart['ascendant_sign']
    asc_name = SIGNS[asc_sign] if 1 <= asc_sign <= 12 else '?'

    console.print()
    console.print(Panel(
        f"[bold cyan]{person['name']}[/bold cyan]\n"
        f"Navamsha Ascendant: {asc_name}\n"
        f"The D9 chart reveals the deeper dharmic pattern, marriage potential,\n"
        f"and the soul's evolutionary direction.",
        title="[bold gold1]Navamsha Chart (D9)[/bold gold1]",
        border_style="gold1",
        padding=(1, 2),
    ))

    # Planet positions table
    planet_table = Table(
        box=box.ROUNDED,
        border_style="gold1",
        header_style="bold white",
        show_lines=True,
        title="D9 Planetary Positions",
    )
    planet_table.add_column("Planet", style="bold", min_width=9)
    planet_table.add_column("D9 Sign", min_width=12)
    planet_table.add_column("D9 House", justify="center")
    planet_table.add_column("Retro", justify="center")

    for row in planet_rows:
        color = PLANET_COLORS.get(row['planet'], 'white')
        sign_name = SIGNS[row['sign']] if 1 <= row['sign'] <= 12 else '?'
        retro = "[bold red]R[/bold red]" if row['is_retrograde'] else "[dim]-[/dim]"

        planet_table.add_row(
            f"[{color}]{row['planet']}[/{color}]",
            sign_name,
            str(row['house']),
            retro,
        )

    console.print(planet_table)
    console.print()


# ---------------------------------------------------------------------------
# Command: transit
# ---------------------------------------------------------------------------

def cmd_transit(args):
    """Display current transits overlaid on the natal chart."""
    if get_current_positions is None or overlay_transits is None or get_transit_summary is None:
        console.print("[red]Error:[/red] Transit modules are not available.")
        sys.exit(1)

    conn = get_connection()
    init_db(conn)
    person = _load_person(args.name, conn)
    chart, planet_rows = _load_chart_data(person['id'], conn)
    sarva_rows = get_ashtakavarga(conn, chart['id'], 'sarva')
    conn.close()

    sav_by_sign = {}
    for row in sarva_rows:
        sav_by_sign[row['sign']] = row['points']

    natal_planets = _db_planets_to_model(planet_rows)
    asc_sign = chart['ascendant_sign']

    # Get current transits
    with console.status("[bold cyan]Calculating current transits..."):
        transit_positions = get_current_positions()
        overlay = overlay_transits(natal_planets, transit_positions, asc_sign)
        summary = get_transit_summary(natal_planets, transit_positions, asc_sign)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    console.print()
    console.print(Panel(
        f"[bold cyan]{person['name']}[/bold cyan] -- Transit Overlay\n"
        f"As of: {now_str}\n"
        f"Natal Ascendant: {format_sign_degree(asc_sign, chart['ascendant_degree'])}",
        title="[bold gold1]Current Transits[/bold gold1]",
        border_style="gold1",
        padding=(1, 2),
    ))

    # Main transit table
    transit_table = Table(
        box=box.ROUNDED,
        border_style="gold1",
        header_style="bold white",
        show_lines=True,
    )
    transit_table.add_column("Transit Planet", style="bold", min_width=14)
    transit_table.add_column("Current Sign", min_width=12)
    transit_table.add_column("SAV", justify="center", min_width=5)
    transit_table.add_column("Natal House", justify="center")
    transit_table.add_column("Key Aspects", min_width=30)

    # Identify important slow transits
    highlight_planets = {'Saturn', 'Jupiter', 'Rahu', 'Ketu'}

    for entry in overlay:
        planet_name = entry['transit_planet']
        color = PLANET_COLORS.get(planet_name, 'white')
        sign_name = SIGNS[entry['transit_sign']] if 1 <= entry['transit_sign'] <= 12 else '?'
        natal_house = entry['natal_house']

        # SAV score for this transit sign
        sav_score = sav_by_sign.get(entry['transit_sign'])
        if sav_score is not None:
            if sav_score >= 5:
                sav_display = f"[green]{sav_score}[/green]"
            elif sav_score <= 2:
                sav_display = f"[red]{sav_score}[/red]"
            else:
                sav_display = f"[yellow]{sav_score}[/yellow]"
        else:
            sav_display = "[dim]-[/dim]"

        # Build aspects description
        aspects_parts = []
        for conj in entry.get('conjunctions', []):
            np_color = PLANET_COLORS.get(conj['natal_planet'], 'white')
            aspects_parts.append(
                f"Conj [{np_color}]{conj['natal_planet']}[/{np_color}] "
                f"({conj['orb']:.1f}\u00b0)"
            )
        for asp in entry.get('aspects', []):
            np_color = PLANET_COLORS.get(asp['natal_planet'], 'white')
            aspects_parts.append(
                f"Asp [{np_color}]{asp['natal_planet']}[/{np_color}] "
                f"(H{asp['aspect_type']})"
            )
        aspects_str = "\n".join(aspects_parts) if aspects_parts else "[dim]-[/dim]"

        # Highlight row for major transit planets
        row_style = "bold" if planet_name in highlight_planets else ""

        transit_table.add_row(
            f"[{color}]{planet_name}[/{color}]",
            sign_name,
            sav_display,
            str(natal_house),
            aspects_str,
            style=row_style,
        )

    console.print(transit_table)

    # Special transit annotations
    special = summary.get('_special', {})

    annotations = []

    # Sade Sati
    sade_sati = special.get('sade_sati', {})
    if sade_sati.get('active'):
        phase = sade_sati.get('phase', 'unknown')
        annotations.append(Panel(
            f"[bold red]Sade Sati is ACTIVE[/bold red]\n"
            f"Phase: {phase}\n"
            f"Saturn is transiting the {sade_sati.get('saturn_house_from_moon', '?')}th house from natal Moon.\n"
            f"This 7.5-year transit brings karmic lessons, increased responsibilities,\n"
            f"and deep transformation.",
            title="[bold red]Sade Sati[/bold red]",
            border_style="red",
        ))

    # Jupiter transit
    jup_transit = special.get('jupiter_transit', {})
    if jup_transit:
        fav_moon = jup_transit.get('favorable_from_moon', False)
        fav_asc = jup_transit.get('favorable_from_asc', False)
        jup_status = "Favorable" if (fav_moon or fav_asc) else "Challenging"
        jup_color = "green" if (fav_moon or fav_asc) else "yellow"
        annotations.append(Panel(
            f"Jupiter transits House {jup_transit.get('house_from_ascendant', '?')} from Asc, "
            f"House {jup_transit.get('house_from_moon', '?')} from Moon\n"
            f"[{jup_color}]Overall: {jup_status}[/{jup_color}]"
            + ("\n[green]Favorable from Moon -- expansion, growth, and opportunities.[/green]" if fav_moon else "")
            + ("\n[green]Favorable from Ascendant -- blessings in personal matters.[/green]" if fav_asc else ""),
            title="[bold yellow]Jupiter Transit[/bold yellow]",
            border_style="yellow",
        ))

    # Rahu-Ketu axis
    rk = special.get('rahu_ketu_axis', {})
    if rk:
        annotations.append(Panel(
            f"Rahu transits natal House {rk.get('rahu_natal_house', '?')} | "
            f"Ketu transits natal House {rk.get('ketu_natal_house', '?')}\n"
            f"Axis houses: {rk.get('axis_houses', [])} -- karmic growth axis active.",
            title="[bold grey50]Rahu-Ketu Axis[/bold grey50]",
            border_style="grey50",
        ))

    if annotations:
        console.print()
        for panel in annotations:
            console.print(panel)

    # Vedha (obstruction) analysis
    if analyze_all_vedha is not None:
        # Find natal Moon sign
        natal_moon_sign = None
        for np in natal_planets:
            if np.planet == 'Moon':
                natal_moon_sign = np.sign
                break

        if natal_moon_sign is not None:
            vedha_results = analyze_all_vedha(transit_positions, natal_moon_sign)

            # Filter to only benefic transits
            benefic_rows = [v for v in vedha_results if v['is_benefic_transit']]

            if benefic_rows:
                console.print()
                vedha_table = Table(
                    title="Gochara Vedha Analysis",
                    box=box.ROUNDED,
                    border_style="dark_orange",
                    header_style="bold white",
                    show_lines=True,
                )
                vedha_table.add_column("Planet", style="bold", min_width=12)
                vedha_table.add_column("Transit House", justify="center", min_width=14)
                vedha_table.add_column("Status", min_width=30)

                for v in benefic_rows:
                    color = PLANET_COLORS.get(v['planet'], 'white')
                    planet_label = f"[{color}]{v['planet']}[/{color}]"
                    house_label = f"H{v['house_from_moon']} from Moon"

                    if v['has_vedha']:
                        blocker_color = PLANET_COLORS.get(v['blocking_planet'], 'white')
                        status = (
                            f"[red]Benefic - OBSTRUCTED by "
                            f"[{blocker_color}]{v['blocking_planet']}[/{blocker_color}]"
                            f" (H{v['vedha_house']})[/red]"
                        )
                    else:
                        status = "[green]Benefic - CLEAR[/green]"

                    vedha_table.add_row(planet_label, house_label, status)

                console.print(vedha_table)

    console.print()


# ---------------------------------------------------------------------------
# Command: dasha
# ---------------------------------------------------------------------------

def cmd_dasha(args):
    """Display Vimshottari dasha periods with current period highlighted."""
    conn = get_connection()
    init_db(conn)
    person = _load_person(args.name, conn)
    maha_rows = get_dasha_periods(conn, person['id'], level='maha')
    antar_rows = get_dasha_periods(conn, person['id'], level='antar')
    pratyantar_rows = get_dasha_periods(conn, person['id'], level='pratyantar')
    conn.close()

    if not maha_rows:
        console.print(f"[red]Error:[/red] No dasha data found for '{person['name']}'.")
        console.print("Run [cyan]python -m vedia new ...[/cyan] to create a chart first.")
        sys.exit(1)

    now = datetime.now()
    now_str = now.isoformat()

    console.print()
    console.print(Panel(
        f"[bold cyan]{person['name']}[/bold cyan] -- Vimshottari Dasha Periods\n"
        f"Born: {person['birth_date']} at {person['birth_time']}",
        title="[bold gold1]Dasha Timeline[/bold gold1]",
        border_style="gold1",
        padding=(1, 2),
    ))

    # Find current maha dasha
    current_maha_id = None
    for m in maha_rows:
        if m['start_date'] <= now_str <= m['end_date']:
            current_maha_id = m['id']
            break

    # Maha dasha table
    maha_table = Table(
        title="Maha Dasha (Major Periods)",
        box=box.ROUNDED,
        border_style="gold1",
        header_style="bold white",
        show_lines=True,
    )
    maha_table.add_column("", justify="center", width=3)
    maha_table.add_column("Planet", style="bold", min_width=9)
    maha_table.add_column("Start", min_width=12)
    maha_table.add_column("End", min_width=12)
    maha_table.add_column("Duration", justify="center")

    for m in maha_rows:
        is_current = m['id'] == current_maha_id
        color = PLANET_COLORS.get(m['planet'], 'white')
        marker = "[bold gold1]\u2605[/bold gold1]" if is_current else ""
        row_style = "bold" if is_current else ""

        # Parse dates for display
        try:
            start_dt = datetime.fromisoformat(m['start_date'])
            end_dt = datetime.fromisoformat(m['end_date'])
            start_display = start_dt.strftime("%Y-%m-%d")
            end_display = end_dt.strftime("%Y-%m-%d")
            duration_days = (end_dt - start_dt).days
            years = duration_days / 365.25
            duration_display = f"{years:.1f}y"
        except (ValueError, TypeError):
            start_display = m['start_date'][:10] if m['start_date'] else '?'
            end_display = m['end_date'][:10] if m['end_date'] else '?'
            duration_display = "?"

        maha_table.add_row(
            marker,
            f"[{color}]{m['planet']}[/{color}]",
            start_display,
            end_display,
            duration_display,
            style=row_style,
        )

    console.print(maha_table)

    # Current period detail
    if current_maha_id is not None:
        current_maha = next(m for m in maha_rows if m['id'] == current_maha_id)

        # Find current antar dasha
        current_antar = None
        current_antar_id = None
        for a in antar_rows:
            if a['parent_id'] == current_maha_id and a['start_date'] <= now_str <= a['end_date']:
                current_antar = a
                current_antar_id = a['id']
                break

        # Find current pratyantar dasha
        current_pratyantar = None
        if current_antar_id is not None:
            for p in pratyantar_rows:
                if p['parent_id'] == current_antar_id and p['start_date'] <= now_str <= p['end_date']:
                    current_pratyantar = p
                    break

        # Build current period display
        lines = []
        maha_color = PLANET_COLORS.get(current_maha['planet'], 'white')
        lines.append(f"[bold]Maha Dasha:[/bold]      [{maha_color}]{current_maha['planet']}[/{maha_color}]")

        if current_antar:
            antar_color = PLANET_COLORS.get(current_antar['planet'], 'white')
            try:
                antar_end = datetime.fromisoformat(current_antar['end_date']).strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                antar_end = current_antar['end_date'][:10]
            lines.append(
                f"[bold]Antar Dasha:[/bold]     [{antar_color}]{current_antar['planet']}[/{antar_color}]"
                f"  (until {antar_end})"
            )

        if current_pratyantar:
            prat_color = PLANET_COLORS.get(current_pratyantar['planet'], 'white')
            try:
                prat_end = datetime.fromisoformat(current_pratyantar['end_date']).strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                prat_end = current_pratyantar['end_date'][:10]
            lines.append(
                f"[bold]Pratyantar Dasha:[/bold] [{prat_color}]{current_pratyantar['planet']}[/{prat_color}]"
                f"  (until {prat_end})"
            )

        console.print()
        console.print(Panel(
            "\n".join(lines),
            title="[bold gold1]Current Active Period[/bold gold1]",
            border_style="bold green",
            padding=(1, 2),
        ))

        # Antar dasha breakdown within current maha
        current_antars = [a for a in antar_rows if a['parent_id'] == current_maha_id]
        if current_antars:
            antar_table = Table(
                title=f"Antar Dashas within {current_maha['planet']} Maha Dasha",
                box=box.SIMPLE_HEAVY,
                border_style="blue",
                header_style="bold white",
            )
            antar_table.add_column("", justify="center", width=3)
            antar_table.add_column("Planet", style="bold", min_width=9)
            antar_table.add_column("Start", min_width=12)
            antar_table.add_column("End", min_width=12)

            for a in current_antars:
                is_now = (a['id'] == current_antar_id) if current_antar_id else False
                color = PLANET_COLORS.get(a['planet'], 'white')
                marker = "[bold gold1]\u2605[/bold gold1]" if is_now else ""
                row_style = "bold" if is_now else ""

                try:
                    a_start = datetime.fromisoformat(a['start_date']).strftime('%Y-%m-%d')
                    a_end = datetime.fromisoformat(a['end_date']).strftime('%Y-%m-%d')
                except (ValueError, TypeError):
                    a_start = a['start_date'][:10]
                    a_end = a['end_date'][:10]

                antar_table.add_row(
                    marker,
                    f"[{color}]{a['planet']}[/{color}]",
                    a_start,
                    a_end,
                    style=row_style,
                )

            console.print()
            console.print(antar_table)

    console.print()


# ---------------------------------------------------------------------------
# Command: ask
# ---------------------------------------------------------------------------

def cmd_ask(args):
    """Answer a question about a person's chart using available data."""
    conn = get_connection()
    init_db(conn)
    person = _load_person(args.name, conn)
    chart, planet_rows = _load_chart_data(person['id'], conn)
    yogas_rows = get_yogas(conn, chart['id'])
    shadbala_rows = get_shadbala(conn, chart['id'])

    natal_planets = _db_planets_to_model(planet_rows)
    asc_sign = chart['ascendant_sign']
    question = args.question

    console.print()
    console.print(Panel(
        f"[bold cyan]{person['name']}[/bold cyan]\n"
        f"Question: [italic]{question}[/italic]",
        title="[bold gold1]Vedia Reading[/bold gold1]",
        border_style="gold1",
        padding=(1, 2),
    ))

    # Gather relevant factors
    reading_parts = []

    # Current dasha
    maha_rows = get_dasha_periods(conn, person['id'], level='maha')
    antar_rows = get_dasha_periods(conn, person['id'], level='antar')
    pratyantar_rows = get_dasha_periods(conn, person['id'], level='pratyantar')

    now_str = datetime.now().isoformat()
    current_maha = None
    current_antar = None
    current_pratyantar = None

    for m in maha_rows:
        if m['start_date'] <= now_str <= m['end_date']:
            current_maha = m
            break

    if current_maha:
        for a in antar_rows:
            if a['parent_id'] == current_maha['id'] and a['start_date'] <= now_str <= a['end_date']:
                current_antar = a
                break
        if current_antar:
            for p in pratyantar_rows:
                if p['parent_id'] == current_antar['id'] and p['start_date'] <= now_str <= p['end_date']:
                    current_pratyantar = p
                    break

    dasha_line = "Current Dasha: "
    if current_maha:
        dasha_line += f"{current_maha['planet']}"
        if current_antar:
            dasha_line += f" / {current_antar['planet']}"
            if current_pratyantar:
                dasha_line += f" / {current_pratyantar['planet']}"
    else:
        dasha_line += "Unknown"
    reading_parts.append(dasha_line)

    # Current transits
    transit_info = ""
    if get_current_positions is not None and get_transit_summary is not None:
        with console.status("[bold cyan]Computing current transits..."):
            transit_positions = get_current_positions()
            summary = get_transit_summary(natal_planets, transit_positions, asc_sign)

        # Gather transit highlights
        transit_lines = []
        for planet_name in ('Saturn', 'Jupiter', 'Rahu', 'Ketu'):
            planet_summary = summary.get(planet_name)
            if planet_summary:
                sign_name = SIGNS[planet_summary['transit_sign']] if 1 <= planet_summary['transit_sign'] <= 12 else '?'
                transit_lines.append(
                    f"  {planet_name} in {sign_name} (natal house {planet_summary['natal_house']})"
                )
                for note in planet_summary.get('notes', []):
                    transit_lines.append(f"    - {note}")

        # Special transits
        special = summary.get('_special', {})
        sade_sati = special.get('sade_sati', {})
        if sade_sati.get('active'):
            transit_lines.append(f"  ** Sade Sati ACTIVE ({sade_sati.get('phase', 'unknown')})")

        jup_t = special.get('jupiter_transit', {})
        if jup_t.get('favorable_from_moon') or jup_t.get('favorable_from_asc'):
            transit_lines.append("  ** Jupiter transit is FAVORABLE")

        transit_info = "\n".join(transit_lines)
        if transit_info:
            reading_parts.append(f"Key Transits:\n{transit_info}")

    # Yogas
    if yogas_rows:
        yoga_lines = []
        for y in yogas_rows:
            strength = y.get('strength', 'moderate')
            yoga_lines.append(f"  {y['yoga_name']} ({y['yoga_type']}, {strength})")
        reading_parts.append("Active Yogas:\n" + "\n".join(yoga_lines))

    # Key planet strengths
    if shadbala_rows:
        strong = [sb for sb in shadbala_rows if sb['shadbala_ratio'] >= 1.0]
        weak = [sb for sb in shadbala_rows if sb['shadbala_ratio'] < 0.7]
        if strong:
            reading_parts.append(
                "Strong planets: " + ", ".join(f"{sb['planet']} ({sb['shadbala_ratio']:.2f})" for sb in strong)
            )
        if weak:
            reading_parts.append(
                "Weak planets: " + ", ".join(f"{sb['planet']} ({sb['shadbala_ratio']:.2f})" for sb in weak)
            )

    # Compose the reading text
    full_reading = f"Question: {question}\n\n" + "\n\n".join(reading_parts)

    # Try to use a synthesizer module if it exists
    synthesizer_used = False
    try:
        from .interpret.synthesizer import synthesize_reading
        with console.status("[bold cyan]Synthesizing reading..."):
            synthesized = synthesize_reading(
                question=question,
                person_name=person['name'],
                natal_planets=natal_planets,
                asc_sign=asc_sign,
                current_dasha=(current_maha, current_antar, current_pratyantar),
                yogas=yogas_rows,
                shadbala=shadbala_rows,
                transit_summary=summary if get_current_positions else None,
            )
            full_reading = synthesized
            synthesizer_used = True
    except (ImportError, Exception):
        pass

    # Display the reading
    console.print()
    if not synthesizer_used:
        console.print(Panel(
            "[dim]Note: Full AI synthesis is not yet available. "
            "Showing relevant astrological factors below.[/dim]",
            border_style="dim",
        ))

    console.print(Panel(
        full_reading,
        title="[bold gold1]Reading[/bold gold1]",
        border_style="cyan",
        padding=(1, 2),
    ))

    # Save reading to database
    transit_date = datetime.now().strftime("%Y-%m-%d")
    save_reading(conn, person['id'], 'ask', full_reading, query=question, transit_date=transit_date)
    conn.close()

    console.print(f"\n[dim]Reading saved to database.[/dim]")
    console.print()


# ---------------------------------------------------------------------------
# Command: muhurta
# ---------------------------------------------------------------------------

def cmd_muhurta(args):
    """Evaluate the auspiciousness of a date for a person."""
    if evaluate_muhurta is None:
        console.print("[red]Error:[/red] Muhurta module is not available.")
        sys.exit(1)
    if calculate_planet_positions is None or calculate_julian_day is None:
        console.print("[red]Error:[/red] Ephemeris/ayanamsha modules are not available.")
        sys.exit(1)

    conn = get_connection()
    init_db(conn)
    person = _load_person(args.name, conn)
    chart, planet_rows = _load_chart_data(person['id'], conn)

    natal_planets = _db_planets_to_model(planet_rows)
    natal_asc_sign = chart['ascendant_sign']

    # Find natal Moon sign
    natal_moon_sign = None
    for np in natal_planets:
        if np.planet == 'Moon':
            natal_moon_sign = np.sign
            break
    if natal_moon_sign is None:
        console.print("[red]Error:[/red] Natal Moon not found in chart data.")
        conn.close()
        sys.exit(1)

    # Parse target date
    try:
        target_dt = datetime.strptime(args.date, '%Y-%m-%d')
    except ValueError:
        console.print("[red]Error:[/red] Invalid date format. Use YYYY-MM-DD.")
        conn.close()
        sys.exit(1)

    event_type = getattr(args, 'type', 'general') or 'general'

    # Get current dasha lord
    dasha_lord = None
    maha_rows = get_dasha_periods(conn, person['id'], level='maha')
    if maha_rows:
        target_str = target_dt.isoformat()
        for m in maha_rows:
            if m['start_date'] <= target_str <= m['end_date']:
                dasha_lord = m['planet']
                break

    # Get sarvashtakavarga if available
    sarvashtakavarga = None
    ashtakavarga_rows = get_ashtakavarga(conn, chart['id'])
    if ashtakavarga_rows:
        # get_ashtakavarga returns (bhinna, sarva) or a dict -- handle both
        if isinstance(ashtakavarga_rows, tuple) and len(ashtakavarga_rows) == 2:
            _, sarvashtakavarga = ashtakavarga_rows
        elif isinstance(ashtakavarga_rows, dict):
            sarvashtakavarga = ashtakavarga_rows.get('sarva')

    # Get shadbala if available
    shadbala_rows = get_shadbala(conn, chart['id'])

    conn.close()

    # Calculate transit positions for the target date at noon UTC
    with console.status("[bold cyan]Calculating transit positions..."):
        jd = calculate_julian_day(target_dt.year, target_dt.month, target_dt.day, 12.0, 0.0)
        transit_planets = calculate_planet_positions(jd, natal_asc_sign)

    # Evaluate muhurta
    with console.status("[bold cyan]Evaluating muhurta..."):
        result = evaluate_muhurta(
            natal_planets=natal_planets,
            natal_asc_sign=natal_asc_sign,
            natal_moon_sign=natal_moon_sign,
            transit_planets=transit_planets,
            target_date=target_dt,
            event_type=event_type,
            dasha_lord=dasha_lord,
            shadbala=shadbala_rows,
            sarvashtakavarga=sarvashtakavarga,
        )

    # Display results
    console.print()

    # Date info panel
    moon_info = result['moon_transit']
    moon_sign_name = SIGNS[moon_info['sign']] if 1 <= moon_info['sign'] <= 12 else '?'
    fav_label = "[green]Favorable[/green]" if moon_info['favorable'] else "[red]Unfavorable[/red]"

    console.print(Panel(
        f"[bold cyan]{person['name']}[/bold cyan] -- Muhurta Evaluation\n"
        f"Date: [bold]{result['date']}[/bold] ({result['day_of_week']})\n"
        f"Vara Lord: {_colored_planet_str(result['vara_lord'])}\n"
        f"Event Type: [italic]{event_type}[/italic]\n"
        f"\nMoon Transit: {moon_sign_name} -- {moon_info['nakshatra']}\n"
        f"House from natal Moon: H{moon_info['house_from_natal_moon']} ({fav_label})"
        + (f"\nActive Dasha Lord: {_colored_planet_str(dasha_lord)}" if dasha_lord else ""),
        title="[bold gold1]Muhurta Analysis[/bold gold1]",
        border_style="gold1",
        padding=(1, 2),
    ))

    # Scoring table
    score_table = Table(
        title="Muhurta Scores",
        box=box.ROUNDED,
        border_style="gold1",
        header_style="bold white",
        show_lines=True,
    )
    score_table.add_column("Factor", style="bold", min_width=18)
    score_table.add_column("Score", justify="right", min_width=8)
    score_table.add_column("Weight", justify="right", min_width=8)
    score_table.add_column("Weighted", justify="right", min_width=8)

    score_rows = [
        ("Gochara (Moon transit)", result['gochara_score'], 25),
        ("Vara (Day lord)", result['vara_score'], 15),
        ("Nakshatra", result['nakshatra_score'], 20),
        ("Transit interactions", result['transit_score'], 25),
        ("Ashtakavarga (SAV)", result['ashtakavarga_score'], 15),
    ]

    for label, score, weight in score_rows:
        weighted = score * weight / 10.0
        score_style = "green" if score >= 7.0 else "yellow" if score >= 5.0 else "red"
        score_table.add_row(
            label,
            f"[{score_style}]{score:.1f}[/{score_style}] / 10",
            f"{weight}%",
            f"{weighted:.1f}",
        )

    console.print(score_table)

    # Total score panel
    total = result['total_score']
    ausp = result['auspiciousness']
    if ausp == 'Highly Auspicious':
        ausp_style = "bold green"
    elif ausp == 'Auspicious':
        ausp_style = "green"
    elif ausp == 'Moderate':
        ausp_style = "yellow"
    elif ausp == 'Challenging':
        ausp_style = "dark_orange"
    else:
        ausp_style = "bold red"

    console.print(Panel(
        f"[bold]Total Score:[/bold] [{ausp_style}]{total:.1f} / 100[/{ausp_style}]\n"
        f"[bold]Auspiciousness:[/bold] [{ausp_style}]{ausp}[/{ausp_style}]",
        border_style=ausp_style,
        padding=(1, 2),
    ))

    # Factors list
    if result['factors']:
        console.print()
        console.print("[bold]Factors:[/bold]")
        for factor in result['factors']:
            if any(kw in factor.lower() for kw in ('favorable', 'beneficial', 'protective', 'ideal', 'suitable', 'supportive', 'above average', 'strongly')):
                console.print(f"  [green]+[/green] {factor}")
            elif any(kw in factor.lower() for kw in ('unfavorable', 'difficult', 'challenging', 'inauspicious', 'pressure', 'confusion', 'delays', 'weak', 'below')):
                console.print(f"  [red]-[/red] {factor}")
            else:
                console.print(f"  [dim]*[/dim] {factor}")

    # Recommendations
    if result['recommendations']:
        console.print()
        console.print(Panel(
            "\n".join(f"  {r}" for r in result['recommendations']),
            title="[bold]Recommendations[/bold]",
            border_style="cyan",
            padding=(1, 2),
        ))

    console.print()


# ---------------------------------------------------------------------------
# Command: list
# ---------------------------------------------------------------------------

def cmd_list(args):
    """List all stored persons."""
    conn = get_connection()
    init_db(conn)
    persons = get_all_persons(conn)
    conn.close()

    console.print()

    if not persons:
        console.print(Panel(
            "No charts stored yet.\n"
            "Create one with: [cyan]python -m vedia new --name \"Name\" --date YYYY-MM-DD --time HH:MM:SS --location \"City\"[/cyan]",
            title="[bold gold1]Vedia[/bold gold1]",
            border_style="gold1",
        ))
        return

    table = Table(
        title="Stored Charts",
        box=box.ROUNDED,
        border_style="gold1",
        header_style="bold white",
    )
    table.add_column("Name", style="bold cyan", min_width=15)
    table.add_column("Birth Date", min_width=12)
    table.add_column("Birth Time", min_width=10)
    table.add_column("Location", min_width=20)
    table.add_column("Created", min_width=12)

    for p in persons:
        created = p.get('created_at', '')
        if created and len(created) >= 10:
            created = created[:10]
        table.add_row(
            p['name'],
            p['birth_date'],
            p['birth_time'],
            p['birth_location'],
            created,
        )

    console.print(table)
    console.print()


# ---------------------------------------------------------------------------
# Command: synastry
# ---------------------------------------------------------------------------

def cmd_synastry(args):
    """Compare two charts for compatibility (synastry / Guna Milan)."""
    if analyze_synastry is None:
        console.print("[red]Error:[/red] Synastry module is not available.")
        sys.exit(1)

    conn = get_connection()
    init_db(conn)

    person1 = _load_person(args.name1, conn)
    person2 = _load_person(args.name2, conn)

    chart1, planet_rows1 = _load_chart_data(person1['id'], conn)
    chart2, planet_rows2 = _load_chart_data(person2['id'], conn)

    planets1 = _db_planets_to_model(planet_rows1)
    planets2 = _db_planets_to_model(planet_rows2)

    asc1 = chart1['ascendant_sign']
    asc2 = chart2['ascendant_sign']

    # Find Moon nakshatras
    moon1 = next((p for p in planets1 if p.planet == 'Moon'), None)
    moon2 = next((p for p in planets2 if p.planet == 'Moon'), None)

    if moon1 is None or moon2 is None:
        console.print("[red]Error:[/red] Moon position missing from one or both charts.")
        conn.close()
        sys.exit(1)

    result = analyze_synastry(
        person1_planets=planets1,
        person1_asc_sign=asc1,
        person1_moon_nakshatra=moon1.nakshatra,
        person2_planets=planets2,
        person2_asc_sign=asc2,
        person2_moon_nakshatra=moon2.nakshatra,
    )

    # -- Display --

    console.print()
    console.print(Panel(
        f"[bold cyan]{person1['name']}[/bold cyan]  &  [bold cyan]{person2['name']}[/bold cyan]\n"
        f"Synastry / Compatibility Analysis",
        title="[bold gold1]Vedia -- Synastry[/bold gold1]",
        border_style="gold1",
        padding=(1, 2),
    ))

    # Guna Milan table
    guna = result['guna_milan']
    guna_table = Table(
        title=f"Guna Milan (Ashtakoot) -- {guna['total']}/36  ({guna['percentage']}%)",
        box=box.ROUNDED,
        border_style="gold1",
        header_style="bold white",
        show_lines=True,
    )
    guna_table.add_column("Kuta", style="bold", min_width=14)
    guna_table.add_column("Score", justify="center", min_width=8)
    guna_table.add_column("Max", justify="center", min_width=6)
    guna_table.add_column("Detail", min_width=30)

    for k in guna['kutas']:
        score_color = 'green' if k['score'] >= k['max'] * 0.6 else (
            'yellow' if k['score'] > 0 else 'red'
        )
        detail_parts = []
        if 'person1_varna' in k:
            detail_parts.append(f"{k['person1_varna']} / {k['person2_varna']}")
        if 'person1_group' in k:
            detail_parts.append(f"{k['person1_group']} / {k['person2_group']}")
        if 'quality' in k:
            detail_parts.append(k['quality'])
        if 'person1_animal' in k:
            detail_parts.append(f"{k['person1_animal']} / {k['person2_animal']}")
        if 'person1_lord' in k:
            detail_parts.append(f"{k['person1_lord']} / {k['person2_lord']}")
        if 'person1_gana' in k:
            detail_parts.append(f"{k['person1_gana']} / {k['person2_gana']}")
        if 'person1_sign' in k:
            detail_parts.append(f"{k['person1_sign']} / {k['person2_sign']}")
        if 'person1_nadi' in k:
            detail_parts.append(f"{k['person1_nadi']} / {k['person2_nadi']}")
        detail = " -- ".join(detail_parts) if detail_parts else k.get('description', '')

        guna_table.add_row(
            k['name'],
            f"[{score_color}]{k['score']}[/{score_color}]",
            str(k['max']),
            detail,
        )

    # Total row
    total_color = 'green' if guna['total'] >= 24 else ('yellow' if guna['total'] >= 18 else 'red')
    guna_table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold {total_color}]{guna['total']}[/bold {total_color}]",
        "36",
        f"[bold]{guna['assessment']}[/bold]",
    )

    console.print(guna_table)

    # Venus comparison panel
    venus = result['venus_analysis']
    if venus.get('available'):
        venus_color = 'green' if venus['quality'] == 'Harmonious' else (
            'red' if venus['quality'] == 'Tense' else 'yellow'
        )
        console.print()
        console.print(Panel(
            f"[bold]{person1['name']}[/bold] Venus: "
            f"[magenta]{venus['person1_venus_sign']}[/magenta] "
            f"(H{venus['person1_venus_house']}, {venus['person1_venus_dignity']})\n"
            f"[bold]{person2['name']}[/bold] Venus: "
            f"[magenta]{venus['person2_venus_sign']}[/magenta] "
            f"(H{venus['person2_venus_house']}, {venus['person2_venus_dignity']})\n"
            f"Sign distance: {venus['sign_distance']}  |  "
            f"Quality: [{venus_color}]{venus['quality']}[/{venus_color}]",
            title="[bold magenta]Venus Axis Comparison[/bold magenta]",
            border_style="magenta",
            padding=(0, 2),
        ))

    # 7th lord panel
    seventh = result['seventh_lord']
    seventh_lines = [
        f"[bold]{person1['name']}[/bold] 7th sign: {seventh['person1_7th_sign']} "
        f"(lord: {seventh['person1_7th_lord']})",
        f"[bold]{person2['name']}[/bold] 7th sign: {seventh['person2_7th_sign']} "
        f"(lord: {seventh['person2_7th_lord']})",
    ]
    if 'person1_7th_lord_in_p2_house' in seventh:
        seventh_lines.append(
            f"{person1['name']}'s 7th lord in {seventh.get('person1_7th_lord_sign', '?')} "
            f"-> falls in {person2['name']}'s H{seventh['person1_7th_lord_in_p2_house']}"
        )
    if 'person2_7th_lord_in_p1_house' in seventh:
        seventh_lines.append(
            f"{person2['name']}'s 7th lord in {seventh.get('person2_7th_lord_sign', '?')} "
            f"-> falls in {person1['name']}'s H{seventh['person2_7th_lord_in_p1_house']}"
        )
    if seventh.get('mutual_exchange'):
        seventh_lines.append("[bold green]Mutual exchange of 7th lords![/bold green]")

    console.print()
    console.print(Panel(
        "\n".join(seventh_lines),
        title="[bold blue]7th Lord Exchange[/bold blue]",
        border_style="blue",
        padding=(0, 2),
    ))

    # Ascendant compatibility
    asc_compat = result['ascendant_compatibility']
    asc_q = asc_compat['quality']
    asc_color = 'green' if 'Excellent' in asc_q or 'Good' in asc_q else (
        'red' if 'Challenging' in asc_q else 'yellow'
    )
    console.print()
    console.print(Panel(
        f"{person1['name']}: {asc_compat['person1_asc']} (lord {asc_compat['person1_asc_lord']})\n"
        f"{person2['name']}: {asc_compat['person2_asc']} (lord {asc_compat['person2_asc_lord']})\n"
        f"[{asc_color}]{asc_q}[/{asc_color}]",
        title="[bold cyan]Ascendant Compatibility[/bold cyan]",
        border_style="cyan",
        padding=(0, 2),
    ))

    # Mangal Dosha
    mangal = result['mangal_dosha']
    m1 = mangal['person1']
    m2 = mangal['person2']
    mangal_lines = []
    for label, m in [(person1['name'], m1), (person2['name'], m2)]:
        status = "[red]Manglik[/red]" if m.get('effective') else (
            "[yellow]Manglik (cancelled)[/yellow]" if m.get('manglik') else "[green]Not Manglik[/green]"
        )
        mangal_lines.append(f"{label}: Mars in H{m.get('mars_house', '?')} ({m.get('mars_sign', '?')}) -- {status}")
        for c in m.get('cancellations', []):
            mangal_lines.append(f"  [dim]{c}[/dim]")

    if mangal.get('cancels_out'):
        mangal_lines.append("\n[green]Both Manglik -- Dosha cancels out.[/green]")

    console.print()
    console.print(Panel(
        "\n".join(mangal_lines),
        title="[bold red]Mangal Dosha[/bold red]",
        border_style="red",
        padding=(0, 2),
    ))

    # Overall score panel
    score = result['overall_score']
    assess = result['assessment']
    score_color = 'green' if score >= 70 else ('yellow' if score >= 50 else 'red')
    console.print()
    console.print(Panel(
        f"[bold]Overall Compatibility Score: [{score_color}]{score}/100[/{score_color}][/bold]\n"
        f"Assessment: [bold {score_color}]{assess}[/bold {score_color}]\n\n"
        f"{result['summary']}",
        title="[bold gold1]Overall Compatibility[/bold gold1]",
        border_style="gold1",
        padding=(1, 2),
    ))

    # Save reading
    reading_text = (
        f"Synastry: {person1['name']} & {person2['name']}\n"
        f"Guna Milan: {guna['total']}/36 ({guna['assessment']})\n"
        f"Overall: {score}/100 ({assess})\n\n"
        f"{result['summary']}"
    )
    transit_date = datetime.now().strftime("%Y-%m-%d")
    save_reading(
        conn, person1['id'], 'synastry', reading_text,
        query=f"Compatibility with {person2['name']}", transit_date=transit_date,
    )
    conn.close()

    console.print(f"\n[dim]Reading saved to database.[/dim]")
    console.print()


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog='vedia',
        description='Vedia -- Vedic Astrology Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python -m vedia new --name "Crystal" --date 1985-02-06 --time 03:45:00 --location "Detroit, Michigan"\n'
            '  python -m vedia chart "Crystal"\n'
            '  python -m vedia transit "Crystal"\n'
            '  python -m vedia dasha "Crystal"\n'
            '  python -m vedia ask "Crystal" "How is my career looking?"\n'
            '  python -m vedia list\n'
        ),
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # new
    new_parser = subparsers.add_parser('new', help='Create a new birth chart')
    new_parser.add_argument('--name', required=True, help='Person name')
    new_parser.add_argument('--date', required=True, help='Birth date (YYYY-MM-DD)')
    new_parser.add_argument('--time', required=True, help='Birth time (HH:MM:SS or HH:MM)')
    new_parser.add_argument('--location', required=True, help='Birth location (city, state/country)')

    # chart
    chart_parser = subparsers.add_parser('chart', help='Display a birth chart')
    chart_parser.add_argument('name', help='Person name')

    # d9
    d9_parser = subparsers.add_parser('d9', help='Display Navamsha (D9) chart')
    d9_parser.add_argument('name', help='Person name')

    # transit
    transit_parser = subparsers.add_parser('transit', help='Show current transits')
    transit_parser.add_argument('name', help='Person name')

    # dasha
    dasha_parser = subparsers.add_parser('dasha', help='Show dasha periods')
    dasha_parser.add_argument('name', help='Person name')

    # ask
    ask_parser = subparsers.add_parser('ask', help='Ask a question about a chart')
    ask_parser.add_argument('name', help='Person name')
    ask_parser.add_argument('question', help='Your question')

    # list
    subparsers.add_parser('list', help='List all stored charts')

    # synastry
    synastry_parser = subparsers.add_parser('synastry', help='Compare two charts for compatibility')
    synastry_parser.add_argument('name1', help='First person name')
    synastry_parser.add_argument('name2', help='Second person name')

    # muhurta
    muhurta_parser = subparsers.add_parser('muhurta', help='Evaluate auspiciousness of a date')
    muhurta_parser.add_argument('name', help='Person name')
    muhurta_parser.add_argument('--date', required=True, help='Target date (YYYY-MM-DD)')
    muhurta_parser.add_argument('--type', default='general', help='Event type: court, business, travel, ceremony, medical, general')

    return parser


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main():
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        # No command given -- show help with a styled banner
        console.print()
        console.print(Panel(
            "[bold]Vedic Astrology Engine[/bold]\n\n"
            "Calculate birth charts, dashas, transits, and yogas\n"
            "using the Swiss Ephemeris with Lahiri ayanamsha.",
            title="[bold gold1]Vedia[/bold gold1]",
            border_style="gold1",
            padding=(1, 2),
        ))
        parser.print_help()
        sys.exit(0)

    dispatch = {
        'new': cmd_new,
        'chart': cmd_chart,
        'd9': cmd_d9,
        'transit': cmd_transit,
        'dasha': cmd_dasha,
        'ask': cmd_ask,
        'list': cmd_list,
        'synastry': cmd_synastry,
        'muhurta': cmd_muhurta,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        sys.exit(1)

    try:
        handler(args)
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted.[/dim]")
        sys.exit(130)
    except Exception as exc:
        console.print(f"\n[red]Error:[/red] {exc}")
        console.print("[dim]Use --help for usage information.[/dim]")
        sys.exit(1)
