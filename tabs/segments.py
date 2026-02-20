import streamlit as st
import pandas as pd
from components.charts import (
    age_group_chart,
    card_type_donut,
    channel_fraud_bar,
    fraud_type_breakdown,
    amount_distribution,
)
from components.kpi_cards import (
    render_mini_kpi_row,
    render_page_header,
    render_section_header,
    render_insight_box,
)
from components.styles import COLORS, PLOTLY_CONFIG


def render_segments(df: pd.DataFrame, stats: dict):
    """Render the Customer Segments tab."""
    render_page_header(
        "Customer Segments",
        "Who is most targeted? Break down fraud risk by demographics, card type, and channel.",
    )

    fraud_df = df[df["is_fraud"] == 1]

    age_rates = df.groupby("age_group").apply(lambda g: g["is_fraud"].sum() / len(g) * 100)
    top_age = age_rates.idxmax()
    top_card = fraud_df["card_type"].mode()[0] if len(fraud_df) > 0 else "N/A"
    top_channel = fraud_df["transaction_channel"].mode()[0] if len(fraud_df) > 0 else "N/A"

    render_mini_kpi_row([
        {"label": "Highest Risk Age",   "value": top_age,     "color": COLORS["fraud_red"]},
        {"label": "Most Targeted Card", "value": top_card,    "color": COLORS["chart_1"]},
        {"label": "Riskiest Channel",   "value": top_channel, "color": COLORS["chart_2"]},
        {"label": "Top Fraud Type",     "value": "CNP",       "color": COLORS["chart_3"]},
    ])

    st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

    # ── Row 1: Age + Card Type
    col1, col2 = st.columns([1.4, 1], gap="large")

    with col1:
        render_section_header(
            "Fraud by Age Group",
            "Fraud count (bars) and fraud rate (line) by customer age",
        )
        st.plotly_chart(
            age_group_chart(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="seg_age_chart",
        )

    with col2:
        render_section_header(
            "Fraud by Card Type",
            "Share of fraudulent transactions per card network",
        )
        st.plotly_chart(
            card_type_donut(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="seg_card_donut",
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row 2: Channel + Fraud Type
    col3, col4 = st.columns([1, 1], gap="large")

    with col3:
        render_section_header(
            "Fraud Rate by Channel",
            "Online and phone channels carry the highest risk",
        )
        st.plotly_chart(
            channel_fraud_bar(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="seg_channel_bar",
        )

    with col4:
        render_section_header(
            "Fraud by Attack Type",
            "Card Not Present and Account Takeover dominate",
        )
        st.plotly_chart(
            fraud_type_breakdown(df),
            use_container_width=True,
            config=PLOTLY_CONFIG,
            key="seg_fraud_type",
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Row 3: Amount distribution
    render_section_header(
        "Transaction Amount Distribution",
        "Fraudulent transactions cluster at higher amounts. Capped at $1,000.",
    )
    st.plotly_chart(
        amount_distribution(df),
        use_container_width=True,
        config=PLOTLY_CONFIG,
        key="seg_amount_dist",
    )

    online_rate = df[df["transaction_channel"] == "Online"]["is_fraud"].mean() * 100
    instore_rate = df[df["transaction_channel"] == "In-Store"]["is_fraud"].mean() * 100
    online_vs_instore = online_rate / instore_rate if instore_rate > 0 else 0
    avg_fraud_amount = fraud_df["amount"].mean() if len(fraud_df) > 0 else 0
    avg_legit_amount = df[df["is_fraud"] == 0]["amount"].mean()

    render_insight_box("Segment Insights", [
        f'Online transactions are <strong>{online_vs_instore:.1f}×</strong> more likely fraudulent than in-store',
        f'Age group <strong>{top_age}</strong> has the highest fraud rate at {age_rates[top_age]:.2f}%',
        f'Avg fraud transaction (${avg_fraud_amount:.0f}) is {avg_fraud_amount / avg_legit_amount:.1f}× the avg legitimate (${avg_legit_amount:.0f})',
        'Card Not Present fraud accounts for the largest share of attack types',
    ])
