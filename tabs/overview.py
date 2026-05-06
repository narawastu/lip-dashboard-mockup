"""Tab 1 — Ringkasan Eksekutif. Operational KPI strip + stacked SXI/SSI panels (not paired)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import theme as T
from data import generator as G, reference as R
from components import header as H
from components import charts as C
from components.kpi_card import kpi_card, index_panel
from components.card import card


def _scope(tickets: pd.DataFrame, filters: dict) -> pd.DataFrame:
    return G.filter_tickets(
        tickets,
        channels=filters["channels"],
        topics=filters["topics"],
        requestors=filters["requestors"],
        provinces=filters["provinces"] or None,
        date_range=filters["date_range"],
    )


def render(tickets: pd.DataFrame, social: pd.DataFrame, filters: dict) -> None:
    df = _scope(tickets, filters)
    monthly = G.monthly_summary(tickets)
    monthly_social = G.monthly_social_summary(social)

    # ===== Hero KPI row (operational, no SXI/SSI) =====
    H.section("Ringkasan Operasional")

    total = len(df)
    avg_res = df["resolution_h"].mean() if total else 0
    sla_pct = 100 * df["sla_met"].mean() if total else 0
    backlog = int(total * 0.04)  # mock backlog

    # Compare to previous month for delta
    prev_total = monthly["total"].iloc[-2] if len(monthly) >= 2 else total
    prev_res = monthly["avg_resolution"].iloc[-2] if len(monthly) >= 2 else avg_res
    prev_sla = monthly["sla_pct"].iloc[-2] if len(monthly) >= 2 else sla_pct

    delta_total = ((total - prev_total) / max(prev_total, 1)) * 100
    delta_res = ((avg_res - prev_res) / max(prev_res, 0.1)) * 100
    delta_sla = sla_pct - prev_sla

    spark_total = monthly["total"].tolist()
    spark_res = monthly["avg_resolution"].tolist()
    spark_sla = monthly["sla_pct"].tolist()
    spark_backlog = [int(t * 0.04) for t in spark_total]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Permohonan", f"{total:,}", "tiket",
                 delta=delta_total, delta_suffix="%", spark_values=spark_total)
    with c2:
        kpi_card("Waktu Penyelesaian", f"{avg_res:.2f}", "jam",
                 delta=delta_res, delta_suffix="%", invert_delta=True, spark_values=spark_res,
                 color=T.NAVY_SOFT)
    with c3:
        kpi_card("SLA Compliance", f"{sla_pct:.1f}", "%",
                 delta=delta_sla, delta_suffix=" pp", spark_values=spark_sla,
                 color=T.GOLD)
    with c4:
        kpi_card("Backlog Aktif", f"{backlog:,}", "tiket",
                 delta=-2.4, delta_suffix="%", invert_delta=True, spark_values=spark_backlog,
                 color=T.NAVY_DEEP)

    # ===== SXI panel (full row) =====
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    H.section("Stakeholders Experience Index", "Skor kepuasan dari pelapor setelah tiket diselesaikan, agregat 6 kanal langsung")
    sxi_now = monthly["sxi_pct"].iloc[-1]
    sxi_prev = monthly["sxi_pct"].iloc[-2] if len(monthly) >= 2 else sxi_now
    index_panel(
        tag="SXI", name="Stakeholders Experience Index",
        value=sxi_now, target=R.SXI_TARGET, delta=sxi_now - sxi_prev,
        spark_values=monthly["sxi_pct"].tolist(),
        stripe_class="sxi", accent_color=T.NAVY,
    )

    # ===== SSI panel (full row, separate from SXI) =====
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    H.section("Stakeholders Satisfaction Index", "Indeks sentimen publik dari pemantauan media sosial dan berita online")
    ssi_now = monthly_social["ssi_pct"].iloc[-1]
    ssi_prev = monthly_social["ssi_pct"].iloc[-2] if len(monthly_social) >= 2 else ssi_now
    index_panel(
        tag="SSI", name="Stakeholders Satisfaction Index",
        value=ssi_now, target=R.SSI_TARGET, delta=ssi_now - ssi_prev,
        spark_values=monthly_social["ssi_pct"].tolist(),
        stripe_class="ssi", accent_color=T.GOLD,
    )

    # ===== 2x2 mini cards =====
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    H.section("Komposisi Permohonan")

    g1, g2 = st.columns(2)
    with g1, card("Media Komunikasi"):
        ch_counts = df["channel"].value_counts().reindex([c[0] for c in R.CHANNELS], fill_value=0)
        C.show(C.donut(ch_counts.index.tolist(), ch_counts.values.tolist(), height=300,
                       center_text=f"{total:,}", center_sub="tiket"))
    with g2, card("Klasifikasi Informasi"):
        cl_counts = df["classification"].value_counts().reindex([c[0] for c in R.CLASSIFICATIONS], fill_value=0)
        C.show(C.donut(cl_counts.index.tolist(), cl_counts.values.tolist(), height=300,
                       color_seq=[T.NAVY, T.NAVY_SOFT, T.GOLD, T.RED]))

    g3, g4 = st.columns(2)
    with g3, card("Kategori Pemohon"):
        rq_counts = df["requestor"].value_counts().reindex([r[0] for r in R.REQUESTORS], fill_value=0)
        C.show(C.donut(rq_counts.index.tolist(), rq_counts.values.tolist(), height=300))
    with g4, card("Top 7 Hot Topics"):
        topic_counts = df[df["topic"] != "Lainnya"]["topic"].value_counts().head(7)
        if total:
            pcts = (topic_counts / total * 100).values
            C.show(C.hbar(topic_counts.index.tolist(), pcts.tolist(), height=300, value_suffix="%"))

    # ===== 12-month trend, full width =====
    st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
    H.section("Tren 12 Bulan", "Volume permohonan Jun 2025 → Mei 2026")
    trend_df = monthly.copy()
    trend_df["label"] = trend_df["yearmonth"].apply(G.label_ym)
    with card():
        C.show(C.line_trend(trend_df, "label", "total", target=None, y_suffix="", height=320))
