"""SQLite database setup and queries for Vedia."""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional

from .models import PlanetPosition, ChartData, DashaPeriod, YogaResult, ShadbalaResult

DB_PATH = Path(__file__).parent.parent / 'vedia.db'


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(conn: sqlite3.Connection):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS persons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        birth_date TEXT NOT NULL,
        birth_time TEXT NOT NULL,
        birth_timezone TEXT NOT NULL,
        birth_location TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS charts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL REFERENCES persons(id),
        chart_type TEXT NOT NULL,
        ayanamsha TEXT NOT NULL DEFAULT 'lahiri',
        ayanamsha_value REAL NOT NULL,
        ascendant_sign INTEGER NOT NULL,
        ascendant_degree REAL NOT NULL,
        julian_day REAL NOT NULL,
        sidereal_time REAL NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        UNIQUE(person_id, chart_type)
    );

    CREATE TABLE IF NOT EXISTS planet_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chart_id INTEGER NOT NULL REFERENCES charts(id),
        planet TEXT NOT NULL,
        longitude REAL NOT NULL,
        sign INTEGER NOT NULL,
        sign_degree REAL NOT NULL,
        nakshatra INTEGER NOT NULL,
        nakshatra_pada INTEGER NOT NULL,
        nakshatra_lord TEXT NOT NULL,
        house INTEGER NOT NULL,
        is_retrograde BOOLEAN NOT NULL DEFAULT 0,
        speed REAL,
        dignity TEXT,
        is_combust BOOLEAN NOT NULL DEFAULT 0,
        UNIQUE(chart_id, planet)
    );

    CREATE TABLE IF NOT EXISTS dasha_periods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL REFERENCES persons(id),
        level TEXT NOT NULL,
        planet TEXT NOT NULL,
        parent_id INTEGER REFERENCES dasha_periods(id),
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ashtakavarga (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chart_id INTEGER NOT NULL REFERENCES charts(id),
        type TEXT NOT NULL,
        contributing_planet TEXT,
        sign INTEGER NOT NULL,
        points INTEGER NOT NULL,
        UNIQUE(chart_id, type, contributing_planet, sign)
    );

    CREATE TABLE IF NOT EXISTS yogas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chart_id INTEGER NOT NULL REFERENCES charts(id),
        yoga_name TEXT NOT NULL,
        yoga_type TEXT NOT NULL,
        planets_involved TEXT NOT NULL,
        houses_involved TEXT NOT NULL,
        strength TEXT,
        description TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS shadbala (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chart_id INTEGER NOT NULL REFERENCES charts(id),
        planet TEXT NOT NULL,
        sthana_bala REAL NOT NULL,
        dig_bala REAL NOT NULL,
        kala_bala REAL NOT NULL,
        chesta_bala REAL NOT NULL,
        naisargika_bala REAL NOT NULL,
        drik_bala REAL NOT NULL,
        total_shadbala REAL NOT NULL,
        shadbala_ratio REAL NOT NULL,
        UNIQUE(chart_id, planet)
    );

    CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL REFERENCES persons(id),
        reading_type TEXT NOT NULL,
        query TEXT,
        transit_date TEXT,
        reading_text TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE INDEX IF NOT EXISTS idx_charts_person ON charts(person_id);
    CREATE INDEX IF NOT EXISTS idx_planets_chart ON planet_positions(chart_id);
    CREATE INDEX IF NOT EXISTS idx_dasha_person ON dasha_periods(person_id);
    CREATE INDEX IF NOT EXISTS idx_yogas_chart ON yogas(chart_id);
    """)
    conn.commit()


def save_person(conn: sqlite3.Connection, name: str, birth_date: str, birth_time: str,
                birth_timezone: str, birth_location: str, latitude: float, longitude: float) -> int:
    cur = conn.execute(
        "SELECT id FROM persons WHERE name = ? AND birth_date = ?",
        (name, birth_date)
    )
    row = cur.fetchone()
    if row:
        return row['id']
    cur = conn.execute(
        """INSERT INTO persons (name, birth_date, birth_time, birth_timezone,
           birth_location, latitude, longitude)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, birth_date, birth_time, birth_timezone, birth_location, latitude, longitude)
    )
    conn.commit()
    return cur.lastrowid


