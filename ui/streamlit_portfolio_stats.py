# ui/streamlit_portfolio_stats.py
import streamlit as st

def _skeleton_card():
    c = st.container(border=True)
    c.write(" ")
    c.caption("loading…")
    return c

def render_portfolio_stats(metrics, projects, periods, is_loading=False):
    if is_loading:
        cols = st.columns(4)
        for i in range(4):
            with cols[i]:
                _skeleton_card()
        return

    total_planned = metrics.get("totalPlanned", 0.0)
    total_actual  = metrics.get("totalActual", 0.0)
    # support enum or string statuses
    def sv(x): return x.value if hasattr(x, "value") else x
    active_projects = sum(1 for p in projects if sv(getattr(p, "status", "")) == "in_progress")
    open_periods    = sum(1 for rp in periods if sv(getattr(rp, "status", "")) == "open")

    cards = [
        ("Total Planned Budget", f"${total_planned:,.0f}"),
        ("Total Actual Spend",   f"${total_actual:,.0f}"),
        ("Active Projects",      f"{active_projects}"),
        ("Open Reporting Periods", f"{open_periods}")
    ]

    cols = st.columns(4)
    for col, (title, value) in zip(cols, cards):
        with col:
            box = st.container(border=True)
            box.caption(title)
            box.markdown(
                f"<span style='font-size:26px; font-weight:700'>{value}</span>",
                unsafe_allow_html=True
            )
