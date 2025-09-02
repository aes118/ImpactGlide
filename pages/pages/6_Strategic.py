# pages/6_Strategic.py
import streamlit as st
from sqlalchemy import select
from db import (
    SessionLocal, StrategicIndicator, IndicatorMapping, Indicator,
    IndicatorTarget, IndicatorActual, Direction
)

st.set_page_config(page_title="Strategic Alignment", layout="wide")
st.title("Strategic Alignment")

s = SessionLocal()

# Simple creators (optional)
with st.expander("Add Strategic Indicator"):
    code = st.text_input("Code (unique)")
    name = st.text_input("Name")
    unit = st.text_input("Unit")
    direction = st.selectbox("Direction", [d.value for d in Direction], index=0)
    if st.button("Create KPI"):
        if code and name and unit:
            s.add(StrategicIndicator(code=code, name=name, unit=unit, direction=Direction(direction)))
            s.commit()
            st.success("Strategic indicator created.")

# Data
skpis = s.execute(select(StrategicIndicator)).scalars().all()
inds  = {i.id: i for i in s.execute(select(Indicator)).scalars().all()}
maps  = s.execute(select(IndicatorMapping)).scalars().all()
tmap  = {(t.indicator_id, t.period_id): t.target_value for t in s.execute(select(IndicatorTarget)).scalars().all()}
amap  = {(a.indicator_id, a.period_id): a.actual_value for a in s.execute(select(IndicatorActual)).scalars().all()}

if not skpis:
    st.info("Create at least one Strategic Indicator to see alignment.")
    st.stop()

# Simple mapper (optional)
with st.expander("Map a Project Indicator to a Strategic KPI"):
    if inds:
        kpi = st.selectbox("Strategic KPI", skpis, format_func=lambda k: f"{k.code} – {k.name}")
        ind = st.selectbox("Project Indicator", list(inds.values()), format_func=lambda x: x.name)
        if st.button("Map"):
            s.add(IndicatorMapping(indicator_id=ind.id, strategic_indicator_id=kpi.id))
            s.commit()
            st.success("Mapped.")
    else:
        st.caption("No project indicators yet.")

st.divider()
st.subheader("KPI Status")

for kpi in skpis:
    mapped = [m.indicator_id for m in maps if m.strategic_indicator_id == kpi.id]
    checked = on = 0
    for (ind_id, per_id), tgt in tmap.items():
        if ind_id not in mapped:
            continue
        act = amap.get((ind_id, per_id))
        if act is None:
            continue
        ind = inds.get(ind_id)
        if not ind:
            continue
        checked += 1
        if (kpi.direction == Direction.increase and act >= tgt) or \
           (kpi.direction == Direction.decrease and act <= tgt):
            on += 1
    st.markdown(f"**{kpi.code} – {kpi.name}** ({kpi.unit})  •  On track: **{on} / {checked}**")
