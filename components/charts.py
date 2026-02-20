import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from components.styles import COLORS, CHART_COLORSCALE, FRAUD_COLORSCALE, plotly_layout_defaults


def _apply_layout(fig, title: str = None, height: int = None):
    """Apply standard layout defaults to a figure."""
    defaults = plotly_layout_defaults()
    if title:
        defaults["title"] = dict(
            text=title,
            font=dict(size=14, weight=700, color=COLORS["text_primary"]),
            x=0,
            xanchor="left",
            pad=dict(b=8),
        )
    if height:
        defaults["height"] = height
    fig.update_layout(**defaults)
    return fig


# ─── Overview Charts ──────────────────────────────────────────────────────────

def fraud_donut(df: pd.DataFrame) -> go.Figure:
    """Fraud vs Legitimate donut chart."""
    fraud_count = df["is_fraud"].sum()
    legit_count = len(df) - fraud_count

    fig = go.Figure(go.Pie(
        labels=["Legitimate", "Fraudulent"],
        values=[legit_count, fraud_count],
        hole=0.72,
        marker=dict(
            colors=[COLORS["safe_green"], COLORS["fraud_red"]],
            line=dict(color=COLORS["white"], width=3),
        ),
        textinfo="percent",
        textfont=dict(size=13, color=COLORS["text_primary"]),
        hovertemplate="<b>%{label}</b><br>%{value:,} transactions<br>%{percent}<extra></extra>",
    ))

    fraud_rate = fraud_count / len(df) * 100
    fig.add_annotation(
        text=f"<b>{fraud_rate:.2f}%</b><br><span style='font-size:11px'>Fraud Rate</span>",
        x=0.5, y=0.5,
        font=dict(size=22, color=COLORS["text_primary"]),
        showarrow=False,
        xanchor="center",
        yanchor="middle",
    )

    fig = _apply_layout(fig, height=280)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=12),
        ),
        margin=dict(l=0, r=0, t=10, b=30),
    )
    return fig


def fraud_by_category_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart: fraud count and rate by merchant category."""
    cat_data = df.groupby("merchant_category").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
    ).reset_index()
    cat_data["rate"] = cat_data["fraud"] / cat_data["total"] * 100
    cat_data = cat_data.sort_values("fraud", ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=cat_data["merchant_category"],
        x=cat_data["fraud"],
        orientation="h",
        name="Fraud Count",
        marker=dict(
            color=cat_data["rate"],
            colorscale=[[0, COLORS["border"]], [0.5, COLORS["chart_3"]], [1, COLORS["fraud_red"]]],
            line=dict(width=0),
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Fraud Transactions: %{x:,}<br>"
            "Fraud Rate: %{customdata:.2f}%<extra></extra>"
        ),
        customdata=cat_data["rate"],
    ))

    fig = _apply_layout(fig, height=280)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title=None,
        yaxis_title=None,
    )
    return fig


def monthly_fraud_trend(df: pd.DataFrame) -> go.Figure:
    """Monthly fraud trend line with volume context."""
    monthly = df.groupby("month").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
        fraud_amount=("amount", lambda x: x[df.loc[x.index, "is_fraud"] == 1].sum()),
    ).reset_index()
    monthly["rate"] = monthly["fraud"] / monthly["total"] * 100
    monthly["month_label"] = pd.to_datetime(monthly["month"].astype(str), format="%m").dt.strftime("%b")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=monthly["month_label"],
            y=monthly["total"],
            name="Total Transactions",
            marker=dict(color=COLORS["border"], line=dict(width=0)),
            hovertemplate="<b>%{x}</b><br>Total: %{y:,}<extra></extra>",
            opacity=0.8,
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=monthly["month_label"],
            y=monthly["fraud"],
            name="Fraud Count",
            mode="lines+markers",
            line=dict(color=COLORS["fraud_red"], width=2.5),
            marker=dict(size=7, color=COLORS["fraud_red"],
                        line=dict(color=COLORS["white"], width=2)),
            hovertemplate="<b>%{x}</b><br>Fraud: %{y:,}<extra></extra>",
        ),
        secondary_y=True,
    )

    defaults = plotly_layout_defaults()
    fig.update_layout(**defaults)
    fig.update_layout(
        height=260,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    fig.update_yaxes(
        title_text=None,
        gridcolor=COLORS["border"],
        showgrid=True,
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text=None,
        showgrid=False,
        secondary_y=True,
    )
    return fig


# ─── Trend Charts ─────────────────────────────────────────────────────────────

def hourly_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap of fraud count by hour and day of week."""
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    heat_data = df[df["is_fraud"] == 1].groupby(
        ["day_of_week", "hour"]
    ).size().reset_index(name="count")

    pivot = heat_data.pivot_table(
        index="day_of_week", columns="hour", values="count", fill_value=0
    )
    pivot = pivot.reindex([d for d in day_order if d in pivot.index])
    pivot = pivot.reindex(columns=range(24), fill_value=0)

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"{h:02d}:00" for h in range(24)],
        y=list(pivot.index),
        colorscale=FRAUD_COLORSCALE,
        showscale=True,
        colorbar=dict(
            thickness=12,
            tickfont=dict(size=10, color=COLORS["text_secondary"]),
            outlinecolor=COLORS["border"],
            outlinewidth=1,
        ),
        hovertemplate="<b>%{y} %{x}</b><br>Fraud: %{z:,}<extra></extra>",
    ))

    fig = _apply_layout(fig, height=260)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    fig.update_xaxes(tickangle=0, tickfont=dict(size=9))
    fig.update_yaxes(tickfont=dict(size=11))
    return fig


