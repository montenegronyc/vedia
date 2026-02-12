"""Tests for Vimshottari Dasha calculations.

Verifies the dasha system using Crystal's Moon longitude (~127 degrees)
in Magha nakshatra (lord = Ketu), and checks the full three-level
hierarchy: maha -> antar -> pratyantar.
"""
import pytest
from datetime import datetime
from vedia.calc.dashas import (
    calculate_full_dashas,
    get_current_dasha,
    calculate_dasha_balance,
    calculate_maha_dashas,
)
from vedia.models import DASHA_SEQUENCE, DASHA_YEARS


class TestDashaBalance:
    """Test calculation of the initial dasha balance at birth."""

    def test_crystal_starting_lord(self):
        """Crystal's Moon at ~127 deg -> nakshatra 9 (Magha) -> lord is Ketu."""
        lord, balance = calculate_dasha_balance(127.0)
        assert lord == 'Ketu'

    def test_crystal_balance_range(self):
        """Balance should be between 0 and Ketu's full period (7 years)."""
        lord, balance = calculate_dasha_balance(127.0)
        assert 0 < balance < 7.0

    def test_crystal_balance_value(self):
        """Crystal's balance: Moon at 127 deg.

        nakshatra index = int(127 / 13.3333) = 9
        offset_in_nakshatra = 127 % 13.3333 ~= 7.0003
        remaining_fraction = 1 - 7.0003/13.3333 ~= 0.475
        balance = 7 * 0.475 ~= 3.325 years
        """
        lord, balance = calculate_dasha_balance(127.0)
        assert abs(balance - 3.325) < 0.1

    def test_lee_starting_lord(self):
        """Lee's Moon at ~253 deg -> nakshatra index 18 (Mula) -> lord is Ketu.

        253 / 13.3333 = 18.975, so nakshatra index 18 (0-based).
        NAKSHATRA_LORDS[18] = 'Ketu' (Mula nakshatra).
        """
        lord, balance = calculate_dasha_balance(253.0)
        assert lord == 'Ketu'

    def test_zero_longitude(self):
        """Moon at 0 degrees -> Ashwini nakshatra -> lord is Ketu.

        At 0 degrees, full dasha period remains.
        """
        lord, balance = calculate_dasha_balance(0.0)
        assert lord == 'Ketu'
        assert abs(balance - 7.0) < 0.01


class TestMahaDashas:
    """Test maha dasha period generation."""

    def test_crystal_first_lord(self):
        """First maha dasha lord should be Ketu (Crystal's Magha nakshatra)."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_maha_dashas(127.0, birth_dt)
        assert dashas[0].planet == 'Ketu'
        assert dashas[0].level == 'maha'

    def test_crystal_dasha_sequence(self):
        """Maha dashas follow Vimshottari sequence starting from Ketu.

        The sequence wraps to cover the full 120-year cycle, so a second
        Ketu period appears at the end.
        """
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_maha_dashas(127.0, birth_dt)
        actual = [d.planet for d in dashas]
        # Standard sequence from Ketu, plus wrap-around
        expected_start = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
        assert actual[:9] == expected_start

    def test_covers_120_years(self):
        """Total dasha coverage should span at least 120 years."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_maha_dashas(127.0, birth_dt)
        first_start = dashas[0].start_date
        last_end = dashas[-1].end_date
        total_days = (last_end - first_start).total_seconds() / 86400.0
        total_years = total_days / 365.25
        assert total_years >= 120.0

    def test_consecutive_dates(self):
        """Each maha dasha should start exactly when the previous one ends."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_maha_dashas(127.0, birth_dt)
        for i in range(len(dashas) - 1):
            assert dashas[i].end_date == dashas[i + 1].start_date

    def test_starts_at_birth(self):
        """First dasha should start at the birth datetime."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_maha_dashas(127.0, birth_dt)
        assert dashas[0].start_date == birth_dt


