import streamlit as st
from streamlit_cookies_manager import CookieManager
from ous import handle_redirects, get_user_key, get_token, handle_auth_error
from process_interchange import thanks
from data import fetch_user_info, fetch_paper_info

# Set page configuration
st.set_page_config(page_title="Thank You", layout="wide", initial_sidebar_state="collapsed")

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

# Fetch the PMID of the paper from completed_paper session state or cookies
pmid = cookies.get("completed_paper") or st.session_state.get("completed_paper")
if not pmid:
    st.switch_page("pages/2_pick_paper.py")

# Get user info
user_key = get_user_key(cookies)
token = get_token(cookies)
if not user_key or not token:
    st.error("Not authenticated. Please log in again.")
    st.stop()

success, user_info = fetch_user_info(user_key, token)
if not success:
    st.error(user_info)
    st.stop()

papers_completed = len(user_info.get("CompletedPMIDs", []) or [])
# TO BE ADDRESSED - EXPERIMENTS AND SOLUTIONS ANNOTATED REQUIRES MORE DATA SAVED IN BACKEND
experiments_annotated = user_info.get("ExperimentsAnnotated", 0)
solutions_annotated = user_info.get("SolutionsAnnotated", 0)

# Get the paper title
success, paper_info = fetch_paper_info(pmid, token)
if success and paper_info and "Title" in paper_info:
    paper_name = f"<i>{paper_info['Title']}</i>"
else:
    handle_auth_error(cookies)
    paper_name = f"<i>{pmid}</i>"

body = thanks["body"]

body_html = f"""
<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 70vh; margin-top: -100px;">
  <div style="border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); padding: 32px 32px 16px 32px; max-width: 600px; text-align: center;">
    <h1 style="text-align: center; margin-bottom: 0.5em;">{thanks['title']}</h1>
    <hr style="margin: 1em 0; border: none; border-top: 1px solid #e0e0e0;">
    <p>{body['completed'].format(paper_name=paper_name)}</p>
    <div style="margin: 1.5em 0;">
      <span style="font-size: 1.1em;">
        {body['stats'].format(
            papers_completed=papers_completed,
            experiments_annotated=experiments_annotated,
            solutions_annotated=solutions_annotated
        )}
      </span>
    </div>
    <hr style="margin: 1em 0; border: none; border-top: 1px solid #e0e0e0;">
    <p style="margin-bottom: 0.5em;">{body['cta']}</p>
  </div>
</div>
"""

st.markdown(body_html, unsafe_allow_html=True)

col1, col2, col3 = st.columns([3, 2, 3])
with col2:
    if st.button("Start new annotation", use_container_width=True):
        st.switch_page("pages/2_pick_paper.py")