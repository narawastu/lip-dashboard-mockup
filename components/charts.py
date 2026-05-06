"""Themed Plotly chart factories. Every chart in the app routes through here for consistency."""

from __future__ import annotations

import itertools
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from copy import deepcopy

import theme as T

_chart_counter = itertools.count()


def show(fig: go.Figure, **kwargs) -> None:
    """Wrapper around st.plotly_chart that auto-generates a unique key."""
    kwargs.setdefault("width", "stretch")
    kwargs.setdefault("config", {"displayModeBar": False})
    if "key" not in kwargs:
        kwargs["key"] = f"chart_{next(_chart_counter)}"
    st.plotly_chart(fig, **kwargs)


def _apply(layout_overrides=None) -> dict:
    base = deepcopy(T.PLOTLY_LAYOUT)
    if layout_overrides:
        for k, v in layout_overrides.items():
            base[k] = v
    return base


def _config():
    return {"displayModeBar": False, "staticPlot": False}


def line_trend(df: pd.DataFrame, x: str, y: str, target: float | None = None,
               y_suffix: str = "", height: int = 260, color: str = T.NAVY,
               y_range: tuple | None = None) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y], mode="lines+markers",
        line=dict(color=color, width=3, shape="spline", smoothing=0.6),
        marker=dict(size=7, color=color, line=dict(color="white", width=2)),
        fill="tozeroy" if y_range is None else None,
        fillcolor=f"rgba(0,47,108,0.06)",
        hovertemplate=f"<b>%{{x}}</b><br>%{{y:.2f}}{y_suffix}<extra></extra>",
        name=y,
    ))
    if target is not None:
        fig.add_hline(y=target, line_dash="dash", line_color=T.GOLD, line_width=1.5,
                      annotation_text=f"Target {target}{y_suffix}",
                      annotation_position="top right",
                      annotation_font=dict(color=T.GOLD, size=11))
    layout = _apply()
    layout["height"] = height
    if y_range is not None:
        layout["yaxis"]["range"] = list(y_range)
    fig.update_layout(**layout)
    return fig


def sparkline(values: list, color: str = T.NAVY) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=list(range(len(values))), y=values, mode="lines",
        line=dict(color=color, width=2, shape="spline", smoothing=0.6),
        fill="tozeroy", fillcolor=f"rgba(0,47,108,0.08)",
        hoverinfo="skip",
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=44, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def donut(labels, values, height: int = 280, hole: float = 0.6,
          color_seq: list | None = None, center_text: str | None = None,
          center_sub: str | None = None) -> go.Figure:
    colors = color_seq or T.CAT_PALETTE
    total = sum(values) or 1
    # Show inside-label only when slice is large enough to fit text
    text_per_slice = [
        f"{v / total * 100:.1f}%" if v / total >= 0.06 else ""
        for v in values
    ]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=hole, sort=False,
        marker=dict(colors=colors[: len(labels)], line=dict(color="white", width=2)),
        text=text_per_slice,
        textinfo="text",
        textposition="inside",
        insidetextorientation="horizontal",
        textfont=dict(size=12, color="white", family="Inter"),
        hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>",
    ))
    annotations = []
    if center_text:
        annotations.append(dict(
            text=f"<b style='font-size:22px;color:{T.INK}'>{center_text}</b>"
                 + (f"<br><span style='font-size:11px;color:{T.MUTED}'>{center_sub}</span>" if center_sub else ""),
            x=0.5, y=0.5, showarrow=False,
        ))
    layout = _apply({
        "height": height,
        "showlegend": True,
        "legend": dict(
            orientation="h", y=-0.08, x=0.5, xanchor="center",
            font=dict(size=11, color=T.MUTED, family="Inter"),
            itemsizing="constant",
        ),
        "annotations": annotations,
        "margin": dict(l=8, r=8, t=8, b=24),
    })
    fig.update_layout(**layout)
    return fig


