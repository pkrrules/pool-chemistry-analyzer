"""Tab 2 — traffic-light view of the most recent reading."""

import streamlit as st

from thresholds import CONTEXT_COLUMNS, DATE_COLUMN, PARAMETERS, STATUS_COLORS, STATUS_LABELS, classify


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def render() -> None:
    df = st.session_state["history_df"]
    if df.empty:
        st.warning("No data available.")
        return

    latest = df.sort_values(DATE_COLUMN).iloc[-1]
    st.subheader(f"Current state — as of {latest[DATE_COLUMN].date()}")

    statuses = {p.key: classify(p, latest[p.key]) for p in PARAMETERS}
    n_red = sum(1 for s in statuses.values() if s == "red")
    n_yellow = sum(1 for s in statuses.values() if s == "yellow")

    if n_red:
        st.error(f"🔴 {n_red} parameter(s) need immediate attention.")
    elif n_yellow:
        st.warning(f"🟡 {n_yellow} parameter(s) to watch.")
    else:
        st.success("🟢 All parameters are in the ideal range.")

    cols = st.columns(3)
    for i, p in enumerate(PARAMETERS):
        status = statuses[p.key]
        color = STATUS_COLORS[status]
        value = latest[p.key]
        with cols[i % 3]:
            st.markdown(
                f"""
                <div style="border-left: 6px solid {color}; border-radius: 6px;
                            padding: 0.75rem 1rem; margin-bottom: 1rem;
                            background: {_hex_to_rgba(color, 0.10)};">
                  <div style="font-size: 0.85rem; opacity: 0.7;">{p.label}</div>
                  <div style="font-size: 1.6rem; font-weight: 600;">
                    {value:g}{(' ' + p.unit) if p.unit else ''}
                  </div>
                  <div style="font-size: 0.8rem; color: {color}; font-weight: 600;">
                    {STATUS_LABELS[status]}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown("**Context (not graded green/yellow/red)**")
    ctx_cols = st.columns(len(CONTEXT_COLUMNS))
    for i, key in enumerate(CONTEXT_COLUMNS):
        ctx_cols[i].metric(key.replace("_", " "), f"{latest[key]:g}")
