import streamlit as st
import requests
from pathlib import Path
from process_interchange import resume
from streamlit_cookies_manager import CookieManager
from src.various import get_pmid, handle_redirects
import json

BACKEND_URL = "http://localhost:3000"

st.title(resume["title"])

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

# Fetch the PMID (this is the paper in progress)
pmid = get_pmid(cookies)

# Helper to get token
def get_token():
    return cookies.get("token") or st.session_state.get("token")

# Helper to get user email
def get_user_email():
    return st.session_state.get("userID")

# Fetch user info from backend
def fetch_user_info():
    user_email = get_user_email()
    token = get_token()
    if not user_email or not token:
        st.error("Not authenticated. Please log in again.")
        st.stop()
    try:
        resp = requests.get(
            f"{BACKEND_URL}/users/me",
            params={"email": user_email},
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error("Could not fetch user info from backend.")
            st.stop()
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        st.stop()

# Fetch paper info from backend
def fetch_paper_info(pmid):
    token = get_token()
    try:
        resp = requests.get(
            f"{BACKEND_URL}/papers/{pmid}",
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            return None
    except Exception as e:
        return None

# Abandon paper in backend
def abandon_paper(user_email, pmid):
    token = get_token()
    try:
        resp = requests.post(
            f"{BACKEND_URL}/users/add_abandoned",
            json={"email": user_email, "pmid": pmid},
            cookies={"token": token},
            timeout=10
        )
        return resp.status_code == 200
    except Exception as e:
        return False

# Clear paper in progress in backend
def clear_paper_in_progress(user_email):
    token = get_token()
    try:
        resp = requests.post(
            f"{BACKEND_URL}/users/set_current_pmid",
            json={"email": user_email, "pmid": None},
            cookies={"token": token},
            timeout=10
        )
        return resp.status_code == 200
    except Exception as e:
        return False

user_info = fetch_user_info()
papers_abandoned = user_info.get("AbandonedPMIDs", []) or []
num_abandoned = len(papers_abandoned)
max_abandonments = 2
remaining_restarts = max_abandonments - num_abandoned

# Get paper title from backend
paper_title = None
if pmid:
    paper_info = fetch_paper_info(pmid)
    if paper_info and "Title" in paper_info:
        paper_title = f"<i>{paper_info['Title']}</i>"
    else:
        paper_title = f"<i>{pmid}</i>"
else:
    paper_title = "<i>No paper in progress</i>"

# Dummy values for protocols/solutions/annotated (REPLACE WITH ACTUAL DATA)
protocols = "N"
solutions = "M"
annotated = "Q"

processed_text = resume["paper_in_progress"]["detail"].format(
    paper_title=paper_title,
    protocols=protocols,
    solutions=solutions,
    annotated=annotated,
    num_abandoned=num_abandoned,
    remaining_restarts=remaining_restarts
)

st.markdown(
    f"<div style='border: 1px solid #444; padding: 20px; border-radius: 8px'>{processed_text}</div>",
    unsafe_allow_html=True
)

st.write("")
spacer, col1, big_gap, col2, spacer2 = st.columns([1, 2, 1.5, 2, 1])

with col1:
    if st.button(resume["paper_in_progress"]["buttons"][0]["text"], type="primary"):
        st.switch_page("pages/5_detail_picker.py")
with col2:
    if st.button(resume["paper_in_progress"]["buttons"][1]["text"], disabled=(remaining_restarts <= 0)):
        user_email = get_user_email()
        # Abandon the current paper in backend
        if user_email and pmid:
            abandon_paper(user_email, pmid)
            clear_paper_in_progress(user_email)
        # Clear the "paper_in_progress" cookie and session state
        cookies["paper_in_progress"] = ""
        cookies.save()
        if "paper_in_progress" in st.session_state:
            del st.session_state["paper_in_progress"]
        # Redirect to the "Pick a new paper" page
        st.switch_page("pages/2_pick_paper.py")