def save_chart(conn: sqlite3.Connection, person_id: int, chart: ChartData) -> int:
    cur = conn.execute(
        "SELECT id FROM charts WHERE person_id = ? AND chart_type = ?",
        (person_id, chart.chart_type)
    )
    row = cur.fetchone()
    if row:
        chart_id = row['id']
        conn.execute("DELETE FROM planet_positions WHERE chart_id = ?", (chart_id,))
        conn.execute(
            """UPDATE charts SET ayanamsha_value=?, ascendant_sign=?, ascendant_degree=?,
               julian_day=?, sidereal_time=? WHERE id=?""",
            (chart.ayanamsha_value, chart.ascendant_sign, chart.ascendant_degree,
             chart.julian_day, chart.sidereal_time, chart_id)
        )
    else:
        cur = conn.execute(
            """INSERT INTO charts (person_id, chart_type, ayanamsha, ayanamsha_value,
               ascendant_sign, ascendant_degree, julian_day, sidereal_time)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (person_id, chart.chart_type, chart.ayanamsha, chart.ayanamsha_value,
             chart.ascendant_sign, chart.ascendant_degree, chart.julian_day, chart.sidereal_time)
        )
        chart_id = cur.lastrowid

    for p in chart.planets:
        conn.execute(
            """INSERT INTO planet_positions (chart_id, planet, longitude, sign, sign_degree,
               nakshatra, nakshatra_pada, nakshatra_lord, house, is_retrograde, speed, dignity, is_combust)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (chart_id, p.planet, p.longitude, p.sign, p.sign_degree,
             p.nakshatra, p.nakshatra_pada, p.nakshatra_lord, p.house,
             p.is_retrograde, p.speed, p.dignity, p.is_combust)
        )
    conn.commit()
    return chart_id


def save_dasha_periods(conn: sqlite3.Connection, person_id: int, periods: list[DashaPeriod]):
    conn.execute("DELETE FROM dasha_periods WHERE person_id = ?", (person_id,))
    def _insert(period: DashaPeriod, parent_id=None):
        cur = conn.execute(
            """INSERT INTO dasha_periods (person_id, level, planet, parent_id, start_date, end_date)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (person_id, period.level, period.planet, parent_id,
             period.start_date.isoformat(), period.end_date.isoformat())
        )
        pid = cur.lastrowid
        for sub in period.sub_periods:
            _insert(sub, pid)
    for p in periods:
        _insert(p)
    conn.commit()


def save_yogas(conn: sqlite3.Connection, chart_id: int, yogas_list: list[YogaResult]):
    conn.execute("DELETE FROM yogas WHERE chart_id = ?", (chart_id,))
    for y in yogas_list:
        conn.execute(
            """INSERT INTO yogas (chart_id, yoga_name, yoga_type, planets_involved,
               houses_involved, strength, description)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (chart_id, y.yoga_name, y.yoga_type,
             json.dumps(y.planets_involved), json.dumps(y.houses_involved),
             y.strength, y.description)
        )
    conn.commit()


def save_ashtakavarga(conn: sqlite3.Connection, chart_id: int,
                       bhinna: dict, sarva: dict):
    conn.execute("DELETE FROM ashtakavarga WHERE chart_id = ?", (chart_id,))
    for planet, signs in bhinna.items():
        for sign, points in signs.items():
            conn.execute(
                "INSERT INTO ashtakavarga (chart_id, type, contributing_planet, sign, points) VALUES (?,?,?,?,?)",
                (chart_id, 'bhinna', planet, int(sign), points)
            )
    for sign, points in sarva.items():
        conn.execute(
            "INSERT INTO ashtakavarga (chart_id, type, contributing_planet, sign, points) VALUES (?,?,?,?,?)",
            (chart_id, 'sarva', None, int(sign), points)
        )
    conn.commit()


