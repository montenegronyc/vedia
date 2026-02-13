# Vedia Astrology Engine — Enhancement & Bug Fix Specification

## Context

Vedia is a Swiss Ephemeris-based Vedic astrology MCP server that calculates complete Vedic birth charts, transits, compatibility, and muhurta timing. The system uses the Lahiri (Chitrapaksha) ayanamsha and Whole Sign house system.

The following enhancements and bug fixes were identified during real consultation sessions where specific analytical gaps forced workarounds or limited interpretation quality. They are prioritized by frequency of impact during actual readings.

---

## 🐛 BUG FIX — Priority 1

### Navamsha (D9) Chart Returns Empty

**Current behavior:** `get_chart()` and `calculate_chart()` both return `"d9": []` — an empty array.

**Expected behavior:** The `d9` array should return one entry per planet (Sun through Ketu, plus Ascendant) with:
- `planet`: planet name
- `sign`: sign number (1-12)
- `sign_name`: sign name
- `house`: house number from D9 ascendant
- `degree`: degree within the sign
- `dignity`: dignity in D9 sign (exalted/own/friendly/neutral/enemy/debilitated)
- `is_vargottama`: boolean — true if the planet occupies the same sign in D1 and D9

**Why it matters:** The Navamsha is the most important divisional chart in Vedic astrology. It confirms or denies natal promises, reveals the deeper quality of marriage/partnerships, and determines whether debilitated planets have hidden strength (neecha bhanga through D9 improvement). Without it, relationship readings and dignity assessments are incomplete.

---

## ✨ ENHANCEMENTS — Priority Order

### 1. Bhinnashtakavarga (BAV) — Individual Planet Scores

**Current behavior:** Ashtakavarga data only includes Sarvashtakavarga (SAV) — the aggregate score per sign across all planets.

**Enhancement:** Add a `bav` (Bhinnashtakavarga) object alongside the existing `sarva` object in the ashtakavarga response. Structure:

```json
"ashtakavarga": {
  "sarva": { "1": 28, "2": 26, ... },
  "bav": {
    "Sun":     { "1": 4, "2": 3, ... },
    "Moon":    { "1": 5, "2": 2, ... },
    "Mars":    { "1": 3, "2": 4, ... },
    "Mercury": { "1": 4, "2": 3, ... },
    "Jupiter": { "1": 5, "2": 4, ... },
    "Venus":   { "1": 3, "2": 5, ... },
    "Saturn":  { "1": 4, "2": 5, ... }
  }
}
```

Each planet's BAV shows its individual bindus (0-8) per sign. Rahu and Ketu are traditionally excluded from BAV calculation.

**Why it matters:** When Saturn transits a sign with SAV 27 (average), knowing whether Saturn's own BAV in that sign is 2 (weak) or 5 (strong) radically changes the interpretation. SAV tells you the neighborhood's general support. BAV tells you whether the specific planet has a key to the door.

---

### 2. Muhurta Date Range Scanning

**Current behavior:** `evaluate_timing()` accepts comma-separated dates. Finding an optimal date in a window requires the caller to manually specify individual dates and make multiple calls.

**Enhancement:** Add an optional `date_range` parameter as an alternative to `dates`:

```
evaluate_timing(
  name="Lee",
  date_range="2026-04-15,2026-05-15",
  event_type="court",
  filters={
    "day_of_week": ["Thursday"],       # optional: filter to specific days
    "min_score": 55,                    # optional: minimum total score threshold
    "top_n": 5                          # return top N results, ranked best-first
  }
)
```

**Return format:** Same per-date evaluation structure as current, but filtered and ranked. Include a `rank` field and `dates_scanned` count.

**Why it matters:** In real consultations, timing optimization requires scanning 20-30+ candidate dates. Currently this burns 5-6 tool calls and a lot of context window. A single range query with filters would be transformative for muhurta work.

---

### 3. Full Dasha Tree Query

**Current behavior:** The dashas object returns only the currently active maha/antar/pratyantar periods with their start and end dates.

**Enhancement:** Add a `list_dashas` tool or parameter that returns the full dasha tree for a specified level:

```
list_dashas(
  name="Lee",
  level="pratyantar",           # "maha", "antar", or "pratyantar"
  within_maha="Rahu",           # optional: scope to specific mahadasha
  within_antar="Saturn",        # optional: scope to specific antardasha
  date_range="2026-01-01,2027-01-01"  # optional: filter to date window
)
```

