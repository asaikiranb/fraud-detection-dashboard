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
    page_title="Fraud & Risk Analytics Dashboard",
    page_icon=None,
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


# ─── Top Header + Filter Bar ─────────────────────────────────────────────────
def render_filter_bar(df: pd.DataFrame) -> pd.DataFrame:
    """Render the dashboard header and a clean horizontal filter bar."""

    # ── Brand header
    st.markdown(
        f"""
        <div style="display:flex;align-items:baseline;gap:1rem;
                    padding:0.75rem 0 0.5rem 0;">
            <div style="font-size:1.6rem;font-weight:800;color:{COLORS['text_primary']};
                        letter-spacing:-0.04em;line-height:1;">
                Fraud & Risk Analytics
            </div>
            <div style="font-size:0.7rem;font-weight:600;text-transform:uppercase;
                        letter-spacing:0.1em;color:{COLORS['text_muted']};
                        padding-bottom:0.15rem;">
                Dashboard
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<hr style='border:none;border-top:1px solid {COLORS['border']};margin:0.4rem 0 0.9rem 0;'/>",
        unsafe_allow_html=True,
    )

    # ── Filter row — all dropdowns (selectbox), no multiselect tags
    fraud_types = sorted(df["fraud_type"].dropna().unique().tolist())
    card_types = sorted(df["card_type"].unique().tolist())
    channels = sorted(df["transaction_channel"].unique().tolist())

    _lbl = (
        "font-size:0.62rem;font-weight:700;text-transform:uppercase;"
        f"letter-spacing:0.08em;color:{COLORS['text_secondary']};margin-bottom:3px;"
    )

    f0, f1, f2, f3, f4, f5 = st.columns([1.1, 1.1, 1.6, 1.4, 1.4, 0.6], gap="small")

    with f0:
        st.markdown(f'<div style="{_lbl}">From</div>', unsafe_allow_html=True)
        start_date = st.date_input(
            "from_date",
            value=datetime(2023, 1, 1),
            min_value=datetime(2023, 1, 1),
            max_value=datetime(2023, 12, 31),
            label_visibility="collapsed",
            key="filter_start",
        )

    with f1:
        st.markdown(f'<div style="{_lbl}">To</div>', unsafe_allow_html=True)
        end_date = st.date_input(
            "to_date",
            value=datetime(2023, 12, 31),
            min_value=datetime(2023, 1, 1),
            max_value=datetime(2023, 12, 31),
            label_visibility="collapsed",
            key="filter_end",
        )

    with f2:
        st.markdown(f'<div style="{_lbl}">Fraud Type</div>', unsafe_allow_html=True)
        fraud_type_options = ["All Types"] + fraud_types
        selected_fraud_type = st.selectbox(
            "Fraud Type",
            options=fraud_type_options,
            index=0,
            label_visibility="collapsed",
            key="filter_fraud_type",
        )

    with f3:
        st.markdown(f'<div style="{_lbl}">Card Type</div>', unsafe_allow_html=True)
        card_type_options = ["All Cards"] + card_types
        selected_card = st.selectbox(
            "Card Type",
            options=card_type_options,
            index=0,
            label_visibility="collapsed",
            key="filter_card_type",
        )

    with f4:
        st.markdown(f'<div style="{_lbl}">Channel</div>', unsafe_allow_html=True)
        channel_options = ["All Channels"] + channels
        selected_channel = st.selectbox(
            "Channel",
            options=channel_options,
            index=0,
            label_visibility="collapsed",
            key="filter_channel",
        )

    with f5:
        st.markdown(f'<div style="{_lbl}">Reset</div>', unsafe_allow_html=True)
        if st.button("Reset", key="reset_filters", use_container_width=True):
            st.rerun()

    st.markdown(
        f"<hr style='border:none;border-top:1px solid {COLORS['border']};margin:0.9rem 0 0 0;'/>",
        unsafe_allow_html=True,
    )

    # ── Apply filters
    filtered = df.copy()
    start_ts = pd.Timestamp(start_date)
    end_ts = pd.Timestamp(end_date) + pd.Timedelta(days=1)
    filtered = filtered[(filtered["timestamp"] >= start_ts) & (filtered["timestamp"] < end_ts)]

    if selected_fraud_type != "All Types":
        fraud_mask = (filtered["is_fraud"] == 0) | (filtered["fraud_type"] == selected_fraud_type)
        filtered = filtered[fraud_mask]

    if selected_card != "All Cards":
        filtered = filtered[filtered["card_type"] == selected_card]

    if selected_channel != "All Channels":
        filtered = filtered[filtered["transaction_channel"] == selected_channel]

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
