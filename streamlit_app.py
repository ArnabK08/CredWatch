import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import pickle
import numpy as np

st.set_page_config(page_title="CredWatch Dashboard", layout="wide", page_icon="🏦")

with st.sidebar:
    st.title("🏦 CredWatch")
    st.caption("AML & Credit Risk Suite")
    st.markdown("---")
    st.markdown("**Pipeline outputs**")
    st.markdown("- 10,000 accounts scanned")
    st.markdown("- 50,200 transactions monitored")
    st.markdown("- 100 AML alerts generated")
    st.markdown("- 72% ML model accuracy")
    st.markdown("---")
    st.caption("Run `python run_all.py` to refresh data.")

@st.cache_data
def load_data():
    alerts_df  = pd.read_csv("rules_engine/alerts_output.csv")
    risk_df    = pd.read_csv("credit_risk_model/risk_scored_accounts.csv")
    txns_df    = pd.read_csv("data/raw/transactions.csv", parse_dates=["timestamp"])
    loans_df   = pd.read_csv("data/raw/loans.csv")
    merged_df  = pd.merge(alerts_df, risk_df, on="account_id", how="left")
    return alerts_df, risk_df, txns_df, loans_df, merged_df

try:
    alerts_df, risk_df, txns_df, loans_df, merged_df = load_data()
except FileNotFoundError as e:
    st.error(f"Data file not found: {e}. Make sure you have run `python run_all.py` first, and launch Streamlit from the project root directory.")
    st.stop()

txns_df["date"] = txns_df["timestamp"].dt.date
txns_df["month"] = txns_df["timestamp"].dt.to_period("M").astype(str)

TIER_COLORS = {"Low Risk": "#2ecc71", "Medium Risk": "#f39c12", "High Risk": "#e74c3c"}
RULE_COLORS = {
    "Structuring / Smurfing": "#9b59b6",
    "Velocity Anomaly":        "#3498db",
    "Threshold Breach":        "#e74c3c",
}

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Portfolio Overview",
    "🚨 AML Alerts",
    "💳 Transaction Analysis",
    "🤖 Model Insights",
    "🔍 Custom Scan",
])

