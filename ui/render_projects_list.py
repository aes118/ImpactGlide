# ui/render_projects_list.py
import streamlit as st

STATUS_LABELS = {"planned":"Planned","in_progress":"In Progress","completed":"Completed"}
STATUS_COLORS = {"planned":("#e2e8f0","#334155"), "in_progress":("#dbeafe","#1d4ed8"), "completed":("#dcfce7","#15803d")}

def _status_badge(status: str):
    s = status.value if hasattr(status, "value") else status
    label = STATUS_LABELS.get(s, s)
    bg, fg = STATUS_COLORS.get(s, ("#e2e8f0","#334155"))
    st.markdown(
        f"<span style='padding:4px 8px;border-radius:12px;background:{bg};color:{fg};"
        "border:1px solid rgba(0,0,0,0.06);font-weight:600;font-size:12px'>"
        f"{label}</span>", unsafe_allow_html=True
    )

def render_projects_list(projects, show_limit=5):
    st.subheader("Active Projects")
    if not projects:
        st.info("No projects yet. Create your first project on the Projects page.")
        return
    for p in projects[:show_limit]:
        with st.container():
            st.markdown("---")
            head, badge = st.columns([4,1])
            with head:
                st.markdown(f"**{p.title}**")
                if getattr(p, "description", ""):
                    st.caption(p.description)
            with badge:
                _status_badge(getattr(p, "status", "planned"))
            m1,m2,m3 = st.columns(3)
            m1.caption(f"🏢 {getattr(p,'funder','—')}")
            m2.caption(f"👤 {getattr(p,'manager_user','—')}")
            sd = getattr(p,'start_date', None); ed = getattr(p,'end_date', None)
            m3.caption(f"📆 {sd:%b %d} – {ed:%b %d, %Y}" if sd and ed else "📆 —")
