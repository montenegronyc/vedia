"""Vimshottari Dasha calculation engine.

Computes the primary planetary period system in Vedic astrology. The Moon's
nakshatra at birth determines the starting dasha lord, and the system cycles
through a fixed sequence of nine planetary lords over a 120-year span.

Three levels are computed:
  - Maha Dasha (major period)
  - Antar Dasha (sub-period within each maha)
  - Pratyantar Dasha (sub-sub-period within each antar)
"""

from datetime import datetime, timedelta

from ..models import (
    DASHA_SEQUENCE,
    DASHA_YEARS,
    NAKSHATRA_LORDS,
    DashaPeriod,
    YOGINI_NAMES,
    YOGINI_LORDS,
    YOGINI_YEARS,
    YOGINI_TOTAL_YEARS,
    YoginiPeriod,
)

# Each nakshatra spans 13 degrees 20 minutes = 13.333... degrees
_NAKSHATRA_SPAN = 13.333333

# Total Vimshottari cycle length in years
_TOTAL_CYCLE_YEARS = 120  # sum(DASHA_YEARS.values())

# Conversion factor: one year in days (accounting for leap years)
_DAYS_PER_YEAR = 365.25


def _get_dasha_sequence_from(starting_lord: str) -> list[str]:
    """Return the full 9-planet dasha sequence starting from a given lord.

    Args:
        starting_lord: The planet to begin the sequence from.

    Returns:
        List of 9 planet names in Vimshottari dasha order, starting
        with starting_lord.

    Raises:
        ValueError: If starting_lord is not in DASHA_SEQUENCE.
    """
    if starting_lord not in DASHA_SEQUENCE:
        raise ValueError(
            f"Unknown dasha lord '{starting_lord}'. "
            f"Must be one of: {DASHA_SEQUENCE}"
        )
    idx = DASHA_SEQUENCE.index(starting_lord)
    return DASHA_SEQUENCE[idx:] + DASHA_SEQUENCE[:idx]


def calculate_dasha_balance(moon_longitude: float) -> tuple[str, float]:
    """Determine the first maha dasha lord and remaining balance at birth.

    The Moon's position within its nakshatra determines how much of the
    first dasha period remains. If the Moon is at the very start of a
    nakshatra, nearly the full dasha period remains; at the end, almost
    none remains.

    Args:
        moon_longitude: Sidereal longitude of the Moon in degrees (0-360).

    Returns:
        Tuple of (nakshatra_lord, balance_years) where nakshatra_lord is
        the planet ruling the Moon's nakshatra (and thus the first maha
        dasha lord), and balance_years is the remaining years of that
        dasha at birth.
    """
    # Determine which nakshatra the Moon occupies (0-indexed)
    nakshatra_index = int(moon_longitude / _NAKSHATRA_SPAN)
    # Clamp for edge case of exactly 360.0
    if nakshatra_index >= 27:
        nakshatra_index = 26

    nakshatra_lord = NAKSHATRA_LORDS[nakshatra_index]

    # How far through the nakshatra has the Moon traveled?
    offset_in_nakshatra = moon_longitude % _NAKSHATRA_SPAN
    remaining_fraction = 1.0 - (offset_in_nakshatra / _NAKSHATRA_SPAN)

    balance_years = DASHA_YEARS[nakshatra_lord] * remaining_fraction

    return (nakshatra_lord, balance_years)


