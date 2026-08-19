import pandas as pd

from data_loader import load_table


# ============================================================
# SUPPORTED KPIs
# ============================================================

SUPPORTED_KPIS = [
    "Complaint Rate",
    "Payment Failure Rate",
    "Average Bill Amount",
]


# ============================================================
# KPI CONFIG
# ============================================================

KPI_INFO = {
    "Complaint Rate": {
        "unit": "%",
        "lower_is_better": True,
        "source_table": "COMPLAINTS",
    },
    "Payment Failure Rate": {
        "unit": "%",
        "lower_is_better": True,
        "source_table": "PAYMENTS",
    },
    "Average Bill Amount": {
        "unit": "£",
        "lower_is_better": False,
        "source_table": "BILLING_HISTORY",
    },
}


# ============================================================
# GENERAL HELPERS
# ============================================================

def _normalise_date(value):
    return pd.Timestamp(value).normalize()


def _get_date_column(kpi_name):
    if kpi_name == "Complaint Rate":
        return "COMPLAINT_DATE"

    if kpi_name == "Payment Failure Rate":
        return "PAYMENT_DATE"

    if kpi_name == "Average Bill Amount":
        return "BILL_DATE"

    raise ValueError(f"Unsupported KPI: {kpi_name}")


def _load_kpi_dates(kpi_name):
    table_name = KPI_INFO[kpi_name]["source_table"]
    date_column = _get_date_column(kpi_name)

    df = load_table(table_name).copy()

    if date_column not in df.columns:
        raise ValueError(
            f"{table_name} does not contain required column "
            f"{date_column}."
        )

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce",
    )

    valid_dates = df[date_column].dropna()

    if valid_dates.empty:
        raise ValueError(
            f"{table_name} contains no valid dates in "
            f"{date_column}."
        )

    return {
        "min_date": valid_dates.min().normalize(),
        "max_date": valid_dates.max().normalize(),
    }

def _date_range_for_table(table_name, date_columns):
    """
    Return the available date range for a table.

    Parameters
    ----------
    table_name : str
        Name of the table to load.

    date_columns : list[str]
        Candidate date columns. The first column that exists
        in the table will be used.

    Returns
    -------
    dict
        {
            "min_date": pd.Timestamp,
            "max_date": pd.Timestamp
        }
    """
    df = load_table(table_name).copy()

    # Find the first available date column
    date_column = next(
        (
            column
            for column in date_columns
            if column in df.columns
        ),
        None,
    )

    if date_column is None:
        raise ValueError(
            f"{table_name} does not contain any of the required "
            f"date columns: {', '.join(date_columns)}."
        )

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce",
    )

    valid_dates = df[date_column].dropna()

    if valid_dates.empty:
        raise ValueError(
            f"{table_name} contains no valid dates in "
            f"{date_column}."
        )

    return {
        "min_date": valid_dates.min().normalize(),
        "max_date": valid_dates.max().normalize(),
    }
def get_available_date_range(kpi_name):

    if kpi_name == "Complaint Rate":
        return _date_range_for_table(
            "COMPLAINTS",
            ["COMPLAINT_DATE"],
        )

    if kpi_name == "Payment Failure Rate":
        return _date_range_for_table(
            "PAYMENTS",
            ["PAYMENT_DATE"],
        )

    if kpi_name == "Average Bill Amount":
        return _date_range_for_table(
            "BILLING_HISTORY",
            ["BILL_DATE"], 
        )

    raise ValueError(
        f"Unsupported KPI: {kpi_name}"
    )


# ============================================================
# PERIOD HELPERS
# ============================================================

