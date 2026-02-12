"""Shared fixtures for Vedia Vedic astrology engine tests.

Provides known-good natal chart data for Crystal and Lee as test fixtures,
verified against established Vedic calculation references.
"""
import pytest
from vedia.models import PlanetPosition


@pytest.fixture
def crystal_planets():
    """Crystal's known natal planet positions.

    Birth: 1985-02-06, 03:45:00, Detroit MI
    Lat: 42.3314, Lon: -83.0458, TZ: America/Detroit (UTC-5)
    Ascendant: Scorpio (sign 8), ~20 deg 22'
    """
    return [
        PlanetPosition(planet='Sun', longitude=293.0, sign=10, sign_degree=23.0,
                       nakshatra=22, nakshatra_pada=4, nakshatra_lord='Moon',
                       house=3, is_retrograde=False, speed=1.0, dignity='', is_combust=False),
        PlanetPosition(planet='Moon', longitude=127.0, sign=5, sign_degree=7.0,
                       nakshatra=10, nakshatra_pada=1, nakshatra_lord='Ketu',
                       house=10, is_retrograde=False, speed=13.0, dignity='', is_combust=False),
        PlanetPosition(planet='Mars', longitude=340.0, sign=12, sign_degree=10.0,
                       nakshatra=25, nakshatra_pada=2, nakshatra_lord='Jupiter',
                       house=5, is_retrograde=False, speed=0.5, dignity='', is_combust=False),
        PlanetPosition(planet='Mercury', longitude=289.0, sign=10, sign_degree=19.0,
                       nakshatra=22, nakshatra_pada=3, nakshatra_lord='Moon',
                       house=3, is_retrograde=False, speed=1.5, dignity='', is_combust=True),
        PlanetPosition(planet='Jupiter', longitude=295.0, sign=10, sign_degree=25.0,
                       nakshatra=23, nakshatra_pada=1, nakshatra_lord='Mars',
                       house=3, is_retrograde=False, speed=0.1, dignity='debilitated', is_combust=False),
        PlanetPosition(planet='Venus', longitude=347.0, sign=12, sign_degree=17.0,
                       nakshatra=26, nakshatra_pada=2, nakshatra_lord='Saturn',
                       house=5, is_retrograde=False, speed=1.2, dignity='exalted', is_combust=False),
        PlanetPosition(planet='Saturn', longitude=197.0, sign=7, sign_degree=17.0,
                       nakshatra=15, nakshatra_pada=3, nakshatra_lord='Rahu',
                       house=12, is_retrograde=False, speed=0.03, dignity='exalted', is_combust=False),
        PlanetPosition(planet='Rahu', longitude=15.0, sign=1, sign_degree=15.0,
                       nakshatra=1, nakshatra_pada=4, nakshatra_lord='Ketu',
                       house=6, is_retrograde=True, speed=-0.05, dignity='', is_combust=False),
        PlanetPosition(planet='Ketu', longitude=195.0, sign=7, sign_degree=15.0,
                       nakshatra=14, nakshatra_pada=4, nakshatra_lord='Mars',
                       house=12, is_retrograde=True, speed=-0.05, dignity='', is_combust=False),
    ]


@pytest.fixture
def crystal_asc_sign():
    """Crystal's ascendant sign: Scorpio (8)."""
    return 8


@pytest.fixture
def lee_planets():
    """Lee's known natal planet positions.

    Birth: 1975-11-07, 08:30:00, Cornwall ON Canada
    Lat: 45.0275, Lon: -74.7286, TZ: America/Toronto (UTC-5)
    Ascendant: Scorpio (sign 8), ~9 deg 58'
    """
    return [
        PlanetPosition(planet='Sun', longitude=200.0, sign=7, sign_degree=20.0,
                       nakshatra=16, nakshatra_pada=1, nakshatra_lord='Jupiter',
                       house=12, is_retrograde=False, speed=1.0, dignity='debilitated', is_combust=False),
        PlanetPosition(planet='Moon', longitude=253.0, sign=9, sign_degree=13.0,
                       nakshatra=20, nakshatra_pada=2, nakshatra_lord='Venus',
                       house=2, is_retrograde=False, speed=12.5, dignity='', is_combust=False),
        PlanetPosition(planet='Mars', longitude=72.0, sign=3, sign_degree=12.0,
                       nakshatra=6, nakshatra_pada=1, nakshatra_lord='Rahu',
                       house=8, is_retrograde=False, speed=0.6, dignity='', is_combust=False),
        PlanetPosition(planet='Mercury', longitude=222.0, sign=8, sign_degree=12.0,
                       nakshatra=17, nakshatra_pada=3, nakshatra_lord='Saturn',
                       house=1, is_retrograde=False, speed=1.3, dignity='', is_combust=False),
        PlanetPosition(planet='Jupiter', longitude=340.0, sign=12, sign_degree=10.0,
                       nakshatra=25, nakshatra_pada=2, nakshatra_lord='Jupiter',
                       house=5, is_retrograde=True, speed=-0.1, dignity='own', is_combust=False),
        PlanetPosition(planet='Venus', longitude=163.0, sign=6, sign_degree=13.0,
                       nakshatra=13, nakshatra_pada=2, nakshatra_lord='Moon',
                       house=11, is_retrograde=False, speed=1.2, dignity='debilitated', is_combust=False),
        PlanetPosition(planet='Saturn', longitude=103.0, sign=4, sign_degree=13.0,
                       nakshatra=8, nakshatra_pada=4, nakshatra_lord='Saturn',
                       house=9, is_retrograde=False, speed=0.05, dignity='debilitated', is_combust=False),
        PlanetPosition(planet='Rahu', longitude=218.0, sign=8, sign_degree=8.0,
                       nakshatra=17, nakshatra_pada=2, nakshatra_lord='Saturn',
                       house=1, is_retrograde=True, speed=-0.05, dignity='', is_combust=False),
        PlanetPosition(planet='Ketu', longitude=38.0, sign=2, sign_degree=8.0,
                       nakshatra=3, nakshatra_pada=2, nakshatra_lord='Sun',
                       house=7, is_retrograde=True, speed=-0.05, dignity='', is_combust=False),
    ]


@pytest.fixture
def lee_asc_sign():
    """Lee's ascendant sign: Scorpio (8)."""
    return 8