def calculate_maha_dashas(
    moon_longitude: float,
    birth_datetime: datetime,
) -> list[DashaPeriod]:
    """Calculate all maha dasha (major period) entries covering 120 years.

    The first maha dasha begins at birth and lasts for the balance years
    determined by the Moon's position. Subsequent dashas follow the
    Vimshottari sequence from the starting lord, cycling through all nine
    planets and then repeating to fill the full 120-year span.

    Args:
        moon_longitude: Sidereal longitude of the Moon at birth (0-360).
        birth_datetime: Date and time of birth.

    Returns:
        List of DashaPeriod objects with level='maha'.
    """
    starting_lord, balance_years = calculate_dasha_balance(moon_longitude)
    sequence = _get_dasha_sequence_from(starting_lord)

    maha_dashas: list[DashaPeriod] = []
    current_date = birth_datetime

    # First maha dasha: only the balance portion
    balance_days = balance_years * _DAYS_PER_YEAR
    end_date = current_date + timedelta(days=balance_days)
    maha_dashas.append(DashaPeriod(
        level='maha',
        planet=starting_lord,
        start_date=current_date,
        end_date=end_date,
    ))
    current_date = end_date

    # Track total years accumulated (balance + subsequent full dashas)
    total_years = balance_years

    # Subsequent full-cycle dashas: start from the next planet in sequence
    # and keep cycling until we cover 120 years
    cycle_index = 1  # start after the first lord in the sequence
    while total_years < _TOTAL_CYCLE_YEARS:
        lord = sequence[cycle_index % len(sequence)]
        years = DASHA_YEARS[lord]
        days = years * _DAYS_PER_YEAR
        end_date = current_date + timedelta(days=days)

        maha_dashas.append(DashaPeriod(
            level='maha',
            planet=lord,
            start_date=current_date,
            end_date=end_date,
        ))

        current_date = end_date
        total_years += years
        cycle_index += 1

    return maha_dashas


def _calculate_sub_periods(
    parent: DashaPeriod,
    level: str,
) -> list[DashaPeriod]:
    """Generic sub-period calculation used for both antar and pratyantar.

    Sub-periods within a parent period follow the Vimshottari sequence
    starting from the parent's planet lord. Each sub-period's duration is
    proportional to its lord's dasha years relative to the total 120-year
    cycle, applied to the parent's actual duration in days.

    Args:
        parent: The parent DashaPeriod to subdivide.
        level: The level label for the sub-periods ('antar' or 'pratyantar').

    Returns:
        List of DashaPeriod objects at the specified level.
    """
    sequence = _get_dasha_sequence_from(parent.planet)
    parent_total_days = (parent.end_date - parent.start_date).total_seconds() / 86400.0

    sub_periods: list[DashaPeriod] = []
    current_date = parent.start_date

    for lord in sequence:
        fraction = DASHA_YEARS[lord] / _TOTAL_CYCLE_YEARS
        sub_days = parent_total_days * fraction
        end_date = current_date + timedelta(days=sub_days)

        sub_periods.append(DashaPeriod(
            level=level,
            planet=lord,
            start_date=current_date,
            end_date=end_date,
        ))

        current_date = end_date

    return sub_periods


def calculate_antar_dashas(maha_dasha: DashaPeriod) -> list[DashaPeriod]:
    """Calculate antar dasha (sub-periods) within a maha dasha.

    Antar dashas start from the maha dasha lord and cycle through the
    Vimshottari sequence. Each antar dasha's duration is proportional
    to its lord's years divided by 120, applied to the maha dasha's
    actual duration.

    Args:
        maha_dasha: The parent maha dasha period.

    Returns:
        List of DashaPeriod objects with level='antar'. These are also
        stored in maha_dasha.sub_periods.
    """
    sub_periods = _calculate_sub_periods(maha_dasha, 'antar')
    maha_dasha.sub_periods = sub_periods
    return sub_periods


def calculate_pratyantar_dashas(antar_dasha: DashaPeriod) -> list[DashaPeriod]:
    """Calculate pratyantar dasha (sub-sub-periods) within an antar dasha.

    Same proportional logic as antar dashas, one level deeper. Pratyantar
    dashas start from the antar dasha lord.

    Args:
        antar_dasha: The parent antar dasha period.

    Returns:
        List of DashaPeriod objects with level='pratyantar'. These are also
        stored in antar_dasha.sub_periods.
    """
    sub_periods = _calculate_sub_periods(antar_dasha, 'pratyantar')
    antar_dasha.sub_periods = sub_periods
    return sub_periods


def calculate_full_dashas(
    moon_longitude: float,
    birth_datetime: datetime,
) -> list[DashaPeriod]:
    """Calculate the complete three-level Vimshottari dasha hierarchy.

    Computes all maha dashas, then populates each with its antar dashas,
    and each antar with its pratyantar dashas. The returned list contains
    the top-level maha dashas; antar and pratyantar are accessible via
    the sub_periods attribute.

    Args:
        moon_longitude: Sidereal longitude of the Moon at birth (0-360).
        birth_datetime: Date and time of birth.

    Returns:
        List of DashaPeriod objects (maha level) with fully populated
        sub_periods trees.
    """
    maha_dashas = calculate_maha_dashas(moon_longitude, birth_datetime)

    for maha in maha_dashas:
        antars = calculate_antar_dashas(maha)
        for antar in antars:
            calculate_pratyantar_dashas(antar)

    return maha_dashas


