# ui/project_form.py
import streamlit as st
import datetime as dt
import re
from db import SessionLocal, Project, Status, generate_reporting_periods

EMAIL_RE = re.compile(r"[^@]+@[^@]+\.[^@]+")

def project_form(existing: Project | None = None):
    s = SessionLocal()
    st.subheader("Edit Project" if existing else "Create New Project")
    with st.form("project_form", clear_on_submit=(existing is None)):
        colA, colB = st.columns(2)
        title  = colA.text_input("Project Title *", value=getattr(existing, "title", ""))
        funder = colB.text_input("Funder *", value=getattr(existing, "funder", ""))

        colC, colD = st.columns(2)
        manager = colC.text_input("Project Manager *", value=getattr(existing, "manager_user", ""))
        status_v = colD.selectbox("Status", [s.value for s in Status],
                                  index=( [s.value for s in Status].index(existing.status.value) if existing else 0 ))

        colE, colF = st.columns(2)
        start = colE.date_input("Start Date *", value=getattr(existing, "start_date", dt.date.today()))
        end   = colF.date_input("End Date *",   value=getattr(existing, "end_date",   dt.date.today().replace(month=12,day=31)))
        overhead = st.number_input("Overhead Rate", min_value=0.0, max_value=1.0,
                                   value=getattr(existing, "overhead_rate", 0.15), step=0.01)
        desc = st.text_area("Description", value=getattr(existing, "description", ""), height=90)
        notes= st.text_area("Notes", value=getattr(existing, "notes", ""), height=70)

        cancel = st.form_submit_button("Cancel")
        save   = st.form_submit_button("Save")

        if save:
            errs=[]
            if not title: errs.append("Title is required.")
            if not funder: errs.append("Funder is required.")
            if not manager or not EMAIL_RE.match(manager): errs.append("Valid manager email required.")
            if start > end: errs.append("Start must be on/before End.")
            if errs:
                for e in errs: st.error(e)
                return False

            if existing is None:
                p = Project(title=title, description=desc, start_date=start, end_date=end,
                            status=Status(status_v), manager_user=manager, funder=funder,
                            overhead_rate=overhead, notes=notes, revised_on=dt.date.today())
                s.add(p); s.commit()
                generate_reporting_periods(s, p)
                st.success("Project created and reporting periods generated.")
            else:
                existing.title=title; existing.description=desc
                existing.start_date=start; existing.end_date=end
                existing.status=Status(status_v)
                existing.manager_user=manager; existing.funder=funder
                existing.overhead_rate=overhead; existing.notes=notes
                existing.revised_on=dt.date.today()
                s.commit()
                st.success("Project updated.")
            return True
    return False
