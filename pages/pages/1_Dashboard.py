import streamlit as st
from sqlalchemy import select
from db import SessionLocal, Project, ReportingPeriod, BudgetLine, Indicator
from ui.streamlit_portfolio_stats import render_portfolio_stats
from ui.render_projects_list import render_projects_list
from ui.render_recent_activity import render_recent_activity

st.set_page_config(page_title="Portfolio Overview", layout="wide")
st.title("Portfolio Overview")

s = SessionLocal()
projects     = s.execute(select(Project)).scalars().all()
periods      = s.execute(select(ReportingPeriod)).scalars().all()
budget_lines = s.execute(select(BudgetLine)).scalars().all()
indicators   = s.execute(select(Indicator)).scalars().all()

metrics = {
    "totalPlanned": sum(b.planned_amount or 0 for b in budget_lines),
    "totalActual":  sum(b.actual_amount  or 0 for b in budget_lines),
}
render_portfolio_stats(metrics, projects, periods, is_loading=False)

left, right = st.columns([2,1], gap="large")
with left:
    render_projects_list(projects, show_limit=5)
with right:
    render_recent_activity(periods, projects, limit=8)