**Return format:**
```json
{
  "maha": { "planet": "Rahu", "start": "2018-06-19", "end": "2036-06-18" },
  "antar": { "planet": "Saturn", "start": "2023-07-25", "end": "2026-05-31" },
  "pratyantars": [
    { "planet": "Saturn", "start": "2023-07-25", "end": "2024-01-15" },
    { "planet": "Mercury", "start": "2024-01-15", "end": "2024-06-20" },
    ...
    { "planet": "Jupiter", "start": "2026-01-13", "end": "2026-05-31" }
  ]
}
```

**Why it matters:** Precise event timing requires knowing exactly when sub-periods begin and end. When Crystal entered Moon-Sun-Venus pratyantar 10 days before the breakup, that was a critical interpretive detail — but I had to infer it from contextual data rather than query it directly.

---

### 4. Additional Divisional Charts (D7, D10)

**Current behavior:** Only D1 (Rasi) and D9 (Navamsha, currently broken) are calculated.

**Enhancement:** Add at minimum:

- **D7 (Saptamsha):** Children and progeny. Same structure as D9 — planet positions by sign, house, and dignity in the divisional chart.
- **D10 (Dashamsha):** Career and profession. Same structure.

Ideal implementation: a generic `get_divisional(name, division)` tool or parameter on `get_chart` that accepts any standard division (D1-D60), calculating at minimum D1, D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D27, D30, D40, D45, D60 (the Shodashvarga set).

**Return format per divisional chart:**
```json
{
  "division": "D7",
  "name": "Saptamsha",
  "ascendant": { "sign": 4, "sign_name": "Cancer", "degree": 15.2 },
  "planets": [
    {
      "planet": "Jupiter",
      "sign": 4,
      "sign_name": "Cancer",
      "house": 1,
      "dignity": "exalted",
      "is_vargottama": false
    },
    ...
  ]
}
```

**Why it matters:** Custody and children questions are central to Lee's ongoing legal situation. The D7 chart is the primary tool for analyzing children-related outcomes. The D10 would sharpen all career readings. These come up in nearly every comprehensive consultation.

---

### 5. Yogini Dasha (Secondary Timing System)

**Current behavior:** Only Vimshottari Dasha is calculated.

**Enhancement:** Add Yogini Dasha as a secondary timing system, returned alongside Vimshottari:

The Yogini Dasha cycle is 36 years total, with 8 sub-periods:

| Yogini | Planet | Duration |
|--------|--------|----------|
| Mangala | Moon | 1 year |
| Pingala | Sun | 2 years |
| Dhanya | Jupiter | 3 years |
| Bhramari | Mars | 4 years |
| Bhadrika | Mercury | 5 years |
| Ulka | Saturn | 6 years |
| Siddha | Venus | 7 years |
| Sankata | Rahu | 8 years |

Starting yogini is determined by: (birth nakshatra number + 3) mod 8, mapped to the sequence above.

**Return format:** Same structure as Vimshottari — current maha, antar, pratyantar with start/end dates. Add to dashas object:

```json
"dashas": {
  "vimshottari": {
    "current_maha": { ... },
    "current_antar": { ... },
    "current_pratyantar": { ... }
  },
  "yogini": {
    "current_maha": { ... },
    "current_antar": { ... },
    "current_pratyantar": { ... }
  }
}
```

**Why it matters:** When Vimshottari and Yogini dashas agree on the nature of a period, prediction confidence increases substantially. When they disagree, it flags periods that need more nuanced interpretation. Two timing systems are always better than one.

---

## Implementation Notes

- All calculations should use the **Lahiri (Chitrapaksha) ayanamsha** consistently
- **Whole Sign house system** throughout
- Divisional chart calculations should derive from the same Swiss Ephemeris planetary longitudes already computed for D1
- BAV calculations use the standard Parashari bindhu system (each planet contributes 0 or 1 bindhu per sign based on classical rules)
- Yogini Dasha start point requires the Moon's birth nakshatra, which is already computed

## Testing

After implementation, verify against Lee's chart (Nov 7, 1975, 8:30 AM, Cornwall ON):
- D9 should return non-empty planet positions; check whether natal Venus (debilitated in D1 Virgo) improves in D9
- BAV for Saturn in Pisces (sign 12) — this is where Saturn is currently transiting Lee's 5th house
- Dasha tree: Rahu-Saturn antardasha pratyantars should list Jupiter starting ~Jan 13, 2026
- Muhurta range: scan all Thursdays in April-May 2026 for court, verify May 7 scores highest
