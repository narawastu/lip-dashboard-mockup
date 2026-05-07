"""Page-scoped inline filter row. Used on Per Kanal for wilayah + demografi cuts."""

from __future__ import annotations

import streamlit as st

import theme as T
from data import reference as R


PK_KEYS = ["flt_pk_wilayah", "flt_pk_usia", "flt_pk_gender"]


def reset_per_kanal_filters() -> None:
    for k in PK_KEYS:
        if k in st.session_state:
            del st.session_state[k]


def render_per_kanal_inline() -> dict:
    """Inline filter row for the Per Kanal page. Returns selected values."""

    if st.session_state.get("_pk_reset_pending"):
        st.session_state["_pk_reset_pending"] = False
        reset_per_kanal_filters()

    label_html = (
        f"<div style='display:flex;align-items:baseline;justify-content:space-between;"
        f"margin-top:6px;margin-bottom:8px;'>"
        f"<div style='font-size:11px;font-weight:700;letter-spacing:0.12em;"
        f"text-transform:uppercase;color:{T.SUBTLE};'>FILTER ANALISA</div></div>"
    )
    st.markdown(label_html, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([3, 3, 3, 1])
    with c1:
        wilayah = st.multiselect(
            "Wilayah Koordinasi",
            options=R.WILAYAH_NAMES,
            default=st.session_state.get("flt_pk_wilayah", []),
            placeholder=f"Semua ({len(R.WILAYAH_NAMES)})",
            key="flt_pk_wilayah",
            label_visibility="visible",
        )
    with c2:
        usia = st.multiselect(
            "Usia",
            options=[a[0] for a in R.AGE_BRACKETS],
            default=st.session_state.get("flt_pk_usia", []),
            placeholder=f"Semua ({len(R.AGE_BRACKETS)})",
            key="flt_pk_usia",
            label_visibility="visible",
        )
    with c3:
        gender = st.multiselect(
            "Jenis Kelamin",
            options=[g[0] for g in R.GENDERS],
            default=st.session_state.get("flt_pk_gender", []),
            placeholder=f"Semua ({len(R.GENDERS)})",
            key="flt_pk_gender",
            label_visibility="visible",
        )
    with c4:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        any_active = bool(wilayah or usia or gender)
        if any_active:
            if st.button("Reset", key="flt_pk_reset", width="stretch",
                         help="Reset filter analisa di tab ini"):
                st.session_state["_pk_reset_pending"] = True
                st.rerun()

    # Subtle separator under the filter row
    st.markdown(
        f"<div style='border-bottom:1px solid {T.BORDER};margin:8px 0 18px 0;'></div>",
        unsafe_allow_html=True,
    )

    return {
        "wilayah": wilayah,
        "usia": usia,
        "gender": gender,
        "any_active": any_active,
    }


def sparse_callout(n: int, threshold: int = 30) -> bool:
    """Show an amber callout when filter combo yields very few rows.
    Returns True if a callout (or empty state) was shown — caller may want to skip charts."""
    if n == 0:
        st.markdown(
            f"""
            <div style='background:rgba(220,38,38,0.06);border:1px solid rgba(220,38,38,0.3);
                        border-radius:10px;padding:14px 16px;margin-bottom:14px;
                        color:{T.NEG};font-size:13px;'>
              <b>Tidak ada data untuk kombinasi filter ini.</b><br>
              <span style='color:{T.MUTED};font-weight:500;'>Coba longgarkan filter wilayah atau demografi.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return True
    if n < threshold:
        st.markdown(
            f"""
            <div style='background:rgba(217,119,6,0.07);border:1px solid rgba(217,119,6,0.3);
                        border-radius:10px;padding:12px 16px;margin-bottom:14px;
                        color:#92400E;font-size:13px;'>
              Hanya <b>{n}</b> tiket dengan filter ini. Data mungkin tidak representatif.
            </div>
            """,
            unsafe_allow_html=True,
        )
    return False
