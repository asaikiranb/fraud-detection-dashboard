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
from data.generate_data import generate_fraud_dataset


def render_overview(df: pd.DataFrame, stats: dict):
    """Render the Executive Overview tab."""

    # ── Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Executive Overview</div>
        <div class="page-subtitle">Comprehensive fraud intelligence for 2023 · 50,000 transactions analyzed</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Top KPI Row
    render_executive_kpis(stats)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── Middle Row: Donut + Category Bar
    col_left, col_right = st.columns([1, 1.6], gap="large")

    with col_left:
        st.markdown('<div class="section-header">Transaction Split</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Fraud vs legitimate transaction distribution</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            fraud_donut(df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

        # Quick insight boxes
        fraud_df = df[df["is_fraud"] == 1]
        top_cat = fraud_df["merchant_category"].mode()[0]
        top_channel = fraud_df["transaction_channel"].mode()[0]
        peak_hour = fraud_df["hour"].mode()[0]

        st.markdown(f"""
        <div class="insight-box">
            <div class="insight-title">Key Signals</div>
            <div class="insight-item">Highest fraud category: <strong>{top_cat}</strong></div>
            <div class="insight-item">Riskiest channel: <strong>{top_channel}</strong></div>
            <div class="insight-item">Peak fraud hour: <strong>{peak_hour:02d}:00 – {peak_hour+1:02d}:00</strong></div>
            <div class="insight-item">{df['state'].nunique()} states with active fraud activity</div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-header">Fraud by Merchant Category</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Fraud incident count colored by rate intensity</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            fraud_by_category_bar(df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Bottom Row: Monthly Trend + Fraud Type
    col_a, col_b = st.columns([1.8, 1], gap="large")

    with col_a:
        st.markdown('<div class="section-header">Monthly Fraud Trend</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Total transaction volume (bars) vs fraud count (line) by month</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            monthly_fraud_trend(df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with col_b:
        st.markdown('<div class="section-header">Fraud by Attack Type</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Incidents by fraud classification</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            fraud_type_breakdown(df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    # ── Footer note
    st.markdown(
        '<div class="last-updated">Data: Synthetic Credit Card Fraud Dataset · 2023 · 50,000 transactions</div>',
        unsafe_allow_html=True
    )
