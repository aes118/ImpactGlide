import streamlit as st
import datetime as dt
import pandas as pd
from sqlalchemy import select
from db import SessionLocal, init_db, Project, ReportingPeriod, PeriodStatus, FrameworkNode, FrameworkLevel, Indicator

st.set_page_config(page_title="ImpactGLIDE", layout="wide")
st.title("GLIDE Grants & Impact")

init_db()
session = SessionLocal()

page = st.sidebar.radio("Navigate", ["Projects","Framework","Reporting"])

# --- Projects ---
if page=="Projects":
    st.subheader("New Project")
    with st.form("new_project"):
        title = st.text_input("Title")
        start = st.date_input("Start date", dt.date.today())
        end = st.date_input("End date", dt.date.today().replace(month=12, day=31))
        overhead = st.number_input("Overhead rate",0.0,0.5,0.15,step=0.01)
        submit = st.form_submit_button("Create")
        if submit and title:
            p = Project(title=title,start_date=start,end_date=end,overhead_rate=overhead)
            session.add(p); session.commit()
            st.success("Created.")

    st.subheader("Projects")
    for p in session.execute(select(Project)).scalars().all():
        with st.expander(f"{p.title} ({p.start_date}→{p.end_date})"):
            if st.button("Generate Reporting Periods", key=f"gen_{p.id}"):
                # Baseline
                rp = ReportingPeriod(project_id=p.id,label="Baseline",start_date=p.start_date,end_date=p.start_date,
                                     due_date=p.start_date+dt.timedelta(days=15),status=PeriodStatus.open)
                session.merge(rp)
                # Quarters
                for year in range(p.start_date.year,p.end_date.year+1):
                    for q,(sm,em) in {"Q1":(1,3),"Q2":(4,6),"Q3":(7,9),"Q4":(10,12)}.items():
                        start=dt.date(year,sm,1); end=dt.date(year,em,28)
                        if end<p.start_date or start>p.end_date: continue
                        label=f"{q}-{year}"
                        rp=ReportingPeriod(project_id=p.id,label=label,start_date=start,end_date=end,
                                           due_date=end+dt.timedelta(days=15),status=PeriodStatus.open)
                        session.merge(rp)
                session.commit(); st.success("Reporting periods generated.")
            periods=session.execute(select(ReportingPeriod).where(ReportingPeriod.project_id==p.id)).scalars().all()
            if periods:
                st.dataframe(pd.DataFrame([{"Label":rp.label,"Start":rp.start_date,"End":rp.end_date,"Status":rp.status} for rp in periods]))

# --- Framework ---
if page=="Framework":
    st.subheader("Add Outcomes, Outputs, Indicators")
    projects=session.execute(select(Project)).scalars().all()
    if projects:
        proj=st.selectbox("Project",projects,format_func=lambda x:x.title)
        with st.form("add_outcome"):
            out=st.text_input("Outcome")
            if st.form_submit_button("Add Outcome") and out:
                node=FrameworkNode(project_id=proj.id,level=FrameworkLevel.outcome,title=out)
                session.add(node); session.commit()
        outcomes=session.execute(select(FrameworkNode).where(FrameworkNode.project_id==proj.id,FrameworkNode.level==FrameworkLevel.outcome)).scalars().all()
        if outcomes:
            with st.form("add_output"):
                parent=st.selectbox("Outcome",outcomes,format_func=lambda n:n.title)
                outp=st.text_input("Output")
                if st.form_submit_button("Add Output") and outp:
                    node=FrameworkNode(project_id=proj.id,parent_node_id=parent.id,level=FrameworkLevel.output,title=outp)
                    session.add(node); session.commit()
        outputs=session.execute(select(FrameworkNode).where(FrameworkNode.project_id==proj.id,FrameworkNode.level==FrameworkLevel.output)).scalars().all()
        if outputs:
            with st.form("add_indicator"):
                parent=st.selectbox("Output",outputs,format_func=lambda n:n.title)
                ind=st.text_input("Indicator")
                if st.form_submit_button("Add Indicator") and ind:
                    i=Indicator(project_id=proj.id,framework_node_id=parent.id,name=ind)
                    session.add(i); session.commit()

# --- Reporting ---
if page=="Reporting":
    st.subheader("Enter results")
    projects=session.execute(select(Project)).scalars().all()
    if projects:
        proj=st.selectbox("Project",projects,format_func=lambda x:x.title)
        periods=session.execute(select(ReportingPeriod).where(ReportingPeriod.project_id==proj.id)).scalars().all()
        if periods:
            st.write("Periods:",[p.label for p in periods])
