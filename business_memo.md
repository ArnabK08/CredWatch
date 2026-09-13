# Business Recommendation Memo: CredWatch Implementation

**To:** Chief Risk Officer, Retail Banking Division  
**From:** Data Engineering & Risk Analytics Team  
**Date:** September 13, 2026  
**Subject:** Implementation of "CredWatch" — Unified AML & Credit Risk Suite  

---

## 1. Business Problem

Our AML compliance team and credit underwriting team have historically operated in silos. An account holder can be flagged for suspicious transaction velocity by compliance while simultaneously being approved for a limit increase by the credit department.

Our previous transaction monitoring system relied on hardcoded thresholds, requiring engineering tickets to adjust parameters (e.g., changing a structuring threshold from $10k to $9k), which delayed regulatory responsiveness. We needed an integrated, configurable system to monitor transaction and credit risk concurrently.

## 2. The CredWatch Solution

**CredWatch** is an end-to-end analytics pipeline covering both domains:

- **Configurable Rule Engine** — a JSON-driven Python engine that evaluates daily transaction logs against known AML typologies (structuring, velocity spikes, threshold breaches).
- **Credit Risk ML Model** — a Logistic Regression model that predicts loan default probability based on credit utilization, existing defaults, and loan-to-income ratios.
- **Unified Dashboard** — a Power BI reporting layer joining AML alerts with ML risk tiers.

## 3. Key Findings

Based on our run over the synthetic dataset (10,000 accounts, 50,000+ transactions):

- **Alert Volume:** 100 unique AML alerts generated.
- **Structuring Detected:** Accounts executing multiple transactions clustering near the $10,000 reporting threshold, successfully flagged by the rules engine.
- **Model Accuracy:** 72% accuracy (F1-score 0.40 on defaults) reflecting a highly realistic, noisy dataset and the inherent imbalance in credit risk. 
- **Feature Interpretability:** loan_to_income_ratio (coef: ~0.65) and existing_defaults (coef: ~0.33) are the strongest positive predictors of default, consistent with underwriting intuition.

## 4. Risk Tiering Framework

Accounts are bucketed into three tiers based on predicted default probability:

1. **High Risk (> 70%)** — severe likelihood of default.
2. **Medium Risk (30–70%)** — elevated risk requiring monitoring.
3. **Low Risk (< 30%)** — standard portfolio accounts.

## 5. Strategic Recommendations

1. **Immediate Account Freezes** — any account triggering an AML "Threshold Breach" that is also classified as "High Risk" by the ML model should be frozen pending manual review.
2. **Dynamic Thresholds** — the compliance team should review `rules_config.json` quarterly and adjust `velocity` parameters for seasonal transaction volume changes.
3. **Cross-Training** — begin onboarding AML investigators onto the Power BI dashboard so credit risk tiers can be incorporated into Suspicious Activity Report (SAR) narratives.