def hbar(labels, values, height: int = 320, color: str = T.NAVY,
         value_suffix: str = "", color_per_bar: list | None = None,
         x_range: tuple | None = None) -> go.Figure:
    sorted_idx = np.argsort(values)
    labels_s = [labels[i] for i in sorted_idx]
    values_s = [values[i] for i in sorted_idx]
    bar_colors = ([color_per_bar[i] for i in sorted_idx] if color_per_bar else color)
    fig = go.Figure(go.Bar(
        x=values_s, y=labels_s, orientation="h",
        marker=dict(color=bar_colors, line=dict(width=0)),
        text=[f"{v:.2f}{value_suffix}" if isinstance(v, float) and v < 100 else f"{v:,.0f}{value_suffix}"
              for v in values_s],
        textposition="outside",
        textfont=dict(size=11, color=T.INK, family="Inter"),
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>%{x:,.2f}" + value_suffix + "<extra></extra>",
    ))
    layout = _apply({"height": height,
                     "margin": dict(l=8, r=64, t=8, b=8)})
    layout["xaxis"]["showgrid"] = False
    layout["xaxis"]["showticklabels"] = False
    if x_range is not None:
        layout["xaxis"]["range"] = list(x_range)
    layout["yaxis"]["gridcolor"] = "rgba(0,0,0,0)"
    fig.update_layout(**layout)
    return fig


def gauge(value: float, target: float, max_value: float = 100,
          height: int = 240, color: str = T.NAVY) -> go.Figure:
    bar_color = T.POS if value >= target else T.RED
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number=dict(suffix="%", font=dict(size=44, color=T.INK, family="Inter")),
        gauge=dict(
            axis=dict(
                range=[0, max_value],
                tickmode="array",
                tickvals=[0, 25, 50, 75, 100],
                ticktext=["0", "25", "50", "75", "100"],
                tickwidth=1,
                tickcolor=T.BORDER,
                tickfont=dict(size=10, color=T.SUBTLE, family="Inter"),
            ),
            bar=dict(color=bar_color, thickness=0.32),
            bgcolor="white",
            borderwidth=0,
            steps=[
                dict(range=[0, target], color="rgba(220,38,38,0.05)"),
                dict(range=[target, max_value], color="rgba(22,163,74,0.05)"),
            ],
            threshold=dict(line=dict(color=T.GOLD, width=3), thickness=0.9, value=target),
        ),
    ))
    layout = _apply({"height": height, "margin": dict(l=24, r=24, t=24, b=8)})
    fig.update_layout(**layout)
    return fig


def stacked_area(df: pd.DataFrame, x: str, y_cols: list, colors: list,
                 labels: list | None = None, height: int = 280) -> go.Figure:
    fig = go.Figure()
    labels = labels or y_cols
    for col, c, lbl in zip(y_cols, colors, labels):
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col], mode="lines", name=lbl,
            stackgroup="one", line=dict(width=0.5, color=c),
            fillcolor=c, hovertemplate=f"<b>{lbl}</b>: %{{y:.1f}}%<extra></extra>",
        ))
    layout = _apply({"height": height, "legend": dict(orientation="h", y=-0.18)})
    layout["yaxis"]["ticksuffix"] = "%"
    fig.update_layout(**layout)
    return fig


def heatmap_hour_day(df: pd.DataFrame, height: int = 320) -> go.Figure:
    days_id = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    hours = list(range(7, 19))
    pivot = (
        df.assign(hour=df["timestamp"].dt.hour, dow=df["timestamp"].dt.dayofweek)
        .query("hour >= 7 and hour <= 18")
        .groupby(["dow", "hour"]).size().unstack(fill_value=0).reindex(range(7), fill_value=0)
    )
    z = pivot.reindex(columns=hours, fill_value=0).values
    fig = go.Figure(go.Heatmap(
        z=z, x=[f"{h:02d}:00" for h in hours], y=days_id,
        colorscale=[[0, "#F1F5F9"], [0.4, "#93C5FD"], [1, T.NAVY]],
        showscale=True,
        colorbar=dict(thickness=10, len=0.7, tickfont=dict(size=10, color=T.MUTED), outlinewidth=0),
        hovertemplate="<b>%{y} %{x}</b><br>%{z:,} tiket<extra></extra>",
    ))
    layout = _apply({"height": height})
    layout["yaxis"]["gridcolor"] = "rgba(0,0,0,0)"
    layout["xaxis"]["gridcolor"] = "rgba(0,0,0,0)"
    fig.update_layout(**layout)
    return fig


