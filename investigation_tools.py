"""
investigation_tools.py
======================
Investigation tools for the InsightForge AI Operations Intelligence Agent.

Each function compares a CURRENT period against a PREVIOUS period and returns
a structured evidence dictionary the agent reasons over. All column names are
aligned to the actual dataset produced by the `utility_synth` generator (see
DATA_DICTIONARY.md). A helper `build_periods()` and a `run_all()` dispatcher
are included so the agent can request one tool or a full sweep.

Period contract
---------------
Every tool takes a `periods` dict with four dates (str 'YYYY-MM-DD' or
Timestamp):
    current_start, current_end, previous_start, previous_end

Design notes vs. a naive first draft
-------------------------------------
* COMPLAINTS has no SUBCATEGORY column -> we use COMPLAINT_REASON (the 54
  distinct free-text reasons) as the sub-level, and also surface STATUS,
  OUTCOME, RESOLUTION_TYPE and the escalation/ombudsman/repeat/vulnerable
  flags, because for Complaint-Rate investigations *severity trend* matters
  as much as volume.
* BILLING has no BILL_STATUS -> the operationally meaningful split is
  ESTIMATED_FLAG (estimated vs actual) and BILL_TYPE (Regular/Final), plus
  average bill and consumption movement, which is what actually drives
  complaints and debt.
* METER uses READING_DATE / READING_TYPE (not READ_DATE / READ_STATUS) and
  METER_STATUS / METER_TYPE (not METER_FAULT_FLAG / SMART_METER_STATUS).
  Meter faults are a *status value* ('Faulty'), counted point-in-time and
  restricted to faults whose active window overlaps the current period.
* Debt status lives in ACCOUNT_BALANCE (ARREARS_STAGE, DEBT_FLAG, etc.), not
  ACCOUNT_HEALTH. Account Health investigation reads both tables and computes
  the Debt % KPI directly, plus vulnerable/affordability composition.
* CALLS uses CALL_REASON / OUTCOME (not CONTACT_REASON / CALL_OUTCOME) and is
  split by direction, since a rise in *outbound* collections calls tells a
  very different story from a rise in *inbound* billing calls.
"""
from __future__ import annotations
from typing import Dict, Any, Callable

import pandas as pd

from data_loader import load_table


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def build_periods(current_start, current_end, previous_start, previous_end) -> Dict[str, pd.Timestamp]:
    """Normalise the four period boundaries into Timestamps."""
    return {
        "current_start": pd.Timestamp(current_start),
        "current_end": pd.Timestamp(current_end),
        "previous_start": pd.Timestamp(previous_start),
        "previous_end": pd.Timestamp(previous_end),
    }


