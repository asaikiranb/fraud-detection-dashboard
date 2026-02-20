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
    initial_sidebar_state="collapsed",
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


# ─── Top Filter Bar ───────────────────────────────────────────────────────────
def render_filter_bar(df: pd.DataFrame) -> pd.DataFrame:
    """Render a compact horizontal filter bar beneath the brand header."""

    # Brand header row
    brand_col, spacer = st.columns([1, 3])
    with brand_col:
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:0.6rem;padding:0.5rem 0 0.25rem 0;">
                <div style="width:32px;height:32px;background:{COLORS['text_primary']};
                            border-radius:8px;display:flex;align-items:center;
                            justify-content:center;font-size:16px;flex-shrink:0;">🔍</div>
                <div>
                    <div style="font-size:1rem;font-weight:800;color:{COLORS['text_primary']};
                                letter-spacing:-0.02em;line-height:1.1;">FraudLens</div>
                    <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.07em;
                                color:{COLORS['text_muted']};">Detection Dashboard</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"<hr style='border:none;border-top:1px solid {COLORS['border']};margin:0.5rem 0 0.85rem 0;'/>",
        unsafe_allow_html=True,
    )

    # ── Filter row
    fraud_types = sorted(df["fraud_type"].dropna().unique().tolist())
    card_types = sorted(df["card_type"].unique().tolist())
    channels = sorted(df["transaction_channel"].unique().tolist())

    f0, f1, f2, f3, f4, f5 = st.columns([1.2, 1.2, 1.8, 1.8, 1.8, 0.7], gap="small")

    with f0:
        st.markdown(
            f"<div style='font-size:0.65rem;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.07em;color:{COLORS['text_secondary']};margin-bottom:4px;'>From</div>",
            unsafe_allow_html=True,
        )
        start_date = st.date_input(
            "from_date",
            value=datetime(2023, 1, 1),
            min_value=datetime(2023, 1, 1),
            max_value=datetime(2023, 12, 31),
            label_visibility="collapsed",
            key="filter_start",
        )

    with f1:
        st.markdown(
            f"<div style='font-size:0.65rem;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.07em;color:{COLORS['text_secondary']};margin-bottom:4px;'>To</div>",
            unsafe_allow_html=True,
        )
        end_date = st.date_input(
            "to_date",
            value=datetime(2023, 12, 31),
            min_value=datetime(2023, 1, 1),
            max_value=datetime(2023, 12, 31),
            label_visibility="collapsed",
            key="filter_end",
        )

    with f2:
        st.markdown(
            f"<div style='font-size:0.65rem;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.07em;color:{COLORS['text_secondary']};margin-bottom:4px;'>Fraud Type</div>",
            unsafe_allow_html=True,
        )
        selected_types = st.multiselect(
            "Fraud Type",
            options=fraud_types,
            default=fraud_types,
            label_visibility="collapsed",
            key="filter_fraud_type",
            placeholder="All types",
        )

    with f3:
        st.markdown(
            f"<div style='font-size:0.65rem;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.07em;color:{COLORS['text_secondary']};margin-bottom:4px;'>Card Type</div>",
            unsafe_allow_html=True,
        )
        selected_cards = st.multiselect(
            "Card Type",
            options=card_types,
            default=card_types,
            label_visibility="collapsed",
            key="filter_card_type",
            placeholder="All cards",
        )

    with f4:
        st.markdown(
            f"<div style='font-size:0.65rem;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.07em;color:{COLORS['text_secondary']};margin-bottom:4px;'>Channel</div>",
            unsafe_allow_html=True,
        )
        selected_channels = st.multiselect(
            "Channel",
            options=channels,
            default=channels,
            label_visibility="collapsed",
            key="filter_channel",
            placeholder="All channels",
        )

    with f5:
        st.markdown(
            f"<div style='font-size:0.65rem;font-weight:700;text-transform:uppercase;"
            f"letter-spacing:0.07em;color:{COLORS['text_secondary']};margin-bottom:4px;'>Reset</div>",
            unsafe_allow_html=True,
        )
        if st.button("↺ Reset", key="reset_filters", use_container_width=True):
            st.rerun()

    st.markdown(
        f"<hr style='border:none;border-top:1px solid {COLORS['border']};margin:0.85rem 0 0 0;'/>",
        unsafe_allow_html=True,
    )

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

    filtered_df = render_filter_bar(raw_df)

    if len(filtered_df) == 0:
        st.warning("No transactions match the current filters. Please adjust your selection.")
        return

    stats = compute_stats(filtered_df)

    # ── Tab Navigation
    tabs = st.tabs([
        "  Executive Overview  ",
        "  Temporal Trends  ",
        "  Geographic Analysis  ",
        "  Customer Segments  ",
        "  Transaction Explorer  ",
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
