# Revised Streamlit App with Tabs, Popups, File Upload, GLIDE Branding

import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from PIL import Image
import uuid
import streamlit as st
import base64
import os

# --- CONFIG ---
st.set_page_config(page_title="Grant Application Portal", layout="wide")

def add_png_logo(path: str,
                 width_px: int = 140,
                 top_px: int = 14,
                 right_px: int = 18,
                 link: str | None = None,
                 max_height_px: int = 84):
    if not os.path.exists(path):
        st.error(f"Logo file not found: {path}")
        return
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    img = f'<img src="data:image/png;base64,{b64}" alt="GLIDE Logo" style="width:100%;height:auto;max-height:{max_height_px}px;display:block;object-fit:contain;" />'
    if link:
        img = f'<a href="{link}" target="_blank" rel="noopener">{img}</a>'

    st.markdown(f"""
        <style>
            .glide-logo-fixed {{
                position: fixed;
                top: {top_px}px;
                right: {right_px}px;
                width: {width_px}px;
                z-index: 10000;
                background: #fff;
                padding: 6px 8px;
                border-radius: 10px;
                box-shadow: 0 2px 8px rgba(0,0,0,.12);
                pointer-events: none;        /* don't block UI */
            }}
            .glide-logo-fixed a, .glide-logo-fixed img {{ pointer-events: auto; }}
        </style>
        <div class="glide-logo-fixed">{img}</div>
    """, unsafe_allow_html=True)

# Call once, before your tabs/content:
add_png_logo("glide_logo.png", width_px=140, top_px=14, right_px=18, link="https://glideae.org")



# --- STATE INIT ---
def generate_id():
    return str(uuid.uuid4())[:8]

for key in ["impacts", "outcomes", "outputs", "activities", "workplan", "budget"]:
    if key not in st.session_state:
        st.session_state[key] = []

# --- APP TABS ---
tabs = st.tabs(["📘 Instructions", "🧱 Logframe", "🗂️ Workplan", "💵 Budget", "📤 Export"])

# ---------------- TAB 1: Instructions ----------------
tabs[0].markdown("""
# 📝 Welcome to the Falcon Awards Application Portal

Please complete each section of your application:
1. **Logframe** – your project goals, results, and indicators
2. **Workplan** – planned activities and timelines
3. **Budget** – detailed costing for each activity

Once done, export your application as an Excel file.

**Contact us**: grants@glide.org | +971-XXX-XXXX
""")

# ---------------- TAB 2: Logframe ----------------
tabs[1].header("📊 Build Your Logframe")

# Upload existing file to resume
uploaded_file = tabs[1].file_uploader("Resume Previous Submission (Excel)", type="xlsx")

# Display and add popups for each level
with tabs[1].expander("➕ Add Impact"):
    with st.form("impact_form"):
        imp_name = st.text_input("Impact Objective")
        imp_indicator = st.text_input("Impact Indicator (optional)")
        imp_baseline = st.text_input("Baseline (optional)")
        imp_target = st.text_input("Target (optional)")
        imp_result = st.text_input("Result to Date (optional)")
        if st.form_submit_button("Add Impact") and imp_name:
            st.session_state.impacts.append({
                "id": generate_id(), "level": "Impact", "name": imp_name,
                "indicator": imp_indicator, "baseline": imp_baseline,
                "target": imp_target, "result": imp_result
            })

with tabs[1].expander("➕ Add Outcome"):
    if st.session_state.impacts:
        with st.form("outcome_form"):
            out_name = st.text_input("Outcome")
            out_impact = st.selectbox("Linked to Impact", st.session_state.impacts, format_func=lambda x: x['name'])
            out_indicator = st.text_input("Outcome Indicator")
            out_baseline = st.number_input("Baseline", key="ob")
            out_target = st.number_input("Target", key="ot")
            out_result = st.number_input("Result to Date", key="or")
            if st.form_submit_button("Add Outcome") and out_name:
                st.session_state.outcomes.append({
                    "id": generate_id(), "level": "Outcome", "name": out_name,
                    "parent_id": out_impact["id"], "indicator": out_indicator,
                    "baseline": out_baseline, "target": out_target, "result": out_result
                })
    else:
        st.warning("Add at least one Impact first.")

