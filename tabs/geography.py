import streamlit as st
import pandas as pd
from components.charts import us_choropleth, top_cities_bar
from components.kpi_cards import render_mini_kpi_row
from components.styles import COLORS


def render_geography(df: pd.DataFrame, stats: dict):
    """Render the Geographic Analysis tab."""

    # ── Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Geographic Analysis</div>
        <div class="page-subtitle">Where is fraud concentrated? State and city-level fraud distribution across the US.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── State stats
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
        {"label": "States Affected", "value": f"{most_states}", "color": COLORS["chart_1"]},
        {"label": "Highest Rate State", "value": top_state["state"], "color": COLORS["fraud_red"]},
        {"label": "Peak State Rate", "value": f"{top_state['rate']:.2f}%", "color": COLORS["fraud_red"]},
        {"label": "Avg State Rate", "value": f"{avg_state_rate:.2f}%", "color": COLORS["chart_2"]},
    ])

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── Choropleth Map (full width)
    st.markdown('<div class="section-header">Fraud Rate by State</div>', unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
        "Hover over a state to see fraud rate, count, and total amount. "
        "Darker red = higher fraud concentration.</div>",
        unsafe_allow_html=True
    )
    st.plotly_chart(
        us_choropleth(df),
        use_container_width=True,
        config={"displayModeBar": False, "scrollZoom": False},
    )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row: Top Cities + State Table
    col1, col2 = st.columns([1, 1.2], gap="large")

    with col1:
        st.markdown('<div class="section-header">Top Cities by Fraud Volume</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Absolute fraud event count by city</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            top_cities_bar(df, n=10),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with col2:
        st.markdown('<div class="section-header">State Drill-Down</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Top 15 states by fraud rate — click column headers to sort</div>",
            unsafe_allow_html=True
        )

        display_states = state_data.sort_values("rate", ascending=False).head(15)[[
            "state", "state_name", "fraud", "total", "rate", "fraud_amount"
        ]].copy()
        display_states.columns = ["Code", "State", "Fraud Events", "Total Tx", "Fraud Rate %", "Fraud Amount ($)"]
        display_states["Fraud Rate %"] = display_states["Fraud Rate %"].round(2)
        display_states["Fraud Amount ($)"] = display_states["Fraud Amount ($)"].apply(lambda x: f"${x:,.0f}")
        display_states["Total Tx"] = display_states["Total Tx"].apply(lambda x: f"{x:,}")
        display_states["Fraud Events"] = display_states["Fraud Events"].apply(lambda x: f"{x:,}")
        display_states = display_states.reset_index(drop=True)

        st.dataframe(
            display_states,
            use_container_width=True,
            height=360,
            hide_index=True,
        )

    # ── Insight
    high_risk_states = state_data[state_data["rate"] > state_data["rate"].mean() + state_data["rate"].std()]

    st.markdown(f"""
    <div class="insight-box" style="margin-top:1rem">
        <div class="insight-title">Geographic Insights</div>
        <div class="insight-item"><strong>{top_state['state_name']}</strong> has the highest fraud rate at {top_state['rate']:.2f}%</div>
        <div class="insight-item"><strong>{top_state_volume['state_name']}</strong> has the highest absolute fraud volume ({top_state_volume['fraud']:,} events)</div>
        <div class="insight-item">{len(high_risk_states)} states exceed one standard deviation above the mean fraud rate</div>
        <div class="insight-item">Average fraud rate across all states: {avg_state_rate:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)
