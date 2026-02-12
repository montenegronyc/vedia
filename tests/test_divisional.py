"""Tests for divisional chart (varga) calculations.

Covers D2 (Hora), D3 (Drekkana), D9 (Navamsha), and the general
dispatcher and full-chart calculation functions.
"""
import pytest
from vedia.calc.divisional import (
    calculate_d9_position,
    calculate_d2_position,
    calculate_d3_position,
    get_divisional_sign,
    calculate_divisional_chart,
    SUPPORTED_VARGAS,
)


class TestNavamsha:
    """Test D9 (Navamsha) calculations.

    Navamsha divides each sign into 9 padas of 3 deg 20 min.
    Starting sign depends on element: Fire->Aries, Earth->Capricorn,
    Air->Libra, Water->Cancer.
    """

    def test_aries_0_degrees(self):
        """Aries (fire) at 0 deg -> pada 0 -> Aries."""
        assert calculate_d9_position(1, 0.0) == 1

    def test_aries_3_33_degrees(self):
        """Aries at 3.34 deg -> pada 1 -> Taurus."""
        assert calculate_d9_position(1, 3.34) == 2

    def test_fire_sign_start(self):
        """All fire signs (Aries, Leo, Sagittarius) start from Aries."""
        assert calculate_d9_position(1, 0.0) == 1
        assert calculate_d9_position(5, 0.0) == 1
        assert calculate_d9_position(9, 0.0) == 1

    def test_earth_sign_start(self):
        """Earth signs (Taurus, Virgo, Capricorn) start from Capricorn."""
        assert calculate_d9_position(2, 0.0) == 10
        assert calculate_d9_position(6, 0.0) == 10
        assert calculate_d9_position(10, 0.0) == 10

    def test_water_sign_start(self):
        """Water signs (Cancer, Scorpio, Pisces) start from Cancer."""
        assert calculate_d9_position(4, 0.0) == 4
        assert calculate_d9_position(8, 0.0) == 4
        assert calculate_d9_position(12, 0.0) == 4

    def test_air_sign_start(self):
        """Air signs (Gemini, Libra, Aquarius) start from Libra."""
        assert calculate_d9_position(3, 0.0) == 7
        assert calculate_d9_position(7, 0.0) == 7
        assert calculate_d9_position(11, 0.0) == 7

    def test_last_pada_wraps(self):
        """The last pada of a sign should wrap around correctly."""
        # Aries at 29.5 deg -> pada 8 (last) -> ((1-1+8)%12)+1 = 9 (Sagittarius)
        assert calculate_d9_position(1, 29.5) == 9

    def test_boundary_degree(self):
        """Degree at exact boundary between padas.

        At exactly 3.3333 degrees: pada = int(3.3333/3.3333) = 1 -> Taurus.
        """
        assert calculate_d9_position(1, 3.3334) == 2

    def test_all_signs_valid(self):
        """Every sign at multiple degrees produces a valid navamsha sign."""
        for sign in range(1, 13):
            for deg in [0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 29.0]:
                result = calculate_d9_position(sign, deg)
                assert 1 <= result <= 12, f"sign={sign}, deg={deg}, result={result}"


class TestHora:
    """Test D2 (Hora) calculations.

    Each sign is divided into two halves of 15 degrees.
    Odd signs: first half -> Leo, second half -> Cancer.
    Even signs: first half -> Cancer, second half -> Leo.
    """

    def test_odd_sign_first_half(self):
        """Aries (odd) at 7 deg -> first half -> Leo (5)."""
        assert calculate_d2_position(1, 7.0) == 5

    def test_odd_sign_second_half(self):
        """Aries (odd) at 20 deg -> second half -> Cancer (4)."""
        assert calculate_d2_position(1, 20.0) == 4

    def test_even_sign_first_half(self):
        """Taurus (even) at 7 deg -> first half -> Cancer (4)."""
        assert calculate_d2_position(2, 7.0) == 4

    def test_even_sign_second_half(self):
        """Taurus (even) at 20 deg -> second half -> Leo (5)."""
        assert calculate_d2_position(2, 20.0) == 5

    def test_result_always_cancer_or_leo(self):
        """Hora always returns either Cancer (4) or Leo (5)."""
        for sign in range(1, 13):
            for deg in [0.0, 7.0, 14.9, 15.0, 22.0, 29.0]:
                result = calculate_d2_position(sign, deg)
                assert result in (4, 5), f"sign={sign}, deg={deg}, result={result}"


