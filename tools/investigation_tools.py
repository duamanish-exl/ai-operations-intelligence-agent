import pandas as pd

from data_loader import load_table


def investigate_complaints(periods):

    complaints = load_table("COMPLAINTS")

    complaints["COMPLAINT_DATE"] = pd.to_datetime(
        complaints["COMPLAINT_DATE"]
    )

    current = complaints[
        (complaints["COMPLAINT_DATE"] >= periods["current_start"])
        & (complaints["COMPLAINT_DATE"] <= periods["current_end"])
    ]

    previous = complaints[
        (complaints["COMPLAINT_DATE"] >= periods["previous_start"])
        & (complaints["COMPLAINT_DATE"] <= periods["previous_end"])
    ]

    return {
        "investigation": "Complaint Investigation",

        "current_complaints": len(current),
        "previous_complaints": len(previous),

        "categories": {
            "current": current["CATEGORY"].value_counts().to_dict(),
            "previous": previous["CATEGORY"].value_counts().to_dict()
        },

        "subcategories": {
            "current": current["SUBCATEGORY"].value_counts().to_dict(),
            "previous": previous["SUBCATEGORY"].value_counts().to_dict()
        },

        "severity": {
            "current": current["SEVERITY"].value_counts().to_dict(),
            "previous": previous["SEVERITY"].value_counts().to_dict()
        },

        "channels": {
            "current": current["CHANNEL"].value_counts().to_dict(),
            "previous": previous["CHANNEL"].value_counts().to_dict()
        },

        "root_causes": {
            "current": current["ROOT_CAUSE_DRIVER"].value_counts().to_dict(),
            "previous": previous["ROOT_CAUSE_DRIVER"].value_counts().to_dict()
        }
    }


def investigate_billing(periods):

    billing = load_table("BILLING_HISTORY")

    billing["BILL_DATE"] = pd.to_datetime(
        billing["BILL_DATE"]
    )

    current = billing[
        (billing["BILL_DATE"] >= periods["current_start"])
        & (billing["BILL_DATE"] <= periods["current_end"])
    ]

    previous = billing[
        (billing["BILL_DATE"] >= periods["previous_start"])
        & (billing["BILL_DATE"] <= periods["previous_end"])
    ]

    return {
        "investigation": "Billing Investigation",

        "current_bills": len(current),
        "previous_bills": len(previous),

        "current_total_billed": current["BILL_AMOUNT"].sum(),
        "previous_total_billed": previous["BILL_AMOUNT"].sum(),

        "current_bill_status": current["BILL_STATUS"].value_counts().to_dict(),
        "previous_bill_status": previous["BILL_STATUS"].value_counts().to_dict()
    }


def investigate_meter(periods):

    readings = load_table("METER_READING")
    meters = load_table("METER_INFORMATION")

    readings["READ_DATE"] = pd.to_datetime(
        readings["READ_DATE"]
    )

    current = readings[
        (readings["READ_DATE"] >= periods["current_start"])
        & (readings["READ_DATE"] <= periods["current_end"])
    ]

    previous = readings[
        (readings["READ_DATE"] >= periods["previous_start"])
        & (readings["READ_DATE"] <= periods["previous_end"])
    ]

    return {
        "investigation": "Meter Investigation",

        "reading_status": {
            "current": current["READ_STATUS"].value_counts().to_dict(),
            "previous": previous["READ_STATUS"].value_counts().to_dict()
        },

        "reading_types": {
            "current": current["READ_TYPE"].value_counts().to_dict(),
            "previous": previous["READ_TYPE"].value_counts().to_dict()
        },

        "meter_faults": meters["METER_FAULT_FLAG"].value_counts().to_dict(),

        "smart_meter_status": meters["SMART_METER_STATUS"].value_counts().to_dict()
    }


def investigate_payments(periods):

    payments = load_table("PAYMENTS")

    payments["PAYMENT_DATE"] = pd.to_datetime(
        payments["PAYMENT_DATE"]
    )

    current = payments[
        (payments["PAYMENT_DATE"] >= periods["current_start"])
        & (payments["PAYMENT_DATE"] <= periods["current_end"])
    ]

    previous = payments[
        (payments["PAYMENT_DATE"] >= periods["previous_start"])
        & (payments["PAYMENT_DATE"] <= periods["previous_end"])
    ]

    return {
        "investigation": "Payment Investigation",

        "current_payments": len(current),
        "previous_payments": len(previous),

        "current_payment_status": current[
            "PAYMENT_STATUS"
        ].value_counts().to_dict(),

        "previous_payment_status": previous[
            "PAYMENT_STATUS"
        ].value_counts().to_dict(),

        "current_payment_methods": current[
            "PAYMENT_METHOD"
        ].value_counts().to_dict(),

        "previous_payment_methods": previous[
            "PAYMENT_METHOD"
        ].value_counts().to_dict()
    }


def investigate_customer_interactions(periods):

    calls = load_table("CALLS")

    calls["CALL_DATE"] = pd.to_datetime(
        calls["CALL_DATE"]
    )

    current = calls[
        (calls["CALL_DATE"] >= periods["current_start"])
        & (calls["CALL_DATE"] <= periods["current_end"])
    ]

    previous = calls[
        (calls["CALL_DATE"] >= periods["previous_start"])
        & (calls["CALL_DATE"] <= periods["previous_end"])
    ]

    return {
        "investigation": "Customer Interaction Investigation",

        "current_calls": len(current),
        "previous_calls": len(previous),

        "contact_reasons": {
            "current": current["CONTACT_REASON"].value_counts().to_dict(),
            "previous": previous["CONTACT_REASON"].value_counts().to_dict()
        },

        "call_outcomes": {
            "current": current["CALL_OUTCOME"].value_counts().to_dict(),
            "previous": previous["CALL_OUTCOME"].value_counts().to_dict()
        }
    }


def investigate_account_health(periods):

    accounts = load_table("ACCOUNT_HEALTH")

    accounts["SNAPSHOT_DATE"] = pd.to_datetime(
        accounts["SNAPSHOT_DATE"]
    )

    current = accounts[
        (accounts["SNAPSHOT_DATE"] >= periods["current_start"])
        & (accounts["SNAPSHOT_DATE"] <= periods["current_end"])
    ]

    previous = accounts[
        (accounts["SNAPSHOT_DATE"] >= periods["previous_start"])
        & (accounts["SNAPSHOT_DATE"] <= periods["previous_end"])
    ]

    return {
        "investigation": "Account Health Investigation",

        "current_accounts": current["ACCOUNT_NUMBER"].nunique(),
        "previous_accounts": previous["ACCOUNT_NUMBER"].nunique(),

        "account_types": {
            "current": current["ACCOUNT_TYPE"].value_counts().to_dict(),
            "previous": previous["ACCOUNT_TYPE"].value_counts().to_dict()
        },

        "vulnerability": {
            "current": current["VULNERABILITY_FLAG"].value_counts().to_dict(),
            "previous": previous["VULNERABILITY_FLAG"].value_counts().to_dict()
        },

        "debt_status": {
            "current": current["DEBT_STATUS"].value_counts().to_dict(),
            "previous": previous["DEBT_STATUS"].value_counts().to_dict()
        }
    }