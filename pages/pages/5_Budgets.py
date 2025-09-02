# pages/5_Budgets.py
import streamlit as st
from sqlalchemy import select
from db import SessionLocal, Project, Activity, BudgetLine

st.set_page_config(page_title="Budgets", layout="wide")
st.title("Budgets")

s = SessionLocal()

# Choose project
projects = s.execute(select(Project)).scalars().all()
if not projects:
    st.info("Create a project first.")
    st.stop()
p = st.selectbox("Project", projects, format_func=lambda x: x.title)

# Activities for that project
acts = s.execute(select(Activity).where(Activity.project_id == p.id)).scalars().all()
if not acts:
    st.warning("Add activities first on the Activities page.")
    st.stop()

# Add budget line
st.subheader("Add Budget Line")
with st.form("new_bl", clear_on_submit=True):
    a = st.selectbox("Activity", acts, format_func=lambda x: x.title)
    fy = st.text_input("Fiscal year *", "FY25")
    planned = st.number_input("Planned amount *", min_value=0.0, value=0.0, step=100.0)
    actual  = st.number_input("Actual amount",  min_value=0.0, value=0.0, step=100.0)
    if st.form_submit_button("Save"):
        if not fy:
            st.error("Fiscal year is required.")
        else:
            s.add(BudgetLine(project_id=p.id, activity_id=a.id, fiscal_year=fy,
                             planned_amount=planned, actual_amount=actual))
            s.commit()
            st.success("Budget line added.")
            st.experimental_rerun()

# List budget lines + totals
st.subheader("Budget Lines")
bls = s.execute(select(BudgetLine).where(BudgetLine.project_id == p.id)).scalars().all()
tot_planned = sum(b.planned_amount for b in bls)
tot_actual  = sum(b.actual_amount  for b in bls)
st.write(f"**Totals** — Planned: {tot_planned:,.0f} | Actual: {tot_actual:,.0f}")

for b in bls:
    act = next((x for x in acts if x.id == b.activity_id), None)
    st.write(f"- {b.fiscal_year} | {act.title if act else b.activity_id} "
             f"| Planned {b.planned_amount:,.0f} | Actual {b.actual_amount:,.0f}")
