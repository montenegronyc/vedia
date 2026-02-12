"""Integration tests for Vedia pipeline."""
import pytest
import sqlite3
from pathlib import Path
from datetime import datetime

from vedia.models import PlanetPosition, ChartData, YogaResult, ShadbalaResult
from vedia.db import (
    get_connection, init_db, save_person, save_chart,
    get_person_by_name, get_chart, get_planet_positions,
    save_yogas, save_shadbala, save_ashtakavarga,
)


@pytest.fixture
def test_db(tmp_path):
    """Create a temporary test database."""
    db_path = tmp_path / "test_vedia.db"
    conn = get_connection(db_path)
    init_db(conn)
    yield conn
    conn.close()


@pytest.fixture
def sample_planets():
    """Sample planet positions for testing."""
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


class TestDatabasePipeline:
    def test_save_and_retrieve_person(self, test_db):
        person_id = save_person(test_db, "Test Person", "2000-01-01", "12:00:00",
                               "America/New_York", "New York", 40.7128, -74.0060)
        assert person_id > 0
        person = get_person_by_name(test_db, "Test Person")
        assert person is not None
        assert person['name'] == "Test Person"

    def test_save_and_retrieve_chart(self, test_db, sample_planets):
        person_id = save_person(test_db, "Chart Test", "2000-01-01", "12:00:00",
                               "UTC", "London", 51.5074, -0.1278)
        chart_data = ChartData(
            person_name="Chart Test", birth_date="2000-01-01",
            birth_time="12:00:00", birth_timezone="UTC",
            birth_location="London", latitude=51.5074, longitude=-0.1278,
            chart_type='D1', ayanamsha='lahiri', ayanamsha_value=23.5,
            ascendant_sign=8, ascendant_degree=20.0,
            julian_day=2451545.0, sidereal_time=18.0,
            planets=sample_planets,
        )
        chart_id = save_chart(test_db, person_id, chart_data)
        assert chart_id > 0

        chart = get_chart(test_db, person_id, 'D1')
        assert chart is not None
        assert chart['ascendant_sign'] == 8

        planets = get_planet_positions(test_db, chart_id)
        assert len(planets) == 9

    def test_duplicate_person_returns_existing(self, test_db):
        id1 = save_person(test_db, "Dupe", "2000-01-01", "12:00:00",
                         "UTC", "London", 51.0, -0.1)
        id2 = save_person(test_db, "Dupe", "2000-01-01", "12:00:00",
                         "UTC", "London", 51.0, -0.1)
        assert id1 == id2

    def test_chart_upsert(self, test_db, sample_planets):
        person_id = save_person(test_db, "Upsert", "2000-01-01", "12:00:00",
                               "UTC", "London", 51.0, -0.1)
        chart_data = ChartData(
            person_name="Upsert", birth_date="2000-01-01",
            birth_time="12:00:00", birth_timezone="UTC",
            birth_location="London", latitude=51.0, longitude=-0.1,
            chart_type='D1', ayanamsha='lahiri', ayanamsha_value=23.5,
            ascendant_sign=8, ascendant_degree=20.0,
            julian_day=2451545.0, sidereal_time=18.0,
            planets=sample_planets,
        )
        id1 = save_chart(test_db, person_id, chart_data)
        id2 = save_chart(test_db, person_id, chart_data)
        assert id1 == id2  # Should update, not create new


class TestYogaDetection:
    def test_full_pipeline(self, sample_planets):
        from vedia.calc.yogas import detect_all_yogas
        yogas = detect_all_yogas(sample_planets, 8)
        assert isinstance(yogas, list)
        for y in yogas:
            assert isinstance(y, YogaResult)
            assert y.yoga_name
            assert y.yoga_type in ('benefic', 'dosha', 'transit_dosha')

    def test_save_and_retrieve_yogas(self, test_db, sample_planets):
        from vedia.calc.yogas import detect_all_yogas
        person_id = save_person(test_db, "Yoga Test", "2000-01-01", "12:00:00",
                               "UTC", "London", 51.0, -0.1)
        chart_data = ChartData(
            person_name="Yoga Test", birth_date="2000-01-01",
            birth_time="12:00:00", birth_timezone="UTC",
            birth_location="London", latitude=51.0, longitude=-0.1,
            chart_type='D1', ayanamsha='lahiri', ayanamsha_value=23.5,
            ascendant_sign=8, ascendant_degree=20.0,
            julian_day=2451545.0, sidereal_time=18.0,
            planets=sample_planets,
        )
        chart_id = save_chart(test_db, person_id, chart_data)
        yogas = detect_all_yogas(sample_planets, 8)
        save_yogas(test_db, chart_id, yogas)
        from vedia.db import get_yogas
        saved = get_yogas(test_db, chart_id)
        assert len(saved) == len(yogas)