with tabs[1].expander("➕ Add Output"):
    if st.session_state.outcomes:
        with st.form("output_form"):
            outp_name = st.text_input("Output")
            outp_outcome = st.selectbox("Linked to Outcome", st.session_state.outcomes, format_func=lambda x: x['name'])
            outp_indicator = st.text_input("Output Indicator")
            outp_baseline = st.number_input("Baseline", key="pb")
            outp_target = st.number_input("Target", key="pt")
            outp_result = st.number_input("Result to Date", key="pr")
            if st.form_submit_button("Add Output") and outp_name:
                st.session_state.outputs.append({
                    "id": generate_id(), "level": "Output", "name": outp_name,
                    "parent_id": outp_outcome["id"], "indicator": outp_indicator,
                    "baseline": outp_baseline, "target": outp_target, "result": outp_result
                })
    else:
        st.warning("Add at least one Outcome first.")

with tabs[1].expander("➕ Add Activity"):
    if st.session_state.outputs:
        with st.form("activity_form"):
            act_name = st.text_input("Activity")
            act_output = st.selectbox("Linked to Output", st.session_state.outputs, format_func=lambda x: x['name'])
            act_indicator = st.text_input("Indicator (optional)")
            act_baseline = st.text_input("Baseline (optional)")
            act_target = st.text_input("Target (optional)")
            act_result = st.text_input("Result to Date (optional)")
            if st.form_submit_button("Add Activity") and act_name:
                st.session_state.activities.append({
                    "id": generate_id(), "level": "Activity", "name": act_name,
                    "parent_id": act_output["id"], "indicator": act_indicator,
                    "baseline": act_baseline, "target": act_target, "result": act_result
                })
    else:
        st.warning("Add at least one Output first.")

# ---------------- TAB 3: Workplan ----------------
tabs[2].header("📆 Define Workplan")
with tabs[2].form("workplan_form"):
    activity = st.text_input("Activity")
    owner = st.text_input("Responsible Person")
    start = st.date_input("Start Date")
    end = st.date_input("End Date")
    milestone = st.text_input("Milestone")
    if st.form_submit_button("Add to Workplan"):
        st.session_state.workplan.append([activity, owner, str(start), str(end), milestone])
if st.session_state.workplan:
    tabs[2].dataframe(st.session_state.workplan, use_container_width=True)

# ---------------- TAB 4: Budget ----------------
tabs[3].header("💵 Define Budget")
with tabs[3].form("budget_form"):
    item = st.text_input("Line Item")
    category = st.selectbox("Category", ["Personnel", "Supplies", "Travel", "Other"])
    quantity = st.number_input("Quantity", value=1)
    unit_cost = st.number_input("Unit Cost", value=0.0)
    total = quantity * unit_cost
    if st.form_submit_button("Add to Budget"):
        st.session_state.budget.append([item, category, quantity, unit_cost, total])
if st.session_state.budget:
    tabs[3].dataframe(st.session_state.budget, use_container_width=True)

# ---------------- TAB 5: Export ----------------
tabs[4].header("📤 Export Your Application")
if tabs[4].button("Generate Excel File"):
    wb = Workbook()
    # Logframe tab
    log_ws = wb.active
    log_ws.title = "Logframe"
    log_ws.append(["Level", "Name", "Parent ID", "Indicator", "Baseline", "Target", "Result"])
    for section in ["impacts", "outcomes", "outputs", "activities"]:
        for row in st.session_state[section]:
            log_ws.append([
                row.get("level"), row.get("name"), row.get("parent_id", "-"),
                row.get("indicator"), row.get("baseline"),
                row.get("target"), row.get("result")
            ])
    # Workplan
    ws2 = wb.create_sheet("Workplan")
    ws2.append(["Activity", "Owner", "Start Date", "End Date", "Milestone"])
    for row in st.session_state.workplan:
        ws2.append(row)
    # Budget
    ws3 = wb.create_sheet("Budget")
    ws3.append(["Line Item", "Category", "Quantity", "Unit Cost", "Total"])
    for row in st.session_state.budget:
        ws3.append(row)
    # Download
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    tabs[4].download_button("📥 Download Excel File", data=output, file_name="Application_Submission.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
