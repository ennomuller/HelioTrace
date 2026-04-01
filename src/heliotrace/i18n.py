"""
Internationalisation helpers for HelioTrace.

Usage
-----
    from heliotrace.i18n import render_page_header, t

    render_page_header(t("page.home.title"))  # call once at the top of each page
"""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from heliotrace.locale.de import DE
from heliotrace.locale.en import EN

_LOCALES: dict[str, dict[str, str]] = {"en": EN, "de": DE}
_LANG_NAMES: dict[str, str] = {"en": "English", "de": "German"}
_LANG_FLAGS: dict[str, str] = {"en": "🇬🇧", "de": "🇩🇪"}
_HEADER_THEME = {
    "desktop_top_margin": "2rem",
    "mobile_top_margin": "0.5rem",
    "button_min_width": "3.5rem",
    "breakpoint": "768px",
}


def t(key: str) -> str:
    """Return the localised string for *key* in the active language.

    Fallback chain: DE → EN → key (so the app never shows a raw key).
    """
    lang = st.session_state.get("lang", "en")
    locale = _LOCALES.get(lang, EN)
    return locale.get(key, EN.get(key, key))


_PAGE_HEADER_CSS = f"""
<style>
    :root {{
        --header-desktop-margin: {_HEADER_THEME["desktop_top_margin"]};
        --header-mobile-margin: {_HEADER_THEME["mobile_top_margin"]};
        --btn-width: {_HEADER_THEME["button_min_width"]};
    }}

    /* Global resets for the header containers */
    .st-key-page-header-desktop, .st-key-page-header-mobile {{
        padding-top: 0;
    }}

    /* Grouped selectors to avoid repetition */
    .st-key-page-header-desktop h1,
    .st-key-page-header-desktop [data-testid="stHeading"] {{
        margin-top: var(--header-desktop-margin);
        padding-top: 0;
    }}

    .st-key-page-header-desktop button {{
        min-width: var(--btn-width);
        min-height: 2.5rem;
    }}

    .st-key-page-header-mobile {{
        display: none;
        margin-top: var(--header-mobile-margin);
    }}

    .st-key-page-header-mobile-toggle {{
        margin-bottom: 0.25rem;
    }}

    @media (max-width: {_HEADER_THEME["breakpoint"]}) {{
        .st-key-page-header-desktop {{ display: none; }}
        .st-key-page-header-mobile {{ display: block; }}
    }}
</style>
"""


@dataclass(frozen=True)
class LangToggleProps:
    """UI metadata for the language switch control."""

    current_lang: str
    target_lang: str
    label: str
    help_text: str


def _get_lang_toggle_props(current_lang: str | None) -> LangToggleProps:
    """Return deterministic UI metadata for the single-action language switch."""
    effective_lang = current_lang if current_lang in _LOCALES else "en"
    target_lang = "de" if effective_lang == "en" else "en"
    target_name = _LANG_NAMES[target_lang]
    return LangToggleProps(
        current_lang=effective_lang,
        target_lang=target_lang,
        label=_LANG_FLAGS[target_lang],
        help_text=f"Switch language to {target_name}",
    )


def _render_lang_toggle_button(props: LangToggleProps, *, key: str) -> None:
    """Render the toggle button and switch locale on click."""
    if st.button(props.label, key=key, help=props.help_text):
        st.session_state["lang"] = props.target_lang
        st.rerun()


def _render_lang_toggle_button_full_width(props: LangToggleProps, *, key: str) -> None:
    """Render a full-width toggle button for mobile layouts."""
    if st.button(props.label, key=key, help=props.help_text, use_container_width=True):
        st.session_state["lang"] = props.target_lang
        st.rerun()


def render_page_header(title: str) -> None:
    """Render a responsive page header with title and language switch."""
    props = _get_lang_toggle_props(st.session_state.get("lang"))
    st.markdown(_PAGE_HEADER_CSS, unsafe_allow_html=True)

    with st.container(key="page-header-desktop"):
        col_title, col_toggle = st.columns([12, 1], vertical_alignment="center")
        with col_title:
            st.title(title)
        with col_toggle:
            _render_lang_toggle_button(props, key="lang_btn_desktop")

    with st.container(key="page-header-mobile"):
        with st.container(key="page-header-mobile-toggle"):
            _render_lang_toggle_button_full_width(props, key="lang_btn_mobile")
        st.title(title)


def render_lang_toggle(title: str) -> None:
    """Backward-compatible alias for the responsive page header helper."""
    render_page_header(title)
