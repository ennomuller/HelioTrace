"""
HelioTrace — Home page.
"""

import streamlit as st

from heliotrace.i18n import render_lang_toggle, t

# ---------------------------------------------------------------------------
# Language toggle
# ---------------------------------------------------------------------------
render_lang_toggle(t("page.home.title"))

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.subheader(t("page.home.subtitle"))
st.markdown(t("page.home.intro"))

st.divider()

# ---------------------------------------------------------------------------
# Quick Start
# ---------------------------------------------------------------------------
st.subheader(t("page.home.quickstart_title"))
st.markdown(t("page.home.quickstart_flow"))
st.info(t("page.home.quickstart_tip"))

st.divider()

# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------
st.subheader(t("page.home.features_title"))
col1, col2 = st.columns(2)
with col1:
    st.markdown(t("page.home.features_col1"))
with col2:
    st.markdown(t("page.home.features_col2"))

st.divider()

# ---------------------------------------------------------------------------
# Science Background
# ---------------------------------------------------------------------------
st.subheader(t("page.home.science_title"))
st.markdown(t("page.home.science_body"))

st.markdown(t("page.home.frameworks_title"))
st.markdown(t("page.home.frameworks_intro"))
st.markdown(t("page.home.frameworks_table"))

st.divider()

# ---------------------------------------------------------------------------
# Acknowledgments
# ---------------------------------------------------------------------------
with st.expander(t("page.home.ack_expander"), expanded=False):
    st.markdown(t("page.home.ack_body"))

st.divider()

# ---------------------------------------------------------------------------
# Data source notice
# ---------------------------------------------------------------------------
st.caption(t("page.home.data_caption"))

# ---------------------------------------------------------------------------
# SEO injection (hidden)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="display:none">
        <h2>Keywords</h2>
        <p>HelioTrace, Solar physics simulation, Heliospheric modeling, Coronal Mass Ejection,
        Space weather forecasting Python, ICME arrival time, Drag-Based Model, GCS model,
        Solar eruption, CME propagation, Streamlit space weather app.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
