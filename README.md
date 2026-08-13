# InsightForge — Investigation Tools

Investigation surface for the **InsightForge AI Operations Intelligence Agent**.
Each tool compares a *current* period against a *previous* period and returns a
structured evidence dictionary the agent reasons over to explain KPI movements
(Debt % and Complaint Rate).

## Files
- `data_loader.py` — cached CSV loader. Set `INSIGHTFORGE_DATA_DIR` to the folder holding the 9 dataset CSVs.
- `investigation_tools.py` — the 7 investigation tools + dispatcher.

## Tools
| Function | Investigates | Primary table(s) |
|---|---|---|
| `investigate_account_health` | Debt % KPI, arrears, recovery, vulnerability | ACCOUNT_HEALTH, ACCOUNT_BALANCE |
| `investigate_billing` | bill amounts, estimated bills, consumption | BILLING_HISTORY |
| `investigate_payments` | failure rate, fail reasons, methods | PAYMENTS |
| `investigate_meter` | reading types, estimation, meter faults | METER_READING, METER_INFORMATION |
| `investigate_customer_interactions` | call volume, reasons, outcomes | CALLS |
| `investigate_complaints` | volume, category, severity, escalation | COMPLAINTS |
| `investigate_tariff_contract` | expiries, tariff/contract mix | CONTRACT |

## Usage
```python
from data_loader import load_table  # noqa
from investigation_tools import build_periods, run_tool, run_all

periods = build_periods(
    current_start="2026-01-01", current_end="2026-02-28",
    previous_start="2025-09-01", previous_end="2025-10-31",
)

evidence = run_tool("account_health", periods)   # one tool
all_evidence = run_all(periods)                    # full sweep
```
Set the data location first:
```bash
export INSIGHTFORGE_DATA_DIR=/path/to/dataset/csv_files
```

## Schema alignment note
An earlier draft referenced columns that don't exist in this dataset
(`SUBCATEGORY`, `BILL_STATUS`, `READ_DATE`, `READ_STATUS`, `METER_FAULT_FLAG`,
`CONTACT_REASON`, `DEBT_STATUS`, `VULNERABILITY_FLAG`). These tools use the
**actual** columns — see the module docstring in `investigation_tools.py` for
the full mapping and the reasoning behind each substitution.
