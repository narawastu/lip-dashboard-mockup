"""Tab 5 — Operasional & drill-down."""

from __future__ import annotations

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st

import theme as T
from data import generator as G, reference as R
from components import header as H
from components import charts as C
from components.card import card


def _scope(tickets, filters):
    return G.filter_tickets(
        tickets, channels=filters["channels"], topics=filters["topics"],
        requestors=filters["requestors"], provinces=filters["provinces"] or None,
        date_range=filters["date_range"],
    )


def _province_choropleth(df: pd.DataFrame) -> go.Figure:
    """Simulate a regional bar (Plotly choropleth would need GeoJSON; we use bar for cleanliness)."""
    counts = df.groupby("province").size().sort_values(ascending=True)
    fig = go.Figure(go.Bar(
        x=counts.values, y=counts.index, orientation="h",
        marker=dict(color=counts.values, colorscale=[[0, "#E2E8F0"], [0.6, "#3D74C2"], [1, T.NAVY]],
                    line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>%{x:,} tiket<extra></extra>",
    ))
    layout = dict(T.PLOTLY_LAYOUT)
    layout["height"] = 600
    layout["xaxis"] = dict(showgrid=False, showticklabels=False, zeroline=False)
    layout["yaxis"] = dict(gridcolor="rgba(0,0,0,0)", zeroline=False)
    layout["margin"] = dict(l=0, r=20, t=8, b=8)
    fig.update_layout(**layout)
    return fig


def render(tickets: pd.DataFrame, filters: dict) -> None:
    df = _scope(tickets, filters)

    H.section("Operasional & Drill-Down", "Analisa beban kerja, performa SLA, dan distribusi geografis")

    # Heatmap + histogram
    c1, c2 = st.columns(2)
    with c1, card("Volume Tiket per Jam × Hari"):
        C.show(C.heatmap_hour_day(df, height=320))
    with c2, card("Distribusi Waktu Penyelesaian (jam)"):
        if len(df):
            res = df["resolution_h"].values
            percentiles = {
                "p50": float(np.percentile(res, 50)),
                "p90": float(np.percentile(res, 90)),
                "p95": float(np.percentile(res, 95)),
            }
            C.show(C.histogram(res, percentiles=percentiles, x_suffix="h", height=320))

    # Backlog trend + rejection
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    c3, c4 = st.columns([2, 1])
    with c3, card("Tren Backlog Harian (Tiket Belum Selesai)"):
        # Simulate backlog trend
        daily = df.groupby(df["timestamp"].dt.date).size().reset_index(name="opened")
        daily["closed"] = (daily["opened"] * np.random.default_rng(7).uniform(0.92, 1.08, size=len(daily))).astype(int)
        daily["backlog"] = (daily["opened"] - daily["closed"]).cumsum().clip(lower=0).rolling(7, min_periods=1).mean()
        daily.columns = ["date", "opened", "closed", "backlog"]
        daily["date_str"] = daily["date"].astype(str)
        fig = go.Figure(go.Scatter(
            x=daily["date_str"], y=daily["backlog"], mode="lines",
            fill="tozeroy", fillcolor="rgba(201,162,39,0.12)",
            line=dict(color=T.GOLD, width=2.5, shape="spline"),
            hovertemplate="<b>%{x}</b><br>Backlog: %{y:.0f}<extra></extra>",
        ))
        layout = dict(T.PLOTLY_LAYOUT)
        layout["height"] = 280
        layout["xaxis"] = {**T.PLOTLY_LAYOUT["xaxis"], "showticklabels": True}
        fig.update_layout(**layout)
        C.show(fig)
    with c4, card("Permohonan Ditolak / Dikecualikan"):
        rejected = df[df["status"] != "Dikabulkan"]
        n_rej = len(rejected)
        rate = (n_rej / max(len(df), 1)) * 100
        st.markdown(f"""
        <div style='font-size:36px;font-weight:800;color:{T.INK};'>{n_rej:,}</div>
        <div style='font-size:13px;color:{T.MUTED};margin-bottom:14px;'>{rate:.2f}% dari total</div>
        """, unsafe_allow_html=True)
        if n_rej > 0:
            reason_counts = rejected["rejection_reason"].value_counts()
            for reason, count in reason_counts.items():
                pct = count / n_rej * 100
                st.markdown(f"""
                <div style='margin-bottom:10px;'>
                  <div style='display:flex;justify-content:space-between;font-size:12px;color:{T.MUTED};margin-bottom:3px;'>
                    <span>{reason}</span><span>{count:,} · {pct:.1f}%</span>
                  </div>
                  <div style='height:6px;background:{T.BORDER};border-radius:3px;overflow:hidden;'>
                    <div style='width:{pct:.1f}%;height:100%;background:{T.NAVY};'></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # Repeat-inquiry + region
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    c5, c6 = st.columns([1, 2])
    with c5, card("Repeat Inquiry"):
        repeat_rate = df["is_repeat"].mean() * 100 if len(df) else 0
        st.markdown(f"""
        <div style='font-size:46px;font-weight:800;color:{T.INK};line-height:1;'>{repeat_rate:.1f}<span style='font-size:24px;color:{T.MUTED};'>%</span></div>
        <div style='font-size:13px;color:{T.MUTED};margin-top:6px;'>Pemohon yang mengirim &gt;1 permohonan</div>
        <div style='margin-top:14px;font-size:12px;color:{T.MUTED};line-height:1.6;'>
        Tinggi → indikasi informasi awal kurang lengkap atau topik kompleks.<br>
        Rendah → resolusi sekali kontak (one-touch resolution) baik.
        </div>
        """, unsafe_allow_html=True)

    with c6, card("Distribusi Permohonan per Provinsi"):
        C.show(_province_choropleth(df))

    # Tickets table
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Tabel Tiket Terkini", "50 tiket terbaru sesuai filter")
    sample = df.sort_values("timestamp", ascending=False).head(50)[
        ["timestamp", "channel", "topic", "requestor", "province", "status",
         "resolution_h", "sxi_score", "sla_met"]
    ].copy()
    sample.columns = ["Waktu", "Kanal", "Topik", "Pemohon", "Provinsi", "Status",
                      "Waktu (jam)", "Skor SXI", "SLA"]
    sample["Waktu (jam)"] = sample["Waktu (jam)"].round(2)
    sample["SLA"] = sample["SLA"].map({True: "✓", False: "✗"})

    st.dataframe(sample, use_container_width=True, height=420, hide_index=True)

    csv = sample.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Unduh CSV", data=csv, file_name="tiket-lip-bi.csv",
                       mime="text/csv")
