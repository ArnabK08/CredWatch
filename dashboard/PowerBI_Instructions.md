# Building the CredWatch Power BI Dashboard

You will need **Power BI Desktop** installed (free from the Microsoft Store).

## Step 1: Import the Data

1. Open Power BI Desktop.
2. On the Home ribbon, click **Get Data** > **Text/CSV**.
3. Navigate to `d:\credwatch\dashboard\dashboard_data.csv` and select it.
4. Click **Load**.

## Step 2: Card — Total Flagged Accounts

1. Click the **Card** visual in the Visualizations pane.
2. Drag `account_id` into the **Fields** box.
3. Change the aggregation to **Count (Distinct)**.
4. In the Format tab, set the title to "Total Flagged Accounts" and turn off "Category label".

## Step 3: Bar Chart — Alerts by Rule Type

1. Click the **Clustered Bar Chart** icon.
2. Drag `rule_triggered` to the **Y-axis**.
3. Drag `account_id` to the **X-axis**, aggregated as **Count (Distinct)**.

## Step 4: Donut Chart — Risk Tier Distribution

1. Click the **Donut Chart** icon.
2. Drag `risk_tier` to **Legend**.
3. Drag `account_id` to **Values** (Count Distinct).
4. In Format > Slices, set colors: High Risk → Red, Medium Risk → Yellow, Low Risk → Green.

## Step 5: Table — Alert Detail

1. Click the **Table** icon.
2. Add these columns in order:
   - `account_id`
   - `rule_triggered`
   - `alert_reason`
   - `risk_tier`
   - `default_probability`

## Step 6: Slicer — Risk Tier Filter

1. Click the **Slicer** icon.
2. Drag `risk_tier` into the Field box.

## Step 7: Save

File > Save As → `credwatch_dashboard.pbix` in `d:\credwatch\dashboard\`.
