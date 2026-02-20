# Fraud & Risk Analytics Dashboard

A Streamlit dashboard for credit card fraud analysis. Clean, minimal design with interactive Plotly charts across five drill-down tabs.

## Setup

```bash
git clone https://github.com/asaikiranb/fraud-detection-dashboard.git
cd fraud-detection-dashboard
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Tabs

| Tab | What it shows |
|-----|--------------|
| Executive Overview | KPI cards, fraud split, category breakdown, monthly trend |
| Temporal Trends | Hour × day heatmap, day-of-week rates, weekly trend, QoQ comparison |
| Geographic Analysis | US choropleth, top cities chart, state drill-down table |
| Customer Segments | Age group risk, card type split, channel rates, attack type breakdown |
| Transaction Explorer | Filterable table with search and CSV export |

## Dataset

Synthetic credit card fraud data — 50,000 transactions across 2023, generated with reproducible seed. Covers 49 US states, 4 card types, 4 transaction channels, 5 fraud types, and 10 merchant categories. No external download required.

## Project Structure

```
app.py                  # Entry point, filter bar, tab routing
data/
  generate_data.py      # Synthetic dataset generator
components/
  styles.py             # Design tokens, shared constants, CSS injection
  kpi_cards.py          # KPI cards, section headers, insight boxes
  charts.py             # All 14 Plotly chart functions
tabs/
  overview.py           # Executive Overview tab
  trends.py             # Temporal Trends tab
  geography.py          # Geographic Analysis tab
  segments.py           # Customer Segments tab
  transactions.py       # Transaction Explorer tab
.streamlit/
  config.toml           # Light theme config
requirements.txt
```

## Stack

- [Streamlit](https://streamlit.io) — UI framework
- [Plotly](https://plotly.com/python/) — Interactive charts
- [Pandas](https://pandas.pydata.org) / [NumPy](https://numpy.org) — Data processing
