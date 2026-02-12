# Vedia v0.1.0 Task List

## Phase 1: Fix Broken Features

- [ ] **1.1 Implement `synthesize_reading()` in `vedia/interpret/synthesizer.py`**
  - `main.py:999` imports it but it doesn't exist — `ask` command is broken
  - Wrapper that parses question for topic keywords, routes to `generate_topic_reading()` or `generate_birth_chart_reading()`
  - Keywords: career/job/work, love/relationship/marriage, health, wealth/money, education, spirituality
  - Fallback: general birth chart reading with dasha + transit overlay

- [ ] **1.2 Display planetary aspects in `chart` command (`vedia/main.py`)**
  - `houses.py:get_aspects()` exists but results never shown
  - Add "Planetary Aspects (Drishti)" table after planet positions
  - Show: Planet | Aspects Houses | Natal Planets Aspected

- [ ] **1.3 Surface vedha results in `transit` command (`vedia/main.py`)**
  - `vedha.py` calculates obstructions but never displayed
  - After transit overlay, show vedha warnings: "Jupiter in 11th from Moon (benefic) OBSTRUCTED by Mars"

## Phase 2: Missing Core Calculations

- [ ] **2.1 Vargottama detection (`vedia/calc/yogas.py`)**
  - Planet in same sign in D1 and D9 = major strength boost
  - Use existing `divisional.py` D9 calculation
  - Add to `detect_all_yogas()`, store as YogaResult

- [ ] **2.2 Graha Yuddha / planetary war (`vedia/calc/yogas.py`)**
  - Planets within 1 degree (excluding Sun/Moon/Rahu/Ketu)
  - Winner = higher longitude; loser significantly weakened
  - Add to `detect_all_yogas()`

- [ ] **2.3 Store and display D9 Navamsha chart**
  - Files: `vedia/main.py`, `vedia/db.py`
  - D9 calculated in `divisional.py` but never saved or shown
  - Save D9 as chart_type='D9' during `new` command
  - Add `python -m vedia d9 "Name"` command
  - Critical for relationship analysis

- [ ] **2.4 Proportional aspect strengths (`vedia/calc/houses.py`)**
  - Currently binary — add traditional weights: Mars 4th=75%/8th=100%, Jupiter 5th=50%/9th=75%, Saturn 3rd=50%/10th=100%
  - Return (sign, strength_pct) tuples
  - Use in transit overlay and chart display

## Phase 3: Synastry & Muhurta

- [ ] **3.1 Synastry / compatibility analysis**
  - New file: `vedia/interpret/synastry.py`
  - CLI: `python -m vedia synastry "Person1" "Person2"`
  - Guna Milan (Ashtakoot matching) — 36-point system based on Moon nakshatras
  - Cross-chart conjunctions, 7th lord exchange, Venus axis comparison
  - D9 overlay between charts, Mangal Dosha compatibility, Ascendant compatibility
  - Scored report with interpretation, stored in readings table

- [ ] **3.2 Muhurta / auspicious timing**
  - New file: `vedia/calc/muhurta.py`
  - CLI: `python -m vedia muhurta "Person" --date "YYYY-MM-DD" --type "court"`
  - Evaluate: transit overlay, Gochara, nakshatra of day, day lord alignment, SAV score, dasha lord strength, vedha
  - Auspiciousness score with interpretation
  - Event types: court, business, travel, ceremony, medical
  - Compare two dates option

- [ ] **3.3 Remedial measures**
  - New file: `vedia/interpret/remedies.py`
  - For weak planets (Shadbala ratio < 0.7) and active doshas
  - Gemstones, mantras, charity/donation, fasting days
  - Surface in `ask` command readings

## Phase 4: Performance & Database

- [ ] **4.1 Add database indexes (`vedia/db.py`)**
  - `idx_dasha_periods_dates ON dasha_periods(person_id, start_date, end_date)`
  - `idx_readings_created ON readings(person_id, created_at DESC)`
  - `idx_yogas_type ON yogas(chart_id, yoga_type)`

- [ ] **4.2 Geocoding cache (`vedia/db.py`, `vedia/geo.py`)**
  - Add `geocoding_cache` table (location_string, lat, lon, timezone)
  - Check cache before API call in `geocode_location()`

- [ ] **4.3 Ashtakavarga transit scoring (`vedia/transit/overlay.py`)**
  - Apply SAV scores to transit analysis
  - "Saturn in 2-bindu sign = weak" vs "Saturn in 5-bindu sign = strong"
  - Display SAV score alongside each transit planet

## Phase 5: Test Foundation

- [ ] **5.1 Core calculation tests**
  - New files: `tests/test_ephemeris.py`, `tests/test_dashas.py`, `tests/test_yogas.py`, `tests/test_houses.py`, `tests/test_divisional.py`
  - Crystal and Lee's charts as primary fixtures (known-good values)
  - Validate: planet positions within 0.1 degree, dasha dates exact, yoga counts, aspect lists
  - Add `pytest` to requirements.txt

- [ ] **5.2 Integration tests**
  - New file: `tests/test_integration.py`
  - Full pipeline: new person -> chart -> dasha -> transit -> ask
  - Synastry pipeline: two people -> synastry report
  - Muhurta pipeline: person -> date evaluation
  - Error cases: invalid dates, missing persons, bad coordinates

## Verification

1. `python -m vedia ask Crystal "How is my career?"` — produces full synthesized reading
2. `python -m vedia chart Crystal` — shows aspects table
3. `python -m vedia transit Crystal` — shows vedha warnings
4. `python -m vedia d9 Crystal` — displays Navamsha chart
5. `python -m vedia synastry Crystal Lee` — produces compatibility report
6. `python -m vedia muhurta Lee --date 2026-04-30 --type court` — evaluates court date
7. `pytest tests/ -v` — passes with 60%+ coverage on calc/

## Deferred to v0.2.0

- Bhava Chalit chart (cusp-based houses)
- Sudarshana Chakra (triple-chart overlay)
- Pushkara navamsha/degree detection
- Ashtakavarga Kaksha subdivision
- Historical transit logging
- Ashtakavarga standalone display command
