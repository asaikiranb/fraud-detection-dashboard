import streamlit as st
import pandas as pd
from components.charts import (
    hourly_heatmap,
    day_of_week_bar,
    weekly_trend,
    quarterly_comparison,
)
from components.kpi_cards import render_mini_kpi_row
from components.styles import COLORS

_SH = (
    'font-size:0.875rem;font-weight:700;color:#1A1A2E;'
    'margin-bottom:0.25rem;padding-bottom:0.5rem;border-bottom:1px solid #E9ECEF;'
)
_SUB = 'font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'


def render_trends(df: pd.DataFrame, stats: dict):
    """Render the Temporal Trends tab."""

    st.markdown(
        '<div style="font-size:1.6rem;font-weight:800;color:#1A1A2E;'
        'letter-spacing:-0.03em;margin-bottom:0.2rem;">Temporal Trends</div>'
        '<div style="font-size:0.85rem;color:#6B7280;margin-bottom:1.5rem;">'
        'When does fraud happen? Identify time-based patterns and seasonal anomalies.</div>',
        unsafe_allow_html=True,
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
        st.markdown(
            f'<div style="{_SH}">Fraud Heatmap: Hour × Day</div>'
            f'<div style="{_SUB}">Darker cells = higher fraud concentration. Fraud peaks late-night.</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            hourly_heatmap(df),
            use_container_width=True,
            config={"displayModeBar": False},
            key="trends_heatmap",
        )

    with col2:
        st.markdown(
            f'<div style="{_SH}">Day-of-Week Fraud Rate</div>'
            f'<div style="{_SUB}">Highlighted bar = highest risk day</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            day_of_week_bar(df),
            use_container_width=True,
            config={"displayModeBar": False},
            key="trends_dow_bar",
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row 2: Weekly trend + QoQ
    col3, col4 = st.columns([1.4, 1], gap="large")

    with col3:
        st.markdown(
            f'<div style="{_SH}">Weekly Fraud Rate Trend</div>'
            f'<div style="{_SUB}">Weekly fraud rate with 4-week rolling average</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            weekly_trend(df),
            use_container_width=True,
            config={"displayModeBar": False},
            key="trends_weekly",
        )

    with col4:
        st.markdown(
            f'<div style="{_SH}">Quarter-over-Quarter</div>'
            f'<div style="{_SUB}">Fraud count and rate across quarters</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            quarterly_comparison(df),
            use_container_width=True,
            config={"displayModeBar": False},
            key="trends_qoq",
        )

    # ── Insight box (inline styles only)
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

    st.markdown(
        f'<div style="background:#F8F9FA;border:1px solid #E9ECEF;border-radius:10px;'
        f'padding:1rem 1.25rem;margin-top:1rem;">'
        f'<div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.06em;color:#6B7280;margin-bottom:0.5rem;">Temporal Insights</div>'
        f'<div style="font-size:0.8rem;color:#1A1A2E;margin-bottom:0.3rem;">'
        f'– {night_pct:.1f}% of all fraud occurs between 10 PM and 4 AM</div>'
        f'<div style="font-size:0.8rem;color:#1A1A2E;margin-bottom:0.3rem;">'
        f'– Weekends account for {weekend_pct:.1f}% of fraud events</div>'
        f'<div style="font-size:0.8rem;color:#1A1A2E;margin-bottom:0.3rem;">'
        f'– Q4 fraud rate is {abs(q4_vs_q1):.2f}% {"higher" if q4_vs_q1 > 0 else "lower"} than Q1</div>'
        f'<div style="font-size:0.8rem;color:#1A1A2E;">'
        f'– Peak hour {peak_hour:02d}:00 recorded {peak_count:,} fraud events</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