def get_investigation_periods(
    start_period=None,
    end_period=None,
    kpi_name="Complaint Rate",
):
    available = get_available_date_range(kpi_name)

    if start_period is None:
        end_period = available["max_date"]
        start_period = max(
            available["min_date"],
            end_period - pd.Timedelta(days=6),
        )

    elif end_period is None:
        end_period = start_period

    start_period = _normalise_date(start_period)
    end_period = _normalise_date(end_period)

    if start_period > end_period:
        raise ValueError(
            "Start period cannot be after end period."
        )

    if start_period < available["min_date"]:
        raise ValueError(
            f"Start period is earlier than the available "
            f"{kpi_name} data."
        )

    if end_period > available["max_date"]:
        raise ValueError(
            f"End period is later than the available "
            f"{kpi_name} data."
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
# CHANGE CALCULATION
# ============================================================

def _calculate_change(
    current_value,
    previous_value,
):
    absolute_change = current_value - previous_value

    if previous_value == 0:
        relative_change = None
    else:
        relative_change = (
            absolute_change / previous_value
        ) * 100

    if absolute_change < 0:
        direction = "improving"
    elif absolute_change > 0:
        direction = "worsening"
    else:
        direction = "stable"

    return {
        "absolute": round(
            absolute_change,
            2,
        ),
        "relative_percent": (
            round(
                relative_change,
                2,
            )
            if relative_change is not None
            else None
        ),
        "direction": direction,
    }


# ============================================================
# COMPLAINT RATE
# ============================================================

def calculate_complaint_rate(
    start_period=None,
    end_period=None,
):
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
        kpi_name="Complaint Rate",
    )

    current = complaints[
        (complaints["COMPLAINT_DATE"] >= periods["current_start"])
        & (complaints["COMPLAINT_DATE"] <= periods["current_end"])
    ]

    current_accounts = accounts[
        (accounts["SNAPSHOT_DATE"] >= periods["current_start"])
        & (accounts["SNAPSHOT_DATE"] <= periods["current_end"])
    ]

    previous = complaints[
        (complaints["COMPLAINT_DATE"] >= periods["previous_start"])
        & (complaints["COMPLAINT_DATE"] <= periods["previous_end"])
    ]

    previous_accounts = accounts[
        (accounts["SNAPSHOT_DATE"] >= periods["previous_start"])
        & (accounts["SNAPSHOT_DATE"] <= periods["previous_end"])
    ]

    current_account_count = (
        current_accounts["ACCOUNT_NUMBER"].nunique()
    )

    previous_account_count = (
        previous_accounts["ACCOUNT_NUMBER"].nunique()
    )

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

    return {
        "kpi": "Complaint Rate",
        "unit": "%",

        "current_period": {
            "start": str(
                periods["current_start"].date()
            ),
            "end": str(
                periods["current_end"].date()
            ),
            "complaints": int(len(current)),
            "accounts": int(current_account_count),
            "complaint_rate": round(
                current_rate,
                2,
            ),
        },

        "previous_period": {
            "start": str(
                periods["previous_start"].date()
            ),
            "end": str(
                periods["previous_end"].date()
            ),
            "complaints": int(len(previous)),
            "accounts": int(previous_account_count),
            "complaint_rate": round(
                previous_rate,
                2,
            ),
        },

        "change": _calculate_change(
            current_rate,
            previous_rate,
        ),
    }


# ============================================================
# PAYMENT FAILURE RATE
# ============================================================