def get_current_dasha(
    dashas: list[DashaPeriod],
    date: datetime = None,
) -> dict[str, DashaPeriod | None]:
    """Find the active maha, antar, and pratyantar dasha for a given date.

    Searches through the pre-computed dasha hierarchy to find which
    periods are active at the specified moment.

    Args:
        dashas: List of maha dasha periods (as returned by
            calculate_full_dashas or calculate_maha_dashas).
        date: The date/time to query. Defaults to the current moment.

    Returns:
        Dict with keys 'maha', 'antar', 'pratyantar', each mapping to the
        active DashaPeriod at that level, or None if not found (e.g. if
        sub-periods have not been computed, or the date falls outside the
        covered range).
    """
    if date is None:
        date = datetime.now()

    result: dict[str, DashaPeriod | None] = {
        'maha': None,
        'antar': None,
        'pratyantar': None,
    }

    # Find active maha dasha
    for maha in dashas:
        if maha.start_date <= date < maha.end_date:
            result['maha'] = maha
            break
    else:
        # Date not within any maha dasha range
        return result

    # Find active antar dasha within the maha
    for antar in result['maha'].sub_periods:
        if antar.start_date <= date < antar.end_date:
            result['antar'] = antar
            break
    else:
        return result

    # Find active pratyantar dasha within the antar
    for pratyantar in result['antar'].sub_periods:
        if pratyantar.start_date <= date < pratyantar.end_date:
            result['pratyantar'] = pratyantar
            break

    return result


# ---------------------------------------------------------------------------
# Yogini Dasha System (36-year cycle, 8 yoginis)
# ---------------------------------------------------------------------------

def calculate_yogini_starting_index(moon_nakshatra: int) -> int:
    """Determine the starting Yogini index from the birth nakshatra number.

    Formula: (nakshatra_number + 3) mod 8.

    Args:
        moon_nakshatra: Birth nakshatra number (1-27).

    Returns:
        Index 0-7 into YOGINI_NAMES.
    """
    return (moon_nakshatra + 3) % 8


def calculate_yogini_balance(moon_longitude: float) -> tuple[str, float]:
    """Determine the first Yogini dasha and remaining balance at birth.

    Args:
        moon_longitude: Sidereal longitude of the Moon in degrees (0-360).

    Returns:
        Tuple of (yogini_name, balance_years).
    """
    nakshatra_index = int(moon_longitude / _NAKSHATRA_SPAN)
    if nakshatra_index >= 27:
        nakshatra_index = 26

    nakshatra_number = nakshatra_index + 1  # 1-based
    yogini_index = calculate_yogini_starting_index(nakshatra_number)
    yogini_name = YOGINI_NAMES[yogini_index]

    offset_in_nakshatra = moon_longitude % _NAKSHATRA_SPAN
    remaining_fraction = 1.0 - (offset_in_nakshatra / _NAKSHATRA_SPAN)
    balance_years = YOGINI_YEARS[yogini_name] * remaining_fraction

    return (yogini_name, balance_years)


def _get_yogini_sequence_from(starting_yogini: str) -> list[str]:
    """Return the 8-yogini sequence starting from the given yogini name."""
    idx = YOGINI_NAMES.index(starting_yogini)
    return YOGINI_NAMES[idx:] + YOGINI_NAMES[:idx]


