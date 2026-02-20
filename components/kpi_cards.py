import streamlit as st
from components.styles import COLORS

# Inline style constants (avoids reliance on injected CSS classes)
_CARD = (
    "background:#FFFFFF;border:1px solid #E9ECEF;border-radius:14px;"
    "padding:1.5rem 1.75rem;"
    "box-shadow:0 1px 3px rgba(0,0,0,0.04),0 1px 2px rgba(0,0,0,0.03);"
    "min-height:130px;"
)
_LABEL = (
    "color:#6B7280;font-size:0.72rem;font-weight:700;text-transform:uppercase;"
    "letter-spacing:0.08em;margin-bottom:0.5rem;"
)
_VALUE = (
    "color:#1A1A2E;font-size:2.2rem;font-weight:800;line-height:1.1;margin-bottom:0.4rem;"
)
_DELTA_NEG = "color:#DC2626;font-size:0.78rem;font-weight:600;margin-bottom:0.25rem;"
_DELTA_POS = "color:#059669;font-size:0.78rem;font-weight:600;margin-bottom:0.25rem;"
_DELTA_NEUTRAL = "color:#6B7280;font-size:0.78rem;font-weight:600;margin-bottom:0.25rem;"
_SUB = "color:#9CA3AF;font-size:0.72rem;margin-top:0.15rem;"


def render_kpi_card(label: str, value: str, delta: str = None,
                    delta_positive: bool = None, sub: str = None,
                    accent_color: str = None):
    """Render a single KPI card with fully inline styles."""
    border_top = f"border-top:3px solid {accent_color};" if accent_color else ""

    if delta:
        if delta_positive is True:
            delta_style = _DELTA_POS
        elif delta_positive is False:
            delta_style = _DELTA_NEG
        else:
            delta_style = _DELTA_NEUTRAL
        delta_html = f'<div style="{delta_style}">{delta}</div>'
    else:
        delta_html = ""

    sub_html = f'<div style="{_SUB}">{sub}</div>' if sub else ""

    st.markdown(
        f'<div style="{_CARD}{border_top}">'
        f'<div style="{_LABEL}">{label}</div>'
        f'<div style="{_VALUE}">{value}</div>'
        f'{delta_html}'
        f'{sub_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_executive_kpis(stats: dict):
    """Render the 4-column executive KPI row."""
    col1, col2, col3, col4 = st.columns(4, gap="small")

    with col1:
        render_kpi_card(
            label="Total Transactions",
            value=f"{stats['total_transactions']:,}",
            sub="Full year 2023",
            accent_color=COLORS["text_primary"],
        )

    with col2:
        render_kpi_card(
            label="Fraud Rate",
            value=f"{stats['fraud_rate']:.2f}%",
            delta=f"↑ {stats['fraud_count']:,} flagged events",
            delta_positive=False,
            sub="vs 1.2% industry avg",
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
            delta=f"vs ${stats['total_amount'] / stats['total_transactions']:,.0f} all-tx avg",
            delta_positive=False,
            sub="Per fraudulent event",
            accent_color=COLORS["chart_2"],
        )

    st.markdown("<div style='margin-top:0.25rem'></div>", unsafe_allow_html=True)


def render_mini_kpi_row(items: list):
    """Render a row of small metric pills."""
    cols = st.columns(len(items), gap="small")
    for col, item in zip(cols, items):
        color = item.get("color", COLORS["text_primary"])
        with col:
            st.markdown(
                f'<div style="background:#F8F9FA;border:1px solid #E9ECEF;'
                f'border-radius:12px;padding:1.1rem 1.25rem;">'
                f'<div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:0.07em;color:#6B7280;margin-bottom:0.4rem;">{item["label"]}</div>'
                f'<div style="font-size:1.5rem;font-weight:800;color:{color};line-height:1.1;">'
                f'{item["value"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
