"""
Internationalisation helpers for HelioTrace.

Usage
-----
    from heliotrace.i18n import t, render_lang_toggle

    render_lang_toggle(t("page.home.title"))  # call once at the top of each page
"""

from __future__ import annotations

import streamlit as st

from heliotrace.locale.de import DE
from heliotrace.locale.en import EN

_LOCALES: dict[str, dict[str, str]] = {"en": EN, "de": DE}


def t(key: str) -> str:
    """Return the localised string for *key* in the active language.

    Fallback chain: DE → EN → key (so the app never shows a raw key).
    """
    lang = st.session_state.get("lang", "en")
    locale = _LOCALES.get(lang, EN)
    return locale.get(key, EN.get(key, key))


def render_lang_toggle(title: str) -> None:
    """Render the page title with 🇬🇧 / 🇩🇪 flag buttons inline on the right."""
    current_lang = st.session_state.get("lang", "en")
    col_title, col_toggle = st.columns([9, 1], vertical_alignment="center")

    with col_title:
        st.title(title)

    with col_toggle:
        c_en, c_de = st.columns(2, gap="small")

        with c_en:
            if st.button(
                "🇪🇳",
                key="lang_btn_en",
                type="primary" if current_lang == "en" else "secondary",
                use_container_width=True,
            ):
                st.session_state["lang"] = "en"
                st.rerun()

        with c_de:
            if st.button(
                "🇩🇪",
                key="lang_btn_de",
                type="primary" if current_lang == "de" else "secondary",
                use_container_width=True,
            ):
                st.session_state["lang"] = "de"
                st.rerun()