def calculate_yogini_maha_dashas(
    moon_longitude: float,
    birth_datetime: datetime,
) -> list[YoginiPeriod]:
    """Calculate Yogini maha dasha periods covering 120+ years.

    The 36-year cycle repeats to cover the same span as Vimshottari.

    Args:
        moon_longitude: Sidereal longitude of the Moon at birth (0-360).
        birth_datetime: Date and time of birth.

    Returns:
        List of YoginiPeriod objects with level='maha'.
    """
    starting_yogini, balance_years = calculate_yogini_balance(moon_longitude)
    sequence = _get_yogini_sequence_from(starting_yogini)

    maha_dashas: list[YoginiPeriod] = []
    current_date = birth_datetime

    # First period: balance portion only
    balance_days = balance_years * _DAYS_PER_YEAR
    end_date = current_date + timedelta(days=balance_days)
    maha_dashas.append(YoginiPeriod(
        level='maha',
        yogini_name=starting_yogini,
        lord=YOGINI_LORDS[starting_yogini],
        start_date=current_date,
        end_date=end_date,
    ))
    current_date = end_date
    total_years = balance_years

    # Subsequent full-period dashas, cycling until 120 years covered
    cycle_index = 1
    while total_years < _TOTAL_CYCLE_YEARS:
        yogini = sequence[cycle_index % 8]
        years = YOGINI_YEARS[yogini]
        days = years * _DAYS_PER_YEAR
        end_date = current_date + timedelta(days=days)

        maha_dashas.append(YoginiPeriod(
            level='maha',
            yogini_name=yogini,
            lord=YOGINI_LORDS[yogini],
            start_date=current_date,
            end_date=end_date,
        ))

        current_date = end_date
        total_years += years
        cycle_index += 1

    return maha_dashas


def _calculate_yogini_sub_periods(
    parent: YoginiPeriod,
    level: str,
) -> list[YoginiPeriod]:
    """Calculate sub-periods within a Yogini parent period.

    Sub-periods follow the Yogini sequence starting from the parent's yogini.
    Duration is proportional to each yogini's years relative to the 36-year total.

    Args:
        parent: The parent YoginiPeriod to subdivide.
        level: Level label for sub-periods ('antar' or 'pratyantar').

    Returns:
        List of YoginiPeriod objects at the specified level.
    """
    sequence = _get_yogini_sequence_from(parent.yogini_name)
    parent_total_days = (parent.end_date - parent.start_date).total_seconds() / 86400.0

    sub_periods: list[YoginiPeriod] = []
    current_date = parent.start_date

    for yogini in sequence:
        fraction = YOGINI_YEARS[yogini] / YOGINI_TOTAL_YEARS
        sub_days = parent_total_days * fraction
        end_date = current_date + timedelta(days=sub_days)

        sub_periods.append(YoginiPeriod(
            level=level,
            yogini_name=yogini,
            lord=YOGINI_LORDS[yogini],
            start_date=current_date,
            end_date=end_date,
        ))

        current_date = end_date

    return sub_periods


def calculate_full_yogini_dashas(
    moon_longitude: float,
    birth_datetime: datetime,
) -> list[YoginiPeriod]:
    """Calculate the complete three-level Yogini dasha hierarchy.

    Computes all maha dashas, then populates each with antar dashas,
    and each antar with pratyantar dashas.

    Args:
        moon_longitude: Sidereal longitude of the Moon at birth (0-360).
        birth_datetime: Date and time of birth.

    Returns:
        List of YoginiPeriod objects (maha level) with fully populated
        sub_periods trees.
    """
    maha_dashas = calculate_yogini_maha_dashas(moon_longitude, birth_datetime)

    for maha in maha_dashas:
        antars = _calculate_yogini_sub_periods(maha, 'antar')
        maha.sub_periods = antars
        for antar in antars:
            pratyantars = _calculate_yogini_sub_periods(antar, 'pratyantar')
            antar.sub_periods = pratyantars

    return maha_dashas


def get_current_yogini_dasha(
    dashas: list[YoginiPeriod],
    date: datetime = None,
) -> dict[str, YoginiPeriod | None]:
    """Find the active Yogini maha, antar, and pratyantar for a given date.

    Args:
        dashas: List of Yogini maha dasha periods.
        date: The date/time to query. Defaults to now.

    Returns:
        Dict with keys 'maha', 'antar', 'pratyantar'.
    """
    if date is None:
        date = datetime.now()

    result: dict[str, YoginiPeriod | None] = {
        'maha': None,
        'antar': None,
        'pratyantar': None,
    }

    for maha in dashas:
        if maha.start_date <= date < maha.end_date:
            result['maha'] = maha
            break
    else:
        return result

    for antar in result['maha'].sub_periods:
        if antar.start_date <= date < antar.end_date:
            result['antar'] = antar
            break
    else:
        return result

    for pratyantar in result['antar'].sub_periods:
        if pratyantar.start_date <= date < pratyantar.end_date:
            result['pratyantar'] = pratyantar
            break

    return result
