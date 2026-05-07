"""Bank Indonesia — Dashboard Layanan Informasi Publik (LIP).
Streamlit mockup for client presentation. Mei 2026."""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*keyword arguments have been deprecated.*")
warnings.filterwarnings("ignore", message=".*use_container_width.*")

import streamlit as st

import theme as T
from data import generator as G
from components import header as H
from components.filters import render_sidebar
from tabs import overview, sxi, ssi, export, per_kanal


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
        "⭐ Detail Indeks",
        "🎯 Per Kanal",
        "💬 SSI · Sentimen Publik",
        "🖼️ Ekspor Infografis",
    ])

    with t1:
        overview.render(tickets, social, filters)
    with t2:
        sxi.render(tickets, filters)
    with t3:
        per_kanal.render(tickets, filters)
    with t4:
        ssi.render(social, filters)
    with t5:
        export.render(tickets, social)


if __name__ == "__main__":
    main()
