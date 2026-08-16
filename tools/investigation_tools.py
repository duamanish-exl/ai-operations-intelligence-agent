from data_loader import load_table
import pandas as pd


# ============================================================
# HELPER
# ============================================================

def filter_period(df, date_column, start_date, end_date):
    """
    Filter a dataframe between two dates.
    """

    df = df.copy()

    df[date_column] = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    return df[
        (df[date_column] >= start_date) &
        (df[date_column] <= end_date)
    ]


# ============================================================
# 1. COMPLAINT INVESTIGATION
# ============================================================

def investigate_complaints(periods):

    complaints = load_table("COMPLAINTS")

    current = filter_period(
        complaints,
        "COMPLAINT_DATE",
        periods["current_start"],
        periods["current_end"]
    )

    previous = filter_period(
        complaints,
        "COMPLAINT_DATE",
        periods["previous_start"],
        periods["previous_end"]
    )

    return {

        "current_complaints": len(current),

        "previous_complaints": len(previous),

        "current_categories": (
            current["CATEGORY"]
            .value_counts()
            .to_dict()
        ),

        "previous_categories": (
            previous["CATEGORY"]
            .value_counts()
            .to_dict()
        ),

        "current_reasons": (
            current["COMPLAINT_REASON"]
            .value_counts()
            .to_dict()
        ),

        "previous_reasons": (
            previous["COMPLAINT_REASON"]
            .value_counts()
            .to_dict()
        ),

        "current_root_cause_drivers": (
            current["ROOT_CAUSE_DRIVER"]
            .value_counts()
            .to_dict()
        ),

        "previous_root_cause_drivers": (
            previous["ROOT_CAUSE_DRIVER"]
            .value_counts()
            .to_dict()
        ),

        "current_channels": (
            current["CHANNEL"]
            .value_counts()
            .to_dict()
        ),

        "previous_channels": (
            previous["CHANNEL"]
            .value_counts()
            .to_dict()
        ),

        "current_severity": (
            current["SEVERITY"]
            .value_counts()
            .to_dict()
        ),

        "previous_severity": (
            previous["SEVERITY"]
            .value_counts()
            .to_dict()
        ),

        "current_escalations": (
            current["ESCALATION_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "previous_escalations": (
            previous["ESCALATION_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "current_repeat_complaints": (
            current["REPEAT_COMPLAINT_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "previous_repeat_complaints": (
            previous["REPEAT_COMPLAINT_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "current_vulnerable_customers": (
            current["VULNERABLE_CUSTOMER_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "previous_vulnerable_customers": (
            previous["VULNERABLE_CUSTOMER_FLAG"]
            .value_counts()
            .to_dict()
        )
    }


# ============================================================
# 2. BILLING INVESTIGATION
# ============================================================

def investigate_billing(periods):

    billing = load_table("BILLING_HISTORY")

    current = filter_period(
        billing,
        "BILL_DATE",
        periods["current_start"],
        periods["current_end"]
    )

    previous = filter_period(
        billing,
        "BILL_DATE",
        periods["previous_start"],
        periods["previous_end"]
    )

    return {

        "current_bills": len(current),

        "previous_bills": len(previous),

        "current_bill_amount": (
            current["BILL_AMOUNT"].sum()
        ),

        "previous_bill_amount": (
            previous["BILL_AMOUNT"].sum()
        ),

        "current_average_bill": (
            current["BILL_AMOUNT"].mean()
            if len(current) > 0 else 0
        ),

        "previous_average_bill": (
            previous["BILL_AMOUNT"].mean()
            if len(previous) > 0 else 0
        ),

        "current_estimated_bills": (
            current["ESTIMATED_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "previous_estimated_bills": (
            previous["ESTIMATED_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "current_bill_types": (
            current["BILL_TYPE"]
            .value_counts()
            .to_dict()
        ),

        "previous_bill_types": (
            previous["BILL_TYPE"]
            .value_counts()
            .to_dict()
        ),

        "current_fuel_types": (
            current["FUEL_TYPE"]
            .value_counts()
            .to_dict()
        ),

        "previous_fuel_types": (
            previous["FUEL_TYPE"]
            .value_counts()
            .to_dict()
        )
    }


# ============================================================
# 3. METER INVESTIGATION
# ============================================================

def investigate_meter(periods):

    readings = load_table("METER_READING")

    current = filter_period(
        readings,
        "READING_DATE",
        periods["current_start"],
        periods["current_end"]
    )

    previous = filter_period(
        readings,
        "READING_DATE",
        periods["previous_start"],
        periods["previous_end"]
    )

    return {

        "current_readings": len(current),

        "previous_readings": len(previous),

        "current_reading_types": (
            current["READING_TYPE"]
            .value_counts()
            .to_dict()
        ),

        "previous_reading_types": (
            previous["READING_TYPE"]
            .value_counts()
            .to_dict()
        ),

        "current_fuel_types": (
            current["FUEL_TYPE"]
            .value_counts()
            .to_dict()
        ),

        "previous_fuel_types": (
            previous["FUEL_TYPE"]
            .value_counts()
            .to_dict()
        ),

        "current_consumption": (
            current["CONSUMPTION_VALUE"].sum()
        ),

        "previous_consumption": (
            previous["CONSUMPTION_VALUE"].sum()
        )
    }


# ============================================================
# 4. PAYMENT INVESTIGATION
# ============================================================

def investigate_payments(periods):

    payments = load_table("PAYMENTS")

    current = filter_period(
        payments,
        "PAYMENT_DATE",
        periods["current_start"],
        periods["current_end"]
    )

    previous = filter_period(
        payments,
        "PAYMENT_DATE",
        periods["previous_start"],
        periods["previous_end"]
    )

    return {

        "current_payments": len(current),

        "previous_payments": len(previous),

        "current_payment_status": (
            current["PAYMENT_STATUS"]
            .value_counts()
            .to_dict()
        ),

        "previous_payment_status": (
            previous["PAYMENT_STATUS"]
            .value_counts()
            .to_dict()
        ),

        "current_payment_methods": (
            current["PAYMENT_METHOD"]
            .value_counts()
            .to_dict()
        ),

        "previous_payment_methods": (
            previous["PAYMENT_METHOD"]
            .value_counts()
            .to_dict()
        ),

        "current_fail_reasons": (
            current["FAIL_REASON"]
            .value_counts()
            .to_dict()
        ),

        "previous_fail_reasons": (
            previous["FAIL_REASON"]
            .value_counts()
            .to_dict()
        ),

        "current_amount_paid": (
            current["AMOUNT_PAID"].sum()
        ),

        "previous_amount_paid": (
            previous["AMOUNT_PAID"].sum()
        )
    }


# ============================================================
# 5. CUSTOMER INTERACTION INVESTIGATION
# ============================================================

def investigate_customer_interactions(periods):

    calls = load_table("CALLS")

    current = filter_period(
        calls,
        "CALL_DATE",
        periods["current_start"],
        periods["current_end"]
    )

    previous = filter_period(
        calls,
        "CALL_DATE",
        periods["previous_start"],
        periods["previous_end"]
    )

    return {

        "current_calls": len(current),

        "previous_calls": len(previous),

        "current_call_reasons": (
            current["CALL_REASON"]
            .value_counts()
            .to_dict()
        ),

        "previous_call_reasons": (
            previous["CALL_REASON"]
            .value_counts()
            .to_dict()
        ),

        "current_outcomes": (
            current["OUTCOME"]
            .value_counts()
            .to_dict()
        ),

        "previous_outcomes": (
            previous["OUTCOME"]
            .value_counts()
            .to_dict()
        ),

        "current_agent_teams": (
            current["AGENT_TEAM"]
            .value_counts()
            .to_dict()
        ),

        "previous_agent_teams": (
            previous["AGENT_TEAM"]
            .value_counts()
            .to_dict()
        ),

        "current_average_call_duration": (
            current["CALL_DURATION_MINS"].mean()
            if len(current) > 0 else 0
        ),

        "previous_average_call_duration": (
            previous["CALL_DURATION_MINS"].mean()
            if len(previous) > 0 else 0
        )
    }


# ============================================================
# 6. ACCOUNT HEALTH INVESTIGATION
# ============================================================

def investigate_account_health(periods):

    accounts = load_table("ACCOUNT_HEALTH")

    current = filter_period(
        accounts,
        "SNAPSHOT_DATE",
        periods["current_start"],
        periods["current_end"]
    )

    previous = filter_period(
        accounts,
        "SNAPSHOT_DATE",
        periods["previous_start"],
        periods["previous_end"]
    )

    return {

        "current_accounts": len(current),

        "previous_accounts": len(previous),

        "current_account_types": (
            current["ACCOUNT_TYPE"]
            .value_counts()
            .to_dict()
        ),

        "previous_account_types": (
            previous["ACCOUNT_TYPE"]
            .value_counts()
            .to_dict()
        ),

        "current_vulnerability": (
            current["VULNERABLE_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "previous_vulnerability": (
            previous["VULNERABLE_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "current_affordability": (
            current["AFFORDABILITY_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "previous_affordability": (
            previous["AFFORDABILITY_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "current_financial_flags": (
            current["FINANCIAL_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "previous_financial_flags": (
            previous["FINANCIAL_FLAG"]
            .value_counts()
            .to_dict()
        ),

        "current_live_status": (
            current["LIVE_STATUS"]
            .value_counts()
            .to_dict()
        ),

        "previous_live_status": (
            previous["LIVE_STATUS"]
            .value_counts()
            .to_dict()
        ),

        "current_average_balance": (
            current["CURRENT_BALANCE"].mean()
            if len(current) > 0 else 0
        ),

        "previous_average_balance": (
            previous["CURRENT_BALANCE"].mean()
            if len(previous) > 0 else 0
        )
    }