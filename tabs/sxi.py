"""Tab 2 — SXI deep-dive."""

from __future__ import annotations

import pandas as pd
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


def render(tickets: pd.DataFrame, filters: dict) -> None:
    df = _scope(tickets, filters)
    monthly = G.monthly_summary(tickets)
    full_period_df = tickets

    H.section("Stakeholders Experience Index", "Indeks kepuasan layanan dari kanal langsung")

    sxi_now = monthly["sxi_pct"].iloc[-1]

    # Top row: gauge + score distribution + trend
    c1, c2 = st.columns([1, 2])
    with c1, card("Nilai SXI Bulan Ini", elevated=True):
        C.show(C.gauge(sxi_now, R.SXI_TARGET, max_value=100, height=240))
        st.markdown(f"<div style='text-align:center;color:{T.MUTED};font-size:12px;margin-top:-12px;'>"
                    f"Target {R.SXI_TARGET:.0f}% · Bulan ini {sxi_now:.2f}%</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
        # Top-2-box headline + breakdown
        scores = df["sxi_score"]
        total = max(len(scores), 1)
        pcts = {s: 100 * (scores == s).sum() / total for s in [5, 4, 3, 2, 1]}
        top2 = pcts[5] + pcts[4]
        palette = {5: T.POS, 4: "#65A30D", 3: T.GOLD, 2: "#F97316", 1: T.NEG}
        breakdown_html = "".join(
            f"<div style='display:flex;align-items:center;justify-content:space-between;"
            f"padding:7px 0;border-top:1px solid {T.BORDER};'>"
            f"<span style='display:flex;align-items:center;gap:8px;font-size:12px;color:{T.INK};'>"
            f"<span style='display:inline-block;width:8px;height:8px;border-radius:2px;"
            f"background:{palette[s]};'></span>{s}★</span>"
            f"<span style='font-size:12px;font-weight:700;color:{T.INK};font-variant-numeric:tabular-nums;'>"
            f"{pcts[s]:.2f}%</span></div>"
            for s in [5, 4, 3, 2, 1]
        )
        st.markdown(f"""
          <div class='bi-card-title' style='border-bottom:none;padding-bottom:0;margin-bottom:6px;'>Distribusi Skor</div>
          <div style='display:flex;align-items:baseline;gap:8px;margin-bottom:10px;'>
            <span style='font-size:30px;font-weight:800;color:{T.INK};letter-spacing:-0.02em;'>{top2:.1f}<span style='font-size:18px;color:{T.SUBTLE};'>%</span></span>
            <span style='font-size:12px;font-weight:600;color:{T.MUTED};'>memberikan 4★ atau 5★</span>
          </div>
          {breakdown_html}
        """, unsafe_allow_html=True)

    with c2, card("Tren SXI 12 Bulan", elevated=True):
        trend = monthly.copy()
        trend["label"] = trend["yearmonth"].apply(G.label_ym)
        sxi_min, sxi_max = trend["sxi_pct"].min(), trend["sxi_pct"].max()
        pad = max(0.5, (sxi_max - sxi_min) * 0.5)
        y_lo = max(85, sxi_min - pad)
        y_hi = min(100, sxi_max + pad)
        C.show(C.line_trend(trend, "label", "sxi_pct", target=None,
                            y_suffix="%", height=300, y_range=(y_lo, y_hi)))
        st.markdown(
            f"<div style='font-size:12px;color:{T.MUTED};margin-top:-8px;'>"
            f"Konsisten <b style='color:{T.POS}'>+{trend['sxi_pct'].mean() - R.SXI_TARGET:.1f} pp</b> di atas target {R.SXI_TARGET:.0f}% sepanjang 12 bulan."
            f"</div>",
            unsafe_allow_html=True,
        )

    # SXI per kanal & per topik
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Penggerak Indeks", "Skor SXI per kanal dan per topik")
    c3, c4 = st.columns(2)
    with c3, card("SXI per Kanal"):
        per_ch = df.groupby("channel")["sxi_score"].mean()
        per_ch_pct = ((per_ch - 1) / 4 * 100).clip(0, 100)
        labels, vals = per_ch_pct.index.tolist(), per_ch_pct.values.tolist()
        lo = max(0, min(vals) - 0.5)
        hi = min(100, max(vals) + 0.5)
        C.show(C.hbar(labels, vals, height=300, value_suffix="%", x_range=(lo, hi)))
    with c4, card("SXI per Topik"):
        per_t = df[df["topic"] != "Lainnya"].groupby("topic")["sxi_score"].mean()
        per_t_pct = ((per_t - 1) / 4 * 100).clip(0, 100)
        labels, vals = per_t_pct.index.tolist(), per_t_pct.values.tolist()
        lo = max(0, min(vals) - 0.5)
        hi = min(100, max(vals) + 0.5)
        C.show(C.hbar(labels, vals, height=300, value_suffix="%", x_range=(lo, hi)))

    # Resolution time per kanal + SLA compliance
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Performa Penyelesaian", "Waktu penyelesaian dan SLA per kanal")
    c5, c6 = st.columns(2)
    with c5, card("Waktu Penyelesaian per Kanal (jam)"):
        sample = df.sample(n=min(len(df), 8000), random_state=1)
        C.show(C.boxplot_by_category(sample, "channel", "resolution_h", height=300))
    with c6, card("SLA Compliance per Kanal"):
        sla = df.groupby("channel").agg(
            on_time=("sla_met", lambda s: 100 * s.mean()),
        ).reset_index()
        sla["late"] = 100 - sla["on_time"]
        C.show(C.stacked_bar(sla, "channel", ["on_time", "late"],
                             colors=[T.POS, T.RED],
                             labels=["Sesuai SLA", "Terlambat"], height=300))

    # Hot topics + classification + requestor
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Komposisi Permohonan", "Topik populer, klasifikasi, dan kategori pemohon")
    c7, c8 = st.columns([2, 1])
    with c7, card("7 Hot Topics"):
        topic_counts = df[df["topic"] != "Lainnya"]["topic"].value_counts().head(7)
        if len(df):
            pcts = (topic_counts / len(df) * 100).values
            C.show(C.hbar(topic_counts.index.tolist(), pcts.tolist(), height=300, value_suffix="%"))
    with c8, card("Klasifikasi Informasi"):
        cl_counts = df["classification"].value_counts().reindex([c[0] for c in R.CLASSIFICATIONS], fill_value=0)
        C.show(C.donut(cl_counts.index.tolist(), cl_counts.values.tolist(), height=300,
                       color_seq=[T.NAVY, T.NAVY_SOFT, T.GOLD, T.RED]))

    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    with card("Kategori Pemohon"):
        rq_counts = df["requestor"].value_counts().reindex([r[0] for r in R.REQUESTORS], fill_value=0)
        C.show(C.donut(rq_counts.index.tolist(), rq_counts.values.tolist(), height=320))
