"""Sticky brand header."""

from __future__ import annotations

import streamlit as st

import theme as T
from data import reference as R


def render_header(period_label: str = R.CURRENT_PERIOD_LABEL) -> None:
    st.markdown(f"""
    <div class="bi-hero">
      <div class="bi-hero-left">
        <div class="bi-hero-logo">BI</div>
        <div>
          <div class="bi-hero-eyebrow">Bank Indonesia · Layanan Informasi Publik</div>
          <div class="bi-hero-title">Stakeholders Experience &amp; Satisfaction</div>
        </div>
      </div>
      <div class="bi-hero-right">
        <div class="bi-hero-period">
          <span class="bi-hero-live-dot"></span>
          {period_label}
          <span class="bi-hero-period-sep">·</span>
          <span class="bi-hero-period-live">Live</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def section(title: str, sub: str | None = None) -> None:
    sub_html = f"<div class='bi-section-sub'>{sub}</div>" if sub else ""
    st.markdown(f"""
    <div class="bi-section">
      <h2>{title}</h2>
      {sub_html}
    </div>
    """, unsafe_allow_html=True)
