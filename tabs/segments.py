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

_SH = (
    'font-size:0.875rem;font-weight:700;color:#1A1A2E;'
    'margin-bottom:0.25rem;padding-bottom:0.5rem;border-bottom:1px solid #E9ECEF;'
)
_SUB = 'font-size:0.78rem;color:#6B7280;margin-bottom:0.75rem;'


def render_segments(df: pd.DataFrame, stats: dict):
    """Render the Customer Segments tab."""

    st.markdown(
        '<div style="font-size:1.4rem;font-weight:800;color:#1A1A2E;'
        'letter-spacing:-0.03em;margin-bottom:0.2rem;">Customer Segments</div>'
        '<div style="font-size:0.85rem;color:#6B7280;margin-bottom:1.5rem;">'
        'Who is most targeted? Break down fraud risk by demographics, card type, and channel.</div>',
        unsafe_allow_html=True,
    )

    fraud_df = df[df["is_fraud"] == 1]

    age_rates = df.groupby("age_group").apply(lambda g: g["is_fraud"].sum() / len(g) * 100)
    top_age = age_rates.idxmax()
    top_card = fraud_df["card_type"].mode()[0] if len(fraud_df) > 0 else "N/A"
    top_channel = fraud_df["transaction_channel"].mode()[0] if len(fraud_df) > 0 else "N/A"

    render_mini_kpi_row([
        {"label": "Highest Risk Age",  "value": top_age,     "color": COLORS["fraud_red"]},
        {"label": "Most Targeted Card","value": top_card,    "color": COLORS["chart_1"]},
        {"label": "Riskiest Channel",  "value": top_channel, "color": COLORS["chart_2"]},
        {"label": "Top Fraud Type",    "value": "CNP",       "color": COLORS["chart_3"]},
    ])

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── Row 1: Age + Card Type
    col1, col2 = st.columns([1.4, 1], gap="large")

    with col1:
        st.markdown(
            f'<div style="{_SH}">Fraud by Age Group</div>'
            f'<div style="{_SUB}">Fraud count (bars) and fraud rate (line) by customer age</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            age_group_chart(df),
            use_container_width=True,
            config={"displayModeBar": False},
            key="seg_age_chart",
        )

    with col2:
        st.markdown(
            f'<div style="{_SH}">Fraud by Card Type</div>'
            f'<div style="{_SUB}">Share of fraudulent transactions per card network</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            card_type_donut(df),
            use_container_width=True,
            config={"displayModeBar": False},
            key="seg_card_donut",
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row 2: Channel + Fraud Type
    col3, col4 = st.columns([1, 1], gap="large")

    with col3:
        st.markdown(
            f'<div style="{_SH}">Fraud Rate by Channel</div>'
            f'<div style="{_SUB}">Online and phone channels carry the highest risk</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            channel_fraud_bar(df),
            use_container_width=True,
            config={"displayModeBar": False},
            key="seg_channel_bar",
        )

    with col4:
        st.markdown(
            f'<div style="{_SH}">Fraud by Attack Type</div>'
            f'<div style="{_SUB}">Card Not Present and Account Takeover dominate</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            fraud_type_breakdown(df),
            use_container_width=True,
            config={"displayModeBar": False},
            key="seg_fraud_type",
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row 3: Amount distribution
    st.markdown(
        f'<div style="{_SH}">Transaction Amount Distribution</div>'
        f'<div style="{_SUB}">Fraudulent transactions cluster at higher amounts. Capped at $1,000.</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        amount_distribution(df),
        use_container_width=True,
        config={"displayModeBar": False},
        key="seg_amount_dist",
    )

    # ── Insight box
    online_rate = df[df["transaction_channel"] == "Online"]["is_fraud"].mean() * 100
    instore_rate = df[df["transaction_channel"] == "In-Store"]["is_fraud"].mean() * 100
    online_vs_instore = online_rate / instore_rate if instore_rate > 0 else 0
    avg_fraud_amount = fraud_df["amount"].mean() if len(fraud_df) > 0 else 0
    avg_legit_amount = df[df["is_fraud"] == 0]["amount"].mean()

    st.markdown(
        f'<div style="background:#F8F9FA;border:1px solid #E9ECEF;border-radius:10px;'
        f'padding:1rem 1.25rem;margin-top:1rem;">'
        f'<div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.06em;color:#6B7280;margin-bottom:0.5rem;">Segment Insights</div>'
        f'<div style="font-size:0.8rem;color:#1A1A2E;margin-bottom:0.3rem;">'
        f'– Online transactions are <strong>{online_vs_instore:.1f}×</strong> more likely fraudulent than in-store</div>'
        f'<div style="font-size:0.8rem;color:#1A1A2E;margin-bottom:0.3rem;">'
        f'– Age group <strong>{top_age}</strong> has the highest fraud rate at {age_rates[top_age]:.2f}%</div>'
        f'<div style="font-size:0.8rem;color:#1A1A2E;margin-bottom:0.3rem;">'
        f'– Avg fraud transaction (${avg_fraud_amount:.0f}) is {avg_fraud_amount/avg_legit_amount:.1f}× the avg legitimate (${avg_legit_amount:.0f})</div>'
        f'<div style="font-size:0.8rem;color:#1A1A2E;">'
        f'– Card Not Present fraud accounts for the largest share of attack types</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
