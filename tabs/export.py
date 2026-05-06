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


def _try_render(tickets, social, selection):
    """Render the poster. Pure Pillow now, no browser deps."""
    return render_poster(tickets, social, selection)


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
            show_kpi_overall = st.checkbox("KPI: Kepuasan Overall", value=True)
            show_kpi_effort = st.checkbox("KPI: Customer Effort", value=True)
            show_kpi_trust = st.checkbox("KPI: Trust", value=True)
            show_kpi_loyalty = st.checkbox("KPI: Loyalty", value=True)
            show_kpi_advokasi = st.checkbox("KPI: Advokasi", value=True)
            show_kpi_total = st.checkbox("KPI: Total tiket", value=False)
            show_kpi_resolution = st.checkbox("KPI: Waktu penyelesaian", value=False)
        with c2:
            show_hot_topics = st.checkbox("7 Hot Topics", value=True)
            show_trend = st.checkbox("Tren 12 bulan", value=True)
            show_channels = st.checkbox("Donut: Media Komunikasi", value=True)
            show_classification = st.checkbox("Donut: Klasifikasi", value=True)
            show_requestor = st.checkbox("Donut: Kategori Pemohon", value=True)
            show_sentiment = st.checkbox("Sentimen sosial", value=True)
            show_footer = st.checkbox("Catatan kaki", value=True)

        st.markdown("---")

        generate = st.button("Generate Preview", type="primary", width="stretch")
        st.caption("Preview di sebelah kanan akan diperbarui setelah tombol ditekan.")

    selection = PosterSelection(
        title=title,
        period=period,
        show_header=show_header,
        show_kpi_overall=show_kpi_overall,
        show_kpi_effort=show_kpi_effort,
        show_kpi_trust=show_kpi_trust,
        show_kpi_loyalty=show_kpi_loyalty,
        show_kpi_advokasi=show_kpi_advokasi,
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
            title, period, show_header,
            show_kpi_overall, show_kpi_effort, show_kpi_trust, show_kpi_loyalty, show_kpi_advokasi,
            show_kpi_total, show_kpi_resolution, show_hot_topics, show_trend,
            show_channels, show_classification, show_requestor, show_sentiment, show_footer,
        )

        # Render only when the user explicitly clicks Generate.
        # First-load: show a placeholder so a missing Chrome engine doesn't crash the tab.
        if generate:
            with st.spinner("Merender poster…"):
                png_bytes, pdf_bytes = _try_render(tickets, social, selection)
            if png_bytes is not None:
                st.session_state["poster_cache"] = {"png": png_bytes, "pdf": pdf_bytes, "key": cache_key}

        cache = st.session_state.get("poster_cache")
        if cache:
            st.image(cache["png"], width=860)

            d1, d2 = st.columns(2)
            with d1:
                st.download_button(
                    "⬇ Unduh PNG (Hi-Res)",
                    data=cache["png"],
                    file_name=f"laporan-{period.lower().replace(' ', '-')}.png",
                    mime="image/png",
                    width="stretch",
                    type="primary",
                )
            with d2:
                st.download_button(
                    "⬇ Unduh PDF",
                    data=cache["pdf"],
                    file_name=f"laporan-{period.lower().replace(' ', '-')}.pdf",
                    mime="application/pdf",
                    width="stretch",
                )

            if cache["key"] != cache_key:
                st.info("Konfigurasi berubah. Klik 'Generate Preview' untuk memperbarui.")
        else:
            st.markdown(f"""
            <div style='padding:60px 20px;text-align:center;color:{T.MUTED};
                        background:{T.BG_TINT};border-radius:12px;border:1px dashed {T.BORDER_STRONG};'>
              <div style='font-size:32px;margin-bottom:12px;'>🖼️</div>
              <div style='font-weight:600;color:{T.INK};margin-bottom:6px;'>Preview belum tersedia</div>
              <div style='font-size:13px;'>Pilih bagian yang ingin dimasukkan, lalu klik <b>Generate Preview</b>.</div>
              <div style='font-size:12px;margin-top:8px;color:{T.SUBTLE};'>
                Render pertama kali pada server cloud bisa memakan ~30 detik untuk setup engine.
              </div>
            </div>
            """, unsafe_allow_html=True)
