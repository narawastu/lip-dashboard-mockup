"""Tab — Per Kanal. Deep-dive for one selected channel."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import theme as T
from data import generator as G, reference as R
from components import header as H
from components import charts as C
from components.card import card
from components.kpi_card import kpi_card


INDEX_COLOR = {
    "overall":  T.NAVY,
    "effort":   "#0F766E",
    "trust":    T.NAVY_GLOW,
    "loyalty":  "#7C3AED",
    "advokasi": T.GOLD,
}

SAMPLE_COMMENTS_BY_CHANNEL = {
    "Walk-in Offline dan Online": [
        ("Sangat Puas", "Petugas sangat membantu dan informasinya jelas. Antrian cepat juga."),
        ("Puas", "Ruang tunggu nyaman, terima kasih atas pelayanannya."),
        ("Netral", "Antrian cukup panjang di jam sibuk, mohon ditingkatkan."),
        ("Tidak Puas", "Petugas ramah, tapi sistem kadang error."),
    ],
    "Email": [
        ("Sangat Puas", "Balasan email cepat dan informasinya lengkap. Mantap."),
        ("Puas", "Informasi di email sudah jelas dan mudah dipahami."),
        ("Netral", "Email balasan agak template, butuh konteks lebih spesifik."),
    ],
    "Telepon": [
        ("Sangat Puas", "Dijawab dengan ramah dan langsung dapat solusi."),
        ("Puas", "Petugas membantu menjelaskan dengan baik."),
        ("Tidak Puas", "Menunggu di telepon terlalu lama, mohon ditingkatkan."),
    ],
    "Livechat": [
        ("Sangat Puas", "Live chat sangat membantu dan responnya cepat."),
        ("Puas", "Live chat responsif dan ramah."),
        ("Netral", "Kadang ada delay, tapi overall membantu."),
    ],
    "Media Sosial": [
        ("Sangat Puas", "Respon di media sosial cepat dan tidak template."),
        ("Puas", "Pelayanan via DM Instagram sangat baik."),
        ("Tidak Puas", "Respon di media sosial kurang cepat, perlu ditingkatkan."),
    ],
    "Visitor Center": [
        ("Sangat Puas", "Petugas Visitor Center informatif dan ramah."),
        ("Puas", "Tour Visitor Center menarik dan edukatif."),
    ],
    "Lainnya": [
        ("Puas", "Pelayanan baik secara keseluruhan."),
    ],
}


def _scope_global(tickets, filters):
    """Apply non-channel filters from sidebar (kept channel free for the per-kanal selector)."""
    return G.filter_tickets(
        tickets,
        topics=filters["topics"],
        requestors=filters["requestors"],
        wilayah=filters["wilayah"] or None,
        usia=filters["usia"] or None,
        gender=filters["gender"] or None,
        date_range=filters["date_range"],
    )


def render(tickets: pd.DataFrame, filters: dict) -> None:
    H.section("Per Kanal", "Deep-dive untuk satu kanal layanan")

    # Channel selector
    selector_col, _ = st.columns([1, 2])
    with selector_col:
        channel = st.selectbox(
            "Pilih Kanal",
            options=[c[0] for c in R.CHANNELS],
            index=0,
            key="per_kanal_channel",
        )

    df_global = _scope_global(tickets, filters)
    df = df_global[df_global["channel"] == channel]

    if len(df) == 0:
        st.info("Tidak ada data untuk kombinasi filter ini.")
        return

    compare_range = filters["compare_range"]

    # ===== 5 KPI cards =====
    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)
    cols = st.columns(5)
    for col_box, (key, label, target, _icon) in zip(cols, R.INDICES):
        score_col = f"score_{key}"
        current = G.top2box(df[score_col])
        if compare_range:
            base = G.filter_tickets(
                tickets, topics=filters["topics"], requestors=filters["requestors"],
                wilayah=filters["wilayah"] or None,
                usia=filters["usia"] or None, gender=filters["gender"] or None,
                date_range=compare_range,
            )
            base = base[base["channel"] == channel]
            baseline = G.top2box(base[score_col]) if len(base) else float("nan")
            delta = current - baseline if pd.notna(baseline) else None
        else:
            delta = current - target

        # Channel-specific 12-month sparkline
        ch_monthly = (
            tickets[tickets["channel"] == channel]
            .groupby("yearmonth")[score_col]
            .apply(lambda s: 100 * (s >= 4).mean())
            .reindex(sorted(tickets["yearmonth"].unique()))
            .tolist()
        )
        with col_box:
            kpi_card(
                label, f"{current:.1f}", "%",
                delta=delta, delta_suffix=" pp",
                spark_values=ch_monthly,
                color=INDEX_COLOR[key],
            )

    # ===== Likert distribution for this channel =====
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Distribusi 5-poin", f"Kanal: {channel}")
    with card():
        rows = []
        for key, label, _t, _i in R.INDICES:
            dist = G.likert_distribution(df[f"score_{key}"])
            rows.append((label, dist))
        C.show(C.likert_stack(rows, height=320))

    # ===== Trend (multi-line) for this channel =====
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Tren Indeks per Bulan", f"Kanal: {channel}")
    ch_tickets = tickets[tickets["channel"] == channel]
    ch_monthly_df = pd.DataFrame({"yearmonth": sorted(ch_tickets["yearmonth"].unique())})
    for key in G.INDEX_KEYS:
        ch_monthly_df[f"t2b_{key}"] = (
            ch_tickets.groupby("yearmonth")[f"score_{key}"]
            .apply(lambda s: 100 * (s >= 4).mean())
            .reindex(ch_monthly_df["yearmonth"]).values
        )
    ch_monthly_df["label"] = ch_monthly_df["yearmonth"].apply(G.label_ym)
    with card():
        C.show(C.multi_line_trend(
            ch_monthly_df, "label",
            y_cols=[f"t2b_{k}" for k in G.INDEX_KEYS],
            colors=[INDEX_COLOR[k] for k in G.INDEX_KEYS],
            labels=[label for _, label, _, _ in R.INDICES],
            height=320,
        ))

    # ===== Demografi & Wilayah breakdown =====
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Breakdown Demografi & Wilayah", f"Kanal: {channel}")

    d1, d2, d3 = st.columns(3)

    with d1, card("Per Usia"):
        rows = []
        for age, _w in R.AGE_BRACKETS:
            sub = df[df["usia"] == age]
            rows.append({
                "Usia": age,
                "Responden": len(sub),
                "Top 2 Boxes (%)": round(G.top2box(sub["score_overall"]), 1) if len(sub) else 0,
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True, height=210)

    with d2, card("Per Jenis Kelamin"):
        rows = []
        for g, _w in R.GENDERS:
            sub = df[df["jenis_kelamin"] == g]
            rows.append({
                "Jenis Kelamin": g,
                "Responden": len(sub),
                "Top 2 Boxes (%)": round(G.top2box(sub["score_overall"]), 1) if len(sub) else 0,
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True, height=140)

    with d3, card("Per Wilayah Koordinasi"):
        rows = []
        for w in R.WILAYAH_NAMES:
            sub = df[df["wilayah"] == w]
            rows.append({
                "Wilayah": w,
                "Responden": len(sub),
                "T2B (%)": round(G.top2box(sub["score_overall"]), 1) if len(sub) else 0,
            })
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True, height=240)

    # ===== Komentar Terbaru =====
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Komentar Terbaru", f"Kanal: {channel}")
    samples = SAMPLE_COMMENTS_BY_CHANNEL.get(channel, SAMPLE_COMMENTS_BY_CHANNEL["Lainnya"])

    sentiment_color = {
        "Sangat Puas": ("pos", T.POS),
        "Puas": ("pos", "#65A30D"),
        "Netral": ("neu", T.MUTED),
        "Tidak Puas": ("neg", "#F97316"),
        "Sangat Tidak Puas": ("neg", T.NEG),
    }
    rows_html = ""
    for sent, text in samples:
        klass, _color = sentiment_color.get(sent, ("neu", T.MUTED))
        rows_html += f"""
        <div class='bi-mention'>
          <div class='bi-mention-meta'>
            <span class='bi-pill {klass}'>{sent}</span>
            <span>•</span><span>{channel}</span>
          </div>
          <div class='bi-mention-text'>{text}</div>
        </div>
        """
    with card():
        st.markdown(rows_html, unsafe_allow_html=True)
