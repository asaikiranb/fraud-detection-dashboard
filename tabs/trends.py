import streamlit as st
import pandas as pd
from components.charts import (
    hourly_heatmap,
    day_of_week_bar,
    weekly_trend,
    quarterly_comparison,
)
from components.kpi_cards import (
    render_mini_kpi_row,
    render_page_header,
    render_section_header,
    render_insight_box,
)
from components.styles import COLORS, PLOTLY_CONFIG


def render_trends(df: pd.DataFrame, stats: dict):
    """Render the Temporal Trends tab."""
    render_page_header(
        "Temporal Trends",
        "When does fraud happen? Identify time-based patterns and seasonal anomalies.",
    )

    fraud_df = df[df["is_fraud"] == 1]
    peak_hour = int(fraud_df["hour"].mode()[0])
    peak_day = fraud_df["day_of_week"].mode()[0][:3]
    peak_month = fraud_df["month_name"].mode()[0]
    peak_quarter = f"Q{int(fraud_df['quarter'].mode()[0])}"

    render_mini_kpi_row([
        {"label": "Peak Hour",    "value": f"{peak_hour:02d}:00", "color": COLORS["fraud_red"]},
        {"label": "Peak Day",     "value": peak_day,              "color": COLORS["chart_1"]},
        {"label": "Peak Month",   "value": peak_month,            "color": COLORS["chart_2"]},
        {"label": "Peak Quarter", "value": peak_quarter,          "color": COLORS["chart_3"]},
    ])

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── Row 1: Heatmap + Day-of-Week
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        render_section_header(
            "Fraud Heatmap: Hour × Day",
            "Darker cells = higher fraud concentration. Fraud peaks late-night.",
        )
        st.plotly_chart(
            hourly_heatmap(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="trends_heatmap",
        )

    with col2:
        render_section_header(
            "Day-of-Week Fraud Rate",
            "Highlighted bar = highest risk day",
        )
        st.plotly_chart(
            day_of_week_bar(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="trends_dow_bar",
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row 2: Weekly trend + QoQ
    col3, col4 = st.columns([1.4, 1], gap="large")

    with col3:
        render_section_header(
            "Weekly Fraud Rate Trend",
            "Weekly fraud rate with 4-week rolling average",
        )
        st.plotly_chart(
            weekly_trend(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="trends_weekly",
        )

    with col4:
        render_section_header(
            "Quarter-over-Quarter",
            "Fraud count and rate across quarters",
        )
        st.plotly_chart(
            quarterly_comparison(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="trends_qoq",
        )

    night_pct = (
        len(fraud_df[(fraud_df["hour"] >= 22) | (fraud_df["hour"] <= 4)]) / len(fraud_df) * 100
        if len(fraud_df) > 0 else 0
    )
    weekend_pct = (
        len(fraud_df[fraud_df["day_of_week"].isin(["Saturday", "Sunday"])]) / len(fraud_df) * 100
        if len(fraud_df) > 0 else 0
    )
    q_rates = df.groupby("quarter").apply(lambda g: g["is_fraud"].sum() / len(g) * 100)
    q4_vs_q1 = float(q_rates.get(4, 0)) - float(q_rates.get(1, 0))
    peak_count = len(fraud_df[fraud_df["hour"] == peak_hour])
    direction = "higher" if q4_vs_q1 > 0 else "lower"

    render_insight_box("Temporal Insights", [
        f'{night_pct:.1f}% of all fraud occurs between 10 PM and 4 AM',
        f'Weekends account for {weekend_pct:.1f}% of fraud events',
        f'Q4 fraud rate is {abs(q4_vs_q1):.2f}% {direction} than Q1',
        f'Peak hour {peak_hour:02d}:00 recorded {peak_count:,} fraud events',
    ])
