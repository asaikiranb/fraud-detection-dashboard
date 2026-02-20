import streamlit as st
from components.styles import COLORS


def render_kpi_card(label: str, value: str, delta: str = None,
                    delta_positive: bool = None, sub: str = None,
                    accent_color: str = None):
    """Render a single custom KPI card with HTML."""
    delta_html = ""
    if delta:
        delta_class = ""
        if delta_positive is True:
            delta_class = "positive"
        elif delta_positive is False:
            delta_class = "negative"
        delta_html = f'<div class="kpi-delta {delta_class}">{delta}</div>'

    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""

    border_style = ""
    if accent_color:
        border_style = f"border-top: 3px solid {accent_color};"

    st.markdown(f"""
    <div class="kpi-card" style="{border_style}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


def render_executive_kpis(stats: dict):
    """Render the 4-column executive KPI row."""
    col1, col2, col3, col4 = st.columns(4, gap="small")

    with col1:
        render_kpi_card(
            label="Total Transactions",
            value=f"{stats['total_transactions']:,}",
            delta=None,
            sub="Full year 2023",
            accent_color=COLORS["text_primary"],
        )

    with col2:
        render_kpi_card(
            label="Fraud Rate",
            value=f"{stats['fraud_rate']:.2f}%",
            delta=f"↑ {stats['fraud_count']:,} flagged transactions",
            delta_positive=False,
            sub="vs 1.2% industry average",
            accent_color=COLORS["fraud_red"],
        )

    with col3:
        render_kpi_card(
            label="Total Fraud Amount",
            value=f"${stats['fraud_amount']:,.0f}",
            delta=f"{stats['fraud_amount'] / stats['total_amount'] * 100:.1f}% of total volume",
            delta_positive=False,
            sub="Estimated loss exposure",
            accent_color=COLORS["warning_amber"],
        )

    with col4:
        render_kpi_card(
            label="Avg Fraud Transaction",
            value=f"${stats['avg_fraud_amount']:,.0f}",
            delta=f"vs ${stats['total_amount'] / stats['total_transactions']:,.0f} avg all tx",
            delta_positive=False,
            sub="Per fraudulent event",
            accent_color=COLORS["chart_2"],
        )

    st.markdown("<div style='margin-top: 0.25rem'></div>", unsafe_allow_html=True)


def render_mini_kpi_row(items: list):
    """
    Render a row of small metric indicators.
    items: list of dicts with keys: label, value, color (optional)
    """
    cols = st.columns(len(items), gap="small")
    for col, item in zip(cols, items):
        with col:
            color = item.get("color", COLORS["text_primary"])
            st.markdown(f"""
            <div style="background:{COLORS['surface']};border:1px solid {COLORS['border']};
                        border-radius:10px;padding:0.9rem 1rem;">
                <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                            letter-spacing:0.07em;color:{COLORS['text_secondary']};
                            margin-bottom:0.3rem;">{item['label']}</div>
                <div style="font-size:1.35rem;font-weight:800;color:{color};
                            line-height:1.1;">{item['value']}</div>
            </div>
            """, unsafe_allow_html=True)
