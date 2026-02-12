# Vedia v0.2.0: MCP Server + Jyotish Agent

## Overview

Two deliverables:
1. **MCP Server** (`vedia/mcp_server.py`) — 6 tools, stdio transport, stateless
2. **Jyotish Agent** (`vedia/jyotish_prompt.md`) — Expert system prompt for Claude

---

## Part 1: MCP Server — 6 Tools

### Design Philosophy

The agent is Claude. It can reason, synthesize, and interpret. It does NOT need:
- Separate getters for yogas, dashas, shadbala (just include them in `get_chart`)
- A reading generator (Claude IS the reading generator)
- Fine-grained aspect/house queries (the chart dump has everything)

What it needs: **fat data dumps** and **action tools**.

### The 6 Tools

```
1. calculate_chart(name, birth_date, birth_time, birth_location)
   Full pipeline: geocode → ephemeris → houses → nakshatras → yogas → dashas →
   ashtakavarga → shadbala → D9 → save to DB
   Returns: EVERYTHING — planets with signs/houses/nakshatras/dignity,
   all yogas, current maha/antar/pratyantar dashas, shadbala scores,
   sarvashtakavarga, D9 positions, ascendant info

2. get_chart(name)
   Load a previously calculated chart from DB.
   Returns: same fat payload as calculate_chart (planets, yogas, dashas,
   shadbala, ashtakavarga, D9, aspects — the whole chart)

3. analyze_transits(name, date?)
   Calculate transits for date (default: today), overlay on natal chart.
   Returns: transit positions, natal house placements, conjunctions,
   aspects, SAV scores per transit sign, vedha obstructions,
   Sade Sati status, major transit highlights

4. analyze_compatibility(name1, name2)
   Full synastry pipeline for two saved persons.
   Returns: Guna Milan 36-point breakdown, Venus axis, 7th lord exchange,
   ascendant compatibility, Mangal Dosha comparison, overall score + assessment

5. evaluate_timing(name, date, event_type?)
   Muhurta evaluation. Optionally pass comma-separated dates to compare.
   Returns: per-date scores (gochara, vara, nakshatra, transits, SAV),
   total auspiciousness, factors, recommendations.
   event_type: general, court, business, travel, ceremony, medical

6. list_charts()
   Returns: all saved persons with name, birth data, ascendant sign
```

### Why 6 is enough

| Old 17-tool design | New 6-tool design |
|---|---|
| get_chart + get_yogas + get_current_dashas + get_planetary_strengths + get_divisional_chart + get_ashtakavarga + get_aspects + get_planet_position + get_house_analysis | `get_chart` returns ALL of this in one call |
| generate_reading | Claude IS the reader — the system prompt teaches it Jyotish |
| get_remedies | System prompt has remedy knowledge; chart data has shadbala for weakness detection |
| compare_dates (separate tool) | `evaluate_timing` accepts multiple dates |
| list_persons | `list_charts` |

### Implementation

