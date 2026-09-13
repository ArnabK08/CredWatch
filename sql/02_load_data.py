import sqlite3
import pandas as pd

db_path = 'data/processed/credwatch.db'
conn = sqlite3.connect(db_path)

conn.execute("DROP TABLE IF EXISTS transactions;")
conn.execute("DROP TABLE IF EXISTS accounts;")

with open('sql/01_schema.sql', 'r') as f:
    conn.executescript(f.read())

loans_df = pd.read_csv('data/raw/loans.csv')
txns_df = pd.read_csv('data/raw/transactions.csv')

loans_df.to_sql('accounts', conn, if_exists='append', index=False)
txns_df.to_sql('transactions', conn, if_exists='append', index=False)

conn.close()
