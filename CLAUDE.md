# Vedia - Vedic Astrology Reader

## Overview

Vedia is a comprehensive Vedic (Jyotish) astrology application that calculates and interprets birth charts (Kundali), planetary transits, dashas, and provides astrological readings based on traditional sidereal/Lahiri ayanamsha calculations.

## Core Requirements

### Input
- **Name**: Full name of the person
- **Birth Date**: Date of birth (YYYY-MM-DD)
- **Birth Time**: Exact time of birth (HH:MM:SS, 24hr format) with timezone
- **Birth Location**: City/Place of birth (resolved to latitude, longitude, timezone)

### Astronomical Calculations (Sidereal/Vedic)

All calculations MUST use the **sidereal zodiac** with **Lahiri (Chitrapaksha) ayanamsha** — not tropical/Western astrology. This is the defining distinction.

#### Birth Chart (Rashi Chart / D-1)
- Ascendant (Lagna) calculated from birth time and location
- Positions of all 9 Vedic grahas (planets):
  - Sun (Surya), Moon (Chandra), Mars (Mangal), Mercury (Budha),
    Jupiter (Guru), Venus (Shukra), Saturn (Shani), Rahu, Ketu
- Each planet's position: rashi (sign), degree, nakshatra, nakshatra pada
- House placement (Bhava) for each planet
- Retrograde status for applicable planets

#### Nakshatras (27 Lunar Mansions)
- Moon's nakshatra at birth (Janma Nakshatra) — this is critical
- Nakshatra lord for each planet
- Pada (quarter) for each planet's nakshatra position

#### Divisional Charts (Varga Charts)
- D-1 (Rashi) — birth chart
- D-9 (Navamsha) — marriage, dharma, deeper soul purpose
- D-10 (Dashamsha) — career
- D-2 (Hora) — wealth
- D-3 (Drekkana) — siblings
- D-7 (Saptamsha) — children
- D-12 (Dwadashamsha) — parents
- D-30 (Trimsamsha) — misfortunes

#### Dasha System (Vimshottari Dasha)
- Full Vimshottari Maha Dasha sequence from birth
- Current Maha Dasha, Antar Dasha (Bhukti), and Pratyantar Dasha
- Start/end dates for each dasha period
- Dasha balance at birth (critical for timing)

#### Planetary Strengths
- Shadbala (six-fold strength) for each planet
- Ashtakavarga points (transit strength scoring)
  - Bhinnashtakavarga (individual planet contributions)
  - Sarvashtakavarga (aggregate scores per sign)
- Planetary dignity: own sign, exaltation, debilitation, moolatrikona
- Combustion status (proximity to Sun)
- Planetary war (Graha Yuddha) detection

#### Yogas (Planetary Combinations)
- Detect and describe major yogas:
  - Raja Yoga, Dhana Yoga, Gaja Kesari Yoga, Budhaditya Yoga,
    Pancha Mahapurusha Yogas (Ruchaka, Bhadra, Hamsa, Malavya, Shasha),
    Viparita Raja Yoga, Neecha Bhanga Raja Yoga, Kemadruma Yoga,
    Sade Sati status, Kaal Sarp Yoga/Dosha, Mangal Dosha
- Each yoga should include: name, planets involved, houses involved, strength assessment, and interpretation

#### Transit Analysis (Gochara)
- Current planetary positions (real-time sidereal)
- Transit planets overlaid on natal chart
- Vedha (obstruction) analysis for transits
- Ashtakavarga-based transit predictions
- Saturn transit (Sade Sati) tracking
- Jupiter transit analysis (through houses from Moon)
- Rahu/Ketu transit axis analysis

### Interpretation Engine

Readings should synthesize multiple factors — not just list positions. For any query:

1. Check relevant natal house(s) and lord(s)
2. Check current dasha/bhukti lord and its natal position
3. Check current transits to relevant houses
4. Check ashtakavarga score of the transited sign
5. Weigh all factors for a balanced interpretation

Topics to support:
- General life overview
- Career and profession
- Relationships and marriage
- Finances and wealth
- Health indicators
- Education
- Spirituality
- Timing of events (muhurta-style guidance)

## Tech Stack

- **Language**: Python 3.12+
- **Astronomical Engine**: Swiss Ephemeris via `pyswisseph` (swisseph) — this is the gold standard for Jyotish software
- **Database**: SQLite via `sqlite3` (stdlib)
- **Geocoding**: `geopy` (for birth location to lat/long/timezone)
- **Timezone**: `timezonefinder` + `pytz` / `zoneinfo`
- **CLI Interface**: `rich` for formatted terminal output
- **Future**: Web interface can be layered on later

## Database Schema (SQLite)

The database stores complete chart data so that follow-up questions, transit checks, and dasha lookups can be performed without recalculation.