```python
from mcp.server.fastmcp import FastMCP
import sys, os

# Ensure vedia package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vedia.db import get_connection, init_db, ...
from vedia.calc.ephemeris import calculate_planet_positions
from vedia.calc.dashas import calculate_full_dashas, get_current_dasha
from vedia.calc.yogas import detect_all_yogas
from vedia.calc.ashtakavarga import calculate_ashtakavarga
from vedia.calc.shadbala import calculate_shadbala
from vedia.calc.divisional import calculate_divisional_chart
from vedia.calc.houses import get_aspects, get_aspects_with_strength
from vedia.transit.current import get_current_positions
from vedia.transit.overlay import overlay_transits, get_transit_summary
from vedia.transit.vedha import analyze_all_vedha
from vedia.interpret.synastry import analyze_synastry
from vedia.calc.muhurta import evaluate_muhurta, compare_dates
from vedia.geo import geocode_location, local_to_utc
from vedia.calc.ayanamsha import calculate_julian_day, get_ayanamsha_value, calculate_ascendant

mcp = FastMCP("Vedia")

@mcp.tool()
def calculate_chart(name: str, birth_date: str, birth_time: str, birth_location: str) -> dict:
    """Calculate a complete Vedic birth chart. Runs the full pipeline and saves to DB.
    birth_date: YYYY-MM-DD, birth_time: HH:MM (24h), birth_location: city/country string."""
    ...

@mcp.tool()
def get_chart(name: str) -> dict:
    """Load a saved chart with all data: planets, yogas, dashas, shadbala, ashtakavarga, D9."""
    ...

@mcp.tool()
def analyze_transits(name: str, date: str = "") -> dict:
    """Analyze transits overlaid on natal chart. date: YYYY-MM-DD (default: today)."""
    ...

@mcp.tool()
def analyze_compatibility(name1: str, name2: str) -> dict:
    """Full synastry/compatibility analysis between two saved persons."""
    ...

@mcp.tool()
def evaluate_timing(name: str, dates: str, event_type: str = "general") -> dict:
    """Muhurta: evaluate one or more dates. dates: comma-separated YYYY-MM-DD.
    event_type: general, court, business, travel, ceremony, medical."""
    ...

@mcp.tool()
def list_charts() -> dict:
    """List all saved persons with birth data and ascendant."""
    ...

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Return format

Every tool returns a dict. On error: `{"error": "message"}`. On success: rich nested data. Example `get_chart` return:

```python
{
    "person": {"name": "Lee", "birth_date": "1978-06-07", ...},
    "ascendant": {"sign": 1, "sign_name": "Aries", "degree": 15.2},
    "planets": [
        {"planet": "Sun", "sign": 5, "sign_name": "Leo", "degree": 22.1,
         "house": 5, "nakshatra": "Purva Phalguni", "nakshatra_pada": 2,
         "dignity": "own_sign", "is_retrograde": false, "is_combust": false,
         "aspects": [{"sign": 11, "house": 11, "strength": 100}]},
        ...
    ],
    "yogas": [
        {"name": "Gaja Kesari", "type": "benefic", "strength": "strong",
         "planets": ["Jupiter", "Moon"], "houses": [12, 9],
         "description": "..."},
        ...
    ],
    "dashas": {
        "current_maha": {"planet": "Venus", "start": "2020-01-01", "end": "2040-01-01"},
        "current_antar": {"planet": "Saturn", "start": "2025-06-01", "end": "2028-08-01"},
        "current_pratyantar": {"planet": "Mercury", "start": "2026-01-15", "end": "2026-06-20"},
    },
    "shadbala": [
        {"planet": "Sun", "total": 385.2, "required": 390, "ratio": 0.99,
         "sthana": 120, "dig": 45, "kala": 30, "chesta": 40, "naisargika": 60, "drik": 90},
        ...
    ],
    "ashtakavarga": {"sarva": {1: 28, 2: 32, ...}},  # sign -> SAV points
    "d9": [
        {"planet": "Sun", "sign": 3, "sign_name": "Gemini", "house": 3},
        ...
    ],
}
```

### Key Design Decisions

- Return dicts, not Rich tables — Claude formats for the user
- Each tool opens/closes its own DB connection — fully stateless
- Default DB path: `~/.vedia/vedia.db`
- Error handling: `{"error": "..."}` not exceptions
- Dates default to today where applicable
- Tool docstrings are the schema — keep them tight, the agent reads them

---

## Part 2: Jyotish Agent System Prompt

### File: `vedia/jyotish_prompt.md`

### Core Sections

**1. Identity**
You are a Jyotish practitioner. Parashari system, Lahiri ayanamsha, Whole Sign houses. Use Vedia tools as your calculation engine — never guess planet positions. Always calculate before interpreting.

**2. Consultation Protocol**
- First call: `get_chart(name)` or `list_charts()` to check who exists
- No chart? Ask for birth details → `calculate_chart`
- Every reading must check: natal chart + current dashas + transits (3-tool sequence)
- For compatibility: both charts must exist first

**3. Interpretation Hierarchy**
- Planet dignity: Exalted > Own > Friendly > Neutral > Enemy > Debilitated
- House strength: Kendra > Trikona > Upachaya > Dusthana
- Dasha: Maha = theme, Antar = sub-theme, Pratyantar = timing trigger
- Transit weight: Saturn > Jupiter > Rahu/Ketu > others
- Yogas: only cite when relevant to the question asked

**4. Jyotish Knowledge Base**
Comprehensive reference for all core concepts — houses, planets, signs, nakshatras, aspects, dashas, ashtakavarga, shadbala, yogas, doshas, divisional charts, gochara, muhurta, remedies (gemstones, mantras, charity, fasting per planet).

**5. Tool Chains**

| Consultation Type | Tools |
|---|---|
| General reading | `get_chart` → `analyze_transits` → interpret |
| Specific question | `get_chart` → `analyze_transits` → interpret with focus |
| Compatibility | `get_chart(A)` → `get_chart(B)` → `analyze_compatibility` |
| Timing / Muhurta | `get_chart` → `evaluate_timing` |
| New person | `calculate_chart` → interpret |

**6. Communication Style**
- Sanskrit terms with English: "Vargottama (same sign in D1 and D9)"
- Direct about challenges, constructive framing
- Cite specific data: planet, sign, house, degree
- Timing = specific date ranges from dashas
- Conflicting factors = explain the tension

**7. Ethics**
- Tendencies not fate — emphasize free will
- No absolute health predictions
- Challenging periods = growth opportunities
- Remedies are supportive practices, not magic

---

## Part 3: Registration & Launch

### Register MCP server

```bash
claude mcp add --transport stdio vedia -- python /Users/lee/dev/vedia/vedia/mcp_server.py
```

Or `.mcp.json` in project root:
```json
{
  "mcpServers": {
    "vedia": {
      "type": "stdio",
      "command": "python",
      "args": ["/Users/lee/dev/vedia/vedia/mcp_server.py"]
    }
  }
}
```

### Launch agent

```bash
claude --system-prompt "$(cat /Users/lee/dev/vedia/vedia/jyotish_prompt.md)"
```

---

## Implementation Order

1. `vedia/mcp_server.py` — 6 tools
2. `.mcp.json` — register with Claude Code
3. `vedia/jyotish_prompt.md` — system prompt
4. Test: launch Claude Code, ask about Crystal's career
5. Iterate on prompt quality

## Files

| File | Purpose |
|------|---------|
| `vedia/mcp_server.py` | MCP server, 6 tools |
| `.mcp.json` | Claude Code registration |
| `vedia/jyotish_prompt.md` | Jyotish expert system prompt |
| `tests/test_mcp.py` | Tool unit tests |

## Dependencies

Add to requirements.txt:
```
mcp[cli]>=1.20.0
```