class TestSynastry:
    def test_analyze_synastry(self):
        from vedia.interpret.synastry import analyze_synastry
        p1 = [
            PlanetPosition(planet='Moon', longitude=127.0, sign=5, sign_degree=7.0,
                          nakshatra=10, nakshatra_pada=1, nakshatra_lord='Ketu',
                          house=10),
            PlanetPosition(planet='Venus', longitude=347.0, sign=12, sign_degree=17.0,
                          nakshatra=26, nakshatra_pada=2, nakshatra_lord='Saturn',
                          house=5, dignity='exalted'),
            PlanetPosition(planet='Mars', longitude=340.0, sign=12, sign_degree=10.0,
                          nakshatra=25, nakshatra_pada=2, nakshatra_lord='Jupiter',
                          house=5),
            PlanetPosition(planet='Sun', longitude=293.0, sign=10, sign_degree=23.0,
                          nakshatra=22, nakshatra_pada=4, nakshatra_lord='Moon', house=3),
            PlanetPosition(planet='Mercury', longitude=289.0, sign=10, sign_degree=19.0,
                          nakshatra=22, nakshatra_pada=3, nakshatra_lord='Moon', house=3),
            PlanetPosition(planet='Jupiter', longitude=295.0, sign=10, sign_degree=25.0,
                          nakshatra=23, nakshatra_pada=1, nakshatra_lord='Mars', house=3),
            PlanetPosition(planet='Saturn', longitude=197.0, sign=7, sign_degree=17.0,
                          nakshatra=15, nakshatra_pada=3, nakshatra_lord='Rahu', house=12),
            PlanetPosition(planet='Rahu', longitude=15.0, sign=1, sign_degree=15.0,
                          nakshatra=1, nakshatra_pada=4, nakshatra_lord='Ketu', house=6),
            PlanetPosition(planet='Ketu', longitude=195.0, sign=7, sign_degree=15.0,
                          nakshatra=14, nakshatra_pada=4, nakshatra_lord='Mars', house=12),
        ]
        p2 = [
            PlanetPosition(planet='Moon', longitude=253.0, sign=9, sign_degree=13.0,
                          nakshatra=20, nakshatra_pada=2, nakshatra_lord='Venus',
                          house=2),
            PlanetPosition(planet='Venus', longitude=163.0, sign=6, sign_degree=13.0,
                          nakshatra=13, nakshatra_pada=2, nakshatra_lord='Moon',
                          house=11, dignity='debilitated'),
            PlanetPosition(planet='Mars', longitude=72.0, sign=3, sign_degree=12.0,
                          nakshatra=6, nakshatra_pada=1, nakshatra_lord='Rahu', house=8),
            PlanetPosition(planet='Sun', longitude=200.0, sign=7, sign_degree=20.0,
                          nakshatra=16, nakshatra_pada=1, nakshatra_lord='Jupiter', house=12),
            PlanetPosition(planet='Mercury', longitude=222.0, sign=8, sign_degree=12.0,
                          nakshatra=17, nakshatra_pada=3, nakshatra_lord='Saturn', house=1),
            PlanetPosition(planet='Jupiter', longitude=340.0, sign=12, sign_degree=10.0,
                          nakshatra=25, nakshatra_pada=2, nakshatra_lord='Jupiter', house=5),
            PlanetPosition(planet='Saturn', longitude=103.0, sign=4, sign_degree=13.0,
                          nakshatra=8, nakshatra_pada=4, nakshatra_lord='Saturn', house=9),
            PlanetPosition(planet='Rahu', longitude=218.0, sign=8, sign_degree=8.0,
                          nakshatra=17, nakshatra_pada=2, nakshatra_lord='Saturn', house=1),
            PlanetPosition(planet='Ketu', longitude=38.0, sign=2, sign_degree=8.0,
                          nakshatra=3, nakshatra_pada=2, nakshatra_lord='Sun', house=7),
        ]
        result = analyze_synastry(p1, 8, 10, p2, 8, 20)
        assert 'guna_milan' in result
        assert 'overall_score' in result
        assert 0 <= result['overall_score'] <= 100
        assert result['guna_milan']['total'] <= 36
        assert result['assessment'] in ('Excellent', 'Good', 'Average', 'Challenging')


