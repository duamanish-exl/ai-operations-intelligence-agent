import pandas as pd
from datetime import datetime

from data_loader import load_table


# ============================================================
# PERIOD HELPERS
# ============================================================

def _normalise_date(value):
    """Convert date/datetime/string values to a normalized pandas timestamp."""
    return pd.Timestamp(value).normalize()


def get_available_date_range():
    """
    Return the available complaint date range.

    This is used by the UI so users cannot select dates outside
    the actual dataset.
    """
    complaints = load_table("COMPLAINTS").copy()

    complaints["COMPLAINT_DATE"] = pd.to_datetime(
        complaints["COMPLAINT_DATE"],
        errors="coerce",
    )

    valid_dates = complaints["COMPLAINT_DATE"].dropna()

    if valid_dates.empty:
        raise ValueError(
            "COMPLAINTS contains no valid COMPLAINT_DATE values."
        )

    return {
        "min_date": valid_dates.min().normalize(),
        "max_date": valid_dates.max().normalize(),
    }


def get_investigation_periods(
    start_period=None,
    end_period=None,
):
    """
    Build the selected period and the immediately preceding
    equivalent period.

    Example:
        Selected:  2025-11-01 -> 2025-11-07
        Previous:  2025-10-25 -> 2025-10-31
    """

    available = get_available_date_range()

    if start_period is None:
        start_period = available["max_date"]

    if end_period is None:
        end_period = available["max_date"]

    start_period = _normalise_date(start_period)
    end_period = _normalise_date(end_period)

    if start_period > end_period:
        raise ValueError(
            "Start period cannot be after end period."
        )

    if start_period < available["min_date"]:
        raise ValueError(
            "Start period is earlier than the available dataset."
        )

    if end_period > available["max_date"]:
        raise ValueError(
            "End period is later than the available dataset."
        )

    period_length = (
        end_period - start_period
    ).days + 1

    previous_end = (
        start_period
        - pd.Timedelta(days=1)
    )

    previous_start = (
        previous_end
        - pd.Timedelta(days=period_length - 1)
    )

    return {
        "current_start": start_period,
        "current_end": end_period,
        "previous_start": previous_start,
        "previous_end": previous_end,
    }


# ============================================================
# COMPLAINT RATE
# ============================================================

def calculate_complaint_rate(
    start_period=None,
    end_period=None,
):
    """
    Calculate Complaint Rate for the selected period and the
    immediately preceding equivalent period.
    """

    complaints = load_table("COMPLAINTS").copy()
    accounts = load_table("ACCOUNT_HEALTH").copy()

    complaints["COMPLAINT_DATE"] = pd.to_datetime(
        complaints["COMPLAINT_DATE"],
        errors="coerce",
    )

    accounts["SNAPSHOT_DATE"] = pd.to_datetime(
        accounts["SNAPSHOT_DATE"],
        errors="coerce",
    )

    periods = get_investigation_periods(
        start_period=start_period,
        end_period=end_period,
    )

    # --------------------------------------------------------
    # CURRENT PERIOD
    # --------------------------------------------------------

    current = complaints[
        (complaints["COMPLAINT_DATE"] >= periods["current_start"])
        & (complaints["COMPLAINT_DATE"] <= periods["current_end"])
    ]

    current_accounts = accounts[
        (accounts["SNAPSHOT_DATE"] >= periods["current_start"])
        & (accounts["SNAPSHOT_DATE"] <= periods["current_end"])
    ]

    # --------------------------------------------------------
    # PREVIOUS PERIOD
    # --------------------------------------------------------

    previous = complaints[
        (complaints["COMPLAINT_DATE"] >= periods["previous_start"])
        & (complaints["COMPLAINT_DATE"] <= periods["previous_end"])
    ]

    previous_accounts = accounts[
        (accounts["SNAPSHOT_DATE"] >= periods["previous_start"])
        & (accounts["SNAPSHOT_DATE"] <= periods["previous_end"])
    ]

    # --------------------------------------------------------
    # ACCOUNT COUNTS
    # --------------------------------------------------------

    current_account_count = (
        current_accounts["ACCOUNT_NUMBER"]
        .nunique()
    )

    previous_account_count = (
        previous_accounts["ACCOUNT_NUMBER"]
        .nunique()
    )

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    current_rate = (
        len(current) / current_account_count * 100
        if current_account_count > 0
        else 0.0
    )

    previous_rate = (
        len(previous) / previous_account_count * 100
        if previous_account_count > 0
        else 0.0
    )

    absolute_change = current_rate - previous_rate

    if previous_rate != 0:
        relative_change = (
            (current_rate - previous_rate)
            / previous_rate
        ) * 100
    else:
        relative_change = None

    if absolute_change < 0:
        direction = "improving"
    elif absolute_change > 0:
        direction = "worsening"
    else:
        direction = "stable"

    return {
        "kpi": "Complaint Rate",

        "current_period": {
            "start": str(periods["current_start"].date()),
            "end": str(periods["current_end"].date()),
            "complaints": int(len(current)),
            "accounts": int(current_account_count),
            "complaint_rate": round(current_rate, 2),
        },

        "previous_period": {
            "start": str(periods["previous_start"].date()),
            "end": str(periods["previous_end"].date()),
            "complaints": int(len(previous)),
            "accounts": int(previous_account_count),
            "complaint_rate": round(previous_rate, 2),
        },

        "change": {
            "absolute": round(absolute_change, 2),
            "relative_percent": (
                round(relative_change, 2)
                if relative_change is not None
                else None
            ),
            "direction": direction,
        },
    }