def calculate_payment_failure_rate(
    start_period=None,
    end_period=None,
):
    payments = load_table("PAYMENTS").copy()

    required_columns = [
        "PAYMENT_DATE",
        "PAYMENT_STATUS",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in payments.columns
    ]

    if missing_columns:
        raise ValueError(
            "PAYMENTS is missing required columns: "
            + ", ".join(missing_columns)
        )

    payments["PAYMENT_DATE"] = pd.to_datetime(
        payments["PAYMENT_DATE"],
        errors="coerce",
    )

    periods = get_investigation_periods(
        start_period=start_period,
        end_period=end_period,
        kpi_name="Payment Failure Rate",
    )

    current = payments[
        (payments["PAYMENT_DATE"] >= periods["current_start"])
        & (payments["PAYMENT_DATE"] <= periods["current_end"])
    ].copy()

    previous = payments[
        (payments["PAYMENT_DATE"] >= periods["previous_start"])
        & (payments["PAYMENT_DATE"] <= periods["previous_end"])
    ].copy()

    failure_statuses = {
        "FAILED",
        "FAILURE",
        "DECLINED",
        "REJECTED",
        "RETURNED",
        "BOUNCED",
        "UNSUCCESSFUL",
        "DISHONOURED",
        "DISHONORED",
    }

    current_status = (
        current["PAYMENT_STATUS"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    previous_status = (
        previous["PAYMENT_STATUS"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    current_failed = int(
        current_status.isin(
            failure_statuses
        ).sum()
    )

    previous_failed = int(
        previous_status.isin(
            failure_statuses
        ).sum()
    )

    current_total = int(len(current))
    previous_total = int(len(previous))

    current_rate = (
        current_failed / current_total * 100
        if current_total > 0
        else 0.0
    )

    previous_rate = (
        previous_failed / previous_total * 100
        if previous_total > 0
        else 0.0
    )

    return {
        "kpi": "Payment Failure Rate",
        "unit": "%",

        "current_period": {
            "start": str(
                periods["current_start"].date()
            ),
            "end": str(
                periods["current_end"].date()
            ),
            "failed_payments": current_failed,
            "total_payments": current_total,
            "payment_failure_rate": round(
                current_rate,
                2,
            ),
        },

        "previous_period": {
            "start": str(
                periods["previous_start"].date()
            ),
            "end": str(
                periods["previous_end"].date()
            ),
            "failed_payments": previous_failed,
            "total_payments": previous_total,
            "payment_failure_rate": round(
                previous_rate,
                2,
            ),
        },

        "change": _calculate_change(
            current_rate,
            previous_rate,
        ),

        "definition": {
            "status_column": "PAYMENT_STATUS",
            "failure_statuses": sorted(
                failure_statuses
            ),
        },
    }


# ============================================================
# AVERAGE BILL AMOUNT
# ============================================================

def calculate_average_bill_amount(
    start_period=None,
    end_period=None,
):
    billing = load_table(
        "BILLING_HISTORY"
    ).copy()

    required_columns = [
        "BILL_DATE",
        "BILL_AMOUNT",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in billing.columns
    ]

    if missing_columns:
        raise ValueError(
            "BILLING_HISTORY is missing required columns: "
            + ", ".join(missing_columns)
        )

    billing["BILL_DATE"] = pd.to_datetime(
        billing["BILL_DATE"],
        errors="coerce",
    )

    billing["BILL_AMOUNT"] = pd.to_numeric(
        billing["BILL_AMOUNT"],
        errors="coerce",
    )

    periods = get_investigation_periods(
        start_period=start_period,
        end_period=end_period,
        kpi_name="Average Bill Amount",
    )

    current = billing[
        (billing["BILL_DATE"] >= periods["current_start"])
        & (billing["BILL_DATE"] <= periods["current_end"])
    ].copy()

    previous = billing[
        (billing["BILL_DATE"] >= periods["previous_start"])
        & (billing["BILL_DATE"] <= periods["previous_end"])
    ].copy()

    current = current.dropna(
        subset=["BILL_AMOUNT"]
    )

    previous = previous.dropna(
        subset=["BILL_AMOUNT"]
    )

    current_average = (
        current["BILL_AMOUNT"].mean()
        if not current.empty
        else 0.0
    )

    previous_average = (
        previous["BILL_AMOUNT"].mean()
        if not previous.empty
        else 0.0
    )

    return {
        "kpi": "Average Bill Amount",
        "unit": "£",

        "current_period": {
            "start": str(
                periods["current_start"].date()
            ),
            "end": str(
                periods["current_end"].date()
            ),
            "bill_count": int(len(current)),
            "average_bill_amount": round(
                current_average,
                2,
            ),
        },

        "previous_period": {
            "start": str(
                periods["previous_start"].date()
            ),
            "end": str(
                periods["previous_end"].date()
            ),
            "bill_count": int(len(previous)),
            "average_bill_amount": round(
                previous_average,
                2,
            ),
        },

        "change": _calculate_change(
            current_average,
            previous_average,
        ),
    }


# ============================================================
# KPI DISPATCHER
# ============================================================

def calculate_kpi(
    kpi_name,
    start_period=None,
    end_period=None,
):
    if kpi_name == "Complaint Rate":
        return calculate_complaint_rate(
            start_period=start_period,
            end_period=end_period,
        )

    if kpi_name == "Payment Failure Rate":
        return calculate_payment_failure_rate(
            start_period=start_period,
            end_period=end_period,
        )

    if kpi_name == "Average Bill Amount":
        return calculate_average_bill_amount(
            start_period=start_period,
            end_period=end_period,
        )

    raise ValueError(
        f"Unsupported KPI: {kpi_name}"
    )
