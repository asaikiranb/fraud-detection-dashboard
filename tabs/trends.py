import streamlit as st
import pandas as pd
from components.charts import (
    hourly_heatmap,
    day_of_week_bar,
    weekly_trend,
    quarterly_comparison,
    monthly_fraud_trend,
)
from components.kpi_cards import render_mini_kpi_row
from components.styles import COLORS


def render_trends(df: pd.DataFrame, stats: dict):
    """Render the Temporal Trends tab."""

    # ── Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Temporal Trends</div>
        <div class="page-subtitle">When does fraud happen? Identify time-based patterns and seasonal anomalies.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Mini KPI row
    fraud_df = df[df["is_fraud"] == 1]
    peak_hour = int(fraud_df["hour"].mode()[0])
    peak_day = fraud_df["day_of_week"].mode()[0][:3]
    peak_month = fraud_df["month_name"].mode()[0]
    peak_quarter = f"Q{int(fraud_df['quarter'].mode()[0])}"

    render_mini_kpi_row([
        {"label": "Peak Hour", "value": f"{peak_hour:02d}:00", "color": COLORS["fraud_red"]},
        {"label": "Peak Day", "value": peak_day, "color": COLORS["chart_1"]},
        {"label": "Peak Month", "value": peak_month, "color": COLORS["chart_2"]},
        {"label": "Peak Quarter", "value": peak_quarter, "color": COLORS["chart_3"]},
    ])

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── Row 1: Heatmap + Day of Week
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.markdown('<div class="section-header">Fraud Heatmap: Hour × Day</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Darker cells = higher fraud concentration. Fraud peaks in late-night hours.</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            hourly_heatmap(df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with col2:
        st.markdown('<div class="section-header">Day-of-Week Fraud Rate</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Highlighted bar = highest risk day</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            day_of_week_bar(df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row 2: Weekly trend + Quarterly comparison
    col3, col4 = st.columns([1.4, 1], gap="large")

    with col3:
        st.markdown('<div class="section-header">Weekly Fraud Rate Trend</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Weekly fraud rate with 4-week rolling average</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            weekly_trend(df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with col4:
        st.markdown('<div class="section-header">Quarter-over-Quarter</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Fraud count and rate comparison across quarters</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            quarterly_comparison(df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    # ── Insight Box
    night_fraud_pct = len(fraud_df[(fraud_df["hour"] >= 22) | (fraud_df["hour"] <= 4)]) / len(fraud_df) * 100
    weekend_fraud = fraud_df[fraud_df["day_of_week"].isin(["Saturday", "Sunday"])]
    weekend_pct = len(weekend_fraud) / len(fraud_df) * 100

    # Q4 vs Q1
    q4_rate = df[df["quarter"] == 4].apply(lambda r: r, axis=1)  # just for count
    q_rates = df.groupby("quarter").apply(lambda g: g["is_fraud"].sum() / len(g) * 100)
    q4_vs_q1 = q_rates.get(4, 0) - q_rates.get(1, 0)

    st.markdown(f"""
    <div class="insight-box" style="margin-top:1rem">
        <div class="insight-title">Temporal Insights</div>
        <div class="insight-item">{night_fraud_pct:.1f}% of all fraud occurs between 10 PM and 4 AM</div>
        <div class="insight-item">Weekends account for {weekend_pct:.1f}% of fraud events</div>
        <div class="insight-item">Q4 fraud rate is {abs(q4_vs_q1):.2f}% {'higher' if q4_vs_q1 > 0 else 'lower'} than Q1 — {'holiday season spike' if q4_vs_q1 > 0 else 'improved controls in Q4'}</div>
        <div class="insight-item">Peak hour is {peak_hour:02d}:00 with {len(fraud_df[fraud_df['hour'] == peak_hour]):,} fraud events</div>
    </div>
    """, unsafe_allow_html=True)
