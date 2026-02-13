"""Tests for Yogini Dasha calculations."""

from datetime import datetime
import pytest

from vedia.calc.dashas import (
    calculate_yogini_starting_index,
    calculate_yogini_balance,
    calculate_yogini_maha_dashas,
    calculate_full_yogini_dashas,
    get_current_yogini_dasha,
)
from vedia.models import YOGINI_NAMES, YOGINI_YEARS, YOGINI_LORDS


class TestYoginiStartingIndex:
    """Test Yogini starting index calculation from birth nakshatra."""

    def test_nakshatra_1(self):
        # (1 + 3) % 8 = 4 -> index 4 = Bhadrika
        assert calculate_yogini_starting_index(1) == 4
        assert YOGINI_NAMES[4] == 'Bhadrika'

    def test_nakshatra_5(self):
        # (5 + 3) % 8 = 0 -> index 0 = Mangala
        assert calculate_yogini_starting_index(5) == 0
        assert YOGINI_NAMES[0] == 'Mangala'

    def test_nakshatra_10_magha(self):
        # Crystal: Magha nakshatra = 10. (10 + 3) % 8 = 5 -> Ulka
        assert calculate_yogini_starting_index(10) == 5
        assert YOGINI_NAMES[5] == 'Ulka'

    def test_nakshatra_19_mula(self):
        # Lee: Mula nakshatra = 19. (19 + 3) % 8 = 6 -> Siddha
        assert calculate_yogini_starting_index(19) == 6
        assert YOGINI_NAMES[6] == 'Siddha'

    def test_all_nakshatras_valid(self):
        for nak in range(1, 28):
            idx = calculate_yogini_starting_index(nak)
            assert 0 <= idx <= 7


class TestYoginiBalance:
    """Test Yogini dasha balance at birth."""

    def test_crystal_balance(self):
        # Crystal: Moon at ~127 degrees
        yogini_name, balance = calculate_yogini_balance(127.0)
        assert yogini_name in YOGINI_NAMES
        assert 0 < balance <= YOGINI_YEARS[yogini_name]

    def test_lee_balance(self):
        # Lee: Moon at ~253 degrees
        yogini_name, balance = calculate_yogini_balance(253.0)
        assert yogini_name in YOGINI_NAMES
        assert 0 < balance <= YOGINI_YEARS[yogini_name]

    def test_start_of_nakshatra_full_balance(self):
        # At exact start of nakshatra, balance should be (nearly) full period
        yogini_name, balance = calculate_yogini_balance(0.0)
        assert balance == pytest.approx(YOGINI_YEARS[yogini_name], rel=0.01)

    def test_end_of_nakshatra_minimal_balance(self):
        # Just before end of first nakshatra (13.333 deg), balance should be near zero
        yogini_name, balance = calculate_yogini_balance(13.33)
        assert balance < 0.1  # Very small balance remaining

    def test_boundary_360(self):
        yogini_name, balance = calculate_yogini_balance(359.9)
        assert yogini_name in YOGINI_NAMES
        assert balance > 0


class TestYoginiMahaDashas:
    """Test Yogini maha dasha period calculations."""

    def test_covers_120_years(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_yogini_maha_dashas(127.0, birth_dt)
        total_days = (dashas[-1].end_date - dashas[0].start_date).total_seconds() / 86400
        assert total_days / 365.25 >= 120

    def test_starts_at_birth(self):
        birth_dt = datetime(1975, 11, 7, 8, 30)
        dashas = calculate_yogini_maha_dashas(253.0, birth_dt)
        assert dashas[0].start_date == birth_dt

    def test_consecutive_dates(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_yogini_maha_dashas(127.0, birth_dt)
        for i in range(len(dashas) - 1):
            assert dashas[i].end_date == dashas[i + 1].start_date

    def test_all_maha_level(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_yogini_maha_dashas(127.0, birth_dt)
        for d in dashas:
            assert d.level == 'maha'

    def test_valid_yogini_names(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_yogini_maha_dashas(127.0, birth_dt)
        for d in dashas:
            assert d.yogini_name in YOGINI_NAMES
            assert d.lord == YOGINI_LORDS[d.yogini_name]

    def test_first_dasha_is_balance(self):
        birth_dt = datetime(1975, 11, 7, 8, 30)
        dashas = calculate_yogini_maha_dashas(253.0, birth_dt)
        yogini_name, balance = calculate_yogini_balance(253.0)
        assert dashas[0].yogini_name == yogini_name
        first_duration_years = (dashas[0].end_date - dashas[0].start_date).total_seconds() / (86400 * 365.25)
        assert first_duration_years == pytest.approx(balance, rel=0.01)


class TestYoginiFullDashas:
    """Test complete Yogini dasha hierarchy."""

    def test_sub_periods_exist(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_yogini_dashas(127.0, birth_dt)
        for d in dashas:
            assert len(d.sub_periods) == 8

    def test_pratyantar_exists(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_yogini_dashas(127.0, birth_dt)
        for antar in dashas[0].sub_periods:
            assert len(antar.sub_periods) == 8

    def test_antar_level(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_yogini_dashas(127.0, birth_dt)
        for antar in dashas[0].sub_periods:
            assert antar.level == 'antar'

    def test_pratyantar_level(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_yogini_dashas(127.0, birth_dt)
        for antar in dashas[0].sub_periods:
            for prat in antar.sub_periods:
                assert prat.level == 'pratyantar'

    def test_antar_consecutive(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_yogini_dashas(127.0, birth_dt)
        antars = dashas[0].sub_periods
        for i in range(len(antars) - 1):
            assert antars[i].end_date == antars[i + 1].start_date

    def test_antar_spans_maha(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_yogini_dashas(127.0, birth_dt)
        maha = dashas[1]  # Use second (full-period) maha
        assert maha.sub_periods[0].start_date == maha.start_date
        # Last antar end should match maha end (within rounding)
        diff = abs((maha.sub_periods[-1].end_date - maha.end_date).total_seconds())
        assert diff < 2  # Less than 2 seconds rounding error


class TestGetCurrentYoginiDasha:
    """Test finding active Yogini dashas at a date."""

    def test_finds_current(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_yogini_dashas(127.0, birth_dt)
        current = get_current_yogini_dasha(dashas, datetime(2026, 2, 13))
        assert current['maha'] is not None
        assert current['antar'] is not None
        assert current['pratyantar'] is not None

    def test_returns_none_outside_range(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_yogini_dashas(127.0, birth_dt)
        # Way before birth
        current = get_current_yogini_dasha(dashas, datetime(1900, 1, 1))
        assert current['maha'] is None

    def test_at_birth(self):
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_yogini_dashas(127.0, birth_dt)
        current = get_current_yogini_dasha(dashas, birth_dt)
        assert current['maha'] is not None
        assert current['maha'].yogini_name == dashas[0].yogini_name
