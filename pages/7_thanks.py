import streamlit as st
from streamlit_cookies_manager import CookieManager
from src.various import get_pmid, handle_redirects
from process_interchange import thanks
import pandas as pd
import json
import os

# Set page configuration
st.set_page_config(page_title="Thank You", layout="wide", initial_sidebar_state="collapsed")

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

# Handle redirects if necessary
handle_redirects(cookies)

# Fetch the PMID of the paper
pmid = get_pmid(cookies)

# Path to folder with JSON papers
JSON_FOLDER = "Full_text_jsons"

# Path to the users table
USERS_TABLE_PATH =  r"AWS_S3/users_table.xlsx" 

# Load the users table
users_df = pd.read_excel(USERS_TABLE_PATH)

# Get the current user's completed papers
current_user_id = st.session_state.get("userID")
if current_user_id:
    user_row = users_df[users_df["userID"] == current_user_id]
    if not user_row.empty:
        papers_completed = len(eval(user_row["Papers completed"].values[0]))
    else:
        papers_completed = 0
else:
    papers_completed = 0

# Load the paper metadata to get the paper name
def get_paper_name(pmid):
    for filename in os.listdir(JSON_FOLDER):
        if filename.endswith(".json"):
            with open(os.path.join(JSON_FOLDER, filename), "r", encoding="utf-8") as f:
                raw = json.load(f)
                doc = raw[0]["documents"][0]
                front = doc["passages"][0]  # front matter
                meta = front["infons"]
                if meta.get("article-id_pmid") == pmid:
                    return front["text"]  # Return the paper title
    return None

paper_name = get_paper_name(pmid)

# Set experiments and solutions annotated to 0 for now
experiments_annotated = 0
solutions_annotated = 0

# ...existing code...

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

        if "paper_in_progress" in st.session_state:
            del st.session_state["paper_in_progress"]
        
        cookies["paper_in_progress"] = ""
        cookies.save()

        users_df.loc[users_df["userID"] == current_user_id, "Paper in progress"] = None
        users_df.to_excel(USERS_TABLE_PATH, index=False)
        st.switch_page("pages/2_pick_paper.py")
