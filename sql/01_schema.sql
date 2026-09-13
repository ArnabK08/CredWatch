CREATE TABLE IF NOT EXISTS accounts (
    account_id        TEXT PRIMARY KEY,
    income            REAL,
    loan_amount       REAL,
    existing_defaults INTEGER,
    credit_utilization REAL,
    tenure            INTEGER,
    is_default        INTEGER
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    timestamp      TEXT,
    account_id     TEXT,
    receiver       TEXT,
    amount         REAL,
    channel        TEXT,
    FOREIGN KEY(account_id) REFERENCES accounts(account_id)
);
