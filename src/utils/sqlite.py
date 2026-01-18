from typing import List
import sqlite3
import pandas as pd


def list_sqlite_tables(sqlite_path: str) -> List[str]:
    conn = sqlite3.connect(sqlite_path)
    try:
        rows = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;",
            conn,
        )
        return rows["name"].tolist()
    finally:
        conn.close()
