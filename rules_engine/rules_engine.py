import json
import pandas as pd

with open('rules_engine/rules_config.json', 'r') as f:
    config = json.load(f)

rules = {rule['rule_name']: rule for rule in config['rules']}

txns_df = pd.read_csv('data/raw/transactions.csv')
txns_df['timestamp'] = pd.to_datetime(txns_df['timestamp'])

alerts = []

r1 = rules['Structuring / Smurfing']
min_amt = r1['parameters']['min_amount']
max_amt = r1['parameters']['max_amount']
min_count = r1['parameters']['min_count']
window = r1['parameters']['time_window_days']

suspicious_amts = txns_df[(txns_df['amount'] >= min_amt) & (txns_df['amount'] <= max_amt)]
suspicious_amts = suspicious_amts.sort_values(['account_id', 'timestamp'])

for account, group in suspicious_amts.groupby('account_id'):
    if len(group) >= min_count:
        for i in range(len(group) - min_count + 1):
            subset = group.iloc[i:i+min_count]
            time_diff = (subset['timestamp'].iloc[-1] - subset['timestamp'].iloc[0]).days
            if time_diff <= window:
                total_amt = subset['amount'].sum()
                alerts.append({
                    'account_id': account,
                    'rule_triggered': r1['rule_name'],
                    'severity_score': r1['severity_score'],
                    'alert_reason': f"Structuring: {min_count} transactions totaling ${total_amt:,.2f} in {time_diff} days; severity {r1['severity_score']}."
                })
                break

r2 = rules['Velocity Anomaly']
max_daily = r2['parameters']['max_daily_transactions']

txns_df['date'] = txns_df['timestamp'].dt.date
daily_counts = txns_df.groupby(['account_id', 'date']).size().reset_index(name='daily_txn_count')
velocity_breaches = daily_counts[daily_counts['daily_txn_count'] > max_daily]

for _, row in velocity_breaches.iterrows():
    alerts.append({
        'account_id': row['account_id'],
        'rule_triggered': r2['rule_name'],
        'severity_score': r2['severity_score'],
        'alert_reason': f"Velocity Anomaly: {row['daily_txn_count']} transactions on {row['date']}; severity {r2['severity_score']}."
    })

r3 = rules['Threshold Breach']
threshold = r3['parameters']['threshold_amount']

breaches = txns_df[txns_df['amount'] > threshold]

for _, row in breaches.iterrows():
    alerts.append({
        'account_id': row['account_id'],
        'rule_triggered': r3['rule_name'],
        'severity_score': r3['severity_score'],
        'alert_reason': f"Threshold Breach: transaction of ${row['amount']:,.2f} on {row['date']}; severity {r3['severity_score']}."
    })

alerts_df = pd.DataFrame(alerts)
alerts_df = alerts_df.drop_duplicates(subset=['account_id', 'rule_triggered'])
alerts_df.to_csv('rules_engine/alerts_output.csv', index=False)
