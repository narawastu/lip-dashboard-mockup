"""Tab 4 — Ekspor Infografis. Composer + live preview + download."""

from __future__ import annotations

import streamlit as st
import pandas as pd
from datetime import date

import theme as T
from data import reference as R
from components import header as H
from components.card import card
from components.infographic import PosterSelection, render_poster


def render(tickets: pd.DataFrame, social: pd.DataFrame) -> None:
    H.section("Ekspor Infografis", "Komposisi laporan poster — pilih elemen, lalu unduh sebagai PNG atau PDF")

    left, right = st.columns([1, 2])

    with left, card("Konfigurasi Laporan", elevated=True):
        title = st.text_input("Judul laporan",
                              value="Laporan Layanan Informasi Publik",
                              key="poster_title")
        period = st.text_input("Periode (label)",
                               value=R.CURRENT_PERIOD_LABEL,
                               key="poster_period")

        st.markdown("---")
        st.markdown(f"<div class='bi-card-title' style='border-bottom:none;padding-bottom:0;margin-bottom:8px;'>Bagian yang Dimasukkan</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            show_header = st.checkbox("Header + judul", value=True)
            show_kpi_sxi = st.checkbox("KPI: SXI", value=True)
            show_kpi_ssi = st.checkbox("KPI: SSI", value=True)
            show_kpi_total = st.checkbox("KPI: Total tiket", value=True)
            show_kpi_resolution = st.checkbox("KPI: Waktu penyelesaian", value=True)
            show_hot_topics = st.checkbox("7 Hot Topics", value=True)
        with c2:
            show_trend = st.checkbox("Tren 12 bulan", value=True)
            show_channels = st.checkbox("Donut: Media Komunikasi", value=True)
            show_classification = st.checkbox("Donut: Klasifikasi", value=True)
            show_requestor = st.checkbox("Donut: Kategori Pemohon", value=True)
            show_sentiment = st.checkbox("Sentimen sosial", value=True)
            show_footer = st.checkbox("Catatan kaki", value=True)

        st.markdown("---")

        generate = st.button("Generate Preview", type="primary", use_container_width=True)
        st.caption("Preview di sebelah kanan akan diperbarui setelah tombol ditekan.")

    selection = PosterSelection(
        title=title,
        period=period,
        show_header=show_header,
        show_kpi_sxi=show_kpi_sxi,
        show_kpi_ssi=show_kpi_ssi,
        show_kpi_total=show_kpi_total,
        show_kpi_resolution=show_kpi_resolution,
        show_hot_topics=show_hot_topics,
        show_trend=show_trend,
        show_channels_donut=show_channels,
        show_classification_donut=show_classification,
        show_requestor_donut=show_requestor,
        show_sentiment=show_sentiment,
        show_footer=show_footer,
    )

    with right, card("Live Preview (1080×1920)", elevated=True):
        cache_key = (
            title, period, show_header, show_kpi_sxi, show_kpi_ssi, show_kpi_total,
            show_kpi_resolution, show_hot_topics, show_trend, show_channels,
            show_classification, show_requestor, show_sentiment, show_footer,
        )

        if generate or "poster_cache" not in st.session_state:
            with st.spinner("Merender poster…"):
                png_bytes, pdf_bytes = render_poster(tickets, social, selection)
            st.session_state["poster_cache"] = {"png": png_bytes, "pdf": pdf_bytes, "key": cache_key}

        cache = st.session_state.get("poster_cache")
        if cache:
            st.image(cache["png"], width=860)

            d1, d2 = st.columns(2)
            with d1:
                st.download_button(
                    "⬇ Unduh PNG (Hi-Res)",
                    data=cache["png"],
                    file_name=f"laporan-lip-bi-{period.lower().replace(' ', '-')}.png",
                    mime="image/png",
                    use_container_width=True,
                    type="primary",
                )
            with d2:
                st.download_button(
                    "⬇ Unduh PDF",
                    data=cache["pdf"],
                    file_name=f"laporan-lip-bi-{period.lower().replace(' ', '-')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            if cache["key"] != cache_key:
                st.info("Konfigurasi berubah. Klik 'Generate Preview' untuk memperbarui.")
