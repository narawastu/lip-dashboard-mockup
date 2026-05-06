"""Tab 3 — SSI / social sentiment."""

from __future__ import annotations

import pandas as pd
import streamlit as st
import numpy as np

import theme as T
from data import generator as G, reference as R
from components import header as H
from components import charts as C
from components.card import card


SAMPLE_MENTIONS = [
    ("Positif", "X (Twitter)", "Pelayanan Bicara BI cepat banget responnya, baru kirim email pagi sudah dibalas detail. Mantap 👏"),
    ("Positif", "Instagram", "Penjelasan tentang BI-FAST di livechat sangat membantu, terima kasih BI."),
    ("Negatif", "X (Twitter)", "Antrian telepon ke 131 lama banget hari ini, sudah 30 menit belum diangkat 😩"),
    ("Netral", "Berita Online", "Bank Indonesia rilis laporan Layanan Informasi Publik bulan Mei 2026 dengan total 7.024 permohonan."),
    ("Positif", "TikTok", "Edukasi tentang dompet elektronik dari akun BI bermanfaat banget buat UMKM seperti saya."),
    ("Positif", "Facebook", "Walk-in di Visitor Center cepat dilayani, petugasnya ramah dan informatif."),
    ("Negatif", "Instagram", "Form permohonan informasi di website agak ribet, bisa disederhanakan tidak?"),
    ("Netral", "YouTube", "Tutorial BIFAST yang dipublikasikan BI sangat detail, cocok untuk pemula."),
    ("Positif", "X (Twitter)", "Respons BI di sosmed top — tidak template dan benar-benar menjawab pertanyaan."),
    ("Negatif", "Berita Online", "Sebagian permohonan informasi dikecualikan karena masuk kategori sensitif. Akademisi minta klarifikasi."),
]


def _scope(tickets, filters):
    return G.filter_tickets(
        tickets, channels=filters["channels"], topics=filters["topics"],
        requestors=filters["requestors"], provinces=filters["provinces"] or None,
        date_range=filters["date_range"],
    )


def render(social: pd.DataFrame, filters: dict) -> None:
    monthly = G.monthly_social_summary(social)

    H.section("Stakeholders Satisfaction Index", "Sentimen publik dari pemantauan media sosial dan berita online")

    ssi_now = monthly["ssi_pct"].iloc[-1]

    c1, c2 = st.columns([1, 2])
    with c1, card("Nilai SSI Bulan Ini", elevated=True):
        C.show(C.gauge(ssi_now, R.SSI_TARGET, max_value=100, height=240))
        last = monthly.iloc[-1]
        st.markdown(f"""
        <div style='text-align:center;color:{T.MUTED};font-size:12px;margin-top:-12px;'>
          Target {R.SSI_TARGET:.0f}% · Bulan ini {ssi_now:.2f}%
        </div>
        <dl class='bi-stat-list'>
          <dt>Total mention bulan ini</dt><dd>{int(last['total']):,}</dd>
          <dt>Rata-rata respons sosmed</dt><dd>{last['avg_response_min']:.1f} menit</dd>
          <dt>Sentimen positif</dt><dd style='color:{T.POS}'>{last['positif_pct']:.1f}%</dd>
          <dt>Sentimen negatif</dt><dd style='color:{T.NEG}'>{last['negatif_pct']:.1f}%</dd>
        </dl>
        """, unsafe_allow_html=True)

    with c2, card("Tren Sentimen 12 Bulan", elevated=True):
        trend = monthly.copy()
        trend["label"] = trend["yearmonth"].apply(G.label_ym)
        C.show(C.stacked_area(trend, "label",
                              ["positif_pct", "netral_pct", "negatif_pct"],
                              colors=[T.POS, T.NEU, T.NEG],
                              labels=["Positif", "Netral", "Negatif"],
                              height=300))

    # Share of voice + volume vs sentiment
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Lanskap Sosial", "Distribusi platform & topik")
    c3, c4 = st.columns(2)
    with c3, card("Share of Voice per Platform"):
        plat_counts = social["platform"].value_counts().reindex([p[0] for p in R.PLATFORMS], fill_value=0)
        C.show(C.donut(plat_counts.index.tolist(), plat_counts.values.tolist(), height=320))

    with c4, card("Volume vs Sentimen per Topik"):
        topic_stats = social.groupby("topic").agg(
            volume=("timestamp", "size"),
            ssi=("sentiment", lambda s: 100 * (s == "Positif").mean() + 50 * (s == "Netral").mean()),
        ).reset_index()
        topic_stats = topic_stats[topic_stats["topic"] != "Lainnya"]
        C.show(C.scatter_volume_sentiment(
            topic_stats["topic"].tolist(),
            topic_stats["volume"].tolist(),
            topic_stats["ssi"].tolist(),
            height=320,
        ))

    # Top trending topics + top mentions
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Topik & Mention Teratas", "Apa yang paling diperbincangkan publik")
    c5, c6 = st.columns([1, 2])

    with c5, card("Top Trending Topics"):
        topic_recent = social[social["yearmonth"] == "2026-05"]["topic"].value_counts().head(7)
        topic_prev = social[social["yearmonth"] == "2026-04"]["topic"].value_counts()
        rows_html = ""
        for t, count in topic_recent.items():
            prev = topic_prev.get(t, count)
            delta = ((count - prev) / max(prev, 1)) * 100
            ssi_t = (
                100 * (social[social["topic"] == t]["sentiment"] == "Positif").mean()
                + 50 * (social[social["topic"] == t]["sentiment"] == "Netral").mean()
            )
            klass = "pos" if ssi_t >= 70 else ("neg" if ssi_t < 50 else "neu")
            arrow = "▲" if delta > 0 else "▼"
            color = T.POS if delta > 0 else T.NEG
            rows_html += f"""
            <div style='display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid {T.BORDER};'>
              <div>
                <div style='font-size:13px;font-weight:600;color:{T.INK}'>{t}</div>
                <div style='font-size:11px;color:{T.MUTED};margin-top:2px;'>{count:,} mention</div>
              </div>
              <div style='display:flex;flex-direction:column;align-items:flex-end;gap:2px;'>
                <span class='bi-pill {klass}'>{ssi_t:.0f}% pos</span>
                <span style='font-size:11px;color:{color};font-weight:600;'>{arrow} {abs(delta):.0f}%</span>
              </div>
            </div>
            """
        st.markdown(rows_html, unsafe_allow_html=True)

    with c6, card("Top Mentions Bulan Ini"):
        for sent, plat, text in SAMPLE_MENTIONS[:7]:
            klass = {"Positif": "pos", "Negatif": "neg", "Netral": "neu"}[sent]
            engagement = np.random.default_rng(hash(text) & 0xFFFF).integers(150, 4500)
            st.markdown(f"""
            <div class='bi-mention'>
              <div class='bi-mention-meta'>
                <span class='bi-pill {klass}'>{sent}</span>
                <span>•</span>
                <span>{plat}</span>
                <span>•</span>
                <span>{engagement:,} engagement</span>
              </div>
              <div class='bi-mention-text'>{text}</div>
            </div>
            """, unsafe_allow_html=True)

    # Response time breakdown
    st.markdown("<div style='margin-top:18px;'></div>", unsafe_allow_html=True)
    H.section("Waktu Respons Sosial Media", "Median menit per platform")
    plat_resp = social.groupby("platform")["response_minutes"].median().sort_values()
    with card():
        C.show(C.hbar(plat_resp.index.tolist(), plat_resp.values.tolist(), height=260,
                      value_suffix=" mnt"))
