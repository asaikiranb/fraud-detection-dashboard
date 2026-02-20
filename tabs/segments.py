import streamlit as st
import pandas as pd
from components.charts import (
    age_group_chart,
    card_type_donut,
    channel_fraud_bar,
    fraud_type_breakdown,
    amount_distribution,
)
from components.kpi_cards import render_mini_kpi_row
from components.styles import COLORS


def render_segments(df: pd.DataFrame, stats: dict):
    """Render the Customer Segments tab."""

    # ── Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Customer Segments</div>
        <div class="page-subtitle">Who is most targeted? Break down fraud risk by demographics, card type, and channel.</div>
    </div>
    """, unsafe_allow_html=True)

    fraud_df = df[df["is_fraud"] == 1]

    # ── Top segment stats
    age_rates = df.groupby("age_group").apply(lambda g: g["is_fraud"].sum() / len(g) * 100)
    top_age = age_rates.idxmax()
    top_card = fraud_df["card_type"].mode()[0]
    top_channel = fraud_df["transaction_channel"].mode()[0]
    top_fraud_type = fraud_df["fraud_type"].mode()[0]

    render_mini_kpi_row([
        {"label": "Highest Risk Age Group", "value": top_age, "color": COLORS["fraud_red"]},
        {"label": "Most Targeted Card", "value": top_card, "color": COLORS["chart_1"]},
        {"label": "Riskiest Channel", "value": top_channel, "color": COLORS["chart_2"]},
        {"label": "Top Fraud Type", "value": "CNP", "color": COLORS["chart_3"]},
    ])

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── Row 1: Age group + Card type
    col1, col2 = st.columns([1.4, 1], gap="large")

    with col1:
        st.markdown('<div class="section-header">Fraud by Age Group</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Fraud count (bars) and fraud rate (line) by customer age group</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            age_group_chart(df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with col2:
        st.markdown('<div class="section-header">Fraud by Card Type</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Share of fraudulent transactions per card network</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            card_type_donut(df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row 2: Channel + Fraud Type
    col3, col4 = st.columns([1, 1], gap="large")

    with col3:
        st.markdown('<div class="section-header">Fraud Rate by Channel</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Online and phone channels carry the highest fraud risk</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            channel_fraud_bar(df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with col4:
        st.markdown('<div class="section-header">Fraud by Attack Type</div>', unsafe_allow_html=True)
        st.markdown(
            "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
            "Card Not Present and Account Takeover dominate</div>",
            unsafe_allow_html=True
        )
        st.plotly_chart(
            fraud_type_breakdown(df),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row 3: Amount distribution (full width)
    st.markdown('<div class="section-header">Transaction Amount Distribution</div>', unsafe_allow_html=True)
    st.markdown(
        "<div style='font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'>"
        "Fraudulent transactions tend to cluster at higher amounts. Capped at $1,000 for readability.</div>",
        unsafe_allow_html=True
    )
    st.plotly_chart(
        amount_distribution(df),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    # ── Segment Insights
    online_rate = df[df["transaction_channel"] == "Online"]["is_fraud"].mean() * 100
    instore_rate = df[df["transaction_channel"] == "In-Store"]["is_fraud"].mean() * 100
    online_vs_instore = online_rate / instore_rate if instore_rate > 0 else 0

    avg_fraud_amount = fraud_df["amount"].mean()
    avg_legit_amount = df[df["is_fraud"] == 0]["amount"].mean()

    st.markdown(f"""
    <div class="insight-box" style="margin-top:1rem">
        <div class="insight-title">Segment Insights</div>
        <div class="insight-item">Online transactions are <strong>{online_vs_instore:.1f}×</strong> more likely to be fraudulent than in-store</div>
        <div class="insight-item">Age group <strong>{top_age}</strong> has the highest fraud rate at {age_rates[top_age]:.2f}%</div>
        <div class="insight-item">Average fraud transaction (${avg_fraud_amount:.0f}) is {avg_fraud_amount/avg_legit_amount:.1f}× the average legitimate transaction (${avg_legit_amount:.0f})</div>
        <div class="insight-item"><strong>Card Not Present</strong> fraud accounts for the highest share of attack types</div>
    </div>
    """, unsafe_allow_html=True)
