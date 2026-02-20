import streamlit as st
import pandas as pd
from datetime import datetime

from data.generate_data import generate_fraud_dataset
from components.styles import inject_css, COLORS
from tabs.overview import render_overview
from tabs.trends import render_trends
from tabs.geography import render_geography
from tabs.segments import render_segments
from tabs.transactions import render_transactions

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FraudLens — Fraud Detection Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Inject CSS ───────────────────────────────────────────────────────────────
inject_css()


# ─── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data():
    return generate_fraud_dataset(n_transactions=50_000)


@st.cache_data(show_spinner=False)
def compute_stats(df: pd.DataFrame) -> dict:
    total = len(df)
    fraud = int(df["is_fraud"].sum())
    fraud_amount = float(df[df["is_fraud"] == 1]["amount"].sum())
    avg_fraud_amount = float(df[df["is_fraud"] == 1]["amount"].mean())
    total_amount = float(df["amount"].sum())
    return {
        "total_transactions": total,
        "fraud_count": fraud,
        "fraud_rate": fraud / total * 100,
        "fraud_amount": fraud_amount,
        "avg_fraud_amount": avg_fraud_amount,
        "total_amount": total_amount,
        "legitimate_count": total - fraud,
    }


# ─── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    with st.sidebar:
        # Brand
        st.markdown("""
        <div class="sidebar-brand">
            <div class="brand-icon">🔍</div>
            <div>
                <div class="brand-name">FraudLens</div>
                <div class="brand-sub">Detection Dashboard</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Date Range
        st.markdown('<div class="sidebar-filter-label">Date Range</div>', unsafe_allow_html=True)
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input(
                "From",
                value=datetime(2023, 1, 1),
                min_value=datetime(2023, 1, 1),
                max_value=datetime(2023, 12, 31),
                label_visibility="collapsed",
            )
        with col_d2:
            end_date = st.date_input(
                "To",
                value=datetime(2023, 12, 31),
                min_value=datetime(2023, 1, 1),
                max_value=datetime(2023, 12, 31),
                label_visibility="collapsed",
            )

        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

        # ── Fraud Type
        st.markdown('<div class="sidebar-filter-label">Fraud Type</div>', unsafe_allow_html=True)
        fraud_types = sorted(df["fraud_type"].dropna().unique().tolist())
        selected_types = st.multiselect(
            "Fraud type",
            options=fraud_types,
            default=fraud_types,
            label_visibility="collapsed",
        )

        st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)

        # ── Card Type
        st.markdown('<div class="sidebar-filter-label">Card Type</div>', unsafe_allow_html=True)
        card_types = sorted(df["card_type"].unique().tolist())
        selected_cards = st.multiselect(
            "Card type",
            options=card_types,
            default=card_types,
            label_visibility="collapsed",
        )

        st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)

        # ── Transaction Channel
        st.markdown('<div class="sidebar-filter-label">Channel</div>', unsafe_allow_html=True)
        channels = sorted(df["transaction_channel"].unique().tolist())
        selected_channels = st.multiselect(
            "Channel",
            options=channels,
            default=channels,
            label_visibility="collapsed",
        )

        st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

        # ── Reset button
        if st.button("Reset Filters", use_container_width=True):
            st.rerun()

        # ── Dataset info
        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:0.7rem;color:{COLORS['text_muted']};line-height:1.6;">
            <strong style="color:{COLORS['text_secondary']}">Dataset</strong><br>
            Synthetic Credit Card Fraud<br>
            50,000 transactions · 2023<br>
            Generated with reproducible seed
        </div>
        """, unsafe_allow_html=True)

    # ── Apply filters
    filtered = df.copy()

    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1)
    filtered = filtered[(filtered["timestamp"] >= start_ts) & (filtered["timestamp"] < end_ts)]

    if selected_types:
        fraud_mask = (filtered["is_fraud"] == 0) | (filtered["fraud_type"].isin(selected_types))
        filtered = filtered[fraud_mask]

    if selected_cards:
        filtered = filtered[filtered["card_type"].isin(selected_cards)]

    if selected_channels:
        filtered = filtered[filtered["transaction_channel"].isin(selected_channels)]

    return filtered


# ─── Main App ─────────────────────────────────────────────────────────────────
def main():
    with st.spinner("Loading fraud intelligence data..."):
        raw_df = load_data()

    filtered_df = render_sidebar(raw_df)

    if len(filtered_df) == 0:
        st.warning("No transactions match the current filters. Please adjust your selection.")
        return

    stats = compute_stats(filtered_df)

    # ── Tab Navigation
    tabs = st.tabs([
        "Executive Overview",
        "Temporal Trends",
        "Geographic Analysis",
        "Customer Segments",
        "Transaction Explorer",
    ])

    with tabs[0]:
        render_overview(filtered_df, stats)

    with tabs[1]:
        render_trends(filtered_df, stats)

    with tabs[2]:
        render_geography(filtered_df, stats)

    with tabs[3]:
        render_segments(filtered_df, stats)

    with tabs[4]:
        render_transactions(filtered_df, stats)


if __name__ == "__main__":
    main()
