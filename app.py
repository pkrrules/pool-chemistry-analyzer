"""
Pool Chemistry Analyzer — Streamlit entry point.

Run with:
    uv run streamlit run app.py
"""

import streamlit as st

from data_io import load_default_history
from tabs import current_tab, history_tab, upload_tab

st.set_page_config(page_title="Pool Chemistry Analyzer", page_icon="🏊", layout="wide")

if "history_df" not in st.session_state:
    st.session_state["history_df"] = load_default_history()
if "using_uploaded_data" not in st.session_state:
    st.session_state["using_uploaded_data"] = False

st.title("🏊 Pool Chemistry Analyzer")
st.caption(
    "Upload your own weekly readings, or explore the synthetic 5-year demo "
    "history shown by default."
)

tab_upload, tab_current, tab_history = st.tabs(
    ["📤 Upload CSV", "🚦 Current State", "📈 Historical Trends"]
)

with tab_upload:
    upload_tab.render()

with tab_current:
    current_tab.render()

with tab_history:
    history_tab.render()
