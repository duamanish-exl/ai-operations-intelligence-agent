"""
data_loader.py
==============
Single entry point for reading the synthetic operations dataset. Every
investigation tool calls load_table(name) rather than reading CSVs directly,
so the data location, caching and dtype handling live in one place.

Configure the dataset location via the INSIGHTFORGE_DATA_DIR environment
variable, or edit DEFAULT_DATA_DIR below.
"""
from __future__ import annotations
import os
from functools import lru_cache
from pathlib import Path

import pandas as pd

DEFAULT_DATA_DIR = Path(os.environ.get("INSIGHTFORGE_DATA_DIR", "./data"))

# Canonical table name -> CSV filename
TABLES = {
    "ACCOUNT_HEALTH": "ACCOUNT_HEALTH.csv",
    "ACCOUNT_BALANCE": "ACCOUNT_BALANCE.csv",
    "BILLING_HISTORY": "BILLING_HISTORY.csv",
    "METER_READING": "METER_READING.csv",
    "METER_INFORMATION": "METER_INFORMATION.csv",
    "PAYMENTS": "PAYMENTS.csv",
    "COMPLAINTS": "COMPLAINTS.csv",
    "CALLS": "CALLS.csv",
    "CONTRACT": "CONTRACT.csv",
}


@lru_cache(maxsize=None)
def load_table(name: str) -> pd.DataFrame:
    """Load a table by canonical name. Result is cached for the session."""
    name = name.upper()
    if name not in TABLES:
        raise KeyError(f"Unknown table '{name}'. Available: {sorted(TABLES)}")
    path = DEFAULT_DATA_DIR / TABLES[name]
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Set INSIGHTFORGE_DATA_DIR to the folder holding the CSVs."
        )
    return pd.read_csv(path)


def clear_cache() -> None:
    """Drop cached tables (e.g. after regenerating the dataset)."""
    load_table.cache_clear()
