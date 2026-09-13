import sqlite3
import pandas as pd
import sys
import os

print("\n" + "="*60)
print("  STEP: 2.5 Test Risk Queries (SQL)")
print("  Script: sql/03_risk_queries.sql")
print("="*60)

try:
    conn = sqlite3.connect('data/processed/credwatch.db')
    with open('sql/03_risk_queries.sql', 'r') as f:
        sql_script = f.read()

    queries = [q.strip() for q in sql_script.split(';') if q.strip()]
    for i, query in enumerate(queries):
        if "LIMIT" in query or "SELECT" in query.upper():
            print(f"\n--- Query {i+1} Output ---")
            df = pd.read_sql_query(query, conn)
            print(df.to_string(index=False))
    conn.close()
    print("\n[OK] 2.5 Test Risk Queries (SQL) complete.")
except Exception as e:
    print(f"\n[ERROR] Failed to run queries: {e}")
    sys.exit(1)
