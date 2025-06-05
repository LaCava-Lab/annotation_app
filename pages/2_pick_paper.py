import streamlit as st
import os
import json
import random
import pandas as pd
from process_interchange import pick_paper

st.set_page_config(page_title=pick_paper["title"], layout="wide", initial_sidebar_state="collapsed")
st.title(pick_paper["title"])

from src.various import get_pmid, handle_redirects
from streamlit_cookies_manager import CookieManager
from src.database import get_papersDB

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")

if not cookies.ready():
    st.stop()

handle_redirects(cookies)

pmid = get_pmid(cookies, False)

# If paper already in progress then redirect to the annotation page
if pmid:
    st.switch_page("pages/5_detail_picker.py")

st.markdown(pick_paper["detail"])

# Path to the users table
USERS_TABLE_PATH = r"AWS_S3/users_table.xlsx"

# Load the users table
users_df = pd.read_excel(USERS_TABLE_PATH)

# Get the current user's completed papers
current_user_id = st.session_state.get("userID")
if current_user_id:
    user_row = users_df[users_df["userID"] == current_user_id]
    if not user_row.empty:
        papers_completed = user_row["Papers completed"].values[0]
        if isinstance(papers_completed, str):
            papers_completed = eval(papers_completed)  # Convert string to list
    else:
        papers_completed = []
else:
    papers_completed = []

# Get the current user's abandoned papers
if current_user_id:
    user_row = users_df[users_df["userID"] == current_user_id]
    if not user_row.empty:
        if "Papers abandoned" in user_row.columns:
            papers_abandoned = user_row["Papers abandoned"].values[0]
            if isinstance(papers_abandoned, str):
                papers_abandoned = eval(papers_abandoned)
        else:
            papers_abandoned = []
    else:
        papers_abandoned = []
else:
    papers_abandoned = []

all_papers = get_papersDB()

# Function to refresh paper list
def refresh_paper_list():
    num_to_select = min(5, len(all_papers))
    if num_to_select < 5:
        st.warning("Not enough papers available to display 5 options.")
    st.session_state.paper_choices = random.sample(all_papers, k=num_to_select)
    st.session_state.selected_option = None
    # Clear checkbox states
    for k in ["a", "b", "c", "d", "e"]:
        if k in st.session_state:
            del st.session_state[k]

# Initialize session state for paper choices
if "paper_choices" not in st.session_state:
    refresh_paper_list()

# Initialize session state for selected option
def select(option, key):
    if st.session_state.selected_option == option:
        st.session_state.selected_option = None
        st.session_state[key] = False
    else:
        st.session_state.selected_option = option
        for k in ["a", "b", "c", "d", "e"]:
            if k != key:
                st.session_state[k] = False

# Display the 5 random papers
for i, paper in enumerate(st.session_state.paper_choices):
    key = chr(ord("a") + i)
    label = (
        f"**{', '.join(paper['Authors'])}**, "
        f"*{paper['Title']}* "
        f"({paper['Year']})\n\n"
    )
    # Dynamically construct the metadata parts
    metadata_parts = []
    if paper.get('Journal', ''):
        metadata_parts.append(f"**Journal:** {paper['Journal']}")
    if paper.get('Issue', ''):
        metadata_parts.append(f"**Issue:** {paper['Issue']}")
    if paper.get('Volume', ''):
        metadata_parts.append(f"**Volume:** {paper['Volume']}")
    if paper.get('Pages', ''):
        metadata_parts.append(f"**Pages:** {paper['Pages']}")

    # Join metadata parts with a comma
    if metadata_parts:
        label += ", ".join(metadata_parts) + "\n\n"

    if paper.get('DOI_URL'):
        label += f"[**Link**]({paper['DOI_URL']})"

    st.checkbox(label, key=key, value=st.session_state.get(key, False),
                on_change=select, args=(paper["PMID"], key))

# Navigation buttons
col2, col3 = st.columns([6, 6])
with col2:
    if st.button(pick_paper["buttons"][0]["text"], type="primary", key="go_button", disabled=not st.session_state.selected_option):
        selected_paper = next(paper for paper in st.session_state.paper_choices if paper["PMID"] == st.session_state.selected_option)
        st.session_state["selected_paper"] = selected_paper["PMID"]
        cookies["selected_paper"] = selected_paper["PMID"]
        st.switch_page(pick_paper["buttons"][0]["page_link"])

with col3:
    st.button(pick_paper["buttons"][1]["text"], type="secondary", key="refresh_button", on_click=refresh_paper_list)