import streamlit as st
from streamlit_cookies_manager import CookieManager
from src.various import handle_redirects
from process_interchange import thanks
import requests

# Set page configuration
st.set_page_config(page_title="Thank You", layout="wide", initial_sidebar_state="collapsed")

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

BACKEND_URL = "http://localhost:3000"

# Fetch the PMID of the paper from completed_paper session state or cookies
pmid = cookies.get("completed_paper") or st.session_state.get("completed_paper")
if not pmid:
    st.switch_page("pages/2_pick_paper.py")

def get_token():
    return cookies.get("token") or st.session_state.get("token")

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

# Get user info and stats
user_info = fetch_user_info()
st.write("DEBUG user_info:", user_info)
papers_completed = len(user_info.get("CompletedPMIDs", []) or [])
# TO BE ADDRESSED - EXPERIMENTS AND SOLUTIONS ANNOTATED REQUIRES MORE DATA SAVED IN BACKEND
experiments_annotated = user_info.get("ExperimentsAnnotated", 0)
solutions_annotated = user_info.get("SolutionsAnnotated", 0)

# Get the paper title
paper_info = fetch_paper_info(pmid)
if paper_info and "Title" in paper_info:
    paper_name = f"<i>{paper_info['Title']}</i>"
else:
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