with tab1:
    st.header("Portfolio Overview")

    total   = len(risk_df)
    high    = len(risk_df[risk_df["risk_tier"] == "High Risk"])
    medium  = len(risk_df[risk_df["risk_tier"] == "Medium Risk"])
    alerted = alerts_df["account_id"].nunique()
    dual    = len(merged_df[merged_df["risk_tier"] == "High Risk"])                          

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Accounts",       f"{total:,}")
    c2.metric("High Risk",            f"{high:,}",   delta=f"{high/total*100:.1f}%",  delta_color="inverse")
    c3.metric("Medium Risk",          f"{medium:,}")
    c4.metric("AML Alerts",           f"{len(alerts_df):,}")
    c5.metric("Dual-Flagged Accounts",f"{dual:,}",   delta="⚠️ Priority", delta_color="inverse")

    st.markdown("---")

    colL, colR = st.columns(2)

    with colL:
        st.subheader("Risk Tier Distribution")
        tier_counts = risk_df["risk_tier"].value_counts().reset_index()
        tier_counts.columns = ["Risk Tier", "Count"]
        fig = px.pie(
            tier_counts, values="Count", names="Risk Tier",
            color="Risk Tier", color_discrete_map=TIER_COLORS,
            hole=0.45,
        )
        fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)

    with colR:
        st.subheader("AML Alerts by Rule")
        rule_counts = alerts_df["rule_triggered"].value_counts().reset_index()
        rule_counts.columns = ["Rule", "Count"]
        fig2 = px.bar(
            rule_counts, x="Count", y="Rule", orientation="h",
            color="Rule", color_discrete_map=RULE_COLORS,
            text="Count",
        )
        fig2.update_traces(textposition="outside")
        fig2.update_layout(showlegend=False, yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Default Probability Distribution by Risk Tier")
    fig3 = px.histogram(
        risk_df, x="default_probability", color="risk_tier",
        color_discrete_map=TIER_COLORS, nbins=60, barmode="overlay",
        opacity=0.7, labels={"default_probability": "Default Probability (%)", "risk_tier": "Tier"},
    )
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.header("AML Alerts Investigation")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_tier = st.selectbox(
            "Filter by Credit Risk Tier",
            ["All", "High Risk", "Medium Risk", "Low Risk"],
        )
    with col_f2:
        selected_rule = st.selectbox(
            "Filter by AML Rule",
            ["All"] + alerts_df["rule_triggered"].unique().tolist(),
        )

    filtered = merged_df.copy()
    if selected_tier != "All":
        filtered = filtered[filtered["risk_tier"] == selected_tier]
    if selected_rule != "All":
        filtered = filtered[filtered["rule_triggered"] == selected_rule]

    st.markdown(f"**{len(filtered)} alerts** match current filters.")

    st.subheader("Alert Heatmap: Rule vs Risk Tier")
    heat_data = (
        merged_df.groupby(["rule_triggered", "risk_tier"])
        .size()
        .reset_index(name="count")
        .pivot(index="rule_triggered", columns="risk_tier", values="count")
        .fillna(0)
    )
    fig_heat = go.Figure(data=go.Heatmap(
        z=heat_data.values,
        x=heat_data.columns.tolist(),
        y=heat_data.index.tolist(),
        colorscale="Reds",
        text=heat_data.values.astype(int),
        texttemplate="%{text}",
    ))
    fig_heat.update_layout(
        xaxis_title="Credit Risk Tier", yaxis_title="AML Rule",
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.subheader("Severity Score Distribution")
    fig_sev = px.box(
        merged_df, x="rule_triggered", y="severity_score",
        color="rule_triggered", color_discrete_map=RULE_COLORS,
        labels={"rule_triggered": "Rule", "severity_score": "Severity Score"},
    )
    fig_sev.update_layout(showlegend=False, xaxis_title="")
    st.plotly_chart(fig_sev, use_container_width=True)

    st.subheader("Alert Detail Table")
    st.dataframe(
        filtered[["account_id", "rule_triggered", "severity_score", "alert_reason", "risk_tier", "default_probability"]]
        .sort_values("severity_score", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
    )

with tab3:
    st.header("Transaction Analysis")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Transactions", f"{len(txns_df):,}")
    c2.metric("Total Volume",       f"${txns_df['amount'].sum():,.0f}")
    c3.metric("Avg Transaction",    f"${txns_df['amount'].mean():,.2f}")
    c4.metric("Max Transaction",    f"${txns_df['amount'].max():,.2f}")

    st.markdown("---")

    colA, colB = st.columns(2)

    with colA:
        st.subheader("Monthly Transaction Volume")
        monthly = (
            txns_df.groupby("month")["amount"]
            .agg(total="sum", count="count")
            .reset_index()
        )
        fig_m = px.bar(
            monthly, x="month", y="total",
            labels={"month": "Month", "total": "Total Volume ($)"},
            color_discrete_sequence=["#3498db"],
            text_auto=".2s",
        )
        fig_m.update_traces(textposition="outside")
        st.plotly_chart(fig_m, use_container_width=True)

    with colB:
        st.subheader("Transactions by Channel")
        ch = txns_df["channel"].value_counts().reset_index()
        ch.columns = ["Channel", "Count"]
        fig_ch = px.pie(ch, values="Count", names="Channel", hole=0.4)
        fig_ch.update_layout(legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_ch, use_container_width=True)

    st.subheader("Transaction Amount Distribution (log scale)")
    fig_hist = px.histogram(
        txns_df, x="amount", nbins=80, log_y=True,
        color_discrete_sequence=["#9b59b6"],
        labels={"amount": "Amount ($)"},
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("Daily Transaction Count (Trend)")
    daily_cnt = txns_df.groupby("date").size().reset_index(name="count")
    daily_cnt["date"] = pd.to_datetime(daily_cnt["date"])
    fig_trend = px.line(
        daily_cnt, x="date", y="count",
        labels={"date": "Date", "count": "Number of Transactions"},
        color_discrete_sequence=["#2ecc71"],
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with tab4:
    st.header("Credit Risk Model Insights")

    try:
        with open("credit_risk_model/model.pkl", "rb") as f:
            bundle = pickle.load(f)
        model  = bundle["model"]
        scaler = bundle["scaler"]
        features = ["income", "loan_amount", "existing_defaults",
                    "credit_utilization", "tenure", "loan_to_income_ratio"]

        c1, c2, c3 = st.columns(3)
        c1.metric("Model Type",      "Logistic Regression")
        c2.metric("Training Size",   "8,000 accounts")
        c3.metric("Test Accuracy",   "72%")

        st.markdown("---")
        colA, colB = st.columns(2)

        with colA:
            st.subheader("Feature Coefficients")
            coef_df = pd.DataFrame({
                "Feature":     features,
                "Coefficient": model.coef_[0],
            }).sort_values("Coefficient", ascending=True)
            fig_coef = px.bar(
                coef_df, x="Coefficient", y="Feature", orientation="h",
                color="Coefficient",
                color_continuous_scale=["#2ecc71", "#f39c12", "#e74c3c"],
                labels={"Coefficient": "Log-Odds Coefficient"},
            )
            fig_coef.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_coef, use_container_width=True)

        with colB:
            st.subheader("Credit Utilization vs Default Probability")
            sample = loans_df.merge(risk_df, on="account_id", how="left").sample(n=1500, random_state=42)
            fig_scatter = px.scatter(
                sample, x="credit_utilization", y="default_probability",
                color="risk_tier", color_discrete_map=TIER_COLORS,
                opacity=0.6,
                labels={"credit_utilization": "Credit Utilization", "default_probability": "Default Prob (%)"},
                trendline="lowess",
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        st.subheader("Income vs Loan Amount (by Risk Tier)")
        sample2 = loans_df.merge(risk_df, on="account_id", how="left").sample(n=2000, random_state=7)
        fig_inc = px.scatter(
            sample2, x="income", y="loan_amount",
            color="risk_tier", color_discrete_map=TIER_COLORS,
            opacity=0.5, size_max=8,
            labels={"income": "Annual Income ($)", "loan_amount": "Loan Amount ($)"},
        )
        st.plotly_chart(fig_inc, use_container_width=True)

        st.subheader("🎯 Live Default Probability Calculator")
        with st.form("predict_form"):
            p1, p2, p3 = st.columns(3)
            inc  = p1.number_input("Annual Income ($)",      value=50000, step=1000)
            loan = p2.number_input("Loan Amount ($)",        value=20000, step=1000)
            util = p3.slider("Credit Utilization (0-1)",     0.0, 1.0, 0.3, 0.01)
            p4, p5, p6 = st.columns(3)
            defs = p4.number_input("Existing Defaults",      value=0, step=1)
            ten  = p5.number_input("Tenure (months)",        value=24, step=1)
            lti  = p6.number_input("Loan-to-Income Ratio",   value=round(loan/inc, 2) if inc else 0.4, step=0.01)
            submitted = st.form_submit_button("Predict Default Probability")

        if submitted:
            X_input = np.array([[inc, loan, defs, util, ten, lti]])
            X_scaled = scaler.transform(X_input)
            prob = model.predict_proba(X_scaled)[0][1] * 100
            tier = "High Risk" if prob >= 70 else ("Medium Risk" if prob >= 30 else "Low Risk")
            color_map = {"High Risk": "red", "Medium Risk": "orange", "Low Risk": "green"}
            st.markdown(
                f"### Predicted Default Probability: "
                f"<span style='color:{color_map[tier]};font-size:2rem'><b>{prob:.1f}%</b></span> "
                f"— **{tier}**",
                unsafe_allow_html=True,
            )

    except FileNotFoundError:
        st.warning("model.pkl not found. Run `python credit_risk_model/train_model.py` first.")

with tab5:
    st.header("Scan Custom Transaction File")
    st.markdown(
        "Upload a `transactions.csv` with columns: "
        "`transaction_id`, `timestamp`, `account_id`, `receiver`, `amount`, `channel`"
    )
    uploaded_file = st.file_uploader("Upload transactions.csv", type=["csv"])

    if uploaded_file is not None:
        new_txns = pd.read_csv(uploaded_file)
        new_txns["timestamp"] = pd.to_datetime(new_txns["timestamp"])
        new_txns["date"] = new_txns["timestamp"].dt.date
        st.success(f"Loaded **{len(new_txns):,}** rows across **{new_txns['account_id'].nunique():,}** accounts.")

        if st.button("🔍 Run Full Rules Engine"):
            with st.spinner("Scanning all 3 AML rules..."):
                with open("rules_engine/rules_config.json", "r") as f:
                    config = json.load(f)
                rules = {rule["rule_name"]: rule for rule in config["rules"]}
                alerts = []

                r1 = rules["Structuring / Smurfing"]
                suspicious = new_txns[
                    (new_txns["amount"] >= r1["parameters"]["min_amount"]) &
                    (new_txns["amount"] <= r1["parameters"]["max_amount"])
                ].sort_values(["account_id", "timestamp"])
                for acct, grp in suspicious.groupby("account_id"):
                    mc = r1["parameters"]["min_count"]
                    if len(grp) >= mc:
                        for i in range(len(grp) - mc + 1):
                            sub = grp.iloc[i:i + mc]
                            diff = (sub["timestamp"].iloc[-1] - sub["timestamp"].iloc[0]).days
                            if diff <= r1["parameters"]["time_window_days"]:
                                alerts.append({
                                    "account_id": acct,
                                    "rule_triggered": r1["rule_name"],
                                    "severity_score": r1["severity_score"],
                                    "alert_reason": f"Structuring: {mc} txns totaling ${sub['amount'].sum():,.2f} in {diff} days",
                                })
                                break

                r2 = rules["Velocity Anomaly"]
                daily = new_txns.groupby(["account_id", "date"]).size().reset_index(name="count")
                for _, row in daily[daily["count"] > r2["parameters"]["max_daily_transactions"]].iterrows():
                    alerts.append({
                        "account_id": row["account_id"],
                        "rule_triggered": r2["rule_name"],
                        "severity_score": r2["severity_score"],
                        "alert_reason": f"Velocity Anomaly: {row['count']} txns on {row['date']}",
                    })

                r3 = rules["Threshold Breach"]
                for _, row in new_txns[new_txns["amount"] > r3["parameters"]["threshold_amount"]].iterrows():
                    alerts.append({
                        "account_id": row["account_id"],
                        "rule_triggered": r3["rule_name"],
                        "severity_score": r3["severity_score"],
                        "alert_reason": f"Threshold Breach: ${row['amount']:,.2f} on {row['date']}",
                    })

                if alerts:
                    df_out = pd.DataFrame(alerts).drop_duplicates(subset=["account_id", "rule_triggered"])
                    st.error(f"⚠️ Found **{len(df_out)}** unique alerts across {df_out['account_id'].nunique()} accounts.")

                    rule_summary = df_out["rule_triggered"].value_counts().reset_index()
                    rule_summary.columns = ["Rule", "Count"]
                    fig = px.bar(rule_summary, x="Count", y="Rule", orientation="h",
                                 color="Rule", color_discrete_map=RULE_COLORS, text="Count")
                    fig.update_traces(textposition="outside")
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(
                        df_out.sort_values("severity_score", ascending=False).reset_index(drop=True),
                        use_container_width=True,
                    )

                    csv = df_out.to_csv(index=False).encode()
                    st.download_button("⬇️ Download Alerts CSV", csv, "alerts_output.csv", "text/csv")
                else:
                    st.success("✅ No anomalies detected across all 3 rules.")
