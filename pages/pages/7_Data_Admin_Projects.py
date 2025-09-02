import io
import streamlit as st
import pandas as pd
from sqlalchemy import select, func
from db import (
    SessionLocal, Project, ReportingPeriod, PeriodStatus,
    generate_reporting_periods
)
from import_export import df_from_query, to_csv_download, upsert_from_df

st.set_page_config(page_title="Data Admin – Projects", layout="wide")
st.title("Data • Project")

s = SessionLocal()

# ============================= Actions bar =============================
c1, c2, c3, c4, c5 = st.columns([1,1,1,1,1])
add_clicked     = c1.button("➕ Add")
import_clicked  = c2.button("⬆️ Import")
export_clicked  = c3.button("⬇️ Export")
schema_clicked  = c4.button("📐 Schema")
delete_clicked  = c5.button("🗑️ Delete All", type="secondary")

st.divider()

# ============================= Add (single quick add) ==================
if add_clicked:
    with st.form("add_project"):
        title = st.text_input("Title *")
        col1, col2 = st.columns(2)
        start = col1.date_input("Start date *")
        end   = col2.date_input("End date *")
        manager = st.text_input("Manager email *")
        funder  = st.text_input("Funder *")
        desc    = st.text_area("Description")
        over    = st.number_input("Overhead rate", 0.0, 1.0, 0.15, 0.01)
        go = st.form_submit_button("Create")
        if go:
            if not (title and manager and funder):
                st.error("Title, Manager, Funder are required.")
            else:
                p = Project(title=title, start_date=start, end_date=end,
                            manager_user=manager, funder=funder,
                            description=desc, overhead_rate=over)
                s.add(p); s.commit()
                generate_reporting_periods(s, p)
                st.success("Project created; reporting periods generated.")
                st.experimental_rerun()

# ============================= Export ==============================
if export_clicked:
    FIELDS = ["id","title","description","start_date","end_date","status",
              "manager_user","funder","overhead_rate","notes","revised_on"]
    df = df_from_query(s, Project, FIELDS)
    csv, name = to_csv_download(df, "projects_export.csv")
    st.download_button("Download CSV", data=csv, file_name=name, mime="text/csv")

# ============================= Import ===============================
if import_clicked:
    st.info("Upload a CSV/Excel with headers: id,title,description,start_date,end_date,status,manager_user,funder,overhead_rate,notes,revised_on")
    file = st.file_uploader("Choose file", type=["csv","xlsx"])
    if file:
        up = pd.read_excel(file) if file.name.lower().endswith(".xlsx") else pd.read_csv(file)
        st.write("Preview:")
        st.dataframe(up.head(20), use_container_width=True)
        if st.button("Apply updates / inserts", type="primary"):
            from db import Status  # enum
            created, updated = upsert_from_df(
                s, Project, up,
                id_field="id",
                enum_fields={"status": {x.value for x in Status}},
                date_fields=["start_date","end_date","revised_on"],
                create_missing=True, update_existing=True,
                required_fields=["title","start_date","end_date","manager_user","funder"]
            )
            st.success(f"Applied. Created: {created}, Updated: {updated}")
            st.info("Tip: use the button below to generate reporting periods for any new projects without periods.")

        # optional batch: generate periods for any project lacking them
        if st.button("Generate reporting periods for ALL projects without periods"):
            proj_ids = [p.id for p in s.execute(select(Project.id)).scalars().all()]
            has_periods = {pid for (pid,) in s.execute(select(ReportingPeriod.project_id).group_by(ReportingPeriod.project_id)).all()}
            to_gen = [pid for pid in proj_ids if pid not in has_periods]
            for pid in to_gen:
                p = s.get(Project, pid)
                if p: generate_reporting_periods(s, p)
            st.success(f"Generated periods for {len(to_gen)} projects.")

# ============================= Schema view =========================
if schema_clicked:
    st.caption("Columns in table `project` (from db.py):")
    st.code("""
id               INTEGER (pk)
title            TEXT (required)
description      TEXT
start_date       DATE (required)
end_date         DATE (required)
status           ENUM('planned','in_progress','completed') default 'planned'
manager_user     TEXT (required)
funder           TEXT (required)
overhead_rate    REAL default 0.15
notes            TEXT
revised_on       DATE
""", language="text")

# ============================= Delete all ==========================
if delete_clicked:
    if st.checkbox("Yes, I understand this will delete ALL Project rows permanently."):
        s.query(Project).delete()
        s.commit()
        st.warning("All projects deleted.")

# ============================= Table (like Base44 grid) ============
st.subheader("Project table")
rows = s.execute(select(Project)).scalars().all()
import pandas as pd
df = pd.DataFrame([{
    "title": p.title,
    "description": p.description,
    "start_date": p.start_date,
    "end_date": p.end_date,
    "status": p.status.value if hasattr(p.status, "value") else p.status,
    "manager_user": p.manager_user,
    "funder": p.funder
} for p in rows])
st.dataframe(df, use_container_width=True)
