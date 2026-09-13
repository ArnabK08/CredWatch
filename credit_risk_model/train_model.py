import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler

df = pd.read_csv('data/processed/model_features.csv')

features = ['income', 'loan_amount', 'existing_defaults', 'credit_utilization', 'tenure', 'loan_to_income_ratio']
X = df[features]
y = df['is_default']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = LogisticRegression(class_weight='balanced')
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

for feature, coef in zip(features, model.coef_[0]):
    print(f"{feature}: {coef:.4f}")

X_all_scaled = scaler.transform(X)
probabilities = model.predict_proba(X_all_scaled)[:, 1]
df['default_probability'] = np.round(probabilities * 100, 2)

def assign_tier(prob):
    if prob < 30:
        return 'Low Risk'
    elif prob < 70:
        return 'Medium Risk'
    else:
        return 'High Risk'

df['risk_tier'] = df['default_probability'].apply(assign_tier)

output_df = df[['account_id', 'default_probability', 'risk_tier']]
output_df.to_csv('credit_risk_model/risk_scored_accounts.csv', index=False)

with open('credit_risk_model/model.pkl', 'wb') as f:
    pickle.dump({'model': model, 'scaler': scaler}, f)