class TestFullDashas:
    """Test the complete three-level dasha hierarchy."""

    def test_crystal_full_dashas(self):
        """Crystal's full dashas should have maha periods with sub-periods."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_dashas(127.0, birth_dt)
        assert len(dashas) >= 9
        assert dashas[0].planet == 'Ketu'
        assert dashas[0].level == 'maha'

    def test_sub_periods_exist(self):
        """Each maha dasha should have exactly 9 antar (sub) periods."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_dashas(127.0, birth_dt)
        for d in dashas:
            assert len(d.sub_periods) == 9, (
                f"Maha {d.planet} has {len(d.sub_periods)} antars, expected 9"
            )

    def test_pratyantar_periods_exist(self):
        """Each antar dasha should have exactly 9 pratyantar (sub-sub) periods."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_dashas(127.0, birth_dt)
        # Check first maha dasha's antar periods
        for antar in dashas[0].sub_periods:
            assert len(antar.sub_periods) == 9, (
                f"Antar {antar.planet} has {len(antar.sub_periods)} pratyantars, expected 9"
            )

    def test_antar_sequence_starts_from_maha_lord(self):
        """Antar periods within a maha should start from the maha lord."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_dashas(127.0, birth_dt)
        for maha in dashas:
            assert maha.sub_periods[0].planet == maha.planet

    def test_antar_dates_are_consecutive(self):
        """Antar periods within a maha should have consecutive dates."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_dashas(127.0, birth_dt)
        for maha in dashas:
            for i in range(len(maha.sub_periods) - 1):
                assert maha.sub_periods[i].end_date == maha.sub_periods[i + 1].start_date

    def test_antar_span_matches_maha(self):
        """Antar periods should collectively span the same duration as their maha."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_dashas(127.0, birth_dt)
        for maha in dashas:
            assert maha.sub_periods[0].start_date == maha.start_date
            # Allow tiny floating-point rounding in timedelta
            diff = abs((maha.sub_periods[-1].end_date - maha.end_date).total_seconds())
            assert diff < 1.0, f"Maha {maha.planet} end mismatch: {diff}s"


class TestGetCurrentDasha:
    """Test the current dasha lookup function."""

    def test_at_birth(self):
        """At birth, the current maha dasha should be the starting lord."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_dashas(127.0, birth_dt)
        current = get_current_dasha(dashas, birth_dt)
        assert current['maha'] is not None
        assert current['maha'].planet == 'Ketu'

    def test_at_birth_has_antar(self):
        """At birth, antar dasha should also be found."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_dashas(127.0, birth_dt)
        current = get_current_dasha(dashas, birth_dt)
        assert current['antar'] is not None
        assert current['antar'].planet == 'Ketu'  # Ketu/Ketu at start

    def test_at_birth_has_pratyantar(self):
        """At birth, pratyantar dasha should also be found."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_dashas(127.0, birth_dt)
        current = get_current_dasha(dashas, birth_dt)
        assert current['pratyantar'] is not None

    def test_later_date(self):
        """Querying a later date should return a different dasha period."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_dashas(127.0, birth_dt)
        # 10 years after birth, should be in Venus maha dasha
        # (Ketu balance ~3.3 years, then Venus 20 years)
        query_date = datetime(1995, 2, 6, 3, 45)
        current = get_current_dasha(dashas, query_date)
        assert current['maha'] is not None
        assert current['maha'].planet == 'Venus'

    def test_outside_range_returns_none(self):
        """A date far in the future (beyond 120 years) returns None maha."""
        birth_dt = datetime(1985, 2, 6, 3, 45)
        dashas = calculate_full_dashas(127.0, birth_dt)
        future_date = datetime(2200, 1, 1)
        current = get_current_dasha(dashas, future_date)
        assert current['maha'] is None


class TestLeesDashas:
    """Test dasha calculations using Lee's Moon longitude."""

    def test_lee_starting_lord(self):
        """Lee's Moon at 253 deg -> Mula nakshatra (index 18) -> lord is Ketu."""
        birth_dt = datetime(1975, 11, 7, 8, 30)
        dashas = calculate_full_dashas(253.0, birth_dt)
        assert dashas[0].planet == 'Ketu'

    def test_lee_sequence(self):
        """Lee's dasha sequence starts from Ketu (Mula nakshatra lord)."""
        birth_dt = datetime(1975, 11, 7, 8, 30)
        dashas = calculate_full_dashas(253.0, birth_dt)
        actual = [d.planet for d in dashas]
        # Ketu starts, then follows Vimshottari sequence
        expected_start = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
        assert actual[:9] == expected_start
