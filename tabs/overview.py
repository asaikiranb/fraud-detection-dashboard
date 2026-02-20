import streamlit as st
import pandas as pd
from components.kpi_cards import render_executive_kpis
from components.charts import (
    fraud_donut,
    fraud_by_category_bar,
    monthly_fraud_trend,
    fraud_type_breakdown,
)
from components.styles import COLORS


def render_overview(df: pd.DataFrame, stats: dict):
    """Render the Executive Overview tab."""

    st.markdown(
        '<div style="font-size:1.4rem;font-weight:800;color:#1A1A2E;'
        'letter-spacing:-0.03em;margin-bottom:0.2rem;">Executive Overview</div>'
        '<div style="font-size:0.85rem;color:#6B7280;margin-bottom:1.5rem;">'
        'Comprehensive fraud intelligence · 50,000 transactions · 2023</div>',
        unsafe_allow_html=True,
    )

    render_executive_kpis(stats)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── Row 1: Donut + Category Bar
    col_left, col_right = st.columns([1, 1.6], gap="large")

    with col_left:
        st.markdown(
            '<div style="font-size:0.875rem;font-weight:700;color:#1A1A2E;'
            'margin-bottom:0.25rem;padding-bottom:0.5rem;border-bottom:1px solid #E9ECEF;">'
            'Transaction Split</div>'
            '<div style="font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;">'
            'Fraud vs legitimate distribution</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            fraud_donut(df),
            use_container_width=True,
            config={"displayModeBar": False},
            key="overview_donut",
        )

        fraud_df = df[df["is_fraud"] == 1]
        top_cat = fraud_df["merchant_category"].mode()[0]
        top_channel = fraud_df["transaction_channel"].mode()[0]
        peak_hour = int(fraud_df["hour"].mode()[0])

        st.markdown(
            f'<div style="background:#F8F9FA;border:1px solid #E9ECEF;border-radius:10px;'
            f'padding:1rem 1.25rem;margin-top:0.5rem;">'
            f'<div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.06em;color:#6B7280;margin-bottom:0.5rem;">Key Signals</div>'
            f'<div style="font-size:0.8rem;color:#1A1A2E;margin-bottom:0.3rem;">– Highest fraud category: <strong>{top_cat}</strong></div>'
            f'<div style="font-size:0.8rem;color:#1A1A2E;margin-bottom:0.3rem;">– Riskiest channel: <strong>{top_channel}</strong></div>'
            f'<div style="font-size:0.8rem;color:#1A1A2E;margin-bottom:0.3rem;">– Peak fraud hour: <strong>{peak_hour:02d}:00 – {peak_hour+1:02d}:00</strong></div>'
            f'<div style="font-size:0.8rem;color:#1A1A2E;">– {df["state"].nunique()} states with active fraud</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            '<div style="font-size:0.875rem;font-weight:700;color:#1A1A2E;'
            'margin-bottom:0.25rem;padding-bottom:0.5rem;border-bottom:1px solid #E9ECEF;">'
            'Fraud by Merchant Category</div>'
            '<div style="font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;">'
            'Fraud count colored by rate intensity</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            fraud_by_category_bar(df),
            use_container_width=True,
            config={"displayModeBar": False},
            key="overview_category_bar",
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row 2: Monthly Trend + Fraud Type
    col_a, col_b = st.columns([1.8, 1], gap="large")

    with col_a:
        st.markdown(
            '<div style="font-size:0.875rem;font-weight:700;color:#1A1A2E;'
            'margin-bottom:0.25rem;padding-bottom:0.5rem;border-bottom:1px solid #E9ECEF;">'
            'Monthly Fraud Trend</div>'
            '<div style="font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;">'
            'Transaction volume (bars) vs fraud count (line)</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            monthly_fraud_trend(df),
            use_container_width=True,
            config={"displayModeBar": False},
            key="overview_monthly_trend",
        )

    with col_b:
        st.markdown(
            '<div style="font-size:0.875rem;font-weight:700;color:#1A1A2E;'
            'margin-bottom:0.25rem;padding-bottom:0.5rem;border-bottom:1px solid #E9ECEF;">'
            'Fraud by Attack Type</div>'
            '<div style="font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;">'
            'Incidents by fraud classification</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            fraud_type_breakdown(df),
            use_container_width=True,
            config={"displayModeBar": False},
            key="overview_fraud_type",
        )

    st.markdown(
        '<div style="font-size:0.7rem;color:#9CA3AF;text-align:right;padding-top:0.5rem;">'
        'Synthetic Credit Card Fraud Dataset · 2023 · 50,000 transactions</div>',
        unsafe_allow_html=True,
    )