def day_of_week_bar(df: pd.DataFrame) -> go.Figure:
    """Fraud rate by day of week."""
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_short = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    dow = df.groupby("day_of_week").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
    ).reindex(day_order).reset_index()
    dow["rate"] = dow["fraud"] / dow["total"] * 100
    dow["day_short"] = day_short

    max_rate = dow["rate"].max()
    colors = [
        COLORS["fraud_red"] if r == max_rate else COLORS["chart_3"]
        for r in dow["rate"]
    ]

    fig = go.Figure(go.Bar(
        x=dow["day_short"],
        y=dow["rate"],
        marker=dict(color=colors, line=dict(width=0)),
        text=dow["rate"].apply(lambda x: f"{x:.2f}%"),
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text_secondary"]),
        hovertemplate="<b>%{x}</b><br>Fraud Rate: %{y:.3f}%<br>Fraud Count: %{customdata:,}<extra></extra>",
        customdata=dow["fraud"],
    ))

    fig = _apply_layout(fig, height=240)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), xaxis_title=None)
    fig.update_yaxes(title_text="Fraud Rate (%)", ticksuffix="%")
    return fig


def quarterly_comparison(df: pd.DataFrame) -> go.Figure:
    """Quarter-over-quarter fraud comparison."""
    qtr = df.groupby("quarter").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
        fraud_amount=("amount", lambda x: x[df.loc[x.index, "is_fraud"] == 1].sum()),
    ).reset_index()
    qtr["rate"] = qtr["fraud"] / qtr["total"] * 100
    qtr["quarter_label"] = qtr["quarter"].apply(lambda q: f"Q{q}")

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Fraud Count by Quarter", "Fraud Rate by Quarter"],
        horizontal_spacing=0.1,
    )

    fig.add_trace(
        go.Bar(
            x=qtr["quarter_label"],
            y=qtr["fraud"],
            marker=dict(
                color=[COLORS["chart_1"], COLORS["chart_2"], COLORS["chart_3"], COLORS["chart_4"]],
                line=dict(width=0),
            ),
            hovertemplate="<b>%{x}</b><br>Fraud: %{y:,}<extra></extra>",
            showlegend=False,
        ),
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=qtr["quarter_label"],
            y=qtr["rate"],
            mode="lines+markers",
            line=dict(color=COLORS["fraud_red"], width=2.5),
            marker=dict(size=9, color=COLORS["fraud_red"],
                        line=dict(color=COLORS["white"], width=2)),
            hovertemplate="<b>%{x}</b><br>Rate: %{y:.3f}%<extra></extra>",
            showlegend=False,
        ),
        row=1, col=2,
    )

    defaults = plotly_layout_defaults()
    fig.update_layout(**defaults)
    fig.update_layout(
        height=260,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    fig.update_annotations(font=dict(size=12, color=COLORS["text_secondary"]))
    for axis in ["xaxis", "xaxis2"]:
        fig.update_layout(**{axis: dict(showgrid=False)})
    return fig


def weekly_trend(df: pd.DataFrame) -> go.Figure:
    """Weekly fraud trend with rolling average."""
    weekly = df.groupby("week").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
    ).reset_index()
    weekly["rate"] = weekly["fraud"] / weekly["total"] * 100
    weekly["rolling_rate"] = weekly["rate"].rolling(4, min_periods=1).mean()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=weekly["week"],
        y=weekly["rate"],
        mode="lines",
        name="Weekly Rate",
        line=dict(color=COLORS["border"], width=1.5),
        hovertemplate="Week %{x}<br>Rate: %{y:.3f}%<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=weekly["week"],
        y=weekly["rolling_rate"],
        mode="lines",
        name="4-Week Avg",
        line=dict(color=COLORS["text_primary"], width=2.5),
        hovertemplate="Week %{x}<br>4W Avg: %{y:.3f}%<extra></extra>",
    ))

    fig = _apply_layout(fig, height=230)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
    fig.update_yaxes(title_text="Fraud Rate (%)", ticksuffix="%")
    fig.update_xaxes(title_text="Week of Year")
    return fig


