import streamlit as st
from pathlib import Path
from process_interchange import resume
from streamlit_cookies_manager import CookieManager
from src.various import get_pmid, handle_redirects, get_token, get_user_key, handle_auth_error, get_user_progress
from src.database import fetch_user_info, fetch_paper_info, abandon_paper, clear_paper_in_progress, set_abandon_limit

st.title(resume["title"])

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

# Fetch the PMID (this is the paper in progress)
pmid = get_pmid(cookies)

user_key = get_user_key(cookies)
token = get_token(cookies)

# Fetch user info from backend
success, user_info = fetch_user_info(user_key, token)
if not success:
    st.error(user_info)
    st.stop()

papers_abandoned = user_info.get("AbandonedPMIDs", []) or []
num_abandoned = len(papers_abandoned)
max_abandonments = 2

# Ensure remaining_restarts is never negative
remaining_restarts = max(0, max_abandonments - num_abandoned)

# Check the abandon limit variable
abandon_limit_reached = user_info.get("AbandonLimit", False)

# Get paper title from backend
paper_title = None
if pmid:
    success, paper_info = fetch_paper_info(pmid, token)
    if success and paper_info and "Title" in paper_info:
        paper_title = f"<i>{paper_info['Title']}</i>"
    else:
        # If paper not found, just clear paper in progress and redirect
        if isinstance(paper_info, str) and "Paper not found" in paper_info:
            clear_paper_in_progress(user_key, token)
            cookies["paper_in_progress"] = ""
            cookies.save()
            if "paper_in_progress" in st.session_state:
                del st.session_state["paper_in_progress"]
            st.switch_page("pages/2_pick_paper.py")
        else:
            handle_auth_error(cookies)
else:
    st.switch_page("pages/2_pick_paper.py")

# Number of protocols and solutions annotated
protocols, solutions, annotated = get_user_progress(cookies, pmid)

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
    # Button is only enabled if abandon_limit_reached is False
    if st.button(
        resume["paper_in_progress"]["buttons"][1]["text"],
        disabled=abandon_limit_reached,
    ):
        # Abandon the current paper in backend
        if user_key and pmid:
            abandon_paper(user_key, pmid, token)
            clear_paper_in_progress(user_key, token)
        # Clear the "paper_in_progress" cookie and session state
        cookies["paper_in_progress"] = ""
        cookies.save()
        if "paper_in_progress" in st.session_state:
            del st.session_state["paper_in_progress"]
        # If this was the last allowed abandonment, set the abandon limit variable in backend
        if remaining_restarts == 1:
            set_abandon_limit(user_key, token)
        # Redirect to the "Pick a new paper" page
        st.switch_page("pages/2_pick_paper.py")