# FraudLens — Fraud Detection Dashboard

A production-quality, executive-grade Streamlit dashboard for credit card fraud analysis. Built with a clean, minimal white design and rich interactive visualizations.

## Features

- **Executive Overview** — KPI cards, fraud split, category breakdown, monthly trend
- **Temporal Trends** — Hour × day heatmap, day-of-week patterns, weekly trend, quarterly comparison
- **Geographic Analysis** — US choropleth map, top cities, state drill-down table
- **Customer Segments** — Age group risk, card type distribution, channel risk, fraud type breakdown
- **Transaction Explorer** — Filterable/searchable table with CSV export

## Dataset

Synthetic credit card fraud dataset with 50,000 transactions (2023), featuring:
- Realistic fraud rate (~1.7%)
- Multiple fraud types: Card Not Present, Account Takeover, Synthetic Identity, Merchant Fraud, Skimming
- Geographic data across all 50 US states
- Demographic and transaction channel data

## Setup

```bash
# Clone the repo
git clone https://github.com/asaikiranb/fraud-detection-dashboard.git
cd fraud-detection-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`.

## Tech Stack

- **Streamlit** — Dashboard framework
- **Plotly** — Interactive charts
- **Pandas / NumPy** — Data processing
- **Custom CSS** — Clean white design system

## Design Principles

- Minimal white palette with intentional use of red (fraud) and green (safe)
- Executive-first layout: KPIs → overview → drill-downs
- All charts are interactive with hover tooltips
- Global sidebar filters apply across all tabs
