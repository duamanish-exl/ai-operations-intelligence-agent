import pandas as pd

DATA_FOLDER = "data"

def load_table(table_name):
    file_path = f"{DATA_FOLDER}/{table_name}.csv"
    return pd.read_csv(file_path)