def save_shadbala(conn: sqlite3.Connection, chart_id: int, results: list[ShadbalaResult]):
    conn.execute("DELETE FROM shadbala WHERE chart_id = ?", (chart_id,))
    for s in results:
        conn.execute(
            """INSERT INTO shadbala (chart_id, planet, sthana_bala, dig_bala, kala_bala,
               chesta_bala, naisargika_bala, drik_bala, total_shadbala, shadbala_ratio)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (chart_id, s.planet, s.sthana_bala, s.dig_bala, s.kala_bala,
             s.chesta_bala, s.naisargika_bala, s.drik_bala, s.total_shadbala, s.shadbala_ratio)
        )
    conn.commit()


def save_reading(conn: sqlite3.Connection, person_id: int, reading_type: str,
                  reading_text: str, query: str = None, transit_date: str = None) -> int:
    cur = conn.execute(
        """INSERT INTO readings (person_id, reading_type, query, transit_date, reading_text)
           VALUES (?, ?, ?, ?, ?)""",
        (person_id, reading_type, query, transit_date, reading_text)
    )
    conn.commit()
    return cur.lastrowid


def get_person_by_name(conn: sqlite3.Connection, name: str) -> Optional[dict]:
    cur = conn.execute("SELECT * FROM persons WHERE name LIKE ?", (f'%{name}%',))
    row = cur.fetchone()
    return dict(row) if row else None


def get_chart(conn: sqlite3.Connection, person_id: int, chart_type: str = 'D1') -> Optional[dict]:
    cur = conn.execute(
        "SELECT * FROM charts WHERE person_id = ? AND chart_type = ?",
        (person_id, chart_type)
    )
    row = cur.fetchone()
    return dict(row) if row else None


def get_planet_positions(conn: sqlite3.Connection, chart_id: int) -> list[dict]:
    cur = conn.execute(
        "SELECT * FROM planet_positions WHERE chart_id = ? ORDER BY longitude",
        (chart_id,)
    )
    return [dict(r) for r in cur.fetchall()]


def get_dasha_periods(conn: sqlite3.Connection, person_id: int, level: str = None) -> list[dict]:
    if level:
        cur = conn.execute(
            "SELECT * FROM dasha_periods WHERE person_id = ? AND level = ? ORDER BY start_date",
            (person_id, level)
        )
    else:
        cur = conn.execute(
            "SELECT * FROM dasha_periods WHERE person_id = ? ORDER BY start_date",
            (person_id,)
        )
    return [dict(r) for r in cur.fetchall()]


def get_yogas(conn: sqlite3.Connection, chart_id: int) -> list[dict]:
    cur = conn.execute("SELECT * FROM yogas WHERE chart_id = ?", (chart_id,))
    return [dict(r) for r in cur.fetchall()]


def get_all_persons(conn: sqlite3.Connection) -> list[dict]:
    cur = conn.execute("SELECT * FROM persons ORDER BY name")
    return [dict(r) for r in cur.fetchall()]


def get_shadbala(conn: sqlite3.Connection, chart_id: int) -> list[dict]:
    cur = conn.execute("SELECT * FROM shadbala WHERE chart_id = ?", (chart_id,))
    return [dict(r) for r in cur.fetchall()]


def get_ashtakavarga(conn: sqlite3.Connection, chart_id: int, avtype: str = 'sarva') -> list[dict]:
    cur = conn.execute(
        "SELECT * FROM ashtakavarga WHERE chart_id = ? AND type = ?",
        (chart_id, avtype)
    )
    return [dict(r) for r in cur.fetchall()]
