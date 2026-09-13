import pandas as pd

df = pd.read_csv('data/raw/loans.csv')

df['loan_to_income_ratio'] = df['loan_amount'] / df['income']

features = ['income', 'loan_amount', 'existing_defaults', 'credit_utilization', 'tenure', 'loan_to_income_ratio']
target = 'is_default'

final_df = df[['account_id'] + features + [target]]
final_df.to_csv('data/processed/model_features.csv', index=False)
