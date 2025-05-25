import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="Confirm Selections", layout="wide", initial_sidebar_state="collapsed")

from streamlit_cookies_manager import CookieManager
from src.various import handle_redirects
from src.various import get_pmid

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")

if not cookies.ready():
    st.stop()

handle_redirects(cookies)

# Set this variable to 1, 2, or 3 to test different pages
confirm_page = 2
# Get the PMID from cookies
pmid = get_pmid(cookies)

def get_doi_link(pmid):
    JSON_FOLDER = "Full_text_jsons"
    for filename in os.listdir(JSON_FOLDER):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(JSON_FOLDER, filename), "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    doc = raw[0]["documents"][0]
                    for passage in doc["passages"]:
                        infons = passage.get("infons", {})
                        doi = infons.get("article-id_doi")
                        if doi:
                            return f"https://doi.org/{doi}"
            except Exception:
                continue
    return None

doi_link = get_doi_link(pmid)

# --- Title and always-shown instructions ---
st.markdown(
    """
    <div style="margin-top: -75px;">
        <h1 style="font-size: 2.2rem; margin-bottom: 0.5rem;">Paper Annotation</h1>
        <span style="font-size:20px"><b>Coffee break : Confirm your selections</b></span>
    </div>
    """,
    unsafe_allow_html=True,
)

if confirm_page == 1:
    st.markdown("#### Experiment and Solution Types")

    # Editable table for experiments and solutions
    exp_df = pd.DataFrame([
        {
            "Experiment name": "Immunoprecipitation",
            "Alternative Experiment Name": "",
            "Experiment Type": "PI",
            "Solution name": "extraction solution",
            "Alternative Solution Name": "",
            "Solution Type": "PI"
        }
    ])

    edited_df = st.data_editor(
        exp_df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Experiment name": st.column_config.TextColumn("Experiment name", disabled=True),
            "Alternative Experiment Name": st.column_config.TextColumn("Alternative Experiment Name"),
            "Experiment Type": st.column_config.SelectboxColumn(
                "Experiment Type", options=["PI", "non-PI"]
            ),
            "Solution name": st.column_config.TextColumn("Solution name", disabled=True),
            "Alternative Solution Name": st.column_config.TextColumn("Alternative Solution Name"),
            "Solution Type": st.column_config.SelectboxColumn(
                "Solution Type", options=["PI", "non-PI"]
            ),
        },
        key="exp_editor"
    )

    # Validate and correct Solution Type based on Experiment Type
    corrected = False
    for idx, row in edited_df.iterrows():
        if row["Experiment Type"] == "non-PI" and row["Solution Type"] != "non-PI":
            edited_df.at[idx, "Solution Type"] = "non-PI"
            corrected = True

    if corrected:
        st.error("Solution Type was set to 'non-PI' for rows where Experiment Type is 'non-PI'.")

    # Save buttons
    col1, col2 = st.columns([1, 2])
    with col1:
        st.button("Save", use_container_width=True)
    with col2:
        st.button("Save & next", use_container_width=True)
elif confirm_page == 2:
    # Dropdowns for experiment and bait selection (can be expanded as needed)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.selectbox("Experiment", ["Experiment"], key="experiment_select")
    with col2:
        st.selectbox("Bait 1", ["Bait 1"], key="bait_select")

    st.markdown("### Bait details:")

    bait_df = pd.DataFrame([
        {
            "Bait type 1": "Protein",
            "Bait type 2": "Experimental",
            "Name": "ORF2p",
            "Alt name": "",
            "Tag": "N/A",
            "Alt tag": "",
            "Species": "HEK293T",
            "Alt. species": "H.sapiens",
        }
    ])
    st.data_editor(
        bait_df,
        num_rows="dynamic",
        use_container_width=True,
        key="bait_editor",
        column_config={
            "Bait type 1": st.column_config.TextColumn("Bait type 1", disabled=True),
            "Bait type 2": st.column_config.TextColumn("Bait type 2", disabled=True),
            "Name": st.column_config.TextColumn("Name", disabled=True),
            "Alt name": st.column_config.TextColumn("Alt name"),
            "Tag": st.column_config.TextColumn("Tag"),
            "Alt tag": st.column_config.TextColumn("Alt tag"),
            "Species": st.column_config.TextColumn("Species"),
            "Alt. species": st.column_config.TextColumn("Alt. species"),
        }
    )

    st.markdown("### Interactor(s) details:")

    interactor_df = pd.DataFrame([
        {
            "Bait ref": 1,
            "Interactor type": "protein",
            "Name": "",
            "Alternative name": "N/A",
            "Species": "HEK293T",
            "Alternative species": "H.sapiens",
        }
    ])
    st.data_editor(
        interactor_df,
        num_rows="dynamic",
        use_container_width=True,
        key="interactor_editor",
        column_config={
            "Bait ref": st.column_config.TextColumn("Bait ref", disabled=True),
            "Interactor type": st.column_config.TextColumn("Interactor type", disabled=True),
            "Name": st.column_config.TextColumn("Name", disabled=True),
            "Alternative name": st.column_config.TextColumn("Alternative name"),
            "Species": st.column_config.TextColumn("Species"),
            "Alternative species": st.column_config.TextColumn("Alternative species"),
        }
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        st.button("Save", use_container_width=True)
    with col2:
        st.button("Save & next", use_container_width=True)
elif confirm_page == 3:
    # Dropdowns
    col1, col2 = st.columns([1, 1])
    with col1:
        experiment_type = st.selectbox("Experiment Type", ["PI", "non-PI"], key="exp_type_3")
    with col2:
        if experiment_type == "PI":
            solution_type_options = ["PI", "non-PI"]
        else:
            solution_type_options = ["non-PI"]
        solution_type = st.selectbox("Solution Type", solution_type_options, key="sol_type_3")

    # pH, Temperature, Time
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        st.text_input("pH", value="7.4")
    with col2:
        st.text_input("Temperature (°C)", value="4", key="temperature_input")
    with col3:
        st.selectbox(
            "Time",
            [
                "0–5 min", "5–10 min", "10–15 min", "15–30 min", "30–60 min",
                "1–2 h", "2–4 h", "4–8 h", "8–16 h"
            ],
            key="time_select"
        )
    # Radio buttons
    st.radio(
        "Solution details",  # Non-empty label for accessibility
        ["Solution details not listed:", "Solution details listed:"],
        index=1,
        key="solution_details_radio",
        label_visibility="collapsed"  # Hides the label visually
    )

    # Editable table for solution details
    solution_df = pd.DataFrame([
        {
            "Chemical type": "Buffer",
            "Name": "HEPES",
            "Alternative name": "",
            "Quantity": "20",
            "Alternative Quantity": "",
            "Unit": "mM",
            "Alternative unit": ""
        }
    ])
    st.data_editor(
        solution_df,
        num_rows="dynamic",
        use_container_width=True,
        key="solution_editor",
        column_config={
            "Chemical type": st.column_config.SelectboxColumn(
                "Chemical type",
                options=[
                    "Buffer", "Salt", "Detergent", "Enzyme", "Inhibitor",
                    "Reducing agent", "Substrate", "Other"
                ]
            ),
            "Name": st.column_config.TextColumn("Name", disabled=True),
            "Quantity": st.column_config.TextColumn("Quantity", disabled=True),
            "Unit": st.column_config.TextColumn("Unit", disabled=True),
        }
    )

    # Save buttons
    col1, col2 = st.columns([1, 2])
    with col1:
        st.button("Save", use_container_width=True)
    with col2:
        st.button("Save & next", use_container_width=True)