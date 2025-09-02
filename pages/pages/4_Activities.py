# pages/4_Activities.py
import streamlit as st
import datetime as dt
from sqlalchemy import select
from db import SessionLocal, Project, FrameworkNode, FrameworkLevel, Activity, Status

st.set_page_config(page_title="Activities", layout="wide")
st.title("Activities")

session = SessionLocal()

# Select a project
projects = session.execute(select(Project)).scalars().all()
if not projects:
    st.info("Create a project first.")
    st.stop()

project = st.selectbox("Select Project", projects, format_func=lambda x: x.title)

# Load outputs for this project
outputs = session.execute(
    select(FrameworkNode).where(
        FrameworkNode.project_id == project.id,
        FrameworkNode.level == FrameworkLevel.output
    )
).scalars().all()

if not outputs:
    st.warning("Add Outputs in the Framework page first.")
    st.stop()

# --- Create new activity ---
st.subheader("New Activity")
with st.form("new_activity", clear_on_submit=True):
    output = st.selectbox("Output", outputs, format_func=lambda n: n.title)
    title = st.text_input("Activity title *")
    c1, c2 = st.columns(2)
    start = c1.date_input("Start date", dt.date.today())
    end   = c2.date_input("End date", dt.date.today())
    status = st.selectbox("Status", [s.value for s in Status], index=0)
    owner  = st.text_input("Owner (email) *")

    submitted = st.form_submit_button("Save")
    if submitted:
        if not title or not owner:
            st.error("Title and Owner are required.")
        elif start > end:
            st.error("Start date must be before end date.")
        else:
            act = Activity(
                project_id=project.id,
                framework_node_id=output.id,
                title=title,
                start_date=start,
                end_date=end,
                status=Status(status),
                owner_user=owner
            )
            session.add(act)
            session.commit()
            st.success("Activity added.")
            st.experimental_rerun()

# --- List existing activities ---
st.subheader("Current Activities")
activities = session.execute(
    select(Activity).where(Activity.project_id == project.id)
).scalars().all()

if activities:
    for a in activities:
        st.write(
            f"- **{a.title}** | {a.start_date} → {a.end_date} "
            f"| Status: {a.status.value} | Owner: {a.owner_user}"
        )
else:
    st.info("No activities yet.")
