"""Sidebar filter controls."""

from __future__ import annotations

import streamlit as st
from datetime import date

from data import reference as R


def render_sidebar() -> dict:
    with st.sidebar:
        st.markdown(f"<div style='font-weight:700;font-size:18px;margin-bottom:4px;'>Filter</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#64748b;font-size:12px;margin-bottom:16px;'>Berlaku pada semua tab</div>", unsafe_allow_html=True)

        period_choice = st.radio(
            "Periode",
            ["Bulan ini (Mei 2026)", "Bulan lalu (Apr 2026)", "YTD 2026", "12 bulan terakhir", "Custom"],
            index=0,
        )
        date_range = None
        if period_choice == "Custom":
            date_range = st.date_input(
                "Rentang tanggal",
                value=(date(2026, 5, 1), date(2026, 5, 31)),
                min_value=date(2025, 6, 1),
                max_value=date(2026, 5, 31),
            )

        st.markdown("---")

        channels = st.multiselect(
            "Kanal",
            options=[c[0] for c in R.CHANNELS],
            default=[c[0] for c in R.CHANNELS],
        )
        topics = st.multiselect(
            "Topik",
            options=[t[0] for t in R.TOPICS],
            default=[t[0] for t in R.TOPICS],
        )
        requestors = st.multiselect(
            "Kategori Pemohon",
            options=[r[0] for r in R.REQUESTORS],
            default=[r[0] for r in R.REQUESTORS],
        )
        provinces = st.multiselect(
            "Wilayah",
            options=R.PROVINCES,
            default=[],
            help="Kosongkan untuk seluruh Indonesia",
        )

        st.markdown("---")
        st.caption("Data sintetis. Demo untuk presentasi klien.")

    # Resolve period_choice to a date range if not custom
    if period_choice == "Bulan ini (Mei 2026)":
        date_range = (date(2026, 5, 1), date(2026, 5, 31))
    elif period_choice == "Bulan lalu (Apr 2026)":
        date_range = (date(2026, 4, 1), date(2026, 4, 30))
    elif period_choice == "YTD 2026":
        date_range = (date(2026, 1, 1), date(2026, 5, 31))
    elif period_choice == "12 bulan terakhir":
        date_range = (date(2025, 6, 1), date(2026, 5, 31))

    return {
        "period_label": period_choice,
        "date_range": date_range,
        "channels": channels,
        "topics": topics,
        "requestors": requestors,
        "provinces": provinces,
    }
