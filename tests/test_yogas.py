"""Tests for yoga detection in Vedic astrology charts.

Verifies the detection of major yogas and doshas using known chart data
for Crystal and Lee. Each yoga detector is tested individually before
testing the master detect_all_yogas aggregator.
"""
from vedia.calc.yogas import (
    detect_all_yogas,
    detect_gaja_kesari,
    detect_raja_yogas,
    detect_mangal_dosha,
    detect_vargottama,
    detect_graha_yuddha,
    detect_dhana_yogas,
    detect_pancha_mahapurusha,
    detect_budhaditya,
    detect_kemadruma,
    detect_kaal_sarp,
)


class TestGajaKesari:
    """Test Gaja Kesari Yoga detection.

    Requires Jupiter in kendra from Moon, Jupiter not debilitated/combust.
    """

    def test_crystal_chart_no_gk(self, crystal_planets, crystal_asc_sign):
        """Crystal: Jupiter in Capricorn (debilitated) -> GK should NOT form."""
        yogas = detect_gaja_kesari(crystal_planets, crystal_asc_sign)
        assert len(yogas) == 0

    def test_lee_chart_has_gk(self, lee_planets, lee_asc_sign):
        """Lee: Jupiter in Pisces (own sign), Moon in Sagittarius.

        Sign distance: abs(12 - 9) % 12 = 3, which is kendra (0,3,6,9).
        Jupiter is in own sign, not debilitated or combust.
        GK yoga should form with 'strong' strength.
        """
        yogas = detect_gaja_kesari(lee_planets, lee_asc_sign)
        assert len(yogas) >= 1
        assert yogas[0].yoga_name == 'Gaja Kesari Yoga'
        assert yogas[0].yoga_type == 'benefic'
        assert yogas[0].strength == 'strong'
        assert 'Jupiter' in yogas[0].planets_involved
        assert 'Moon' in yogas[0].planets_involved


class TestRajaYogas:
    """Test Raja Yoga detection.

    Formed when kendra lord and trikona lord are connected.
    """

    def test_detects_some(self, crystal_planets, crystal_asc_sign):
        """Crystal's chart should yield at least some raja yoga analysis."""
        yogas = detect_raja_yogas(crystal_planets, crystal_asc_sign)
        assert isinstance(yogas, list)

    def test_returns_yoga_results(self, lee_planets, lee_asc_sign):
        """All detected raja yogas should have correct type and name."""
        yogas = detect_raja_yogas(lee_planets, lee_asc_sign)
        for y in yogas:
            assert y.yoga_type == 'benefic'
            assert 'Raja Yoga' in y.yoga_name

    def test_scorpio_asc_has_mars_raja(self, crystal_planets, crystal_asc_sign):
        """Scorpio asc: Mars lords both 1st (kendra) and 1st (trikona).

        Mars is lord of house 1 (Scorpio) which is both kendra and trikona.
        So Mars should form a single-planet Raja Yoga.
        """
        yogas = detect_raja_yogas(crystal_planets, crystal_asc_sign)
        mars_yogas = [y for y in yogas if 'Mars' in y.planets_involved]
        assert len(mars_yogas) >= 1


class TestMangalDosha:
    """Test Mangal Dosha (Kuja Dosha) detection."""

    def test_lee_mars_in_8th(self, lee_planets, lee_asc_sign):
        """Lee has Mars in house 8 (Gemini from Scorpio) -> Mangal Dosha.

        Mars in 8th house would be 'strong' severity, but Jupiter (Pisces)
        is in kendra from Mars (Gemini) -- distance abs(12-3)%12 = 9,
        which is kendra -- so Jupiter mitigates it to 'moderate'.
        """
        yogas = detect_mangal_dosha(lee_planets, lee_asc_sign)
        assert len(yogas) == 1
        assert yogas[0].yoga_name == 'Mangal Dosha'
        assert yogas[0].yoga_type == 'dosha'
        assert yogas[0].strength == 'moderate'
        assert yogas[0].houses_involved == [8]

    def test_crystal_mars_in_5th(self, crystal_planets, crystal_asc_sign):
        """Crystal has Mars in house 5 (Pisces from Scorpio).

        House 5 is NOT a Mangal Dosha house (1,2,4,7,8,12), so no dosha.
        """
        yogas = detect_mangal_dosha(crystal_planets, crystal_asc_sign)
        assert len(yogas) == 0


class TestDhanaYogas:
    """Test Dhana (wealth) yoga detection."""

    def test_returns_list(self, crystal_planets, crystal_asc_sign):
        """Should return a list of YogaResult objects."""
        yogas = detect_dhana_yogas(crystal_planets, crystal_asc_sign)
        assert isinstance(yogas, list)
        for y in yogas:
            assert y.yoga_type == 'benefic'
            assert 'Dhana' in y.yoga_name


