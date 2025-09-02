import streamlit as st
from sqlalchemy import select
from db import SessionLocal, Project, ReportingPeriod, PeriodStatus
from ui.project_form import project_form
from ui.render_project_card import render_project_card
from db import generate_reporting_periods

st.set_page_config(page_title="Projects", layout="wide")
st.title("Projects")

s = SessionLocal()

# New project
if st.toggle("New project"):
    if project_form(None):
        st.experimental_rerun()

# List & edit
projects = s.execute(select(Project)).scalars().all()
for p in projects:
    render_project_card(p, on_edit=lambda proj=p: project_form(proj))
    if st.button(f"Generate reporting periods for {p.title}", key=f"gen_{p.id}"):
        generate_reporting_periods(s, p)
        st.success("Reporting periods generated.")
        st.experimental_rerun()
