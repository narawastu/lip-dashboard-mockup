"""Tab — Detail Indeks. All 5 satisfaction indices, broken down per kanal, topik, wilayah."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import theme as T
from data import generator as G, reference as R
from components import header as H
from components import charts as C
from components.card import card


INDEX_COLOR = {
    "overall":  T.NAVY,
    "effort":   "#0F766E",
    "trust":    T.NAVY_GLOW,
    "loyalty":  "#7C3AED",
    "advokasi": T.GOLD,
}


def _scope(tickets, filters):
    return G.filter_tickets(
        tickets,
        channels=filters["channels"], topics=filters["topics"],
        requestors=filters["requestors"], wilayah=filters["wilayah"] or None,
        usia=filters["usia"] or None, gender=filters["gender"] or None,
        date_range=filters["date_range"],
    )


def _t2b_table_by(df: pd.DataFrame, group_col: str, group_order=None) -> pd.DataFrame:
    """Build a table: rows = group_col values, columns = T2B per index, plus Responden."""
    rows = []
    if group_order is None:
        group_order = df[group_col].dropna().unique().tolist()
    for v in group_order:
        sub = df[df[group_col] == v]
        if len(sub) == 0:
            continue
        row = {group_col: v, "Responden": len(sub)}
        for key, label, _t, _i in R.INDICES:
            row[label] = G.top2box(sub[f"score_{key}"])
        rows.append(row)
    return pd.DataFrame(rows)


def _format_table(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if col in ("Responden",) or col.endswith(("_label", "wilayah", "channel", "topic")):
            continue
        if pd.api.types.is_numeric_dtype(out[col]):
            out[col] = out[col].round(1)
    return out


def render(tickets: pd.DataFrame, filters: dict) -> None:
    df = _scope(tickets, filters)
    monthly = G.monthly_summary(tickets)

    H.section("Detail Indeks", "Distribusi & breakdown 5 indeks kepuasan: Overall, Effort, Trust, Loyalty, Advokasi")

    # 5 KPI cards (compact)
    cols = st.columns(5)
    for col_box, (key, label, target, _icon) in zip(cols, R.INDICES):
        score_col = f"score_{key}"
        current = G.top2box(df[score_col]) if len(df) else float("nan")
        spark = monthly[f"t2b_{key}"].tolist()
        with col_box:
            from components.kpi_card import kpi_card
            kpi_card(label, f"{current:.1f}", "%",
                     delta=current - target, delta_suffix=" pp vs target",
                     spark_values=spark, color=INDEX_COLOR[key])

    # ===== Likert distribution =====
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Distribusi 5-poin per Indeks")
    with card():
        rows = []
        for key, label, _t, _i in R.INDICES:
            dist = G.likert_distribution(df[f"score_{key}"]) if len(df) else {}
            rows.append((label, dist))
        C.show(C.likert_stack(rows, height=320))

    # ===== 12-month trend (all 5) =====
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Tren 12 Bulan", "Top 2 Boxes (%) per indeks")
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

    # ===== Breakdown tables =====
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Breakdown", "Top 2 Boxes per kanal, topik, dan wilayah koordinasi")

    bcol1, bcol2 = st.columns(2)

    with bcol1, card("Per Kanal"):
        chan_order = [c[0] for c in R.CHANNELS]
        tab1 = _t2b_table_by(df, "channel", chan_order)
        if not tab1.empty:
            tab1 = tab1.rename(columns={"channel": "Kanal"})
            st.dataframe(_format_table(tab1), width="stretch", hide_index=True, height=260)

    with bcol2, card("Per Topik (Top 7)"):
        top_topics = df[df["topic"] != "Lainnya"]["topic"].value_counts().head(7).index.tolist()
        tab2 = _t2b_table_by(df[df["topic"].isin(top_topics)], "topic", top_topics)
        if not tab2.empty:
            tab2 = tab2.rename(columns={"topic": "Topik"})
            st.dataframe(_format_table(tab2), width="stretch", hide_index=True, height=260)

    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    with card("Per Wilayah Koordinasi"):
        tab3 = _t2b_table_by(df, "wilayah", R.WILAYAH_NAMES)
        if not tab3.empty:
            tab3 = tab3.rename(columns={"wilayah": "Wilayah"})
            st.dataframe(_format_table(tab3), width="stretch", hide_index=True, height=240)
