"""Data models for Vedic astrology calculations."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']

SIGNS = [
    '', 'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

SIGN_LORDS = {
    1: 'Mars', 2: 'Venus', 3: 'Mercury', 4: 'Moon', 5: 'Sun', 6: 'Mercury',
    7: 'Venus', 8: 'Mars', 9: 'Jupiter', 10: 'Saturn', 11: 'Saturn', 12: 'Jupiter'
}

NAKSHATRA_NAMES = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

NAKSHATRA_LORDS = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu',
    'Jupiter', 'Saturn', 'Mercury', 'Ketu', 'Venus', 'Sun',
    'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Saturn',
    'Jupiter', 'Saturn', 'Mercury'
]

# Vimshottari dasha years for each planet
DASHA_YEARS = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}

DASHA_SEQUENCE = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']

# Exaltation signs (sign number)
EXALTATION = {
    'Sun': 1, 'Moon': 2, 'Mars': 10, 'Mercury': 6,
    'Jupiter': 4, 'Venus': 12, 'Saturn': 7, 'Rahu': 3, 'Ketu': 9
}

# Debilitation signs
DEBILITATION = {
    'Sun': 7, 'Moon': 8, 'Mars': 4, 'Mercury': 12,
    'Jupiter': 10, 'Venus': 6, 'Saturn': 1, 'Rahu': 9, 'Ketu': 3
}

# Own signs
OWN_SIGNS = {
    'Sun': [5], 'Moon': [4], 'Mars': [1, 8], 'Mercury': [3, 6],
    'Jupiter': [9, 12], 'Venus': [2, 7], 'Saturn': [10, 11],
    'Rahu': [11], 'Ketu': [8]
}

# Moolatrikona signs and degree ranges (sign, start_deg, end_deg)
MOOLATRIKONA = {
    'Sun': (5, 0, 20), 'Moon': (2, 3, 30), 'Mars': (1, 0, 12),
    'Mercury': (6, 15, 20), 'Jupiter': (9, 0, 10), 'Venus': (7, 0, 15),
    'Saturn': (11, 0, 20)
}

# Friendly/enemy relationships (natural)
NATURAL_FRIENDS = {
    'Sun': ['Moon', 'Mars', 'Jupiter'],
    'Moon': ['Sun', 'Mercury'],
    'Mars': ['Sun', 'Moon', 'Jupiter'],
    'Mercury': ['Sun', 'Venus'],
    'Jupiter': ['Sun', 'Moon', 'Mars'],
    'Venus': ['Mercury', 'Saturn'],
    'Saturn': ['Mercury', 'Venus'],
    'Rahu': ['Mercury', 'Venus', 'Saturn'],
    'Ketu': ['Mars', 'Jupiter']
}

NATURAL_ENEMIES = {
    'Sun': ['Venus', 'Saturn'],
    'Moon': [],
    'Mars': ['Mercury'],
    'Mercury': ['Moon'],
    'Jupiter': ['Mercury', 'Venus'],
    'Venus': ['Sun', 'Moon'],
    'Saturn': ['Sun', 'Moon', 'Mars'],
    'Rahu': ['Sun', 'Moon', 'Mars'],
    'Ketu': ['Mercury', 'Venus']
}

# Combustion thresholds (degrees from Sun)
COMBUSTION_DEGREES = {
    'Moon': 12, 'Mars': 17, 'Mercury': 14, 'Jupiter': 11, 'Venus': 10, 'Saturn': 15
}


@dataclass
class PlanetPosition:
    planet: str
    longitude: float          # Absolute sidereal longitude 0-360
    sign: int                 # 1-12
    sign_degree: float        # 0-30
    nakshatra: int            # 1-27
    nakshatra_pada: int       # 1-4
    nakshatra_lord: str
    house: int                # 1-12
    is_retrograde: bool = False
    speed: float = 0.0
    dignity: str = ''         # exalted, own, moolatrikona, friendly, neutral, enemy, debilitated
    is_combust: bool = False


@dataclass
class ChartData:
    person_name: str
    birth_date: str
    birth_time: str
    birth_timezone: str
    birth_location: str
    latitude: float
    longitude: float
    chart_type: str = 'D1'
    ayanamsha: str = 'lahiri'
    ayanamsha_value: float = 0.0
    ascendant_sign: int = 0
    ascendant_degree: float = 0.0
    julian_day: float = 0.0
    sidereal_time: float = 0.0
    planets: list[PlanetPosition] = field(default_factory=list)


@dataclass
class DashaPeriod:
    level: str                # 'maha', 'antar', 'pratyantar'
    planet: str
    start_date: datetime = None
    end_date: datetime = None
    sub_periods: list['DashaPeriod'] = field(default_factory=list)


@dataclass
class YogaResult:
    yoga_name: str
    yoga_type: str
    planets_involved: list[str]
    houses_involved: list[int]
    strength: str = 'moderate'
    description: str = ''


@dataclass
class ShadbalaResult:
    planet: str
    sthana_bala: float = 0.0
    dig_bala: float = 0.0
    kala_bala: float = 0.0
    chesta_bala: float = 0.0
    naisargika_bala: float = 0.0
    drik_bala: float = 0.0
    total_shadbala: float = 0.0
    shadbala_ratio: float = 0.0
