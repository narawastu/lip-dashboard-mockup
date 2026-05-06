"""Bank Indonesia — Dashboard Layanan Informasi Publik (LIP).
Streamlit mockup for client presentation. Mei 2026."""

import streamlit as st

import theme as T
from data import generator as G
from components import header as H
from components.filters import render_sidebar
from tabs import overview, sxi, ssi, export, operations


def main() -> None:
    st.set_page_config(
        page_title="Dashboard LIP — Bank Indonesia",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject theme CSS
    st.markdown(T.CSS, unsafe_allow_html=True)

    # Brand header
    H.render_header()

    # Sidebar filters (returns dict)
    filters = render_sidebar()

    # Generate data once (cached)
    with st.spinner("Memuat data…"):
        tickets = G.generate_tickets()
        social = G.generate_social()

    # Tabs
    t1, t2, t3, t4, t5 = st.tabs([
        "📊 Ringkasan Eksekutif",
        "⭐ SXI · Experience",
        "💬 SSI · Sentimen Publik",
        "🖼️ Ekspor Infografis",
        "⚙️ Operasional & Drill-Down",
    ])

    with t1:
        overview.render(tickets, social, filters)
    with t2:
        sxi.render(tickets, filters)
    with t3:
        ssi.render(social, filters)
    with t4:
        export.render(tickets, social)
    with t5:
        operations.render(tickets, filters)


if __name__ == "__main__":
    main()
