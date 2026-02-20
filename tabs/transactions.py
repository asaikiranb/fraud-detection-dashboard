import streamlit as st
import pandas as pd
from components.styles import COLORS


def render_transactions(df: pd.DataFrame, stats: dict):
    """Render the Transaction Explorer tab."""

    # ── Page Header
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Transaction Explorer</div>
        <div class="page-subtitle">Drill into individual transactions. Filter, search, and export raw data.</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filter Controls
    with st.container():
        f1, f2, f3, f4 = st.columns(4, gap="small")

        with f1:
            st.markdown('<div class="sidebar-filter-label">Show</div>', unsafe_allow_html=True)
            fraud_filter = st.selectbox(
                "Transaction type",
                ["All Transactions", "Fraud Only", "Legitimate Only"],
                label_visibility="collapsed",
            )

        with f2:
            st.markdown('<div class="sidebar-filter-label">Category</div>', unsafe_allow_html=True)
            categories = ["All"] + sorted(df["merchant_category"].unique().tolist())
            cat_filter = st.selectbox("Category", categories, label_visibility="collapsed")

        with f3:
            st.markdown('<div class="sidebar-filter-label">Channel</div>', unsafe_allow_html=True)
            channels = ["All"] + sorted(df["transaction_channel"].unique().tolist())
            ch_filter = st.selectbox("Channel", channels, label_visibility="collapsed")

        with f4:
            st.markdown('<div class="sidebar-filter-label">Min Amount ($)</div>', unsafe_allow_html=True)
            min_amount = st.number_input(
                "Min amount", min_value=0.0, max_value=9999.0, value=0.0,
                step=10.0, label_visibility="collapsed"
            )

    st.markdown("<div style='margin-top:0.75rem'></div>", unsafe_allow_html=True)

    # ── Text search
    search_col, export_col = st.columns([3, 1], gap="small")
    with search_col:
        search_term = st.text_input(
            "Search",
            placeholder="Search by Transaction ID, city, state...",
            label_visibility="collapsed",
        )
    with export_col:
        pass  # placeholder for layout

    # ── Apply Filters
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
            filtered["transaction_id"].str.contains(search_term, case=False, na=False) |
            filtered["city"].str.contains(search_term, case=False, na=False) |
            filtered["state"].str.contains(search_term, case=False, na=False) |
            filtered["state_name"].str.contains(search_term, case=False, na=False)
        )
        filtered = filtered[mask]

    # ── Summary bar above table
    total_shown = len(filtered)
    fraud_shown = filtered["is_fraud"].sum()
    total_amount_shown = filtered["amount"].sum()

    m1, m2, m3, m4 = st.columns(4, gap="small")
    metric_style = (
        "background:#F8F9FA;border:1px solid #E9ECEF;border-radius:8px;"
        "padding:0.65rem 1rem;text-align:center;"
    )
    with m1:
        st.markdown(
            f'<div style="{metric_style}">'
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.07em;color:#6B7280">Showing</div>'
            f'<div style="font-size:1.1rem;font-weight:800;color:#1A1A2E">{total_shown:,}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f'<div style="{metric_style}">'
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.07em;color:#6B7280">Fraud Events</div>'
            f'<div style="font-size:1.1rem;font-weight:800;color:#DC2626">{fraud_shown:,}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m3:
        fraud_pct = fraud_shown / total_shown * 100 if total_shown > 0 else 0
        st.markdown(
            f'<div style="{metric_style}">'
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.07em;color:#6B7280">Fraud Rate</div>'
            f'<div style="font-size:1.1rem;font-weight:800;color:#1A1A2E">{fraud_pct:.2f}%</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f'<div style="{metric_style}">'
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.07em;color:#6B7280">Total Volume</div>'
            f'<div style="font-size:1.1rem;font-weight:800;color:#1A1A2E">${total_amount_shown:,.0f}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    # ── Display table
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
        "Age Group", "Status", "Fraud Type"
    ]

    st.dataframe(
        display_df.head(500),
        use_container_width=True,
        height=420,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn(
                "Status",
                help="FRAUD or Legitimate",
            ),
            "Amount": st.column_config.TextColumn("Amount"),
        }
    )

    if total_shown > 500:
        st.markdown(
            f'<div style="font-size:0.75rem;color:#9CA3AF;text-align:center;margin-top:0.5rem;">'
            f'Showing top 500 of {total_shown:,} filtered results</div>',
            unsafe_allow_html=True
        )

    # ── Export button
    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)
    csv_data = filtered[display_cols].copy()
    csv_data["timestamp"] = csv_data["timestamp"].astype(str)

    csv_bytes = csv_data.to_csv(index=False).encode("utf-8")

    col_exp, col_info = st.columns([1, 3])
    with col_exp:
        st.download_button(
            label="Export to CSV",
            data=csv_bytes,
            file_name="fraud_transactions_export.csv",
            mime="text/csv",
        )
    with col_info:
        st.markdown(
            f'<div style="font-size:0.75rem;color:#9CA3AF;padding-top:0.75rem;">'
            f'Exports {total_shown:,} filtered rows as CSV</div>',
            unsafe_allow_html=True
        )
