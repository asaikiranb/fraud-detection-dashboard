import streamlit as st

# Design tokens
COLORS = {
    "white": "#FFFFFF",
    "surface": "#F8F9FA",
    "border": "#E9ECEF",
    "border_light": "#F1F3F5",
    "text_primary": "#1A1A2E",
    "text_secondary": "#6B7280",
    "text_muted": "#9CA3AF",
    "fraud_red": "#DC2626",
    "fraud_red_light": "#FEF2F2",
    "fraud_red_mid": "#FECACA",
    "safe_green": "#059669",
    "safe_green_light": "#ECFDF5",
    "accent_blue": "#1D4ED8",
    "accent_blue_light": "#EFF6FF",
    "warning_amber": "#D97706",
    "warning_amber_light": "#FFFBEB",
    "chart_1": "#1A1A2E",
    "chart_2": "#374151",
    "chart_3": "#6B7280",
    "chart_4": "#9CA3AF",
    "chart_5": "#D1D5DB",
}

CHART_COLORSCALE = [
    [0.0, "#F8F9FA"],
    [0.25, "#D1D5DB"],
    [0.5, "#6B7280"],
    [0.75, "#374151"],
    [1.0, "#1A1A2E"],
]

FRAUD_COLORSCALE = [
    [0.0, "#ECFDF5"],
    [0.3, "#A7F3D0"],
    [0.6, "#FEF3C7"],
    [0.85, "#FECACA"],
    [1.0, "#DC2626"],
]


