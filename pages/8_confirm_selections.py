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

# --- Breadcrumbs ---
st.markdown(
    """
    <div style="font-size: 15px; margin-bottom: 10px;">
        <a href="#">Experiment picker</a> &gt; 
        <a href="#">Solution picker</a> &gt; 
        <span style="color: #888;">Experiment details</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Title and always-shown instructions ---
st.markdown(
    """
    # Paper Annotation
    <span style="font-size:20px"><b>Coffee break : Confirm your selections</b></span>
    """,
    unsafe_allow_html=True,
)

# --- Page-specific description ---
if confirm_page == 1:
    st.markdown(
        """
        <div style="font-size:15px; margin-top: 10px;">
        In the previous steps you identified all PI and non-PI experiments and the solutions used in the paper. Take a moment to review your selections below before you move on to the next two steps: collect details on the identified PI experiments and PI solution composition.<br>
        You also have the ability to add alternative names typically used for these experiments and solutions in the scientific literature.
        </div>
        """,
        unsafe_allow_html=True,
    )
elif confirm_page == 2:
    st.markdown(
        """
        <div style="font-size:15px; margin-top: 10px;">
        For each of the PI solutions that you identified in the second step, find their detailed composition in the text after selecting the right button for the type of chemical. If the composition of a solution used in the experiments is not described in detail but instead is offered as a reference to previous work, then select that reference (tab "References") when the corresponding button pressed.
        </div>
        """,
        unsafe_allow_html=True,
    )
elif confirm_page == 3:
    st.markdown(
        """
        <div style="font-size:15px; margin-top: 10px;">
        For each of the PI solutions that you identified in the second step, find their detailed composition in the text after selecting the right button for the type of chemical. If the composition of a solution used in the experiments is not described in detail but instead is offered as a reference to previous work, then select that reference (tab "References") when the corresponding button pressed.
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Go to full-text paper button  ---   
if doi_link:
    st.link_button("Go to full-text paper", doi_link)

# --- Page-specific content ---
if confirm_page == 1:
    # Editable table for experiments and solutions
    exp_df = pd.DataFrame([
        {
            "": "○",
            "Experiment name": "Immunoprecipitation",
            "Alternative Experiment Name": "",
            "Experiment Type": "PI",
            "Solution name": "extraction solution",
            "Alternative Solution Name": "",
            "Solution Type": "PI"
        },
        {
            "": "○",
            "Experiment name": "Immunoprecipitation",
            "Alternative Experiment Name": "",
            "Experiment Type": "PI",
            "Solution name": "washing solution",
            "Alternative Solution Name": "lysis buffer",
            "Solution Type": "PI"
        },
        {
            "": "○",
            "Experiment name": "MS screen",
            "Alternative Experiment Name": "Protein Mass spectrometry",
            "Experiment Type": "non-PI",
            "Solution name": "",
            "Alternative Solution Name": "",
            "Solution Type": ""
        }
    ])
    st.data_editor(
        exp_df,
        num_rows="dynamic",
        use_container_width=True,
        key="exp_editor"
    )

    # Save buttons
    col1, col2 = st.columns([1, 2])
    with col1:
        st.button("Save", use_container_width=True)
    with col2:
        st.button("Save & next", use_container_width=True)

elif confirm_page == 2:
    # Dropdowns
    col1, col2 = st.columns([1, 1])
    with col1:
        st.selectbox("Experiment", ["Experiment"], key="experiment_select")
    with col2:
        st.selectbox("Bait 1", ["Bait 1"], key="bait_select")

    st.markdown("### Bait details:")

    bait_df = pd.DataFrame([
        {
            "": "○",
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
        key="bait_editor"
    )

    st.markdown("### Interactor(s) details:")

    interactor_df = pd.DataFrame([
        {
            "": "○",
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
        key="interactor_editor"
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
        st.selectbox("Experiment", ["Experiment"], key="experiment_select")
    with col2:
        st.selectbox("Solution", ["Solution"], key="solution_select")

    # pH, Temperature, Time
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        st.text_input("pH", value="7.4")
    with col2:
        st.text_input("Temperature", value="4")
        st.markdown('<span style="position:relative; left:40px; top:-38px;">°C</span>', unsafe_allow_html=True)
    with col3:
        st.selectbox("Time", ["30min - 1h"], key="time_select")

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
            "": "○",
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
        key="solution_editor"
    )

    # Save buttons
    col1, col2 = st.columns([1, 2])
    with col1:
        st.button("Save", use_container_width=True)
    with col2:
        st.button("Save & next", use_container_width=True)