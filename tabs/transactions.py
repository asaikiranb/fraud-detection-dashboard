import streamlit as st
import pandas as pd
from components.styles import COLORS

_SH = (
    'font-size:0.875rem;font-weight:700;color:#1A1A2E;'
    'margin-bottom:0.25rem;padding-bottom:0.5rem;border-bottom:1px solid #E9ECEF;'
)


def render_transactions(df: pd.DataFrame, stats: dict):
    """Render the Transaction Explorer tab."""

    st.markdown(
        '<div style="font-size:1.4rem;font-weight:800;color:#1A1A2E;'
        'letter-spacing:-0.03em;margin-bottom:0.2rem;">Transaction Explorer</div>'
        '<div style="font-size:0.85rem;color:#6B7280;margin-bottom:1.25rem;">'
        'Drill into individual transactions. Filter, search, and export raw data.</div>',
        unsafe_allow_html=True,
    )

    # ── Filter row
    f1, f2, f3, f4 = st.columns(4, gap="small")

    with f1:
        st.markdown(
            '<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            'letter-spacing:0.07em;color:#6B7280;margin-bottom:4px;">Show</div>',
            unsafe_allow_html=True,
        )
        fraud_filter = st.selectbox(
            "show_filter",
            ["All Transactions", "Fraud Only", "Legitimate Only"],
            label_visibility="collapsed",
            key="tx_fraud_filter",
        )

    with f2:
        st.markdown(
            '<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            'letter-spacing:0.07em;color:#6B7280;margin-bottom:4px;">Category</div>',
            unsafe_allow_html=True,
        )
        categories = ["All"] + sorted(df["merchant_category"].unique().tolist())
        cat_filter = st.selectbox(
            "category_filter", categories,
            label_visibility="collapsed",
            key="tx_cat_filter",
        )

    with f3:
        st.markdown(
            '<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            'letter-spacing:0.07em;color:#6B7280;margin-bottom:4px;">Channel</div>',
            unsafe_allow_html=True,
        )
        channels = ["All"] + sorted(df["transaction_channel"].unique().tolist())
        ch_filter = st.selectbox(
            "channel_filter", channels,
            label_visibility="collapsed",
            key="tx_ch_filter",
        )

    with f4:
        st.markdown(
            '<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            'letter-spacing:0.07em;color:#6B7280;margin-bottom:4px;">Min Amount ($)</div>',
            unsafe_allow_html=True,
        )
        min_amount = st.number_input(
            "min_amount",
            min_value=0.0, max_value=9999.0, value=0.0, step=10.0,
            label_visibility="collapsed",
            key="tx_min_amount",
        )

    st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)

    search_term = st.text_input(
        "search_bar",
        placeholder="🔍  Search by Transaction ID, city, or state...",
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

    m_style = (
        "background:#F8F9FA;border:1px solid #E9ECEF;border-radius:8px;"
        "padding:0.65rem 1rem;text-align:center;"
    )
    lbl_style = (
        "font-size:0.65rem;font-weight:700;text-transform:uppercase;"
        "letter-spacing:0.07em;color:#6B7280;"
    )

    m1, m2, m3, m4 = st.columns(4, gap="small")
    with m1:
        st.markdown(
            f'<div style="{m_style}"><div style="{lbl_style}">Showing</div>'
            f'<div style="font-size:1.1rem;font-weight:800;color:#1A1A2E;">{total_shown:,}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div style="{m_style}"><div style="{lbl_style}">Fraud Events</div>'
            f'<div style="font-size:1.1rem;font-weight:800;color:#DC2626;">{fraud_shown:,}</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div style="{m_style}"><div style="{lbl_style}">Fraud Rate</div>'
            f'<div style="font-size:1.1rem;font-weight:800;color:#1A1A2E;">{fraud_pct:.2f}%</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f'<div style="{m_style}"><div style="{lbl_style}">Total Volume</div>'
            f'<div style="font-size:1.1rem;font-weight:800;color:#1A1A2E;">${total_vol:,.0f}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Prepare display dataframe (display copy)
    display_cols = [
        "transaction_id", "timestamp", "amount", "merchant_category",
        "transaction_channel", "card_type", "city", "state",
        "age_group", "is_fraud", "fraud_type",
    ]
    display_df = filtered[display_cols].copy()
    display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    display_df["amount"] = display_df["amount"].apply(lambda x: f"${x:,.2f}")
    display_df["is_fraud"] = display_df["is_fraud"].map({0: "Legitimate", 1: "FRAUD"})
    display_df["fraud_type"] = display_df["fraud_type"].fillna("—")
    display_df.columns = [
        "Transaction ID", "Timestamp", "Amount", "Category",
        "Channel", "Card Type", "City", "State",
        "Age Group", "Status", "Fraud Type",
    ]

    st.dataframe(
        display_df.head(500),
        use_container_width=True,
        height=420,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Status", help="FRAUD or Legitimate"),
            "Amount": st.column_config.TextColumn("Amount"),
        },
    )

    if total_shown > 500:
        st.markdown(
            f'<div style="font-size:0.75rem;color:#9CA3AF;text-align:center;margin-top:0.4rem;">'
            f'Showing top 500 of {total_shown:,} filtered results</div>',
            unsafe_allow_html=True,
        )

    # ── Export (CSV built from raw filtered data, timestamp formatted for export)
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    csv_export = filtered[display_cols].copy()
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
            f'<div style="font-size:0.75rem;color:#9CA3AF;padding-top:0.75rem;">'
            f'Exports all {total_shown:,} filtered rows</div>',
            unsafe_allow_html=True,
        )