def inject_css():
    """Inject custom CSS for the entire dashboard."""
    st.markdown(f"""
    <style>
        /* ─── Reset & Base ─── */
        .stApp {{
            background-color: {COLORS['white']};
        }}

        /* ─── Hide Streamlit Branding ─── */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        /* ─── Main Container ─── */
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            padding-left: 3rem;
            padding-right: 3rem;
            max-width: 1600px;
        }}

        /* ─── Sidebar ─── */
        [data-testid="stSidebar"] {{
            background-color: {COLORS['white']};
            border-right: 1px solid {COLORS['border']};
        }}

        [data-testid="stSidebar"] .block-container {{
            padding: 1.5rem 1rem;
        }}

        /* ─── Tabs ─── */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0px;
            background-color: transparent;
            border-bottom: 2px solid {COLORS['border']};
            padding-bottom: 0;
        }}

        .stTabs [data-baseweb="tab"] {{
            height: 48px;
            background-color: transparent;
            border-radius: 0;
            border: none;
            border-bottom: 2px solid transparent;
            margin-bottom: -2px;
            padding: 0 24px;
            color: {COLORS['text_secondary']};
            font-weight: 500;
            font-size: 0.925rem;
            letter-spacing: 0.01em;
            transition: all 0.15s ease;
        }}

        .stTabs [data-baseweb="tab"]:hover {{
            color: {COLORS['text_primary']};
            background-color: {COLORS['surface']};
        }}

        .stTabs [aria-selected="true"] {{
            color: {COLORS['text_primary']} !important;
            border-bottom: 2px solid {COLORS['text_primary']} !important;
            font-weight: 600 !important;
            background-color: transparent !important;
        }}

        .stTabs [data-baseweb="tab-panel"] {{
            padding-top: 2rem;
        }}

        /* ─── Metrics ─── */
        [data-testid="stMetric"] {{
            background: {COLORS['white']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03);
        }}

        [data-testid="stMetric"] label {{
            color: {COLORS['text_secondary']};
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}

        [data-testid="stMetricValue"] {{
            color: {COLORS['text_primary']};
            font-size: 1.875rem;
            font-weight: 700;
            line-height: 1.2;
        }}

        [data-testid="stMetricDelta"] {{
            font-size: 0.75rem;
            font-weight: 500;
        }}

        /* ─── Selectbox & Date Inputs ─── */
        .stSelectbox > div > div,
        .stDateInput > div > div {{
            border: 1px solid {COLORS['border']} !important;
            border-radius: 8px !important;
            background-color: {COLORS['white']} !important;
            box-shadow: none !important;
            min-height: 38px;
        }}

        .stSelectbox > div > div:focus-within,
        .stDateInput > div > div:focus-within {{
            border-color: {COLORS['text_primary']} !important;
            box-shadow: 0 0 0 2px rgba(26,26,46,0.08) !important;
        }}

        /* Selectbox dropdown option text */
        .stSelectbox [data-testid="stSelectboxVirtualDropdown"] {{
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        }}

        /* ─── Multiselect (kept for Transaction Explorer tab) ─── */
        .stMultiSelect > div > div {{
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            background-color: {COLORS['white']};
        }}

        /* ─── Buttons ─── */
        .stButton > button {{
            background-color: {COLORS['text_primary']};
            color: {COLORS['white']};
            border: none;
            border-radius: 8px;
            font-weight: 500;
            font-size: 0.875rem;
            padding: 0.5rem 1.25rem;
            transition: all 0.15s ease;
        }}

        .stButton > button:hover {{
            background-color: #2D2D4A;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        /* ─── Dataframe / Table ─── */
        [data-testid="stDataFrame"] {{
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            overflow: hidden;
        }}

        /* ─── Divider ─── */
        hr {{
            border: none;
            border-top: 1px solid {COLORS['border']};
            margin: 1rem 0;
        }}

        /* ─── Custom KPI Card ─── */
        .kpi-card {{
            background: {COLORS['white']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            height: 100%;
        }}

        .kpi-card .kpi-label {{
            color: {COLORS['text_secondary']};
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.5rem;
        }}

        .kpi-card .kpi-value {{
            color: {COLORS['text_primary']};
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 0.5rem;
        }}

        .kpi-card .kpi-delta {{
            font-size: 0.75rem;
            font-weight: 600;
        }}

        .kpi-card .kpi-delta.positive {{
            color: {COLORS['safe_green']};
        }}

        .kpi-card .kpi-delta.negative {{
            color: {COLORS['fraud_red']};
        }}

        .kpi-card .kpi-sub {{
            color: {COLORS['text_muted']};
            font-size: 0.7rem;
            margin-top: 0.25rem;
        }}

        /* ─── Section Headers ─── */
        .section-header {{
            color: {COLORS['text_primary']};
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid {COLORS['border']};
        }}

        /* ─── Alert Badge ─── */
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.03em;
        }}

        .badge-fraud {{
            background: {COLORS['fraud_red_light']};
            color: {COLORS['fraud_red']};
        }}

        .badge-safe {{
            background: {COLORS['safe_green_light']};
            color: {COLORS['safe_green']};
        }}

        /* ─── Chart Containers ─── */
        .chart-container {{
            background: {COLORS['white']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.25rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}

        .chart-title {{
            color: {COLORS['text_primary']};
            font-size: 0.875rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}

        .chart-subtitle {{
            color: {COLORS['text_muted']};
            font-size: 0.75rem;
            margin-bottom: 1rem;
        }}

        /* ─── Sidebar Logo / Title ─── */
        .sidebar-brand {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0 0 1.5rem 0;
            border-bottom: 1px solid {COLORS['border']};
            margin-bottom: 1.5rem;
        }}

        .sidebar-brand .brand-icon {{
            width: 36px;
            height: 36px;
            background: {COLORS['text_primary']};
            border-radius: 9px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }}

        .sidebar-brand .brand-name {{
            font-size: 0.9rem;
            font-weight: 800;
            color: {COLORS['text_primary']};
            letter-spacing: -0.02em;
        }}

        .sidebar-brand .brand-sub {{
            font-size: 0.65rem;
            color: {COLORS['text_muted']};
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        /* ─── Sidebar Filter Labels ─── */
        .sidebar-filter-label {{
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            color: {COLORS['text_secondary']};
            margin-bottom: 0.35rem;
        }}

        /* ─── Page Header ─── */
        .page-header {{
            margin-bottom: 1.75rem;
        }}

        .page-header .page-title {{
            font-size: 1.5rem;
            font-weight: 800;
            color: {COLORS['text_primary']};
            letter-spacing: -0.03em;
            margin-bottom: 0.25rem;
        }}

        .page-header .page-subtitle {{
            font-size: 0.875rem;
            color: {COLORS['text_secondary']};
        }}

        /* ─── Insight Box ─── */
        .insight-box {{
            background: {COLORS['surface']};
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            padding: 1rem 1.25rem;
            margin-top: 1rem;
        }}

        .insight-box .insight-title {{
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {COLORS['text_secondary']};
            margin-bottom: 0.5rem;
        }}

        .insight-box .insight-item {{
            font-size: 0.825rem;
            color: {COLORS['text_primary']};
            margin-bottom: 0.3rem;
            display: flex;
            align-items: flex-start;
            gap: 0.5rem;
        }}

        .insight-box .insight-item::before {{
            content: "–";
            color: {COLORS['text_muted']};
            flex-shrink: 0;
        }}

        /* ─── Last Updated ─── */
        .last-updated {{
            font-size: 0.7rem;
            color: {COLORS['text_muted']};
            text-align: right;
            padding-top: 0.5rem;
        }}
    </style>
    """, unsafe_allow_html=True)


def plotly_layout_defaults():
    """Return base layout dict for all Plotly figures."""
    return dict(
        font=dict(family="Inter, -apple-system, sans-serif", color=COLORS["text_primary"]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=30, b=0),
        colorway=[
            COLORS["chart_1"], COLORS["chart_2"], COLORS["chart_3"],
            COLORS["chart_4"], COLORS["chart_5"]
        ],
        xaxis=dict(
            showgrid=True,
            gridcolor=COLORS["border"],
            gridwidth=1,
            zeroline=False,
            linecolor=COLORS["border"],
            tickfont=dict(size=11, color=COLORS["text_secondary"]),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS["border"],
            gridwidth=1,
            zeroline=False,
            linecolor=COLORS["border"],
            tickfont=dict(size=11, color=COLORS["text_secondary"]),
        ),
        hoverlabel=dict(
            bgcolor=COLORS["white"],
            bordercolor=COLORS["border"],
            font=dict(color=COLORS["text_primary"], size=12),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=12, color=COLORS["text_secondary"]),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
