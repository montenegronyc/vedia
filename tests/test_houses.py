"""Tests for house calculations (whole sign house system).

Tests verify:
- get_house: planet sign -> house number given an ascendant
- get_house_lord: house -> ruling planet given an ascendant
- get_aspects: planet -> aspected signs (universal 7th + special aspects)
- get_aspects_with_strength: aspects with proportional strength percentages
- get_house_signification: house number -> signification text
"""
import pytest
from vedia.calc.houses import (
    get_house,
    get_house_lord,
    get_aspects,
    get_aspects_with_strength,
    get_house_signification,
)


class TestGetHouse:
    """Test the whole-sign house calculation."""

    def test_same_sign(self):
        """A planet in the ascendant sign occupies the 1st house."""
        assert get_house(8, 8) == 1  # Scorpio planet in Scorpio ascendant

    def test_opposite_sign(self):
        """A planet in the opposite sign occupies the 7th house."""
        assert get_house(2, 8) == 7  # Taurus from Scorpio = 7th

    def test_wrap_around(self):
        """Houses wrap correctly around the zodiac."""
        assert get_house(1, 8) == 6  # Aries from Scorpio = 6th

    def test_all_houses(self):
        """Every sign from a given ascendant maps to a valid house 1-12."""
        for i in range(1, 13):
            h = get_house(i, 1)
            assert 1 <= h <= 12

    def test_crystal_sun_house(self):
        """Crystal's Sun in Capricorn (10) from Scorpio (8) asc = house 3."""
        assert get_house(10, 8) == 3

    def test_crystal_moon_house(self):
        """Crystal's Moon in Leo (5) from Scorpio (8) asc = house 10."""
        assert get_house(5, 8) == 10

    def test_lee_mars_house(self):
        """Lee's Mars in Gemini (3) from Scorpio (8) asc = house 8."""
        assert get_house(3, 8) == 8


class TestGetHouseLord:
    """Test house lordship lookup based on ascendant."""

    def test_scorpio_ascendant_1st(self):
        """Scorpio is the 1st house sign; its lord is Mars."""
        assert get_house_lord(1, 8) == 'Mars'

    def test_scorpio_ascendant_7th(self):
        """The 7th from Scorpio is Taurus; its lord is Venus."""
        assert get_house_lord(7, 8) == 'Venus'

    def test_scorpio_ascendant_5th(self):
        """The 5th from Scorpio is Pisces; its lord is Jupiter."""
        assert get_house_lord(5, 8) == 'Jupiter'

    def test_scorpio_ascendant_10th(self):
        """The 10th from Scorpio is Leo; its lord is Sun."""
        assert get_house_lord(10, 8) == 'Sun'

    def test_aries_ascendant_1st(self):
        """Aries 1st house lord is Mars."""
        assert get_house_lord(1, 1) == 'Mars'

    def test_all_houses_return_valid_lords(self):
        """Every house for every ascendant should return a known planet."""
        valid_planets = {'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'}
        for asc in range(1, 13):
            for house in range(1, 13):
                lord = get_house_lord(house, asc)
                assert lord in valid_planets, f"asc={asc}, house={house}, lord={lord}"


