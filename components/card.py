"""Card helper. Uses Streamlit's native st.container(border=True) which actually
contains its children, then styles it via CSS to match our brand cards."""

from __future__ import annotations

from contextlib import contextmanager
import streamlit as st


@contextmanager
def card(label: str | None = None, elevated: bool = False):
    """Bordered container with optional title label at top."""
    container = st.container(border=True)
    with container:
        if elevated:
            st.markdown("<div class='bi-card-elev-tag'></div>", unsafe_allow_html=True)
        if label:
            st.markdown(
                f"<div class='bi-card-title'>{label}</div>",
                unsafe_allow_html=True,
            )
        yield container
