"""Tab 1 — Ringkasan Eksekutif. 5-index hero + Likert distribution + ops mini-cards + SSI panel."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import theme as T
from data import generator as G, reference as R
from components import header as H
from components import charts as C
from components.kpi_card import kpi_card, index_panel
from components.card import card


INDEX_COLOR = {
    "overall":  T.NAVY,
    "effort":   "#0F766E",
    "trust":    T.NAVY_GLOW,
    "loyalty":  "#7C3AED",
    "advokasi": T.GOLD,
}


def _scope(tickets: pd.DataFrame, filters: dict) -> pd.DataFrame:
    return G.filter_tickets(
        tickets,
        channels=filters["channels"],
        topics=filters["topics"],
        requestors=filters["requestors"],
        wilayah=filters["wilayah"] or None,
        usia=filters["usia"] or None,
        gender=filters["gender"] or None,
        date_range=filters["date_range"],
    )


def _compare_label_short(label: str) -> str:
    return {
        "Bulan sebelumnya": "vs bulan lalu",
        "Tahun lalu (periode sama)": "vs tahun lalu",
    }.get(label, "vs periode sebelumnya")


def render(tickets: pd.DataFrame, social: pd.DataFrame, filters: dict) -> None:
    df = _scope(tickets, filters)
    monthly = G.monthly_summary(tickets)
    monthly_social = G.monthly_social_summary(social)

    compare_range = filters["compare_range"]
    compare_short = _compare_label_short(filters["compare_label"])

    # ===== 5 satisfaction KPI cards =====
    H.section("Indeks Kepuasan", "Top 2 Boxes (% responden menjawab Puas + Sangat Puas)")

    cols = st.columns(5)
    for col_box, (key, label, target, _icon) in zip(cols, R.INDICES):
        score_col = f"score_{key}"
        t2b_col = f"t2b_{key}"
        current = G.top2box(df[score_col]) if len(df) else float("nan")
        if compare_range:
            base_df = G.filter_tickets(
                tickets,
                channels=filters["channels"], topics=filters["topics"],
                requestors=filters["requestors"], wilayah=filters["wilayah"] or None,
                usia=filters["usia"] or None, gender=filters["gender"] or None,
                date_range=compare_range,
            )
            baseline = G.top2box(base_df[score_col]) if len(base_df) else float("nan")
            delta = current - baseline if pd.notna(baseline) else None
        else:
            delta = None
        spark = monthly[t2b_col].tolist()
        with col_box:
            kpi_card(
                label, f"{current:.1f}", "%",
                delta=delta, delta_suffix=" pp",
                spark_values=spark,
                color=INDEX_COLOR[key],
            )

    # ===== Likert distribution =====
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Distribusi Kepuasan", "Distribusi 5-poin (Sangat Puas → Sangat Tidak Puas) per indeks")
    with card():
        rows = []
        for key, label, _t, _i in R.INDICES:
            score_col = f"score_{key}"
            dist = G.likert_distribution(df[score_col]) if len(df) else {}
            rows.append((label, dist))
        C.show(C.likert_stack(rows, height=320))

    # ===== Operational mini-cards =====
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Performa Operasional")

    total = len(df)
    avg_res = df["resolution_h"].mean() if total else 0
    sla_pct = 100 * df["sla_met"].mean() if total else 0
    backlog = int(total * 0.04)

    spark_total = monthly["total"].tolist()
    spark_res = monthly["avg_resolution"].tolist()
    spark_sla = monthly["sla_pct"].tolist()
    spark_backlog = [int(t * 0.04) for t in spark_total]

    # Compute deltas vs comparison period if set
    if compare_range:
        base_df = G.filter_tickets(
            tickets,
            channels=filters["channels"], topics=filters["topics"],
            requestors=filters["requestors"], wilayah=filters["wilayah"] or None,
            usia=filters["usia"] or None, gender=filters["gender"] or None,
            date_range=compare_range,
        )
        b_total = len(base_df)
        b_avg_res = base_df["resolution_h"].mean() if b_total else 0
        b_sla_pct = 100 * base_df["sla_met"].mean() if b_total else 0
        b_backlog = int(b_total * 0.04)
        delta_total = ((total - b_total) / max(b_total, 1)) * 100
        delta_res = ((avg_res - b_avg_res) / max(b_avg_res, 0.1)) * 100
        delta_sla = sla_pct - b_sla_pct
        delta_backlog = ((backlog - b_backlog) / max(b_backlog, 1)) * 100
    else:
        delta_total = delta_res = delta_sla = delta_backlog = None

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Total Permohonan", f"{total:,}", "tiket",
                 delta=delta_total, delta_suffix="%", spark_values=spark_total)
    with c2:
        kpi_card("Waktu Penyelesaian", f"{avg_res:.2f}", "jam",
                 delta=delta_res, delta_suffix="%", invert_delta=True,
                 spark_values=spark_res, color=T.NAVY_SOFT)
    with c3:
        kpi_card("SLA Compliance", f"{sla_pct:.1f}", "%",
                 delta=delta_sla, delta_suffix=" pp",
                 spark_values=spark_sla, color=T.GOLD)
    with c4:
        kpi_card("Backlog Aktif", f"{backlog:,}", "tiket",
                 delta=delta_backlog, delta_suffix="%", invert_delta=True,
                 spark_values=spark_backlog, color=T.NAVY_DEEP)

    # ===== SSI panel (separate from CSAT 5-index model) =====
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Stakeholders Satisfaction Index", "Indeks sentimen publik dari pemantauan media sosial dan berita online")
    ssi_now = monthly_social["ssi_pct"].iloc[-1]
    ssi_prev = monthly_social["ssi_pct"].iloc[-2] if len(monthly_social) >= 2 else ssi_now
    index_panel(
        tag="SSI", name="Stakeholders Satisfaction Index",
        value=ssi_now, target=R.SSI_TARGET, delta=ssi_now - ssi_prev,
        spark_values=monthly_social["ssi_pct"].tolist(),
        stripe_class="ssi", accent_color=T.GOLD,
    )

    # ===== Composition donuts =====
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
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

    # ===== 12-month trend =====
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Tren Indeks 12 Bulan", "Top 2 Boxes (%) sepanjang Jun 2025 → Mei 2026")
    trend_df = monthly.copy()
    trend_df["label"] = trend_df["yearmonth"].apply(G.label_ym)
    with card():
        C.show(C.multi_line_trend(
            trend_df, "label",
            y_cols=[f"t2b_{k}" for k in G.INDEX_KEYS],
            colors=[INDEX_COLOR[k] for k in G.INDEX_KEYS],
            labels=[label for _, label, _, _ in R.INDICES],
            height=340,
        ))
