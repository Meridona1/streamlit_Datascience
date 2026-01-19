
import sqlite3
import pandas as pd
from pathlib import Path

# Sökväg till databasen som används av hela applikationen
DB_PATH = Path("pages/köksglädje.db")

# Läser SQL-frågor och returnerar resultatet som en DataFrame
def read_sql(query: str, params: tuple = ()) -> pd.DataFrame:
    # Säkerställer att databasen finns innan anslutning
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Databas saknas. {DB_PATH}")

    # Öppnar en säker anslutning till SQLite och kör frågan
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row  # Gör att kolumnnamn följer SQL-alias
        return pd.read_sql_query(query, conn, params=params)