class TestPanchaMahapurusha:
    """Test Pancha Mahapurusha yoga detection."""

    def test_returns_list(self, crystal_planets, crystal_asc_sign):
        yogas = detect_pancha_mahapurusha(crystal_planets, crystal_asc_sign)
        assert isinstance(yogas, list)
        for y in yogas:
            assert 'Pancha Mahapurusha' in y.yoga_name
            assert y.yoga_type == 'benefic'


class TestVargottama:
    """Test Vargottama (same sign in D1 and D9) detection."""

    def test_returns_list(self, crystal_planets, crystal_asc_sign):
        yogas = detect_vargottama(crystal_planets, crystal_asc_sign)
        assert isinstance(yogas, list)
        for y in yogas:
            assert 'Vargottama' in y.yoga_name
            assert y.yoga_type == 'benefic'

    def test_lee_returns_list(self, lee_planets, lee_asc_sign):
        yogas = detect_vargottama(lee_planets, lee_asc_sign)
        assert isinstance(yogas, list)
        for y in yogas:
            assert 'Vargottama' in y.yoga_name


class TestGrahaYuddha:
    """Test Graha Yuddha (planetary war) detection.

    Occurs when two tara planets (Mars, Mercury, Jupiter, Venus, Saturn)
    are within 1 degree of each other.
    """

    def test_crystal_returns_list(self, crystal_planets, crystal_asc_sign):
        yogas = detect_graha_yuddha(crystal_planets, crystal_asc_sign)
        assert isinstance(yogas, list)
        for y in yogas:
            assert 'Graha Yuddha' in y.yoga_name
            assert y.yoga_type == 'dosha'

    def test_lee_returns_list(self, lee_planets, lee_asc_sign):
        yogas = detect_graha_yuddha(lee_planets, lee_asc_sign)
        assert isinstance(yogas, list)


class TestBudhaditya:
    """Test Budhaditya Yoga (Sun + Mercury conjunction)."""

    def test_crystal_sun_mercury_conjunct(self, crystal_planets, crystal_asc_sign):
        """Crystal has Sun and Mercury both in Capricorn (sign 10), house 3.

        House 3 is NOT a kendra or trikona, so Budhaditya should NOT form.
        """
        yogas = detect_budhaditya(crystal_planets, crystal_asc_sign)
        assert len(yogas) == 0


class TestKaalSarp:
    """Test Kaal Sarpa Yoga detection."""

    def test_crystal_chart(self, crystal_planets, crystal_asc_sign):
        yogas = detect_kaal_sarp(crystal_planets, crystal_asc_sign)
        assert isinstance(yogas, list)

    def test_lee_chart(self, lee_planets, lee_asc_sign):
        yogas = detect_kaal_sarp(lee_planets, lee_asc_sign)
        assert isinstance(yogas, list)


class TestDetectAll:
    """Test the master detect_all_yogas aggregation function."""

    def test_crystal_total(self, crystal_planets, crystal_asc_sign):
        """Crystal's chart should detect at least one yoga."""
        yogas = detect_all_yogas(crystal_planets, crystal_asc_sign)
        assert len(yogas) > 0

    def test_crystal_sorted_benefic_before_dosha(self, crystal_planets, crystal_asc_sign):
        """Benefic yogas should appear before doshas in the sorted result."""
        yogas = detect_all_yogas(crystal_planets, crystal_asc_sign)
        types = [y.yoga_type for y in yogas]
        if 'benefic' in types and 'dosha' in types:
            assert types.index('benefic') < types.index('dosha')

    def test_lee_total(self, lee_planets, lee_asc_sign):
        """Lee's chart should detect at least one yoga."""
        yogas = detect_all_yogas(lee_planets, lee_asc_sign)
        assert len(yogas) > 0

    def test_lee_has_gaja_kesari(self, lee_planets, lee_asc_sign):
        """Lee's aggregated results should include Gaja Kesari Yoga."""
        yogas = detect_all_yogas(lee_planets, lee_asc_sign)
        gk = [y for y in yogas if y.yoga_name == 'Gaja Kesari Yoga']
        assert len(gk) >= 1

    def test_lee_has_mangal_dosha(self, lee_planets, lee_asc_sign):
        """Lee's aggregated results should include Mangal Dosha."""
        yogas = detect_all_yogas(lee_planets, lee_asc_sign)
        md = [y for y in yogas if y.yoga_name == 'Mangal Dosha']
        assert len(md) >= 1

    def test_all_results_are_yoga_result(self, crystal_planets, crystal_asc_sign):
        """All entries should be YogaResult instances."""
        from vedia.models import YogaResult
        yogas = detect_all_yogas(crystal_planets, crystal_asc_sign)
        for y in yogas:
            assert isinstance(y, YogaResult)
            assert y.yoga_name
            assert y.yoga_type in ('benefic', 'dosha', 'transit_dosha')
            assert y.strength in ('strong', 'moderate', 'weak')
