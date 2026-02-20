import streamlit as st
import pandas as pd
from components.kpi_cards import (
    render_executive_kpis,
    render_page_header,
    render_section_header,
    render_insight_box,
)
from components.charts import (
    fraud_donut,
    fraud_by_category_bar,
    monthly_fraud_trend,
    fraud_type_breakdown,
)
from components.styles import COLORS, PLOTLY_CONFIG


def render_overview(df: pd.DataFrame, stats: dict):
    """Render the Executive Overview tab."""
    render_page_header(
        "Executive Overview",
        "Comprehensive fraud intelligence · 50,000 transactions · 2023",
    )

    render_executive_kpis(stats)

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── Row 1: Donut + Category Bar
    col_left, col_right = st.columns([1, 1.6], gap="large")

    with col_left:
        render_section_header(
            "Transaction Split",
            "Fraud vs legitimate distribution",
        )
        st.plotly_chart(
            fraud_donut(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="overview_donut",
        )

        fraud_df = df[df["is_fraud"] == 1]
        top_cat = fraud_df["merchant_category"].mode()[0]
        top_channel = fraud_df["transaction_channel"].mode()[0]
        peak_hour = int(fraud_df["hour"].mode()[0])

        render_insight_box("Key Signals", [
            f'Highest fraud category: <strong>{top_cat}</strong>',
            f'Riskiest channel: <strong>{top_channel}</strong>',
            f'Peak fraud hour: <strong>{peak_hour:02d}:00 – {peak_hour + 1:02d}:00</strong>',
            f'{df["state"].nunique()} states with active fraud',
        ])

    with col_right:
        render_section_header(
            "Fraud by Merchant Category",
            "Fraud count colored by rate intensity",
        )
        st.plotly_chart(
            fraud_by_category_bar(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="overview_category_bar",
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row 2: Monthly Trend + Fraud Type
    col_a, col_b = st.columns([1.8, 1], gap="large")

    with col_a:
        render_section_header(
            "Monthly Fraud Trend",
            "Transaction volume (bars) vs fraud count (line)",
        )
        st.plotly_chart(
            monthly_fraud_trend(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="overview_monthly_trend",
        )

    with col_b:
        render_section_header(
            "Fraud by Attack Type",
            "Incidents by fraud classification",
        )
        st.plotly_chart(
            fraud_type_breakdown(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="overview_fraud_type",
        )

    st.markdown(
        f'<div style="font-size:0.7rem;color:{COLORS["text_muted"]};text-align:right;padding-top:0.5rem;">'
        'Synthetic Credit Card Fraud Dataset · 2023 · 50,000 transactions</div>',
        unsafe_allow_html=True,
    )