class TestGetAspects:
    """Test planetary aspect calculation (sign-level)."""

    def test_mars_aspects(self):
        """Mars has 4th, 7th, and 8th sign aspects from Aries."""
        aspects = get_aspects('Mars', 1)
        assert 5 in aspects   # 4th aspect -> Leo
        assert 8 in aspects   # 7th aspect -> Scorpio
        assert 9 in aspects   # 8th aspect -> Sagittarius
        assert len(aspects) == 3

    def test_jupiter_aspects(self):
        """Jupiter has 5th, 7th, and 9th sign aspects from Aries."""
        aspects = get_aspects('Jupiter', 1)
        assert 6 in aspects   # 5th aspect -> Virgo
        assert 8 in aspects   # 7th aspect -> Scorpio
        assert 10 in aspects  # 9th aspect -> Capricorn
        assert len(aspects) == 3

    def test_saturn_aspects(self):
        """Saturn has 3rd, 7th, and 10th sign aspects from Aries."""
        aspects = get_aspects('Saturn', 1)
        assert 4 in aspects   # 3rd aspect -> Cancer
        assert 8 in aspects   # 7th aspect -> Scorpio
        assert 11 in aspects  # 10th aspect -> Aquarius
        assert len(aspects) == 3

    def test_sun_only_7th(self):
        """Sun has only the universal 7th aspect."""
        aspects = get_aspects('Sun', 1)
        assert len(aspects) == 1
        assert 8 in aspects  # 7th from Aries = Scorpio(8)

    def test_moon_only_7th(self):
        """Moon has only the universal 7th aspect."""
        aspects = get_aspects('Moon', 3)
        assert len(aspects) == 1
        assert 10 in aspects  # 7th from Gemini(3) = Sagittarius(10)... wait
        # 7th from Gemini: ((3-1+7)%12)+1 = (9%12)+1 = 10. Correct.

    def test_rahu_aspects(self):
        """Rahu has 5th, 7th, and 9th sign aspects."""
        aspects = get_aspects('Rahu', 1)
        assert len(aspects) == 3

    def test_aspects_are_sorted(self):
        """Aspect lists should be sorted by sign number."""
        aspects = get_aspects('Mars', 6)
        assert aspects == sorted(aspects)


class TestGetAspectsWithStrength:
    """Test aspects with proportional strength percentages."""

    def test_mars_proportional(self):
        """Mars: 4th at 75%, 7th at 100%, 8th at 100%."""
        result = get_aspects_with_strength('Mars', 1)
        signs = [r[0] for r in result]
        strengths = {r[0]: r[1] for r in result}
        assert 5 in signs     # 4th aspect -> Leo
        assert strengths[5] == 75
        assert strengths[8] == 100   # 7th aspect
        assert strengths[9] == 100   # 8th aspect

    def test_jupiter_proportional(self):
        """Jupiter: 5th at 50%, 7th at 100%, 9th at 75%."""
        result = get_aspects_with_strength('Jupiter', 1)
        strengths = {r[0]: r[1] for r in result}
        assert strengths[6] == 50    # 5th aspect -> Virgo
        assert strengths[8] == 100   # 7th aspect
        assert strengths[10] == 75   # 9th aspect

    def test_saturn_proportional(self):
        """Saturn: 3rd at 50%, 7th at 100%, 10th at 100%."""
        result = get_aspects_with_strength('Saturn', 1)
        strengths = {r[0]: r[1] for r in result}
        assert strengths[4] == 50    # 3rd aspect -> Cancer
        assert strengths[8] == 100   # 7th aspect
        assert strengths[11] == 100  # 10th aspect

    def test_sun_universal_only(self):
        """Sun has only the universal 7th aspect at 100%."""
        result = get_aspects_with_strength('Sun', 1)
        assert len(result) == 1
        assert result[0] == (8, 100)

    def test_result_sorted_by_sign(self):
        """Results are sorted by sign number."""
        result = get_aspects_with_strength('Mars', 6)
        sign_nums = [r[0] for r in result]
        assert sign_nums == sorted(sign_nums)


class TestHouseSignification:
    """Test house signification text lookup."""

    def test_valid_houses(self):
        """All 12 houses return a non-empty signification string."""
        for h in range(1, 13):
            sig = get_house_signification(h)
            assert isinstance(sig, str)
            assert len(sig) > 0

    def test_first_house_contains_self(self):
        """The 1st house signification should mention 'Self'."""
        sig = get_house_signification(1)
        assert 'Self' in sig

    def test_seventh_house_contains_spouse(self):
        """The 7th house signification should mention 'Spouse'."""
        sig = get_house_signification(7)
        assert 'Spouse' in sig

    def test_invalid_house_zero(self):
        """House 0 raises ValueError."""
        with pytest.raises(ValueError):
            get_house_signification(0)

    def test_invalid_house_thirteen(self):
        """House 13 raises ValueError."""
        with pytest.raises(ValueError):
            get_house_signification(13)

    def test_invalid_house_negative(self):
        """Negative house number raises ValueError."""
        with pytest.raises(ValueError):
            get_house_signification(-1)
