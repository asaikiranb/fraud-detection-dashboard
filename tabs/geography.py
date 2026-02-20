import streamlit as st
import pandas as pd
from components.charts import us_choropleth, top_cities_bar
from components.kpi_cards import (
    render_mini_kpi_row,
    render_page_header,
    render_section_header,
    render_insight_box,
)
from components.styles import COLORS, PLOTLY_CONFIG

_DISPLAY_COLS = ["state", "state_name", "fraud", "total", "rate", "fraud_amount"]
_DISPLAY_HEADERS = ["Code", "State", "Fraud Events", "Total Tx", "Fraud Rate %", "Fraud Amount ($)"]
_TOP_STATES = 15


def render_geography(df: pd.DataFrame, stats: dict):
    """Render the Geographic Analysis tab."""
    render_page_header(
        "Geographic Analysis",
        "Where is fraud concentrated? State and city-level distribution across the US.",
    )

    state_data = df.groupby(["state", "state_name"]).agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
        fraud_amount=("amount", lambda x: x[df.loc[x.index, "is_fraud"] == 1].sum()),
    ).reset_index()
    state_data["rate"] = state_data["fraud"] / state_data["total"] * 100

    top_state = state_data.sort_values("rate", ascending=False).iloc[0]
    top_state_volume = state_data.sort_values("fraud", ascending=False).iloc[0]
    most_states = df["state"].nunique()
    avg_state_rate = state_data["rate"].mean()

    render_mini_kpi_row([
        {"label": "States Affected",    "value": f"{most_states}",              "color": COLORS["chart_1"]},
        {"label": "Highest Rate State", "value": top_state["state"],            "color": COLORS["fraud_red"]},
        {"label": "Peak State Rate",    "value": f"{top_state['rate']:.2f}%",   "color": COLORS["fraud_red"]},
        {"label": "Avg State Rate",     "value": f"{avg_state_rate:.2f}%",      "color": COLORS["chart_2"]},
    ])

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── Choropleth (full width)
    render_section_header(
        "Fraud Rate by State",
        "Hover over a state for fraud rate, count, and amount. Darker = higher risk.",
    )
    st.plotly_chart(
        us_choropleth(df),
        use_container_width=True,
        config={**PLOTLY_CONFIG, "scrollZoom": False},
        key="geo_choropleth",
    )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row: Cities + State table
    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        render_section_header(
            "Top Cities by Fraud Volume",
            "Absolute fraud event count by city",
        )
        st.plotly_chart(
            top_cities_bar(df, n=10),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="geo_cities_bar",
        )

    with col2:
        render_section_header(
            "State Drill-Down",
            f"Top {_TOP_STATES} states by fraud rate — click column headers to sort",
        )
        display_states = (
            state_data.sort_values("rate", ascending=False)
            .head(_TOP_STATES)[_DISPLAY_COLS]
            .copy()
        )
        display_states.columns = _DISPLAY_HEADERS
        display_states["Fraud Rate %"] = display_states["Fraud Rate %"].round(2)
        display_states["Fraud Amount ($)"] = display_states["Fraud Amount ($)"].apply(lambda x: f"${x:,.0f}")
        display_states["Total Tx"] = display_states["Total Tx"].apply(lambda x: f"{x:,}")
        display_states["Fraud Events"] = display_states["Fraud Events"].apply(lambda x: f"{x:,}")

        st.dataframe(
            display_states.reset_index(drop=True),
            use_container_width=True,
            height=440,
            hide_index=True,
        )

    high_risk_states = state_data[state_data["rate"] > state_data["rate"].mean() + state_data["rate"].std()]

    render_insight_box("Geographic Insights", [
        f'<strong>{top_state["state_name"]}</strong> has the highest fraud rate at {top_state["rate"]:.2f}%',
        f'<strong>{top_state_volume["state_name"]}</strong> has the highest absolute fraud volume ({top_state_volume["fraud"]:,} events)',
        f'{len(high_risk_states)} states exceed one standard deviation above the mean fraud rate',
        f'Average fraud rate across all states: {avg_state_rate:.2f}%',
    ])
