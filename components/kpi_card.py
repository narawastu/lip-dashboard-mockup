"""KPI card with sparkline rendered as inline SVG (no chart lib needed)."""

from __future__ import annotations

import math
import streamlit as st

import theme as T


def _sparkline_svg(values: list, color: str = T.NAVY, width: int = 220, height: int = 36) -> str:
    if not values or len(values) < 2:
        return ""
    vmin = min(values)
    vmax = max(values)
    span = max(vmax - vmin, 1e-9)
    pts = []
    fill_pts = [f"0,{height}"]
    last_x = last_y = 0
    for i, v in enumerate(values):
        x = i / (len(values) - 1) * width
        y = height - ((v - vmin) / span) * (height - 8) - 4
        pts.append(f"{x:.1f},{y:.1f}")
        fill_pts.append(f"{x:.1f},{y:.1f}")
        last_x, last_y = x, y
    fill_pts.append(f"{width},{height}")
    h = color.replace("#", "")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    fill_strong = f"rgba({r},{g},{b},0.18)"
    fill_weak = f"rgba({r},{g},{b},0.02)"
    grad_id = f"sparkgrad{abs(hash((color, len(values))))}"
    return f"""
    <svg viewBox="0 0 {width} {height}" preserveAspectRatio="none" class="kpi-spark">
      <defs>
        <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="rgb({r},{g},{b})" stop-opacity="0.22" />
          <stop offset="100%" stop-color="rgb({r},{g},{b})" stop-opacity="0" />
        </linearGradient>
      </defs>
      <polygon points="{' '.join(fill_pts)}" fill="url(#{grad_id})" />
      <polyline points="{' '.join(pts)}" fill="none" stroke="{color}" stroke-width="2"
                stroke-linejoin="round" stroke-linecap="round" />
      <circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="2.6" fill="white" stroke="{color}" stroke-width="2" />
    </svg>
    """


def _delta_chip(delta: float | None, suffix: str = "", invert: bool = False) -> str:
    if delta is None or math.isnan(delta):
        return f"<span class='kpi-delta neu'>—</span>"
    arrow = "▲" if delta > 0 else ("▼" if delta < 0 else "•")
    klass = "neu"
    if delta != 0:
        good = (delta > 0) if not invert else (delta < 0)
        klass = "pos" if good else "neg"
    sign = "+" if delta > 0 else ""
    return f"<span class='kpi-delta {klass}'>{arrow} {sign}{delta:.1f}{suffix}</span>"


def kpi_card(label: str, value_str: str, suffix: str = "", delta: float | None = None,
             delta_suffix: str = "", invert_delta: bool = False,
             spark_values: list | None = None, color: str = T.NAVY) -> None:
    spark = _sparkline_svg(spark_values, color, width=300, height=42) if spark_values else ""
    delta_html = _delta_chip(delta, delta_suffix, invert_delta)
    suffix_html = f"<span class='kpi-suffix'>{suffix}</span>" if suffix else ""
    html = f"""
    <div class="kpi" style="--kpi-accent: {color};">
      <div class="kpi-row">
        <div class="kpi-label">{label}</div>
        {delta_html}
      </div>
      <div>
        <span class="kpi-value">{value_str}</span>{suffix_html}
      </div>
      {spark}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def index_panel(tag: str, name: str, value: float, target: float,
                delta: float | None, spark_values: list,
                stripe_class: str, accent_color: str) -> None:
    """Big SXI/SSI panel for the overview tab. `name` arg kept for backward compat but unused."""
    delta_html = _delta_chip(delta, "%")
    spark = _sparkline_svg(spark_values, accent_color, width=720, height=84)
    above_target = value >= target
    target_label = "Di atas target" if above_target else "Di bawah target"
    margin_above = value - target
    html = f"""
    <div class="bi-index-panel">
      <div class="bi-index-meta">
        <div class="bi-index-badge">
          <span class="bi-index-badge-dot {stripe_class}"></span>
          <span class="bi-index-badge-tag">{tag}</span>
        </div>
        <div class="bi-index-value">{value:.2f}<span style='font-size:24px;color:{T.SUBTLE};font-weight:600;margin-left:4px;'>%</span></div>
        <div style="margin-top:14px;display:flex;flex-wrap:wrap;align-items:center;gap:6px;">
          <span class="bi-index-target">Target {target:.0f}%</span>
          <span class="bi-pill {'pos' if above_target else 'neg'}">{'+' if margin_above >= 0 else ''}{margin_above:.1f} pp · {target_label}</span>
          {delta_html}
        </div>
      </div>
      <div class="bi-index-spark">{spark}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
