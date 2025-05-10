import streamlit as st
import os
import json
import pandas as pd
from streamlit_cookies_manager import CookieManager
from src.various import get_pmid, handle_redirects

# Set page config
st.set_page_config(page_title="Browse Paper", layout="wide", initial_sidebar_state="collapsed")

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

# Paths
JSON_FOLDER = "Full_text_jsons"
USERS_TABLE_PATH = "AWS_S3\\users_table.xlsx"

# Function to load the selected paper's JSON file based on the PMID
def load_paper_by_pmid(pmid):
    for filename in os.listdir(JSON_FOLDER):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(JSON_FOLDER, filename), "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    # Check if the PMID matches
                    doc = raw[0]["documents"][0]
                    front = doc["passages"][0]  # Front matter
                    meta = front["infons"]
                    extracted_pmid = meta.get("article-id_pmid", None)
                    if extracted_pmid == pmid:
                        return raw
            except Exception as e:
                st.error(f"Error reading file {filename}: {e}")
    st.error(f"No JSON file found for PMID: {pmid}")
    st.stop()

# Fetch the PMID
pmid = get_pmid(cookies)

# Load the selected paper's JSON file
raw = load_paper_by_pmid(pmid)
doc = raw[0]["documents"][0]

# Extract paper metadata
front = doc["passages"][0]  # Front matter
meta = front["infons"]
title = front["text"]
# Extract and clean up authors
authors = []
for k, v in meta.items():
    if k.startswith("name_"):
        parts = v.split(";")
        surname = next((p.split(":")[1] for p in parts if p.startswith("surname:")), "").strip()
        given_names = next((p.split(":")[1] for p in parts if p.startswith("given-names:")), "").strip()
        if surname and given_names:
            authors.append(f"{given_names} {surname}")
        elif surname:
            authors.append(surname)
        elif given_names:
            authors.append(given_names)
authors_str = ", ".join(authors)

# Dynamically construct the metadata parts
metadata_parts = []
if meta.get("issue", "?") != "?":
    metadata_parts.append(f"**Issue:** {meta['issue']}")
if meta.get("volume", "?") != "?":
    metadata_parts.append(f"**Volume:** {meta['volume']}")
fpage = meta.get("fpage", "N/A")
lpage = meta.get("lpage", "N/A")
if fpage != "N/A" and lpage != "N/A":
    metadata_parts.append(f"**Pages:** {fpage}-{lpage}")
year = meta.get("year", "?")
if year != "?":
    metadata_parts.append(f"**Year:** {year}")

# ...existing imports and setup...

# Construct the DOI link if available
doi = meta.get("article-id_doi", "")
doi_link = f"https://doi.org/{doi}" if doi else None

# Display paper metadata with reduced top margin
st.markdown(f"""
    <div style="margin-top: -50px;">
        <h3>You have selected to annotate the paper:</h3>
        <strong>{authors_str}</strong>, <em>{title}</em>
    </div>
""", unsafe_allow_html=True)
if metadata_parts:
    st.markdown(", ".join(metadata_parts))

# Add a centered descriptive paragraph
st.markdown("###")
col1, col2, col3 = st.columns([0.5, 3, 0.5])  # Create three columns for centering
with col2:  # Use the middle column
    st.markdown("""
        <div style="text-align: center; margin-bottom: -100px; margin-top: -40px;">
            Use the link to the full-text paper to scan through it and then answer the quick questionnaire below. 
            In this stage, you can go back through the "Pick another" button and change the paper as many times as you want. 
            You will be allowed to abandon a "Confirmed Paper" later only twice. 
            If you are happy with your selection, press "Confirm paper" to proceed to annotating your current selection.
        </div>
    """, unsafe_allow_html=True)

# Center the "Go to full-text paper" button
st.markdown("###")
col1, col2, col3 = st.columns([1.5, 1, 1])  # Create three columns for centering
with col2:  # Use the middle column
    if doi_link:
        st.button("Go to full-text paper", on_click=lambda: st.write(f"[Go to full-text paper]({doi_link})"))
    else:
        st.warning("DOI link not available for this paper.")
# Questionnaire
st.markdown("### Questionnaire")

# Question 1
st.markdown('<div>1. Is the paper describing wet lab experiments that aim to understand protein interactions?</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 200])  # Create two columns for better layout
with col1:
    st.markdown("")
with col2:
    q1 = st.radio("Question 1", options=["YES", "NO"], horizontal=True, key="q1_radio", label_visibility="collapsed")

# Sub-question 1a
st.markdown('<div style="padding-left: 20px; margin-bottom: 10px;">1a. What is the main method the authors use to understand protein interactions?</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 60])  # Create two columns for better layout
with col1:
    st.markdown("")
with col2:
    q1a = st.text_input("Sub-question 1a", placeholder="Enter the main method here", key="q1a_text", label_visibility="collapsed")

# Sub-question 1b
st.markdown('<div style="padding-left: 20px;">1b. Is this method preserving protein interactions in a cell-free system (e.g., whole cell extracts)?</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 50])  # Create two columns for better layout
with col1:
    st.markdown("")
with col2:
    q1b = st.radio("Sub-question 1b", options=["YES", "NO"], horizontal=True, key="q1b_radio", label_visibility="collapsed")

# Sub-question 1c
st.markdown('<div style="padding-left: 20px;">1c. Is this method using any type of cross-linking to preserve protein interactions?</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 50])  # Create two columns for better layout
with col1:
    st.markdown("")
with col2:
    q1c = st.radio("Sub-question 1c", options=["YES", "NO"], horizontal=True, key="q1c_radio", label_visibility="collapsed")

# Question 2
st.markdown('<div style="margin-bottom: 10px;">2. What is your level of familiarity with the topic of this paper?</div>', unsafe_allow_html=True)
q2 = st.selectbox("Question 2", ["Basic", "Course", "MSc research", "PhD field", "PhD research", "Expert"], key="q2_select", label_visibility="collapsed")

# Question 3
st.markdown('<div style="margin-bottom: 10px;">3. What is your level of familiarity with the methods and experiments in this paper?</div>', unsafe_allow_html=True)
q3 = st.selectbox("Question 3", ["Basic", "Course", "MSc research", "PhD field", "PhD research", "Expert"], key="q3_select", label_visibility="collapsed")

# Navigation buttons
st.markdown("""
    <div style="margin-top: -20px;">
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1.5, 1, 1])  # Adjust column widths to center the buttons properly
with col1:  # Place "Pick another" button in the left column
    if st.button("Pick another paper", type="secondary", key="pick_another_button"):
        st.switch_page("pages/2_pick_paper.py")
with col2:  # Use the middle column for "Confirm paper" button
    if st.button("Confirm paper", type="primary", key="confirm_paper_button"):
        # Navigate to the detail picker page
        st.set_option("client.showSidebarNavigation", False)
        st.switch_page("pages/5_detail_picker.py")