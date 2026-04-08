"""
Tests for the i18n module.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from heliotrace.i18n import _get_lang_toggle_props
from heliotrace.locale.de import DE
from heliotrace.locale.en import EN

_SIDEBAR_STATUS_KEYS = [
    "sidebar.fill_example",
    "sidebar.fill_example_help",
    "sidebar.status_label",
    "sidebar.status_mapping",
    "sidebar.status_legend",
    "sidebar.status_missing",
    "sidebar.status_default",
    "sidebar.status_ready",
    "sidebar.section_event",
    "sidebar.section_target",
    "sidebar.section_gcs",
    "sidebar.section_ht",
    "sidebar.section_drag",
]

# ---------------------------------------------------------------------------
# Key parity
# ---------------------------------------------------------------------------


def test_de_keys_subset_of_en() -> None:
    """Every key in DE must also exist in EN (DE is a full translation of EN)."""
    missing = sorted(set(DE.keys()) - set(EN.keys()))
    assert missing == [], f"Keys in DE but not in EN: {missing}"


def test_en_keys_subset_of_de() -> None:
    """Every key in EN must also exist in DE (no EN string left untranslated)."""
    missing = sorted(set(EN.keys()) - set(DE.keys()))
    assert missing == [], f"Keys in EN but not in DE: {missing}"


def test_en_and_de_have_same_key_count() -> None:
    assert len(EN) == len(DE)


@pytest.mark.parametrize("key", _SIDEBAR_STATUS_KEYS)
def test_sidebar_status_keys_exist_in_both_locales(key: str) -> None:
    assert key in EN
    assert key in DE


# ---------------------------------------------------------------------------
# t() lookup and fallback behaviour
# ---------------------------------------------------------------------------


def test_t_returns_english_string() -> None:
    """t() returns the EN string when lang='en'."""
    import streamlit as st

    with patch.object(type(st.session_state), "get", return_value="en"):
        from heliotrace.i18n import t

        assert t("page.home.title") == EN["page.home.title"]


def test_t_returns_german_string() -> None:
    """t() returns the DE string when lang='de'."""
    with patch("streamlit.session_state") as mock_ss:
        mock_ss.get.return_value = "de"
        from heliotrace.i18n import t

        result = t("page.home.subtitle")
        assert result == DE["page.home.subtitle"]
        assert result != EN["page.home.subtitle"]


def test_t_falls_back_to_en_for_unknown_lang() -> None:
    """t() falls back to EN when an unknown language code is set."""
    with patch("streamlit.session_state") as mock_ss:
        mock_ss.get.return_value = "fr"
        from heliotrace.i18n import t

        assert t("page.home.title") == EN["page.home.title"]


def test_t_falls_back_to_key_for_unknown_key() -> None:
    """t() returns the key itself when it is absent from both locales."""
    with patch("streamlit.session_state") as mock_ss:
        mock_ss.get.return_value = "en"
        from heliotrace.i18n import t

        assert t("this.key.does.not.exist") == "this.key.does.not.exist"


# ---------------------------------------------------------------------------
# Sanity: no empty strings in either locale
# ---------------------------------------------------------------------------


def test_get_lang_toggle_props_defaults_to_english() -> None:
    props = _get_lang_toggle_props(None)

    assert props.current_lang == "en"
    assert props.target_lang == "de"
    assert props.label == "🇩🇪"
    assert props.help_text == "Switch language to German"


def test_get_lang_toggle_props_switches_to_english_from_german() -> None:
    props = _get_lang_toggle_props("de")

    assert props.current_lang == "de"
    assert props.target_lang == "en"
    assert props.label == "🇬🇧"
    assert props.help_text == "Switch language to English"


def test_get_lang_toggle_props_falls_back_for_unknown_language() -> None:
    props = _get_lang_toggle_props("fr")

    assert props.current_lang == "en"
    assert props.target_lang == "de"
    assert props.label == "🇩🇪"
    assert props.help_text == "Switch language to German"


@pytest.mark.parametrize("key", list(EN.keys()))
def test_en_values_non_empty(key: str) -> None:
    assert EN[key].strip(), f"EN['{key}'] is empty or whitespace-only"


@pytest.mark.parametrize("key", list(DE.keys()))
def test_de_values_non_empty(key: str) -> None:
    assert DE[key].strip(), f"DE['{key}'] is empty or whitespace-only"
