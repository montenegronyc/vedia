"""Geocoding and timezone resolution for birth data.

Resolves location strings (city names, addresses) to geographic coordinates
and IANA timezone identifiers. Handles DST-aware conversions between local
birth times and UTC.

Dependencies: geopy, timezonefinder, pytz
"""

from __future__ import annotations

from datetime import datetime
from typing import NamedTuple

import pytz
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from .db import get_connection, init_db, get_cached_geocode, save_geocode_cache


# ---------------------------------------------------------------------------
# Module-level singletons (lazy-friendly, thread-safe for reads)
# ---------------------------------------------------------------------------

_geocoder = Nominatim(user_agent="vedia-astrology", timeout=10)
_tzfinder = TimezoneFinder()


# ---------------------------------------------------------------------------
# Data container
# ---------------------------------------------------------------------------

class GeoResult(NamedTuple):
    """Result of a geocode + timezone lookup."""
    latitude: float
    longitude: float
    timezone: str


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def geocode_location(location_str: str) -> GeoResult:
    """Resolve a location string to latitude, longitude, and IANA timezone.

    Args:
        location_str: City / place name, e.g. "Detroit, Michigan" or
                      "Cornwall, ON, Canada".

    Returns:
        A ``GeoResult`` namedtuple with *latitude*, *longitude*, and
        *timezone* (IANA identifier such as ``"America/Detroit"``).

    Raises:
        ValueError: If the location cannot be geocoded or the timezone
                    cannot be determined from the resulting coordinates.
        ConnectionError: If the geocoding service is unreachable.
    """
    if not location_str or not location_str.strip():
        raise ValueError("Location string must not be empty")

    # Check geocoding cache first
    try:
        conn = get_connection()
        init_db(conn)
        cached = get_cached_geocode(conn, location_str)
        if cached:
            conn.close()
            return GeoResult(
                latitude=cached['latitude'],
                longitude=cached['longitude'],
                timezone=cached['timezone'],
            )
        conn.close()
    except Exception:
        pass  # Fall through to live geocoding on any cache error

    try:
        location = _geocoder.geocode(location_str)
    except GeocoderTimedOut as exc:
        raise ConnectionError(
            f"Geocoding timed out for '{location_str}'. "
            "Check your network connection or try again."
        ) from exc
    except GeocoderServiceError as exc:
        raise ConnectionError(
            f"Geocoding service error for '{location_str}': {exc}"
        ) from exc

    if location is None:
        raise ValueError(f"Could not geocode location: {location_str}")

    lat: float = location.latitude
    lon: float = location.longitude

    tz_str = _tzfinder.timezone_at(lat=lat, lng=lon)
    if tz_str is None:
        raise ValueError(
            f"Could not determine timezone for coordinates: "
            f"{lat:.4f}, {lon:.4f} (location: {location_str})"
        )

    # Save successful result to cache
    try:
        conn = get_connection()
        init_db(conn)
        save_geocode_cache(
            conn, location_str, lat, lon, tz_str,
            display_name=str(location),
        )
        conn.close()
    except Exception:
        pass  # Don't fail the geocode on cache write errors

    return GeoResult(latitude=lat, longitude=lon, timezone=tz_str)


def get_utc_offset(timezone_str: str, date: datetime) -> float:
    """Return the UTC offset **in hours** for *timezone_str* on *date*.

    Correctly accounts for Daylight Saving Time.

    Args:
        timezone_str: IANA timezone identifier (e.g. ``"America/Detroit"``).
        date: A naive ``datetime`` representing the local wall-clock time.
              Only the date (and time, for DST boundaries) matter.

    Returns:
        Decimal hours east of UTC.  For example ``-5.0`` for US Eastern
        Standard Time, ``-4.0`` for US Eastern Daylight Time, or ``5.5``
        for India Standard Time.
    """
    tz = pytz.timezone(timezone_str)
    local_dt = tz.localize(date)
    offset = local_dt.utcoffset()
    if offset is None:
        raise ValueError(
            f"Could not compute UTC offset for {timezone_str} on {date}"
        )
    return offset.total_seconds() / 3600.0