class TestMuhurta:
    def test_evaluate_muhurta(self):
        from vedia.calc.muhurta import evaluate_muhurta
        natal = [
            PlanetPosition(planet='Moon', longitude=127.0, sign=5, sign_degree=7.0,
                          nakshatra=10, nakshatra_pada=1, nakshatra_lord='Ketu', house=10),
            PlanetPosition(planet='Sun', longitude=293.0, sign=10, sign_degree=23.0,
                          nakshatra=22, nakshatra_pada=4, nakshatra_lord='Moon', house=3),
            PlanetPosition(planet='Jupiter', longitude=295.0, sign=10, sign_degree=25.0,
                          nakshatra=23, nakshatra_pada=1, nakshatra_lord='Mars', house=3),
            PlanetPosition(planet='Saturn', longitude=197.0, sign=7, sign_degree=17.0,
                          nakshatra=15, nakshatra_pada=3, nakshatra_lord='Rahu', house=12),
            PlanetPosition(planet='Mars', longitude=340.0, sign=12, sign_degree=10.0,
                          nakshatra=25, nakshatra_pada=2, nakshatra_lord='Jupiter', house=5),
            PlanetPosition(planet='Venus', longitude=347.0, sign=12, sign_degree=17.0,
                          nakshatra=26, nakshatra_pada=2, nakshatra_lord='Saturn', house=5),
            PlanetPosition(planet='Mercury', longitude=289.0, sign=10, sign_degree=19.0,
                          nakshatra=22, nakshatra_pada=3, nakshatra_lord='Moon', house=3),
            PlanetPosition(planet='Rahu', longitude=15.0, sign=1, sign_degree=15.0,
                          nakshatra=1, nakshatra_pada=4, nakshatra_lord='Ketu', house=6),
            PlanetPosition(planet='Ketu', longitude=195.0, sign=7, sign_degree=15.0,
                          nakshatra=14, nakshatra_pada=4, nakshatra_lord='Mars', house=12),
        ]
        # Use the same planets as transit for simplicity
        transit = natal[:]
        target = datetime(2026, 4, 30)
        result = evaluate_muhurta(natal, 8, 5, transit, target, 'court', dasha_lord='Jupiter')
        assert 'total_score' in result
        assert 'auspiciousness' in result
        assert 0 <= result['total_score'] <= 100


class TestRemedies:
    def test_get_remedies(self, sample_planets):
        from vedia.interpret.remedies import get_remedies, format_remedies_text
        remedies = get_remedies(sample_planets, 8, active_dasha_lords=['Rahu'])
        assert isinstance(remedies, list)
        # Should recommend for debilitated Jupiter at minimum
        planets_needing = [r['planet'] for r in remedies]
        assert 'Rahu' in planets_needing  # active dasha lord

        text = format_remedies_text(remedies)
        assert isinstance(text, str)
        assert len(text) > 0


class TestTransitOverlay:
    def test_overlay(self, sample_planets):
        from vedia.transit.overlay import overlay_transits, get_transit_summary
        transit = sample_planets[:]  # Use natal as transit for test
        overlay = overlay_transits(sample_planets, transit, 8)
        assert len(overlay) == 9
        for entry in overlay:
            assert 'transit_planet' in entry
            assert 'natal_house' in entry

    def test_transit_summary(self, sample_planets):
        from vedia.transit.overlay import get_transit_summary
        summary = get_transit_summary(sample_planets, sample_planets, 8)
        assert '_special' in summary
        assert 'sade_sati' in summary['_special']


class TestVedha:
    def test_analyze_all_vedha(self, sample_planets):
        from vedia.transit.vedha import analyze_all_vedha
        results = analyze_all_vedha(sample_planets, 5)  # Moon sign = Leo
        assert len(results) == 9
        for r in results:
            assert 'planet' in r
            assert 'has_vedha' in r
            assert 'is_benefic_transit' in r
