import pandas as pd
from datetime import datetime
from data_loader import load_table


def get_investigation_periods():

    complaints = load_table("COMPLAINTS")
    accounts = load_table("ACCOUNT_HEALTH")

    complaints["COMPLAINT_DATE"] = pd.to_datetime(
        complaints["COMPLAINT_DATE"]
    )

    accounts["SNAPSHOT_DATE"] = pd.to_datetime(
        accounts["SNAPSHOT_DATE"]
    )
    date_format = "%Y-%m-%d"
    current_date = datetime.strptime("2025-11-03", date_format)

    current_start = current_date - pd.Timedelta(days=6)

    previous_end = datetime.strptime("2026-08-03", date_format)

    previous_start = previous_end - pd.Timedelta(days=6)

    return {
        "current_start": current_start,
        "current_end": current_date,
        "previous_start": previous_start,
        "previous_end": previous_end
    }


def calculate_complaint_rate():

    complaints = load_table("COMPLAINTS")
    accounts = load_table("ACCOUNT_HEALTH")

    complaints["COMPLAINT_DATE"] = pd.to_datetime(
        complaints["COMPLAINT_DATE"]
    )

    accounts["SNAPSHOT_DATE"] = pd.to_datetime(
        accounts["SNAPSHOT_DATE"]
    )

    periods = get_investigation_periods()

    current = complaints[
        (complaints["COMPLAINT_DATE"] >= periods["current_start"])
        & (complaints["COMPLAINT_DATE"] <= periods["current_end"])
    ]

    previous = complaints[
        (complaints["COMPLAINT_DATE"] >= periods["previous_start"])
        & (complaints["COMPLAINT_DATE"] <= periods["previous_end"])
    ]

    current_accounts = accounts[
        (accounts["SNAPSHOT_DATE"] >= periods["current_start"])
        & (accounts["SNAPSHOT_DATE"] <= periods["current_end"])
    ]

    previous_accounts = accounts[
        (accounts["SNAPSHOT_DATE"] >= periods["previous_start"])
        & (accounts["SNAPSHOT_DATE"] <= periods["previous_end"])
    ]

    current_account_count = current_accounts["ACCOUNT_NUMBER"].nunique()
    previous_account_count = previous_accounts["ACCOUNT_NUMBER"].nunique()

    current_rate = (
        len(current) / current_account_count * 100
        if current_account_count > 0
        else 0
    )

    previous_rate = (
        len(previous) / previous_account_count * 100
        if previous_account_count > 0
        else 0
    )
    return {
        "kpi": "Complaint Rate",

        "current_period": {
            "start": str(periods["current_start"].date()),
            "end": str(periods["current_end"].date()),
            "complaints": len(current),
            "accounts": current_account_count,
            "complaint_rate": round(current_rate, 2)
        },

        "previous_period": {
            "start": str(periods["previous_start"].date()),
            "end": str(periods["previous_end"].date()),
            "complaints": len(previous),
            "accounts": previous_account_count,
            "complaint_rate": round(previous_rate, 2)
        }
    }