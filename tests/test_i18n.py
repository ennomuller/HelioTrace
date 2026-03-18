"""
Tests for the i18n module.

Covers:
- t() fallback chain (DE → EN → key)
- Key parity: every key in DE must exist in EN and vice versa
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from heliotrace.locale.de import DE
from heliotrace.locale.en import EN

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


@pytest.mark.parametrize("key", list(EN.keys()))
def test_en_values_non_empty(key: str) -> None:
    assert EN[key].strip(), f"EN['{key}'] is empty or whitespace-only"


@pytest.mark.parametrize("key", list(DE.keys()))
def test_de_values_non_empty(key: str) -> None:
    assert DE[key].strip(), f"DE['{key}'] is empty or whitespace-only"
