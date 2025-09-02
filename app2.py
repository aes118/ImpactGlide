# Revised Streamlit Form Logic for Hierarchical Logframe Input
# Baseline/Target/Result required at Outcome & Output only

import streamlit as st
from datetime import date

st.set_page_config(page_title="Hierarchical Logframe Builder")
st.title("📋 Hierarchical Logframe Builder")

# Helper functions for ID generation
import uuid

def generate_id():
    return str(uuid.uuid4())[:8]

# Session state containers
for key in ["impacts", "outcomes", "outputs", "activities"]:
    if key not in st.session_state:
        st.session_state[key] = []

# ---------------- Impact ----------------
st.header("Step 1: Define Impact(s)")
with st.form("impact_form", clear_on_submit=True):
    imp_name = st.text_input("Impact Objective")
    imp_indicator = st.text_input("Impact Indicator (optional)")
    imp_baseline = st.text_input("Baseline (optional)")
    imp_target = st.text_input("Target (optional)")
    imp_result = st.text_input("Result to Date (optional)")
    if st.form_submit_button("Add Impact") and imp_name:
        st.session_state.impacts.append({
            "id": generate_id(),
            "level": "Impact",
            "name": imp_name,
            "indicator": imp_indicator,
            "baseline": imp_baseline,
            "target": imp_target,
            "result": imp_result
        })

if st.session_state.impacts:
    st.table([{"Impact": i["name"]} for i in st.session_state.impacts])

# ---------------- Outcome ----------------
st.header("Step 2: Define Outcomes")
if not st.session_state.impacts:
    st.warning("Please define at least one Impact before adding Outcomes.")
else:
    with st.form("outcome_form", clear_on_submit=True):
        out_name = st.text_input("Outcome Objective")
        out_impact = st.selectbox("Linked Impact", options=st.session_state.impacts, format_func=lambda x: x["name"])
        out_indicator = st.text_input("Outcome Indicator")
        out_baseline = st.number_input("Baseline", value=0.0)
        out_target = st.number_input("Target", value=0.0)
        out_result = st.number_input("Result to Date", value=0.0)
        if st.form_submit_button("Add Outcome") and out_name and out_indicator:
            st.session_state.outcomes.append({
                "id": generate_id(),
                "level": "Outcome",
                "name": out_name,
                "parent_id": out_impact["id"],
                "indicator": out_indicator,
                "baseline": out_baseline,
                "target": out_target,
                "result": out_result
            })

# ---------------- Output ----------------
st.header("Step 3: Define Outputs")
if not st.session_state.outcomes:
    st.warning("Please define at least one Outcome before adding Outputs.")
else:
    with st.form("output_form", clear_on_submit=True):
        outp_name = st.text_input("Output Objective")
        outp_outcome = st.selectbox("Linked Outcome", options=st.session_state.outcomes, format_func=lambda x: x["name"])
        outp_indicator = st.text_input("Output Indicator")
        outp_baseline = st.number_input("Baseline", value=0.0, key="output_baseline")
        outp_target = st.number_input("Target", value=0.0, key="output_target")
        outp_result = st.number_input("Result to Date", value=0.0, key="output_result")
        if st.form_submit_button("Add Output") and outp_name and outp_indicator:
            st.session_state.outputs.append({
                "id": generate_id(),
                "level": "Output",
                "name": outp_name,
                "parent_id": outp_outcome["id"],
                "indicator": outp_indicator,
                "baseline": outp_baseline,
                "target": outp_target,
                "result": outp_result
            })

# ---------------- Activity ----------------
st.header("Step 4: Define Activities")
if not st.session_state.outputs:
    st.warning("Please define at least one Output before adding Activities.")
else:
    with st.form("activity_form", clear_on_submit=True):
        act_name = st.text_input("Activity Name")
        act_output = st.selectbox("Linked Output", options=st.session_state.outputs, format_func=lambda x: x["name"])
        act_indicator = st.text_input("Activity Indicator (optional)")
        act_baseline = st.text_input("Baseline (optional)")
        act_target = st.text_input("Target (optional)")
        act_result = st.text_input("Result to Date (optional)")
        if st.form_submit_button("Add Activity") and act_name:
            st.session_state.activities.append({
                "id": generate_id(),
                "level": "Activity",
                "name": act_name,
                "parent_id": act_output["id"],
                "indicator": act_indicator,
                "baseline": act_baseline,
                "target": act_target,
                "result": act_result
            })
