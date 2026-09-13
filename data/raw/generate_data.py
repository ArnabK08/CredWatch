import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

n_accounts = 10000
account_ids = [f"ACC{str(i).zfill(5)}" for i in range(1, n_accounts + 1)]

income = np.random.normal(60000, 20000, n_accounts).clip(min=20000)
loan_amount = np.random.normal(15000, 8000, n_accounts).clip(min=1000)
existing_defaults = np.random.choice([0, 1, 2], n_accounts, p=[0.8, 0.15, 0.05])
credit_utilization = np.random.uniform(0.1, 0.95, n_accounts)
tenure = np.random.choice([12, 24, 36, 48, 60], n_accounts)

loan_to_income = loan_amount / income
noise = np.random.normal(0, 3, n_accounts)
hidden_risk_score = (credit_utilization * 2) + existing_defaults + (loan_to_income * 5) + noise
is_default = (hidden_risk_score > np.percentile(hidden_risk_score, 85)).astype(int)

loans_df = pd.DataFrame({
    'account_id': account_ids,
    'income': np.round(income, 2),
    'loan_amount': np.round(loan_amount, 2),
    'existing_defaults': existing_defaults,
    'credit_utilization': np.round(credit_utilization, 2),
    'tenure': tenure,
    'is_default': is_default
})

loans_df.to_csv('data/raw/loans.csv', index=False)

n_txns = 50000
start_date = datetime(2023, 1, 1)

dates = [start_date + timedelta(days=random.randint(0, 180), minutes=random.randint(0, 1440)) for _ in range(n_txns)]
senders = np.random.choice(account_ids, n_txns)
receivers = [f"EXT{str(random.randint(1, 5000)).zfill(5)}" for _ in range(n_txns)]
amounts = np.random.exponential(scale=500, size=n_txns).clip(min=5)
channels = np.random.choice(['online', 'branch', 'atm', 'wire'], n_txns, p=[0.6, 0.1, 0.2, 0.1])

structuring_accounts = np.random.choice(account_ids, 50, replace=False)
for acc in structuring_accounts:
    for _ in range(3):
        senders = np.append(senders, acc)
        receivers = np.append(receivers, f"EXT{str(random.randint(1, 5000)).zfill(5)}")
        amounts = np.append(amounts, np.random.uniform(9000, 9900))
        channels = np.append(channels, 'branch')
        dates.append(start_date + timedelta(days=random.randint(0, 5), minutes=random.randint(0, 1440)))

threshold_accounts = np.random.choice(account_ids, 50, replace=False)
for acc in threshold_accounts:
    senders = np.append(senders, acc)
    receivers = np.append(receivers, f"EXT{str(random.randint(1, 5000)).zfill(5)}")
    amounts = np.append(amounts, np.random.uniform(15000, 25000))
    channels = np.append(channels, 'wire')
    dates.append(start_date + timedelta(days=random.randint(0, 180), minutes=random.randint(0, 1440)))

txns_df = pd.DataFrame({
    'timestamp': dates,
    'account_id': senders,
    'receiver': receivers,
    'amount': np.round(amounts, 2),
    'channel': channels
})

txns_df = txns_df.sort_values('timestamp').reset_index(drop=True)
txns_df['transaction_id'] = [f"TXN{str(i).zfill(6)}" for i in range(1, len(txns_df) + 1)]
txns_df = txns_df[['transaction_id', 'timestamp', 'account_id', 'receiver', 'amount', 'channel']]

txns_df.to_csv('data/raw/transactions.csv', index=False)
