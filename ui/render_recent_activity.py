# ui/render_recent_activity.py
import streamlit as st
from datetime import date

BADGE_STYLES = {
    "open":     ("#dbeafe","#1d4ed8"),
    "overdue":  ("#fee2e2","#b91c1c"),
    "submitted":("#fef9c3","#a16207"),
    "approved": ("#dcfce7","#15803d"),
}

def _badge(text, kind="open"):
    bg, fg = BADGE_STYLES.get(kind, ("#e2e8f0","#334155"))
    st.markdown(
        f"<span style='padding:2px 8px;border:1px solid rgba(0,0,0,.06);"
        f"background:{bg};color:{fg};border-radius:10px;font-size:11px;font-weight:600'>{text}</span>",
        unsafe_allow_html=True
    )

def render_recent_activity(periods, projects, limit=8):
    st.subheader("Recent Activity")
    if not periods:
        st.info("No recent activity.")
        return

    proj_title = {p.id: getattr(p, "title", f"Project {p.id}") for p in projects}
    s = sorted(periods, key=lambda rp: rp.due_date or date.min, reverse=True)[:limit]

    for rp in s:
        status = rp.status.value if hasattr(rp, "status") else rp.status
        is_overdue = (rp.due_date and date.today() > rp.due_date and status == "open")
        actual = "overdue" if is_overdue else status
        with st.container():
            st.markdown("---")
            top = st.columns([5,1])
            with top[0]:
                st.markdown(f"**{rp.label}**")
            with top[1]:
                _badge(actual, actual)
            st.caption(proj_title.get(getattr(rp, "project_id", None), "Unknown project"))
            if rp.due_date:
                st.caption(f"Due: {rp.due_date:%b %d, %Y}")