# ─── Geography Charts ─────────────────────────────────────────────────────────

def us_choropleth(df: pd.DataFrame) -> go.Figure:
    """US choropleth map of fraud rate by state."""
    state_data = df.groupby("state").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
        fraud_amount=("amount", lambda x: x[df.loc[x.index, "is_fraud"] == 1].sum()),
    ).reset_index()
    state_data["rate"] = state_data["fraud"] / state_data["total"] * 100
    state_data["state_name"] = df.groupby("state")["state_name"].first().reindex(state_data["state"]).values

    fig = go.Figure(go.Choropleth(
        locations=state_data["state"],
        z=state_data["rate"],
        locationmode="USA-states",
        colorscale=FRAUD_COLORSCALE,
        colorbar=dict(
            title=dict(text="Fraud Rate %", font=dict(size=11)),
            thickness=14,
            tickfont=dict(size=10),
            ticksuffix="%",
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Fraud Rate: %{z:.2f}%<br>"
            "Fraud Count: %{customdata[1]:,}<br>"
            "Fraud Amount: $%{customdata[2]:,.0f}<extra></extra>"
        ),
        customdata=list(zip(
            state_data["state_name"],
            state_data["fraud"],
            state_data["fraud_amount"],
        )),
        marker=dict(line=dict(color=COLORS["white"], width=0.8)),
    ))

    fig.update_layout(
        geo=dict(
            scope="usa",
            showlakes=False,
            showland=True,
            landcolor=COLORS["surface"],
            bgcolor="rgba(0,0,0,0)",
            showframe=False,
            coastlinecolor=COLORS["border"],
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        height=360,
        font=dict(family="Inter, sans-serif", color=COLORS["text_primary"]),
        hoverlabel=dict(
            bgcolor=COLORS["white"],
            bordercolor=COLORS["border"],
            font=dict(color=COLORS["text_primary"], size=12),
        ),
    )
    return fig


def top_cities_bar(df: pd.DataFrame, n: int = 12) -> go.Figure:
    """Top N cities by fraud count."""
    city_data = df[df["is_fraud"] == 1].groupby(["city", "state"]).agg(
        fraud=("is_fraud", "count"),
    ).reset_index().sort_values("fraud", ascending=True).tail(n)
    city_data["label"] = city_data["city"] + ", " + city_data["state"]

    fig = go.Figure(go.Bar(
        y=city_data["label"],
        x=city_data["fraud"],
        orientation="h",
        marker=dict(
            color=COLORS["chart_2"],
            line=dict(width=0),
            opacity=0.85,
        ),
        text=city_data["fraud"].apply(lambda x: f"{x:,}"),
        textposition="outside",
        textfont=dict(size=11, color=COLORS["text_secondary"]),
        hovertemplate="<b>%{y}</b><br>Fraud Count: %{x:,}<extra></extra>",
    ))

    fig = _apply_layout(fig, height=360)
    fig.update_layout(margin=dict(l=0, r=30, t=10, b=0))
    fig.update_xaxes(title_text="Number of Fraud Events")
    fig.update_yaxes(title_text=None, tickfont=dict(size=11))
    return fig


# ─── Segment Charts ───────────────────────────────────────────────────────────

def age_group_chart(df: pd.DataFrame) -> go.Figure:
    """Fraud rate and count by age group."""
    age_order = ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
    age_data = df.groupby("age_group").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
    ).reindex(age_order).reset_index()
    age_data["rate"] = age_data["fraud"] / age_data["total"] * 100

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=age_data["age_group"],
        y=age_data["fraud"],
        name="Fraud Count",
        marker=dict(color=COLORS["chart_2"], line=dict(width=0)),
        hovertemplate="<b>%{x}</b><br>Fraud Count: %{y:,}<br>Rate: %{customdata:.2f}%<extra></extra>",
        customdata=age_data["rate"],
    ))

    fig.add_trace(go.Scatter(
        x=age_data["age_group"],
        y=age_data["rate"],
        name="Fraud Rate",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color=COLORS["fraud_red"], width=2),
        marker=dict(size=8, color=COLORS["fraud_red"], line=dict(color=COLORS["white"], width=2)),
        hovertemplate="<b>%{x}</b><br>Rate: %{y:.2f}%<extra></extra>",
    ))

    defaults = plotly_layout_defaults()
    fig.update_layout(**defaults)
    fig.update_layout(
        height=250,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis2=dict(
            overlaying="y",
            side="right",
            showgrid=False,
            ticksuffix="%",
            tickfont=dict(size=11, color=COLORS["fraud_red"]),
            zeroline=False,
        ),
        legend=dict(orientation="h", y=1.1, x=0, font=dict(size=11)),
    )
    return fig


