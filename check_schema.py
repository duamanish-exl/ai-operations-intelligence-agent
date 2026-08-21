from data_loader import load_table


tables = [
    "COMPLAINTS",
    "BILLING_HISTORY",
    "METER_READING",
    "METER_INFORMATION",
    "PAYMENTS",
    "CALLS",
    "ACCOUNT_HEALTH",
    "ACCOUNT_BALANCE",
    "CONTRACT",
]


for table in tables:

    print("\n" + "=" * 50)
    print(table)
    print("=" * 50)

    try:
        df = load_table(table)

        print("Rows:", len(df))
        print("Columns:")

        for column in df.columns:
            print("  -", column)

    except Exception as e:

        print("ERROR:", type(e).__name__, e)