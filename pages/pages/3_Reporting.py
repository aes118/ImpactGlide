import streamlit as st
from sqlalchemy import select
from db import SessionLocal, Project, ReportingPeriod, Indicator, IndicatorTarget, IndicatorActual

st.set_page_config(page_title="Reporting", layout="wide")
st.title("Reporting – Targets & Actuals")

s = SessionLocal()
projects = s.execute(select(Project)).scalars().all()
if not projects: st.info("Create a project first."); st.stop()

p = st.selectbox("Project", projects, format_func=lambda x: x.title)
periods = s.execute(select(ReportingPeriod).where(ReportingPeriod.project_id==p.id)).scalars().all()
if not periods: st.warning("Generate reporting periods on Projects page."); st.stop()

rp = st.selectbox("Reporting period", periods, format_func=lambda r: r.label)
inds = s.execute(select(Indicator).where(Indicator.project_id==p.id)).scalars().all()
if not inds: st.info("Add indicators on the Framework page."); st.stop()

st.subheader("Enter values")
for ind in inds:
    c1,c2,c3 = st.columns([3,1,1])
    c1.markdown(f"**{ind.name}** ({ind.unit})")
    t = s.execute(select(IndicatorTarget).where(IndicatorTarget.indicator_id==ind.id, IndicatorTarget.period_id==rp.id)).scalar_one_or_none()
    a = s.execute(select(IndicatorActual).where(IndicatorActual.indicator_id==ind.id, IndicatorActual.period_id==rp.id)).scalar_one_or_none()
    tval = c2.number_input("Target", value=t.target_value if t else 0.0, key=f"t_{ind.id}")
    aval = c3.number_input("Actual", value=a.actual_value if a else 0.0, key=f"a_{ind.id}")
    if st.button("Save", key=f"save_{ind.id}"):
        if t: t.target_value = tval
        else: s.add(IndicatorTarget(indicator_id=ind.id, period_id=rp.id, target_value=tval))
        if a: a.actual_value = aval
        else: s.add(IndicatorActual(indicator_id=ind.id, period_id=rp.id, actual_value=aval))
        s.commit(); st.success("Saved.")