class TestDrekkana:
    """Test D3 (Drekkana) calculations.

    Each sign is divided into three decanates of 10 degrees.
    First decanate: same sign.
    Second decanate: 5th from the sign.
    Third decanate: 9th from the sign.
    """

    def test_first_decanate(self):
        """Aries at 5 deg -> 1st decanate -> same sign (Aries)."""
        assert calculate_d3_position(1, 5.0) == 1

    def test_second_decanate(self):
        """Aries at 15 deg -> 2nd decanate -> 5th from Aries = Leo (5)."""
        assert calculate_d3_position(1, 15.0) == 5

    def test_third_decanate(self):
        """Aries at 25 deg -> 3rd decanate -> 9th from Aries = Sagittarius (9)."""
        assert calculate_d3_position(1, 25.0) == 9

    def test_taurus_decanates(self):
        """Taurus decanates: Taurus, Virgo, Capricorn."""
        assert calculate_d3_position(2, 5.0) == 2   # same sign
        assert calculate_d3_position(2, 15.0) == 6   # 5th from Taurus = Virgo
        assert calculate_d3_position(2, 25.0) == 10  # 9th from Taurus = Capricorn

    def test_all_results_valid(self):
        """Every sign and decanate produces a valid sign (1-12)."""
        for sign in range(1, 13):
            for deg in [5.0, 15.0, 25.0]:
                result = calculate_d3_position(sign, deg)
                assert 1 <= result <= 12


class TestDivisionalSign:
    """Test the get_divisional_sign dispatcher."""

    def test_all_supported(self):
        """Every supported varga type returns a valid sign."""
        for varga in SUPPORTED_VARGAS:
            result = get_divisional_sign(1, 15.0, varga)
            assert 1 <= result <= 12

    def test_unsupported_raises(self):
        """An unsupported varga type raises ValueError."""
        with pytest.raises(ValueError):
            get_divisional_sign(1, 15.0, 'D99')

    def test_case_insensitive(self):
        """Chart type should be case-insensitive."""
        result_upper = get_divisional_sign(1, 15.0, 'D9')
        result_lower = get_divisional_sign(1, 15.0, 'd9')
        assert result_upper == result_lower

    def test_d9_matches_direct(self):
        """Dispatcher D9 result should match direct calculate_d9_position."""
        for sign in range(1, 13):
            for deg in [0.0, 10.0, 20.0]:
                assert get_divisional_sign(sign, deg, 'D9') == calculate_d9_position(sign, deg)


class TestFullDivisionalChart:
    """Test calculate_divisional_chart for full D9 charts."""

    def test_d9_chart_length(self, crystal_planets, crystal_asc_sign):
        """D9 chart should have same number of planets as input."""
        d9 = calculate_divisional_chart(crystal_planets, 'D9', crystal_asc_sign, 20.0)
        assert len(d9) == len(crystal_planets)

    def test_d9_chart_valid_signs(self, crystal_planets, crystal_asc_sign):
        """All D9 planet positions should have valid signs and houses."""
        d9 = calculate_divisional_chart(crystal_planets, 'D9', crystal_asc_sign, 20.0)
        for p in d9:
            assert 1 <= p.sign <= 12
            assert 1 <= p.house <= 12

    def test_d9_preserves_planet_names(self, crystal_planets, crystal_asc_sign):
        """D9 chart should preserve the original planet names."""
        d9 = calculate_divisional_chart(crystal_planets, 'D9', crystal_asc_sign, 20.0)
        input_names = [p.planet for p in crystal_planets]
        output_names = [p.planet for p in d9]
        assert input_names == output_names

    def test_d9_preserves_retrograde(self, lee_planets, lee_asc_sign):
        """D9 chart should preserve retrograde status."""
        d9 = calculate_divisional_chart(lee_planets, 'D9', lee_asc_sign, 10.0)
        for orig, div in zip(lee_planets, d9):
            assert orig.is_retrograde == div.is_retrograde

    def test_d9_preserves_longitude(self, lee_planets, lee_asc_sign):
        """D9 chart should preserve the original absolute longitude."""
        d9 = calculate_divisional_chart(lee_planets, 'D9', lee_asc_sign, 10.0)
        for orig, div in zip(lee_planets, d9):
            assert orig.longitude == div.longitude

    def test_unsupported_chart_raises(self, crystal_planets, crystal_asc_sign):
        """Unsupported varga type should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_divisional_chart(crystal_planets, 'D99', crystal_asc_sign, 20.0)

    def test_lee_d9_chart(self, lee_planets, lee_asc_sign):
        """Lee's D9 chart should produce valid positions."""
        d9 = calculate_divisional_chart(lee_planets, 'D9', lee_asc_sign, 10.0)
        assert len(d9) == 9
        for p in d9:
            assert 1 <= p.sign <= 12
            assert 1 <= p.house <= 12