### `persons` table
```sql
CREATE TABLE persons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    birth_date TEXT NOT NULL,          -- ISO 8601 date
    birth_time TEXT NOT NULL,          -- HH:MM:SS
    birth_timezone TEXT NOT NULL,      -- IANA timezone (e.g. America/New_York)
    birth_location TEXT NOT NULL,      -- Original location string
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

### `charts` table
```sql
CREATE TABLE charts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL REFERENCES persons(id),
    chart_type TEXT NOT NULL,           -- 'D1', 'D9', 'D10', etc.
    ayanamsha TEXT NOT NULL DEFAULT 'lahiri',
    ayanamsha_value REAL NOT NULL,     -- Ayanamsha degrees at birth
    ascendant_sign INTEGER NOT NULL,   -- 1-12 (Aries=1)
    ascendant_degree REAL NOT NULL,    -- Degree within sign
    julian_day REAL NOT NULL,          -- JD for the birth moment
    sidereal_time REAL NOT NULL,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(person_id, chart_type)
);
```

### `planet_positions` table
```sql
CREATE TABLE planet_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chart_id INTEGER NOT NULL REFERENCES charts(id),
    planet TEXT NOT NULL,              -- 'Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu'
    longitude REAL NOT NULL,           -- Absolute sidereal longitude (0-360)
    sign INTEGER NOT NULL,             -- 1-12
    sign_degree REAL NOT NULL,         -- Degree within sign (0-30)
    nakshatra INTEGER NOT NULL,        -- 1-27
    nakshatra_pada INTEGER NOT NULL,   -- 1-4
    nakshatra_lord TEXT NOT NULL,      -- Vimshottari lord of nakshatra
    house INTEGER NOT NULL,            -- 1-12 bhava placement
    is_retrograde BOOLEAN NOT NULL DEFAULT 0,
    speed REAL,                        -- Degrees per day
    dignity TEXT,                      -- 'exalted','own','moolatrikona','friendly','neutral','enemy','debilitated'
    is_combust BOOLEAN NOT NULL DEFAULT 0,
    UNIQUE(chart_id, planet)
);
```

### `dasha_periods` table
```sql
CREATE TABLE dasha_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL REFERENCES persons(id),
    level TEXT NOT NULL,               -- 'maha', 'antar', 'pratyantar'
    planet TEXT NOT NULL,              -- Dasha lord
    parent_id INTEGER REFERENCES dasha_periods(id),  -- NULL for maha
    start_date TEXT NOT NULL,          -- ISO 8601 datetime
    end_date TEXT NOT NULL,
    UNIQUE(person_id, level, planet, start_date)
);
```

### `ashtakavarga` table
```sql
CREATE TABLE ashtakavarga (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chart_id INTEGER NOT NULL REFERENCES charts(id),
    type TEXT NOT NULL,                -- 'bhinna' or 'sarva'
    contributing_planet TEXT,          -- NULL for sarva, planet name for bhinna
    sign INTEGER NOT NULL,             -- 1-12
    points INTEGER NOT NULL,           -- Bindus (0-8 for bhinna, 0-56 for sarva)
    UNIQUE(chart_id, type, contributing_planet, sign)
);
```

### `yogas` table
```sql
CREATE TABLE yogas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chart_id INTEGER NOT NULL REFERENCES charts(id),
    yoga_name TEXT NOT NULL,
    yoga_type TEXT NOT NULL,           -- 'raja','dhana','pancha_mahapurusha','dosha', etc.
    planets_involved TEXT NOT NULL,    -- JSON array of planet names
    houses_involved TEXT NOT NULL,     -- JSON array of house numbers
    strength TEXT,                     -- 'strong','moderate','weak'
    description TEXT NOT NULL
);
```

### `shadbala` table
```sql
CREATE TABLE shadbala (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chart_id INTEGER NOT NULL REFERENCES charts(id),
    planet TEXT NOT NULL,
    sthana_bala REAL NOT NULL,        -- Positional strength
    dig_bala REAL NOT NULL,           -- Directional strength
    kala_bala REAL NOT NULL,          -- Temporal strength
    chesta_bala REAL NOT NULL,        -- Motional strength
    naisargika_bala REAL NOT NULL,    -- Natural strength
    drik_bala REAL NOT NULL,          -- Aspectual strength
    total_shadbala REAL NOT NULL,
    shadbala_ratio REAL NOT NULL,     -- Total / Required minimum
    UNIQUE(chart_id, planet)
);
```

### `readings` table
```sql
CREATE TABLE readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER NOT NULL REFERENCES persons(id),
    reading_type TEXT NOT NULL,        -- 'birth_chart','transit','question','dasha'
    query TEXT,                        -- The user's question if applicable
    transit_date TEXT,                 -- Date of transit analysis if applicable
    reading_text TEXT NOT NULL,        -- Full reading output
    created_at TEXT DEFAULT (datetime('now'))
);
```

## Project Structure

```
vedia/
├── CLAUDE.md                  # This file
├── requirements.txt
├── vedia/
│   ├── __init__.py
│   ├── main.py               # CLI entry point
│   ├── db.py                 # SQLite database setup and queries
│   ├── models.py             # Data classes for charts, planets, etc.
│   ├── calc/
│   │   ├── __init__.py
│   │   ├── ephemeris.py      # Swiss Ephemeris wrapper (planet positions)
│   │   ├── ayanamsha.py      # Ayanamsha calculations
│   │   ├── houses.py         # House/Bhava calculations
│   │   ├── nakshatras.py     # Nakshatra lookups and calculations
│   │   ├── divisional.py     # Varga chart calculations (D-9, D-10, etc.)
│   │   ├── dashas.py         # Vimshottari dasha calculations
│   │   ├── shadbala.py       # Six-fold planetary strength
│   │   ├── ashtakavarga.py   # Ashtakavarga calculations
│   │   └── yogas.py          # Yoga detection engine
│   ├── transit/
│   │   ├── __init__.py
│   │   ├── current.py        # Real-time transit positions
│   │   ├── overlay.py        # Transit-to-natal overlay
│   │   └── vedha.py          # Vedha (obstruction) checks
│   ├── interpret/
│   │   ├── __init__.py
│   │   ├── synthesizer.py    # Multi-factor reading synthesis
│   │   ├── houses.py         # House significations
│   │   ├── planets.py        # Planet significations
│   │   ├── nakshatras.py     # Nakshatra interpretations
│   │   └── topics.py         # Topic-based reading generators
│   ├── geo.py                # Geocoding and timezone resolution
│   └── data/
│       ├── nakshatras.json   # Nakshatra reference data
│       ├── yogas.json        # Yoga definitions and rules
│       └── significations.json # House/planet signification data
├── tests/
│   ├── test_ephemeris.py
│   ├── test_dashas.py
│   ├── test_ashtakavarga.py
│   ├── test_yogas.py
│   └── fixtures/             # Known charts for validation
│       └── known_charts.json
└── vedia.db                  # SQLite database (created at runtime)
```

## Key Implementation Notes

### Swiss Ephemeris
- Use `swisseph.set_sid_mode(swisseph.SIDM_LAHIRI)` for Lahiri ayanamsha
- Rahu and Ketu are the **mean nodes** by default (`swisseph.MEAN_NODE`); support true node as option
- Always convert UTC birth time before passing to Swiss Ephemeris
- Ephemeris data files (`.se1`) must be available; use `swisseph.set_ephe_path()` or fallback to built-in Moshier ephemeris

### Accuracy Validation
- Validate against known charts (e.g., publicly available celebrity charts from established Jyotish software)
- Moon position must be accurate to within 1 degree (Moon moves ~13 deg/day, so time precision matters)
- Ascendant changes sign roughly every 2 hours — birth time accuracy is paramount

### Sign & House System
- Use **Whole Sign Houses** as default (most traditional for Jyotish)
- Sign numbering: Aries=1, Taurus=2, ... Pisces=12
- The ascendant sign IS the 1st house in whole-sign

### Aspects (Drishti)
- Use Vedic aspects (NOT Western aspects):
  - All planets aspect the 7th house from their position
  - Mars additionally aspects 4th and 8th
  - Jupiter additionally aspects 5th and 9th
  - Saturn additionally aspects 3rd and 10th
  - Rahu/Ketu: follow the convention of aspecting 5th, 7th, 9th (Jupiter-like)

### Ayanamsha
- Default to Lahiri (Chitrapaksha) but store the value used so charts can theoretically be recomputed with alternate ayanamshas if needed later

## CLI Usage (Target Interface)

```bash
# Create a new chart
python -m vedia new --name "John Doe" --date 1990-06-15 --time 14:30:00 --location "New York, NY"

# View birth chart
python -m vedia chart "John Doe"

# View current transits for a person
python -m vedia transit "John Doe"

# View dasha periods
python -m vedia dasha "John Doe"

# Ask a question (synthesized reading)
python -m vedia ask "John Doe" "How is my career looking this year?"

# List all stored persons
python -m vedia list
```

## Development Guidelines

- Write pure calculation functions that are testable without DB
- Store all intermediate data in SQLite so nothing needs recalculation
- Keep interpretation text separate from calculation logic
- Use dataclasses or Pydantic models for structured chart data
- All dates/times internally in UTC; convert for display only
- Ephemeris calculations are CPU-bound; cache aggressively in DB
- Transit positions should be calculated fresh (they change daily) but natal data is immutable once stored