def local_to_utc(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    timezone_str: str,
) -> datetime:
    """Convert a local birth time to a UTC-aware ``datetime``.

    Args:
        year, month, day, hour, minute, second: Components of the local
            wall-clock time at the birth location.
        timezone_str: IANA timezone identifier for the birth location.

    Returns:
        A timezone-aware ``datetime`` in UTC.
    """
    tz = pytz.timezone(timezone_str)
    naive = datetime(year, month, day, hour, minute, second)
    local_dt = tz.localize(naive)
    return local_dt.astimezone(pytz.UTC)


def format_location_info(
    location_str: str,
    lat: float,
    lon: float,
    tz_str: str,
) -> str:
    """Return a human-readable summary of resolved location data.

    Example output::

        Detroit, Michigan (42.3314N, 83.0458W, America/Detroit)
    """
    lat_dir = "N" if lat >= 0 else "S"
    lon_dir = "E" if lon >= 0 else "W"
    return (
        f"{location_str} "
        f"({abs(lat):.4f}{lat_dir}, {abs(lon):.4f}{lon_dir}, {tz_str})"
    )


# ---------------------------------------------------------------------------
# Quick self-test (not a substitute for a real test suite)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    TESTS = [
        {
            "query": "Detroit, Michigan",
            "expected_lat": 42.33,
            "expected_lon": -83.05,
            "expected_tz": "America/Detroit",
            "lat_tol": 0.15,
            "lon_tol": 0.15,
        },
        {
            "query": "Cornwall, ON, Canada",
            "expected_lat": 45.02,
            "expected_lon": -74.73,
            "expected_tz": "America/Toronto",
            "lat_tol": 0.15,
            "lon_tol": 0.15,
        },
    ]

    passed = 0
    failed = 0

    for t in TESTS:
        query = t["query"]
        print(f"\n--- Testing: {query!r} ---")
        try:
            result = geocode_location(query)
            print(f"  lat={result.latitude:.4f}, lon={result.longitude:.4f}, tz={result.timezone}")
            print(f"  formatted: {format_location_info(query, result.latitude, result.longitude, result.timezone)}")

            # Latitude check
            if abs(result.latitude - t["expected_lat"]) > t["lat_tol"]:
                print(f"  FAIL: latitude {result.latitude:.4f} not within "
                      f"{t['lat_tol']} of expected {t['expected_lat']:.2f}")
                failed += 1
                continue

            # Longitude check
            if abs(result.longitude - t["expected_lon"]) > t["lon_tol"]:
                print(f"  FAIL: longitude {result.longitude:.4f} not within "
                      f"{t['lon_tol']} of expected {t['expected_lon']:.2f}")
                failed += 1
                continue

            # Timezone check
            if result.timezone != t["expected_tz"]:
                print(f"  FAIL: timezone {result.timezone!r} != expected {t['expected_tz']!r}")
                failed += 1
                continue

            # UTC offset smoke test (January = standard time for both)
            winter_date = datetime(2024, 1, 15, 12, 0, 0)
            offset = get_utc_offset(result.timezone, winter_date)
            print(f"  UTC offset on 2024-01-15: {offset:+.1f}h")
            if result.timezone == "America/Detroit" and offset != -5.0:
                print(f"  FAIL: expected -5.0 for EST, got {offset}")
                failed += 1
                continue
            if result.timezone == "America/Toronto" and offset != -5.0:
                print(f"  FAIL: expected -5.0 for EST, got {offset}")
                failed += 1
                continue

            # Summer DST check
            summer_date = datetime(2024, 7, 15, 12, 0, 0)
            offset_summer = get_utc_offset(result.timezone, summer_date)
            print(f"  UTC offset on 2024-07-15: {offset_summer:+.1f}h")
            if offset_summer != -4.0:
                print(f"  FAIL: expected -4.0 for EDT, got {offset_summer}")
                failed += 1
                continue

            # local_to_utc round-trip
            utc_dt = local_to_utc(1990, 6, 15, 14, 30, 0, result.timezone)
            print(f"  1990-06-15 14:30 local -> {utc_dt.isoformat()} UTC")

            print("  PASS")
            passed += 1

        except Exception as exc:
            print(f"  ERROR: {exc}")
            failed += 1

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
    print("All tests passed.")
