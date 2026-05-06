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
from components import wilayah as W


def _scope(tickets, filters):
    return G.filter_tickets(
        tickets, channels=filters["channels"], topics=filters["topics"],
        requestors=filters["requestors"], wilayah=filters["wilayah"] or None,
        usia=filters["usia"] or None, gender=filters["gender"] or None,
        date_range=filters["date_range"],
    )


def _wilayah_volume_bar(df: pd.DataFrame) -> go.Figure:
    """Per-wilayah ticket volume."""
    counts = (
        df.groupby("wilayah").size()
        .reindex(R.WILAYAH_NAMES, fill_value=0)
        .sort_values(ascending=True)
    )
    fig = go.Figure(go.Bar(
        x=counts.values, y=counts.index, orientation="h",
        marker=dict(color=counts.values, colorscale=[[0, "#E2E8F0"], [0.6, "#3D74C2"], [1, T.NAVY]],
                    line=dict(width=0)),
        text=[f"{v:,}" for v in counts.values],
        textposition="outside", textfont=dict(size=11, color=T.INK, family="Inter"),
        cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>%{x:,} tiket<extra></extra>",
    ))
    layout = dict(T.PLOTLY_LAYOUT)
    layout["height"] = 240
    layout["xaxis"] = dict(showgrid=False, showticklabels=False, zeroline=False)
    layout["yaxis"] = dict(gridcolor="rgba(0,0,0,0)", zeroline=False)
    layout["margin"] = dict(l=8, r=80, t=8, b=8)
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

    with c6, card("Volume Permohonan per Wilayah Koordinasi"):
        C.show(_wilayah_volume_bar(df))

    # ===== Tren per Wilayah Koordinasi (categorization + table) =====
    st.markdown("<div style='margin-top:22px;'></div>", unsafe_allow_html=True)
    H.section(
        "Peta Tren Kepuasan per Wilayah Koordinasi",
        "Klasifikasi pola tren kepuasan Overall dalam 3 bulan terakhir",
    )

    buckets = W.categorize_wilayah_trends(tickets, "score_overall", window=3)

    pattern_palette = {
        "naik_terus":  ("#16A34A", "Naik Terus", "↗",
                        "Tren naik konsisten dalam 3 bulan terakhir"),
        "naik_turun":  ("#3B82F6", "Naik → Turun", "↗→↘",
                        "Naik di awal periode, lalu turun di bulan terakhir"),
        "turun_naik":  ("#7C3AED", "Turun → Naik", "↘→↗",
                        "Turun di awal periode, lalu naik di bulan terakhir"),
        "turun_terus": ("#DC2626", "Turun Terus", "↘",
                        "Tren turun konsisten dalam 3 bulan terakhir"),
        "datar":       ("#94A3B8", "Stabil", "→",
                        "Tidak ada perubahan signifikan"),
    }

    pattern_cols = st.columns(4)
    for col_box, key in zip(pattern_cols, ["naik_terus", "naik_turun", "turun_naik", "turun_terus"]):
        color, lbl, arrow, desc = pattern_palette[key]
        items = buckets.get(key, [])
        with col_box:
            list_html = ""
            if items:
                for w_name, vals, latest in items:
                    list_html += (
                        f"<div style='display:flex;justify-content:space-between;"
                        f"align-items:center;padding:6px 0;border-top:1px solid {T.BORDER};font-size:12px;'>"
                        f"<span style='color:{T.INK};'>{w_name}</span>"
                        f"<span style='color:{T.MUTED};font-variant-numeric:tabular-nums;'>{latest:.1f}%</span>"
                        f"</div>"
                    )
            else:
                list_html = (
                    f"<div style='padding:14px 0;color:{T.SUBTLE};font-size:12px;text-align:center;'>"
                    f"Tidak ada wilayah</div>"
                )
            st.markdown(f"""
            <div style='background:{T.SURFACE};border:1px solid {T.BORDER};border-radius:12px;padding:14px 16px;'>
              <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;'>
                <span style='font-weight:700;color:{color};font-size:14px;'>{lbl} <span style='font-size:13px;'>({arrow})</span></span>
                <span style='font-weight:700;color:{T.INK};font-size:18px;'>{len(items)}</span>
              </div>
              <div style='font-size:11px;color:{T.MUTED};margin-bottom:6px;line-height:1.4;'>{desc}</div>
              {list_html}
            </div>
            """, unsafe_allow_html=True)

    # Detail table per wilayah with sparklines isn't trivial in Streamlit; show t2b table.
    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
    with card("Detail T2B per Wilayah (5 Indeks)"):
        rows = []
        for w_name in R.WILAYAH_NAMES:
            sub = df[df["wilayah"] == w_name]
            row = {"Wilayah": w_name, "Responden": len(sub)}
            for k, label, _t, _i in R.INDICES:
                row[label] = round(G.top2box(sub[f"score_{k}"]), 1) if len(sub) else 0
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True, height=240)

    # Tickets table
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Tabel Tiket Terkini", "50 tiket terbaru sesuai filter")
    sample = df.sort_values("timestamp", ascending=False).head(50)[
        ["timestamp", "channel", "topic", "requestor", "wilayah", "status",
         "resolution_h", "score_overall", "sla_met"]
    ].copy()
    sample.columns = ["Waktu", "Kanal", "Topik", "Pemohon", "Wilayah", "Status",
                      "Waktu (jam)", "Skor Overall", "SLA"]
    sample["Waktu (jam)"] = sample["Waktu (jam)"].round(2)
    sample["SLA"] = sample["SLA"].map({True: "✓", False: "✗"})

    st.dataframe(sample, width="stretch", height=420, hide_index=True)

    csv = sample.to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Unduh CSV", data=csv, file_name="tiket-lip.csv",
                       mime="text/csv")