def _split(df: pd.DataFrame, date_col: str, periods: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (current, previous) slices of df on date_col."""
    d = pd.to_datetime(df[date_col])
    current = df[(d >= periods["current_start"]) & (d <= periods["current_end"])]
    previous = df[(d >= periods["previous_start"]) & (d <= periods["previous_end"])]
    return current, previous


def _delta(cur: float, prev: float) -> dict:
    """Absolute and % change, guarding divide-by-zero."""
    change = cur - prev
    pct = (change / prev * 100) if prev else None
    return {"current": round(cur, 2), "previous": round(prev, 2),
            "change": round(change, 2), "pct_change": round(pct, 1) if pct is not None else None}


def _vc(series: pd.Series) -> dict:
    return series.value_counts(dropna=False).to_dict()


# ---------------------------------------------------------------------------
# 1. Complaint Investigation
# ---------------------------------------------------------------------------
def investigate_complaints(periods: dict) -> Dict[str, Any]:
    complaints = load_table("COMPLAINTS")
    current, previous = _split(complaints, "COMPLAINT_DATE", periods)

    def esc_rate(df):
        return round(df["ESCALATION_FLAG"].mean() * 100, 1) if len(df) else 0.0

    return {
        "investigation": "Complaint Investigation",
        "volume": _delta(len(current), len(previous)),
        "categories": {"current": _vc(current["CATEGORY"]), "previous": _vc(previous["CATEGORY"])},
        # COMPLAINT_REASON is the sub-level (dataset has no SUBCATEGORY column)
        "reasons_top10": {
            "current": current["COMPLAINT_REASON"].value_counts().head(10).to_dict(),
            "previous": previous["COMPLAINT_REASON"].value_counts().head(10).to_dict(),
        },
        "root_causes": {"current": _vc(current["ROOT_CAUSE_DRIVER"]), "previous": _vc(previous["ROOT_CAUSE_DRIVER"])},
        "severity": {"current": _vc(current["SEVERITY"]), "previous": _vc(previous["SEVERITY"])},
        "channels": {"current": _vc(current["CHANNEL"]), "previous": _vc(previous["CHANNEL"])},
        "status": {"current": _vc(current["STATUS"]), "previous": _vc(previous["STATUS"])},
        "outcome": {"current": _vc(current[current["OUTCOME"] != ""]["OUTCOME"]),
                     "previous": _vc(previous[previous["OUTCOME"] != ""]["OUTCOME"])},
        "escalation_rate_pct": {"current": esc_rate(current), "previous": esc_rate(previous)},
        "ombudsman_referrals": {"current": int(current["OMBUDSMAN_REFERRAL_FLAG"].sum()),
                                  "previous": int(previous["OMBUDSMAN_REFERRAL_FLAG"].sum())},
        "repeat_complaints": {"current": int(current["REPEAT_COMPLAINT_FLAG"].sum()),
                               "previous": int(previous["REPEAT_COMPLAINT_FLAG"].sum())},
        "vulnerable_complainants": {"current": int(current["VULNERABLE_CUSTOMER_FLAG"].sum()),
                                     "previous": int(previous["VULNERABLE_CUSTOMER_FLAG"].sum())},
    }


# ---------------------------------------------------------------------------
# 2. Billing Investigation
# ---------------------------------------------------------------------------
def investigate_billing(periods: dict) -> Dict[str, Any]:
    billing = load_table("BILLING_HISTORY")
    current, previous = _split(billing, "BILL_DATE", periods)

    def est_rate(df):
        return round(df["ESTIMATED_FLAG"].mean() * 100, 1) if len(df) else 0.0

    def avg_bill(df):
        return round(df["BILL_AMOUNT"].mean(), 2) if len(df) else 0.0

    return {
        "investigation": "Billing Investigation",
        "bill_volume": _delta(len(current), len(previous)),
        "total_billed": _delta(current["BILL_AMOUNT"].sum(), previous["BILL_AMOUNT"].sum()),
        "average_bill": {"current": avg_bill(current), "previous": avg_bill(previous)},
        # No BILL_STATUS column: the meaningful splits are estimated vs actual, and bill type
        "estimated_bill_rate_pct": {"current": est_rate(current), "previous": est_rate(previous)},
        "bill_type": {"current": _vc(current["BILL_TYPE"]), "previous": _vc(previous["BILL_TYPE"])},
        "avg_elec_kwh": {"current": round(current["CONSUMPTION_ELEC_KWH"].mean(), 1) if len(current) else 0.0,
                          "previous": round(previous["CONSUMPTION_ELEC_KWH"].mean(), 1) if len(previous) else 0.0},
        "avg_gas_m3": {"current": round(current["CONSUMPTION_GAS_M3"].mean(), 1) if len(current) else 0.0,
                        "previous": round(previous["CONSUMPTION_GAS_M3"].mean(), 1) if len(previous) else 0.0},
        "fuel_mix": {"current": _vc(current["FUEL_TYPE"]), "previous": _vc(previous["FUEL_TYPE"])},
    }


# ---------------------------------------------------------------------------
# 3. Meter & Consumption Investigation
# ---------------------------------------------------------------------------
def investigate_meter(periods: dict) -> Dict[str, Any]:
    readings = load_table("METER_READING")
    meters = load_table("METER_INFORMATION")
    current, previous = _split(readings, "READING_DATE", periods)

    def est_read_rate(df):
        if not len(df):
            return 0.0
        return round(df["READING_TYPE"].str.contains("Estimated").mean() * 100, 1)

    # Meter faults active during the CURRENT period (status is a value, not a flag)
    faults = meters[meters["METER_STATUS"] == "Faulty"].copy()
    faults["EFFECTIVE_FROM"] = pd.to_datetime(faults["EFFECTIVE_FROM"])
    faults["EFFECTIVE_TO"] = pd.to_datetime(faults["EFFECTIVE_TO"])
    faults_current = faults[(faults["EFFECTIVE_FROM"] <= periods["current_end"]) &
                            (faults["EFFECTIVE_TO"] >= periods["current_start"])]
    faults_previous = faults[(faults["EFFECTIVE_FROM"] <= periods["previous_end"]) &
                             (faults["EFFECTIVE_TO"] >= periods["previous_start"])]

    return {
        "investigation": "Meter & Consumption Investigation",
        "reading_volume": _delta(len(current), len(previous)),
        "reading_types": {"current": _vc(current["READING_TYPE"]), "previous": _vc(previous["READING_TYPE"])},
        "estimated_read_rate_pct": {"current": est_read_rate(current), "previous": est_read_rate(previous)},
        "avg_consumption": {"current": round(current["CONSUMPTION_VALUE"].mean(), 1) if len(current) else 0.0,
                             "previous": round(previous["CONSUMPTION_VALUE"].mean(), 1) if len(previous) else 0.0},
        "active_meter_faults": {"current": faults_current["ACCOUNT_NUMBER"].nunique(),
                                 "previous": faults_previous["ACCOUNT_NUMBER"].nunique()},
        "meter_type_mix": _vc(meters[meters["IS_CURRENT"] == True]["METER_TYPE"]),
        "meter_status_mix": _vc(meters[meters["IS_CURRENT"] == True]["METER_STATUS"]),
    }


# ---------------------------------------------------------------------------
# 4. Payment Investigation
# ---------------------------------------------------------------------------
def investigate_payments(periods: dict) -> Dict[str, Any]:
    payments = load_table("PAYMENTS")
    current, previous = _split(payments, "PAYMENT_DATE", periods)

    def fail_rate(df):
        if not len(df):
            return 0.0
        attempts = df[df["PAYMENT_STATUS"].isin(["Successful", "Failed", "Partial"])]
        return round((attempts["PAYMENT_STATUS"] != "Successful").mean() * 100, 1) if len(attempts) else 0.0

    return {
        "investigation": "Payment Investigation",
        "payment_volume": _delta(len(current), len(previous)),
        "payment_status": {"current": _vc(current["PAYMENT_STATUS"]), "previous": _vc(previous["PAYMENT_STATUS"])},
        "failure_rate_pct": {"current": fail_rate(current), "previous": fail_rate(previous)},
        "fail_reasons": {
            "current": _vc(current[current["PAYMENT_STATUS"] == "Failed"]["FAIL_REASON"]),
            "previous": _vc(previous[previous["PAYMENT_STATUS"] == "Failed"]["FAIL_REASON"]),
        },
        "payment_methods": {"current": _vc(current["PAYMENT_METHOD"]), "previous": _vc(previous["PAYMENT_METHOD"])},
        "payment_types": {"current": _vc(current["PAYMENT_TYPE"]), "previous": _vc(previous["PAYMENT_TYPE"])},
    }


# ---------------------------------------------------------------------------
# 5. Customer Interaction Investigation
# ---------------------------------------------------------------------------
def investigate_customer_interactions(periods: dict) -> Dict[str, Any]:
    calls = load_table("CALLS")
    current, previous = _split(calls, "CALL_DATE", periods)

    return {
        "investigation": "Customer Interaction Investigation",
        "call_volume": _delta(len(current), len(previous)),
        "direction": {"current": _vc(current["CALL_DIRECTION"]), "previous": _vc(previous["CALL_DIRECTION"])},
        # dataset uses CALL_REASON / OUTCOME (not CONTACT_REASON / CALL_OUTCOME)
        "call_reasons": {"current": _vc(current["CALL_REASON"]), "previous": _vc(previous["CALL_REASON"])},
        "outcomes": {"current": _vc(current["OUTCOME"]), "previous": _vc(previous["OUTCOME"])},
        "agent_teams": {"current": _vc(current["AGENT_TEAM"]), "previous": _vc(previous["AGENT_TEAM"])},
        "avg_duration_mins": {"current": round(current["CALL_DURATION_MINS"].mean(), 1) if len(current) else 0.0,
                               "previous": round(previous["CALL_DURATION_MINS"].mean(), 1) if len(previous) else 0.0},
    }


# ---------------------------------------------------------------------------
# 6. Account Health Investigation  (+ Debt % KPI)
# ---------------------------------------------------------------------------
def investigate_account_health(periods: dict) -> Dict[str, Any]:
    health = load_table("ACCOUNT_HEALTH")
    balance = load_table("ACCOUNT_BALANCE")

    h_cur, h_prev = _split(health, "SNAPSHOT_DATE", periods)
    b_cur, b_prev = _split(balance, "SNAPSHOT_DATE", periods)

    # Debt % KPI computed on the latest snapshot within each period (live accounts)
    def debt_pct(df):
        live = df[df["LIVE_STATUS"] == "Live"]
        if not len(live):
            return 0.0
        last = live.sort_values("SNAPSHOT_DATE").groupby("ACCOUNT_NUMBER").tail(1)
        return round(last["DEBT_FLAG"].mean() * 100, 1)

    def vuln_pct(df):
        live = df[df["LIVE_STATUS"] == "Live"]
        if not len(live):
            return 0.0
        last = live.sort_values("SNAPSHOT_DATE").groupby("ACCOUNT_NUMBER").tail(1)
        return round(last["VULNERABLE_FLAG"].mean() * 100, 1)

    return {
        "investigation": "Account Health Investigation",
        "active_accounts": {"current": h_cur[h_cur["LIVE_STATUS"] == "Live"]["ACCOUNT_NUMBER"].nunique(),
                             "previous": h_prev[h_prev["LIVE_STATUS"] == "Live"]["ACCOUNT_NUMBER"].nunique()},
        "debt_pct_kpi": {"current": debt_pct(b_cur), "previous": debt_pct(b_prev)},
        "financial_flag": {"current": _vc(h_cur["FINANCIAL_FLAG"]), "previous": _vc(h_prev["FINANCIAL_FLAG"])},
        # Debt status lives in ACCOUNT_BALANCE (ARREARS_STAGE), not a DEBT_STATUS column
        "arrears_stage": {"current": _vc(b_cur["ARREARS_STAGE"]), "previous": _vc(b_prev["ARREARS_STAGE"])},
        "debt_band": {"current": _vc(b_cur["DEBT_BAND"]), "previous": _vc(b_prev["DEBT_BAND"])},
        "debt_age_band": {"current": _vc(b_cur["DEBT_AGE_BAND"]), "previous": _vc(b_prev["DEBT_AGE_BAND"])},
        "collection_action": {"current": _vc(b_cur["COLLECTION_ACTION"]), "previous": _vc(b_prev["COLLECTION_ACTION"])},
        "payment_plan_status": {"current": _vc(b_cur["PAYMENT_PLAN_STATUS"]), "previous": _vc(b_prev["PAYMENT_PLAN_STATUS"])},
        "recovery_outcome": {"current": _vc(b_cur["RECOVERY_OUTCOME"]), "previous": _vc(b_prev["RECOVERY_OUTCOME"])},
        "breathing_space": {"current": int(b_cur["BREATHING_SPACE_FLAG"].sum()),
                             "previous": int(b_prev["BREATHING_SPACE_FLAG"].sum())},
        "vulnerable_pct": {"current": vuln_pct(h_cur), "previous": vuln_pct(h_prev)},
        "account_types": {"current": _vc(h_cur["ACCOUNT_TYPE"]), "previous": _vc(h_prev["ACCOUNT_TYPE"])},
    }


# ---------------------------------------------------------------------------
# 7. Tariff & Contract Investigation
# ---------------------------------------------------------------------------
def investigate_tariff_contract(periods: dict) -> Dict[str, Any]:
    contract = load_table("CONTRACT")

    # Contracts expiring within the current period (renewal / price-shock risk)
    end = pd.to_datetime(contract["CONTRACT_END_DATE"], errors="coerce")
    expiring_current = contract[(end >= periods["current_start"]) & (end <= periods["current_end"])]
    expiring_previous = contract[(end >= periods["previous_start"]) & (end <= periods["previous_end"])]

    return {
        "investigation": "Tariff & Contract Investigation",
        "contracts_expiring": _delta(len(expiring_current), len(expiring_previous)),
        "contract_type_mix": _vc(contract["CONTRACT_TYPE"]),
        "tariff_mix": contract["TARIFF_NAME"].value_counts().head(10).to_dict(),
        "status_mix": _vc(contract["STATUS"]),
        "acquisition_channel": _vc(contract["ACQUISITION_CHANNEL"]),
        "near_expiry_le_30d": int((contract["DAYS_TO_EXPIRY_AT_ASOF"].between(0, 30)).sum()),
        "expiring_tariffs_current": expiring_current["TARIFF_NAME"].value_counts().head(10).to_dict(),
    }


# ---------------------------------------------------------------------------
# dispatcher
# ---------------------------------------------------------------------------
TOOLS: Dict[str, Callable[[dict], dict]] = {
    "complaints": investigate_complaints,
    "billing": investigate_billing,
    "meter": investigate_meter,
    "payments": investigate_payments,
    "customer_interactions": investigate_customer_interactions,
    "account_health": investigate_account_health,
    "tariff_contract": investigate_tariff_contract,
}


def run_tool(name: str, periods: dict) -> dict:
    if name not in TOOLS:
        raise KeyError(f"Unknown tool '{name}'. Available: {sorted(TOOLS)}")
    return TOOLS[name](periods)


def run_all(periods: dict) -> Dict[str, dict]:
    return {name: fn(periods) for name, fn in TOOLS.items()}
