import pandas as pd
import os

alerts_df = pd.read_csv('rules_engine/alerts_output.csv')
risk_df = pd.read_csv('credit_risk_model/risk_scored_accounts.csv')

dashboard_df = pd.merge(alerts_df, risk_df, on='account_id', how='left')

dashboard_df.to_csv('dashboard/dashboard_data.csv', index=False)
print("Dashboard data fixed and regenerated!")
