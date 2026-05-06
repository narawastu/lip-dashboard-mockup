"""Sidebar filter controls."""

from __future__ import annotations

import streamlit as st
from datetime import date, timedelta

from data import reference as R
from data import generator as G


PERIOD_LABELS = [
    "Bulan ini (Mei 2026)",
    "Bulan lalu (Apr 2026)",
    "YTD 2026",
    "12 bulan terakhir",
    "Custom",
]

COMPARE_LABELS = [
    "Bulan sebelumnya",
    "Tahun lalu (periode sama)",
    "Tidak ada",
]


def _resolve_period(choice: str, custom_range=None) -> tuple:
    if choice == "Bulan ini (Mei 2026)":
        return (date(2026, 5, 1), date(2026, 5, 31))
    if choice == "Bulan lalu (Apr 2026)":
        return (date(2026, 4, 1), date(2026, 4, 30))
    if choice == "YTD 2026":
        return (date(2026, 1, 1), date(2026, 5, 31))
    if choice == "12 bulan terakhir":
        return (date(2025, 6, 1), date(2026, 5, 31))
    if choice == "Custom" and custom_range and len(custom_range) == 2:
        return custom_range
    return (date(2026, 5, 1), date(2026, 5, 31))


def render_sidebar() -> dict:
    # Reset state if requested
    if st.session_state.get("_filter_reset_pending"):
        st.session_state["_filter_reset_pending"] = False
        for key in list(st.session_state.keys()):
            if key.startswith("flt_"):
                del st.session_state[key]

    with st.sidebar:
        st.markdown(
            "<div style='display:flex;justify-content:space-between;align-items:center;'>"
            "<div style='font-weight:700;font-size:18px;'>Filter</div>"
            "<div></div></div>", unsafe_allow_html=True,
        )
        st.markdown("<div style='color:#64748b;font-size:12px;margin-bottom:14px;'>Berlaku pada semua tab</div>", unsafe_allow_html=True)

        if st.button("Reset filter", width="stretch", key="flt_reset_btn"):
            st.session_state["_filter_reset_pending"] = True
            st.rerun()

        st.markdown("---")

        period_choice = st.radio(
            "Periode", PERIOD_LABELS, index=0, key="flt_period",
        )
        custom_range = None
        if period_choice == "Custom":
            custom_range = st.date_input(
                "Rentang tanggal",
                value=(date(2026, 5, 1), date(2026, 5, 31)),
                min_value=date(2025, 6, 1),
                max_value=date(2026, 5, 31),
                key="flt_custom_range",
            )

        compare_choice = st.radio(
            "Bandingkan dengan", COMPARE_LABELS, index=0, key="flt_compare",
        )

        st.markdown("---")

        channels = st.multiselect(
            "Kanal", options=[c[0] for c in R.CHANNELS],
            default=[c[0] for c in R.CHANNELS], key="flt_channels",
        )
        topics = st.multiselect(
            "Topik", options=[t[0] for t in R.TOPICS],
            default=[t[0] for t in R.TOPICS], key="flt_topics",
        )
        wilayah = st.multiselect(
            "Wilayah Koordinasi", options=R.WILAYAH_NAMES,
            default=R.WILAYAH_NAMES, key="flt_wilayah",
        )

        with st.expander("Demografi", expanded=False):
            usia = st.multiselect(
                "Usia", options=[a[0] for a in R.AGE_BRACKETS],
                default=[a[0] for a in R.AGE_BRACKETS], key="flt_usia",
            )
            gender = st.multiselect(
                "Jenis Kelamin", options=[g[0] for g in R.GENDERS],
                default=[g[0] for g in R.GENDERS], key="flt_gender",
            )

        with st.expander("Lainnya", expanded=False):
            requestors = st.multiselect(
                "Kategori Pemohon", options=[r[0] for r in R.REQUESTORS],
                default=[r[0] for r in R.REQUESTORS], key="flt_requestors",
            )

        st.markdown("---")
        st.caption("Data sintetis. Demo untuk presentasi klien.")

    date_range = _resolve_period(period_choice, custom_range)
    # Resolve comparison range
    if compare_choice == "Bulan sebelumnya":
        compare_range = G.previous_period(date_range)
    elif compare_choice == "Tahun lalu (periode sama)":
        compare_range = G.same_period_prior_year(date_range)
    else:
        compare_range = None

    return {
        "period_label": period_choice,
        "compare_label": compare_choice,
        "date_range": date_range,
        "compare_range": compare_range,
        "channels": channels,
        "topics": topics,
        "wilayah": wilayah,
        "usia": usia,
        "gender": gender,
        "requestors": requestors,
        "provinces": [],  # legacy field, kept for compat
    }
