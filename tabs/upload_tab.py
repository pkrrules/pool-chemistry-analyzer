"""Tab 1 — upload a CSV of weekly pool chemistry readings."""

import streamlit as st

from data_io import CsvValidationError, TEMPLATE_PATH, load_default_history, validate_and_parse


def render() -> None:
    st.subheader("Upload your pool chemistry log")
    st.write(
        "Upload a CSV of weekly readings to drive the **Current State** and "
        "**Historical Trends** tabs. Until you upload one, those tabs show "
        "synthetic demo data."
    )

    with open(TEMPLATE_PATH, "rb") as f:
        st.download_button(
            "Download CSV template",
            f,
            file_name="pool_chemistry_template.csv",
            mime="text/csv",
        )

    uploaded = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded is not None:
        try:
            df = validate_and_parse(uploaded)
        except CsvValidationError as exc:
            st.error(f"Upload failed: {exc}")
        else:
            st.session_state["history_df"] = df
            st.session_state["using_uploaded_data"] = True
            st.success(
                f"Loaded {len(df)} row(s). Current State and Historical Trends "
                "now reflect this file."
            )

    if st.session_state.get("using_uploaded_data"):
        st.info("Currently showing your uploaded data.")
        if st.button("Reset to synthetic demo data"):
            st.session_state["history_df"] = load_default_history()
            st.session_state["using_uploaded_data"] = False
            st.rerun()
    else:
        st.caption("Currently showing synthetic demo data.")

    st.divider()
    st.markdown("**Preview**")
    st.dataframe(st.session_state["history_df"], width='stretch')
