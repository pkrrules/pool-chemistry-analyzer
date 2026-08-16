"""Tab 3 — historical trend lines per parameter, with the ideal band shaded."""

import plotly.express as px
import streamlit as st

from thresholds import DATE_COLUMN, PARAMETERS

PLOTLY_TEMPLATE = "plotly_white"
GOOD_BAND = "rgba(12,163,12,0.10)"


def render() -> None:
    df = st.session_state["history_df"]
    if df.empty:
        st.warning("No data available.")
        return

    st.subheader("Historical trends")

    date_min, date_max = df[DATE_COLUMN].min().date(), df[DATE_COLUMN].max().date()
    date_range = st.slider("Date range", date_min, date_max, (date_min, date_max))
    fdf = df[df[DATE_COLUMN].dt.date.between(*date_range)]

    if fdf.empty:
        st.info("No readings in the selected date range.")
        return

    param_by_label = {p.label: p for p in PARAMETERS}
    chosen = st.multiselect(
        "Parameters to show", list(param_by_label.keys()), default=list(param_by_label.keys())
    )

    for label in chosen:
        p = param_by_label[label]
        st.markdown(f"**{p.label} over time** ({p.unit or 'unitless'})")
        fig = px.line(fdf, x=DATE_COLUMN, y=p.key, markers=True)
        lo, hi = p.green
        fig.add_hrect(
            y0=lo, y1=hi, fillcolor=GOOD_BAND, line_width=0,
            annotation_text="ideal", annotation_position="top left",
        )
        fig.update_layout(template=PLOTLY_TEMPLATE, margin=dict(t=10), yaxis_title=p.unit or "")
        st.plotly_chart(fig, width='stretch')

    with st.expander("Water temperature (context, not graded)"):
        fig = px.line(fdf, x=DATE_COLUMN, y="Water_Temperature_F", markers=True)
        fig.update_layout(template=PLOTLY_TEMPLATE, margin=dict(t=10))
        st.plotly_chart(fig, width='stretch')

    with st.expander("Show data / download CSV"):
        st.dataframe(fdf, width='stretch')
        st.download_button(
            "Download filtered CSV",
            fdf.to_csv(index=False).encode(),
            file_name="pool_chemistry_filtered.csv",
        )
