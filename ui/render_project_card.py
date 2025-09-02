# ui/render_project_card.py
import streamlit as st
from datetime import date

STATUS_LABELS = {"planned":"Planned","in_progress":"In Progress","completed":"Completed"}
STATUS_COLORS = {"planned":("#e2e8f0","#334155"), "in_progress":("#dbeafe","#1d4ed8"), "completed":("#dcfce7","#15803d")}

def _badge(status: str):
    s = status.value if hasattr(status, "value") else status
    label = STATUS_LABELS.get(s, s)
    bg, fg = STATUS_COLORS.get(s, ("#e2e8f0","#334155"))
    st.markdown(
        f"<span style='padding:4px 8px;border-radius:12px;background:{bg};color:{fg};"
        "border:1px solid rgba(0,0,0,0.06);font-weight:600;font-size:12px'>"
        f"{label}</span>", unsafe_allow_html=True
    )

def _progress_pct(start, end):
    if not start or not end: return 0
    today = date.today()
    if today <= start: return 0
    if today >= end:   return 100
    return round((today - start).days / max(1,(end - start).days) * 100)

def render_project_card(p, on_edit=None, details_url: str | None = None):
    box = st.container(border=True)
    with box:
        top = st.columns([6,2])
        with top[0]:
            st.markdown(f"### {p.title}")
            if getattr(p, "description", None):
                st.caption(p.description)
        with top[1]:
            _badge(getattr(p, "status", "planned"))

        pct = _progress_pct(getattr(p,"start_date",None), getattr(p,"end_date",None))
        sub = st.columns([5,1])
        with sub[0]:
            st.caption("Progress")
            st.progress(pct/100)
        with sub[1]:
            st.markdown(f"<div style='text-align:right;font-weight:600'>{pct}%</div>", unsafe_allow_html=True)

        c1,c2,c3 = st.columns(3)
        c1.caption(f"🏢 {getattr(p,'funder','—')}")
        c2.caption(f"👤 {getattr(p,'manager_user','—')}")
        sd = getattr(p,'start_date', None); ed = getattr(p,'end_date', None)
        c3.caption(f"📆 {sd:%b %d} - {ed:%b %d, %Y}" if sd and ed else "📆 —")

        a1, a2 = st.columns([4,1])
        if details_url:
            a1.link_button("View Details ↗", details_url, type="secondary", use_container_width=True)
        else:
            a1.button("View Details", disabled=True, use_container_width=True)
        if on_edit:
            a2.button("✏️", key=f"edit_{p.id}", help="Edit Project", on_click=lambda: on_edit(p))