def histogram(values, height: int = 280, percentiles: dict | None = None,
              x_suffix: str = "") -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=values, nbinsx=40, marker=dict(color=T.NAVY_SOFT, line=dict(color=T.NAVY, width=0.5)),
        hovertemplate="%{x}: %{y:,}<extra></extra>",
    ))
    if percentiles:
        for label, val in percentiles.items():
            fig.add_vline(x=val, line_dash="dash", line_color=T.RED, line_width=1.2,
                          annotation_text=f"{label}={val:.2f}{x_suffix}",
                          annotation_position="top",
                          annotation_font=dict(color=T.RED, size=10))
    layout = _apply({"height": height})
    fig.update_layout(**layout)
    return fig


def scatter_volume_sentiment(topics: list, volumes: list, sentiments: list,
                             height: int = 320) -> go.Figure:
    colors = [T.POS if s >= 70 else (T.GOLD if s >= 50 else T.NEG) for s in sentiments]
    fig = go.Figure(go.Scatter(
        x=volumes, y=sentiments, mode="markers+text",
        marker=dict(size=[max(20, min(80, v / 50)) for v in volumes],
                    color=colors, line=dict(color="white", width=2), opacity=0.8),
        text=topics, textposition="top center",
        textfont=dict(size=11, color=T.INK),
        hovertemplate="<b>%{text}</b><br>Volume: %{x:,}<br>Skor sentimen: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=50, line_dash="dot", line_color=T.MUTED, line_width=1)
    layout = _apply({"height": height})
    layout["xaxis"]["title"] = "Volume mention"
    layout["yaxis"]["title"] = "Skor sentimen (%)"
    layout["yaxis"]["range"] = [0, 100]
    fig.update_layout(**layout)
    return fig


def _hex_to_rgba(hex_color: str, alpha: float = 0.2) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def boxplot_by_category(df: pd.DataFrame, x: str, y: str, height: int = 280) -> go.Figure:
    fig = go.Figure()
    cats = list(df[x].unique())
    color = T.NAVY
    for c in cats:
        fig.add_trace(go.Box(
            y=df[df[x] == c][y], name=c,
            marker=dict(color=color, outliercolor=T.RED, size=4),
            line=dict(color=color, width=1.5),
            boxpoints=False,
            fillcolor=_hex_to_rgba(color, 0.12),
            whiskerwidth=0.6,
        ))
    layout = _apply({"height": height, "showlegend": False,
                     "margin": dict(l=48, r=12, t=8, b=40)})
    layout["yaxis"]["title"] = "Jam"
    layout["yaxis"]["title_font"] = dict(size=11, color=T.SUBTLE)
    fig.update_layout(**layout)
    return fig


def stacked_bar(df: pd.DataFrame, x: str, y_cols: list, colors: list,
                labels: list | None = None, height: int = 280) -> go.Figure:
    fig = go.Figure()
    labels = labels or y_cols
    for col, c, lbl in zip(y_cols, colors, labels):
        fig.add_trace(go.Bar(
            x=df[x], y=df[col], name=lbl, marker=dict(color=c),
            hovertemplate=f"<b>{lbl}</b>: %{{y:.1f}}%<extra></extra>",
        ))
    layout = _apply({"height": height, "barmode": "stack",
                     "legend": dict(orientation="h", y=-0.2)})
    layout["yaxis"]["ticksuffix"] = "%"
    fig.update_layout(**layout)
    return fig


def score_distribution_bar(scores: list, height: int = 80) -> go.Figure:
    """Single horizontal stacked bar showing 1★–5★ distribution."""
    counts = pd.Series(scores).value_counts().reindex([5, 4, 3, 2, 1], fill_value=0)
    total = counts.sum()
    pcts = (counts / total * 100).values
    palette = ["#16A34A", "#65A30D", "#C9A227", "#F97316", "#DC2626"]
    fig = go.Figure()
    for i, (lbl, pct, col) in enumerate(zip([f"{s}★" for s in [5, 4, 3, 2, 1]], pcts, palette)):
        fig.add_trace(go.Bar(
            x=[pct], y=["Skor"], orientation="h", name=lbl, marker=dict(color=col),
            text=[f"{lbl} {pct:.1f}%"] if pct > 4 else "",
            textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=11, family="Inter"),
            hovertemplate=f"<b>{lbl}</b>: %{{x:.1f}}%<extra></extra>",
        ))
    layout = _apply({"height": height, "barmode": "stack", "showlegend": False,
                     "margin": dict(l=0, r=0, t=4, b=4)})
    layout["xaxis"]["visible"] = False
    layout["yaxis"]["visible"] = False
    fig.update_layout(**layout)
    return fig
