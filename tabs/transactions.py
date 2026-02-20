import streamlit as st
import pandas as pd
from components.kpi_cards import render_page_header
from components.styles import COLORS

_TABLE_ROW_LIMIT = 500
_DISPLAY_COLS = [
    "transaction_id", "timestamp", "amount", "merchant_category",
    "transaction_channel", "card_type", "city", "state",
    "age_group", "is_fraud", "fraud_type",
]
_DISPLAY_HEADERS = [
    "Transaction ID", "Timestamp", "Amount", "Category",
    "Channel", "Card Type", "City", "State",
    "Age Group", "Status", "Fraud Type",
]

_METRIC_CARD = (
    f"background:{COLORS['surface']};border:1px solid {COLORS['border']};"
    "border-radius:8px;padding:0.65rem 1rem;text-align:center;"
)
_METRIC_LABEL = (
    f"font-size:0.65rem;font-weight:700;text-transform:uppercase;"
    f"letter-spacing:0.07em;color:{COLORS['text_secondary']};"
)
_FILTER_LABEL = (
    f"font-size:0.65rem;font-weight:700;text-transform:uppercase;"
    f"letter-spacing:0.07em;color:{COLORS['text_secondary']};margin-bottom:4px;"
)


def _metric_card(label: str, value: str, value_color: str = None) -> str:
    color = value_color or COLORS["text_primary"]
    return (
        f'<div style="{_METRIC_CARD}">'
        f'<div style="{_METRIC_LABEL}">{label}</div>'
        f'<div style="font-size:1.1rem;font-weight:800;color:{color};">{value}</div>'
        f'</div>'
    )


def render_transactions(df: pd.DataFrame, stats: dict):
    """Render the Transaction Explorer tab."""
    render_page_header(
        "Transaction Explorer",
        "Drill into individual transactions. Filter, search, and export raw data.",
    )

    # ── Filter row
    f1, f2, f3, f4 = st.columns(4, gap="small")

    with f1:
        st.markdown(f'<div style="{_FILTER_LABEL}">Show</div>', unsafe_allow_html=True)
        fraud_filter = st.selectbox(
            "show_filter",
            ["All Transactions", "Fraud Only", "Legitimate Only"],
            label_visibility="collapsed",
            key="tx_fraud_filter",
        )

    with f2:
        st.markdown(f'<div style="{_FILTER_LABEL}">Category</div>', unsafe_allow_html=True)
        categories = ["All"] + sorted(df["merchant_category"].unique().tolist())
        cat_filter = st.selectbox(
            "category_filter", categories,
            label_visibility="collapsed",
            key="tx_cat_filter",
        )

    with f3:
        st.markdown(f'<div style="{_FILTER_LABEL}">Channel</div>', unsafe_allow_html=True)
        channels = ["All"] + sorted(df["transaction_channel"].unique().tolist())
        ch_filter = st.selectbox(
            "channel_filter", channels,
            label_visibility="collapsed",
            key="tx_ch_filter",
        )

    with f4:
        st.markdown(f'<div style="{_FILTER_LABEL}">Min Amount ($)</div>', unsafe_allow_html=True)
        min_amount = st.number_input(
            "min_amount",
            min_value=0.0, max_value=9999.0, value=0.0, step=10.0,
            label_visibility="collapsed",
            key="tx_min_amount",
        )

    st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)

    search_term = st.text_input(
        "search_bar",
        placeholder="Search by Transaction ID, city, or state...",
        label_visibility="collapsed",
        key="tx_search",
    )

    # ── Apply filters
    filtered = df.copy()

    if fraud_filter == "Fraud Only":
        filtered = filtered[filtered["is_fraud"] == 1]
    elif fraud_filter == "Legitimate Only":
        filtered = filtered[filtered["is_fraud"] == 0]

    if cat_filter != "All":
        filtered = filtered[filtered["merchant_category"] == cat_filter]

    if ch_filter != "All":
        filtered = filtered[filtered["transaction_channel"] == ch_filter]

    if min_amount > 0:
        filtered = filtered[filtered["amount"] >= min_amount]

    if search_term:
        mask = (
            filtered["transaction_id"].str.contains(search_term, case=False, na=False)
            | filtered["city"].str.contains(search_term, case=False, na=False)
            | filtered["state"].str.contains(search_term, case=False, na=False)
            | filtered["state_name"].str.contains(search_term, case=False, na=False)
        )
        filtered = filtered[mask]

    # ── Summary metrics
    total_shown = len(filtered)
    fraud_shown = int(filtered["is_fraud"].sum())
    fraud_pct = fraud_shown / total_shown * 100 if total_shown > 0 else 0
    total_vol = filtered["amount"].sum()

    m1, m2, m3, m4 = st.columns(4, gap="small")
    with m1:
        st.markdown(_metric_card("Showing", f"{total_shown:,}"), unsafe_allow_html=True)
    with m2:
        st.markdown(_metric_card("Fraud Events", f"{fraud_shown:,}", COLORS["fraud_red"]), unsafe_allow_html=True)
    with m3:
        st.markdown(_metric_card("Fraud Rate", f"{fraud_pct:.2f}%"), unsafe_allow_html=True)
    with m4:
        st.markdown(_metric_card("Total Volume", f"${total_vol:,.0f}"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Display table (formatted copy, separate from CSV export)
    display_df = filtered[_DISPLAY_COLS].copy()
    display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    display_df["amount"] = display_df["amount"].apply(lambda x: f"${x:,.2f}")
    display_df["is_fraud"] = display_df["is_fraud"].map({0: "Legitimate", 1: "FRAUD"})
    display_df["fraud_type"] = display_df["fraud_type"].fillna("—")
    display_df.columns = _DISPLAY_HEADERS

    st.dataframe(
        display_df.head(_TABLE_ROW_LIMIT),
        use_container_width=True,
        height=520,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Status", help="FRAUD or Legitimate"),
            "Amount": st.column_config.TextColumn("Amount"),
        },
    )

    if total_shown > _TABLE_ROW_LIMIT:
        st.markdown(
            f'<div style="font-size:0.75rem;color:{COLORS["text_muted"]};text-align:center;margin-top:0.4rem;">'
            f'Showing top {_TABLE_ROW_LIMIT} of {total_shown:,} filtered results</div>',
            unsafe_allow_html=True,
        )

    # ── Export (raw datetime formatted separately for CSV)
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    csv_export = filtered[_DISPLAY_COLS].copy()
    csv_export["timestamp"] = csv_export["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    csv_bytes = csv_export.to_csv(index=False).encode("utf-8")

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        st.download_button(
            label="Export to CSV",
            data=csv_bytes,
            file_name="fraud_transactions_export.csv",
            mime="text/csv",
            key="tx_export_btn",
        )
    with col_info:
        st.markdown(
            f'<div style="font-size:0.75rem;color:{COLORS["text_muted"]};padding-top:0.75rem;">'
            f'Exports all {total_shown:,} filtered rows</div>',
            unsafe_allow_html=True,
        )
