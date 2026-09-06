"""Shared Plotly chart builders for the hospital dashboard."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# ─── Colour palette ───────────────────────────────────────────────────────────
COLORS = {
    "critical":    "#ef4444",
    "high":        "#f59e0b",
    "normal":      "#22c55e",
    "icu":         "#6366f1",
    "equipment":   "#0ea5e9",
    "bg":          "#0f172a",
    "surface":     "#1e293b",
    "text":        "#f1f5f9",
    "grid":        "#334155",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text"], family="Inter, sans-serif"),
    xaxis=dict(gridcolor=COLORS["grid"], linecolor=COLORS["grid"]),
    yaxis=dict(gridcolor=COLORS["grid"], linecolor=COLORS["grid"]),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def _apply_layout(fig, **extra):
    layout = {**PLOTLY_LAYOUT, **extra}
    fig.update_layout(**layout)
    return fig


# ─── Bed Occupancy Bar Chart ──────────────────────────────────────────────────

def bed_occupancy_bar(df: pd.DataFrame) -> go.Figure:
    colors = df["Occupancy (%)"].apply(
        lambda p: COLORS["critical"] if p >= 90 else (COLORS["high"] if p >= 75 else COLORS["normal"])
    ).tolist()

    fig = go.Figure(go.Bar(
        x=df["Department"],
        y=df["Occupancy (%)"],
        marker_color=colors,
        text=df["Occupancy (%)"].apply(lambda v: f"{v}%"),
        textposition="outside",
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Occupancy: %{y}%<br>"
            "<extra></extra>"
        ),
    ))
    fig.add_hline(y=90, line_dash="dot", line_color=COLORS["critical"],
                  annotation_text="Critical (90%)", annotation_font_color=COLORS["critical"])
    fig.add_hline(y=75, line_dash="dot", line_color=COLORS["high"],
                  annotation_text="High (75%)", annotation_font_color=COLORS["high"])
    fig.update_yaxes(range=[0, 105])
    return _apply_layout(fig, title="Bed Occupancy by Department (%)")


# ─── Bed Stacked Bar (Occupied / Reserved / Available) ────────────────────────

def bed_stacked_bar(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for col, color in [
        ("Occupied",  COLORS["critical"]),
        ("Reserved",  COLORS["high"]),
        ("Available", COLORS["normal"]),
    ]:
        fig.add_trace(go.Bar(
            name=col,
            x=df["Department"],
            y=df[col],
            marker_color=color,
        ))
    fig.update_layout(barmode="stack")
    return _apply_layout(fig, title="Bed Distribution by Department",
                         legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                                     yanchor="bottom", y=1.02, xanchor="right", x=1))


# ─── ICU Gauge ────────────────────────────────────────────────────────────────

def icu_gauge(pct: float, branch: str) -> go.Figure:
    color = (COLORS["critical"] if pct >= 90 else
             COLORS["high"]     if pct >= 75 else
             COLORS["normal"])
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct,
        delta={"reference": 75, "increasing": {"color": COLORS["critical"]}},
        title={"text": f"ICU Occupancy — {branch}", "font": {"color": COLORS["text"]}},
        gauge={
            "axis":  {"range": [0, 100], "tickcolor": COLORS["text"]},
            "bar":   {"color": color},
            "bgcolor": COLORS["surface"],
            "bordercolor": COLORS["grid"],
            "steps": [
                {"range": [0,  75], "color": "rgba(34,197,94,0.15)"},
                {"range": [75, 90], "color": "rgba(245,158,11,0.15)"},
                {"range": [90,100], "color": "rgba(239,68,68,0.15)"},
            ],
            "threshold": {"line": {"color": COLORS["critical"], "width": 3}, "value": 90},
        },
        number={"suffix": "%", "font": {"color": COLORS["text"]}},
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color=COLORS["text"]),
                      margin=dict(l=20, r=20, t=60, b=20),
                      height=250)
    return fig


# ─── Equipment Pie ────────────────────────────────────────────────────────────

def equipment_pie(df: pd.DataFrame) -> go.Figure:
    counts = df["Status"].value_counts().reset_index()
    counts.columns = ["Status", "Count"]
    color_map = {
        "Operational":       COLORS["normal"],
        "In Use":            COLORS["equipment"],
        "Under Maintenance": COLORS["high"],
        "Offline":           COLORS["critical"],
    }
    colors = [color_map.get(s, "#94a3b8") for s in counts["Status"]]
    fig = go.Figure(go.Pie(
        labels=counts["Status"],
        values=counts["Count"],
        hole=0.5,
        marker_colors=colors,
        textinfo="label+percent",
        textfont_color=COLORS["text"],
    ))
    return _apply_layout(fig, title="Equipment Status Distribution",
                         margin=dict(l=10, r=10, t=50, b=10))


# ─── Hourly Trend Line ────────────────────────────────────────────────────────

def hourly_trend_line(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    branch_colors = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444"]
    for i, col in enumerate([c for c in df.columns if c != "Hour"]):
        fig.add_trace(go.Scatter(
            x=df["Hour"],
            y=df[col],
            name=col,
            mode="lines+markers",
            line=dict(color=branch_colors[i % len(branch_colors)], width=2),
            marker=dict(size=4),
        ))
    fig.add_hline(y=90, line_dash="dot", line_color=COLORS["critical"],
                  annotation_text="Critical", annotation_font_color=COLORS["critical"])
    fig.add_hline(y=75, line_dash="dot", line_color=COLORS["high"],
                  annotation_text="High", annotation_font_color=COLORS["high"])
    return _apply_layout(fig, title="24-Hour Bed Occupancy Trend (%)",
                         yaxis=dict(range=[0, 105], gridcolor=COLORS["grid"]),
                         xaxis=dict(tickangle=-45, gridcolor=COLORS["grid"]),
                         legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                                     yanchor="bottom", y=1.02))


# ─── Equipment Heatmap (Branch × Equipment type) ─────────────────────────────

def equipment_heatmap(df: pd.DataFrame) -> go.Figure:
    # Count "Offline" + "Under Maintenance" per branch × equipment
    concern = df[df["Status"].isin(["Offline", "Under Maintenance"])]
    pivot = (concern.groupby(["Branch", "Equipment"])
                    .size()
                    .unstack(fill_value=0))
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, "#1e293b"], [0.5, COLORS["high"]], [1, COLORS["critical"]]],
        hoverongaps=False,
        text=pivot.values,
        texttemplate="%{text}",
        showscale=True,
        colorbar=dict(tickfont=dict(color=COLORS["text"])),
    ))
    return _apply_layout(fig, title="Equipment Issues Heatmap (Offline + Maintenance)",
                         xaxis=dict(tickangle=-35, gridcolor=COLORS["grid"]),
                         yaxis=dict(gridcolor=COLORS["grid"]),
                         margin=dict(l=10, r=10, t=50, b=80))


# ─── ICU Bar Comparison ───────────────────────────────────────────────────────

def icu_comparison_bar(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Occupied", x=df["Branch"],
                         y=df["ICU Occupied"], marker_color=COLORS["critical"]))
    fig.add_trace(go.Bar(name="Available", x=df["Branch"],
                         y=df["ICU Available"], marker_color=COLORS["normal"]))
    fig.add_trace(go.Bar(name="Ventilated", x=df["Branch"],
                         y=df["Ventilated"], marker_color=COLORS["icu"]))
    fig.update_layout(barmode="group")
    return _apply_layout(fig, title="ICU Beds — Occupied vs Available vs Ventilated",
                         legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                                     yanchor="bottom", y=1.02, xanchor="right", x=1))
