# Customer Intelligence Platform

Premium AI-powered customer analytics SaaS built with Streamlit. The platform helps revenue, retention, and growth teams identify churn risk, prioritize customer actions, and forecast near-term revenue from a single executive workspace.

## What It Solves

Companies often have customer, order, engagement, and retention data spread across disconnected systems. This app turns those signals into a practical decision layer:

- Which customers are most likely to churn?
- How much revenue is exposed?
- Which customer segments need attention?
- What retention action should the business take next?
- Can teams score new customer data without rebuilding the ML pipeline?

## Core Capabilities

- Customer segmentation using behavioral and transaction features
- Churn probability scoring
- Next-month revenue prediction
- Revenue-at-risk prioritization
- Business-rule configuration for risk thresholds and CRM actions
- Executive KPI dashboard
- Retention priority queue
- Manual customer what-if scoring
- CSV upload scoring with column mapping
- Data contract for onboarding company datasets

## Product Experience

The UI is designed as an enterprise analytics product, not a notebook demo:

- Dark premium SaaS theme
- Executive KPI cards
- Decision-focused dashboard sections
- Risk distribution and top-risk customer views
- Styled sidebar control panel
- CRM-ready action recommendations
- Streamlit-native components for reliable rendering

## Project Structure

```text
.
├── app.py
├── requirements.txt
├── run_pipeline.py
├── CASE_STUDY_DS.ipynb
└── src/
    └── customer_analytics/
        ├── config.py
        ├── data_generation.py
        ├── evaluation.py
        ├── features.py
        ├── modeling.py
        ├── pipeline.py
        └── segmentation.py
```

## Local Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Streamlit Cloud Deployment

Use these settings in Streamlit Community Cloud:

- Repository: `MOHAMMED-GHANIM-SIDDIQUI/customer-intelligence-platform`
- Branch: `master`
- Main file path: `app.py`
- Python version: `3.12`

Dependencies are declared in `requirements.txt`.

## Using Company Data

Use the **Score New Data** workflow to upload customer data and map your company columns to the model feature contract. Required fields include:

- `income`
- `tenure_months`
- `visits_per_month`
- `total_orders`
- `total_spend`
- `average_order_value`
- `discount_rate`
- `recency_days`
- `orders_per_active_month`
- `spend_per_visit`
- `order_value_std`

The app then outputs segment, churn probability, predicted spend, revenue at risk, risk level, and recommended retention action.

## Production Note

The current project is based on a synthetic case-study pipeline. For production use, retrain the models on real historical customer outcomes, validated churn labels, and company-specific revenue definitions.
