"""
Streamlit session-state initialisation.

Call ``init_session_state()`` once at the top of every page that uses shared state.
Keeping this in a dedicated module avoids circular imports while remaining
importable only inside a running Streamlit context.
"""

from __future__ import annotations


def init_session_state() -> None:
    """
    Initialise all expected session-state keys with safe ``None`` defaults.

    Only keys that are absent are written, so calling this multiple times is safe.
    """
    import streamlit as st  # local import keeps the module importable outside Streamlit

    from heliotrace.config import KEY_SIM_CONFIG, KEY_SIM_RESULTS

    defaults: dict = {
        KEY_SIM_RESULTS: None,
        KEY_SIM_CONFIG: None,
        "lang": "en",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