def card_type_donut(df: pd.DataFrame) -> go.Figure:
    """Fraud distribution by card type."""
    card_fraud = df[df["is_fraud"] == 1].groupby("card_type").size().reset_index(name="count")

    colors = [COLORS["chart_1"], COLORS["chart_2"], COLORS["chart_3"], COLORS["chart_4"]]

    fig = go.Figure(go.Pie(
        labels=card_fraud["card_type"],
        values=card_fraud["count"],
        hole=0.6,
        marker=dict(colors=colors, line=dict(color=COLORS["white"], width=3)),
        textinfo="percent+label",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>Fraud Count: %{value:,}<br>%{percent}<extra></extra>",
    ))

    fig = _apply_layout(fig, height=250)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=10, b=0),
    )
    return fig


def channel_fraud_bar(df: pd.DataFrame) -> go.Figure:
    """Fraud rate by transaction channel."""
    ch_data = df.groupby("transaction_channel").agg(
        total=("is_fraud", "count"),
        fraud=("is_fraud", "sum"),
    ).reset_index()
    ch_data["rate"] = ch_data["fraud"] / ch_data["total"] * 100
    ch_data = ch_data.sort_values("rate", ascending=False)

    fig = go.Figure(go.Bar(
        x=ch_data["transaction_channel"],
        y=ch_data["rate"],
        marker=dict(
            color=[COLORS["fraud_red"], COLORS["chart_2"], COLORS["chart_3"], COLORS["chart_4"]],
            line=dict(width=0),
        ),
        text=ch_data["rate"].apply(lambda x: f"{x:.2f}%"),
        textposition="outside",
        textfont=dict(size=11),
        hovertemplate="<b>%{x}</b><br>Rate: %{y:.3f}%<br>Count: %{customdata:,}<extra></extra>",
        customdata=ch_data["fraud"],
    ))

    fig = _apply_layout(fig, height=250)
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0), xaxis_title=None)
    fig.update_yaxes(title_text="Fraud Rate (%)", ticksuffix="%")
    return fig


def fraud_type_breakdown(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar: fraud count by fraud type."""
    ft_data = df[df["is_fraud"] == 1].groupby("fraud_type").agg(
        count=("is_fraud", "count"),
        avg_amount=("amount", "mean"),
    ).reset_index().sort_values("count", ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=ft_data["fraud_type"],
        x=ft_data["count"],
        orientation="h",
        name="Fraud Count",
        marker=dict(color=COLORS["chart_1"], line=dict(width=0), opacity=0.85),
        hovertemplate=(
            "<b>%{y}</b><br>Count: %{x:,}<br>"
            "Avg Amount: $%{customdata:,.0f}<extra></extra>"
        ),
        customdata=ft_data["avg_amount"],
    ))

    fig = _apply_layout(fig, height=250)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    fig.update_xaxes(title_text="Number of Incidents")
    fig.update_yaxes(title_text=None)
    return fig


def amount_distribution(df: pd.DataFrame) -> go.Figure:
    """Overlapping histogram: transaction amount for fraud vs legitimate."""
    legit = df[df["is_fraud"] == 0]["amount"]
    fraud = df[df["is_fraud"] == 1]["amount"]

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=legit.clip(upper=1000),
        name="Legitimate",
        marker=dict(color=COLORS["border"], line=dict(width=0)),
        opacity=0.7,
        nbinsx=50,
        hovertemplate="$%{x:.0f} - %{y:,} transactions<extra>Legitimate</extra>",
    ))

    fig.add_trace(go.Histogram(
        x=fraud.clip(upper=1000),
        name="Fraudulent",
        marker=dict(color=COLORS["fraud_red"], line=dict(width=0)),
        opacity=0.7,
        nbinsx=50,
        hovertemplate="$%{x:.0f} - %{y:,} transactions<extra>Fraudulent</extra>",
    ))

    fig = _apply_layout(fig, height=250)
    fig.update_layout(
        barmode="overlay",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", y=1.05, font=dict(size=11)),
    )
    fig.update_xaxes(title_text="Transaction Amount (USD, capped at $1,000)", tickprefix="$")
    fig.update_yaxes(title_text="Count")
    return fig
