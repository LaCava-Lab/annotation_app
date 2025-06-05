import streamlit as st
import pandas as pd
import ast
from pathlib import Path
from streamlit_cookies_manager import CookieManager
from src.various import get_pmid, handle_redirects
from src.database import get_paper_metadata_by_pmid
from process_interchange import resume
import os

# Define the base directory as the parent directory of this script
base_dir = Path(__file__).resolve().parent.parent

# Define file paths relative to the root directory
USERS_TABLE_PATH = base_dir / "AWS_S3" / "users_table.xlsx"
PAPERS_CSV_PATH = base_dir / "Data_folder" / "Papers.csv"

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

st.title(resume["title"])

# Fetch the PMID
pmid = get_pmid(cookies)

# Check if user is logged in
if "userID" in st.session_state:
    user_id = str(st.session_state["userID"]).strip()
    users_df = pd.read_excel(USERS_TABLE_PATH)
    # Preprocess columns
    users_df["userID"] = users_df["userID"].astype(str).str.strip()
    user_row = users_df[users_df["userID"] == user_id]

    # Ensure "Papers completed" column is a list
    users_df.loc[users_df["userID"] == user_id, "Papers completed"] = users_df.loc[users_df["userID"] == user_id, "Papers completed"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else []
    )
    papers_completed = users_df.loc[users_df["userID"] == user_id, "Papers completed"].values[0]
    no_papers = user_row["No.Papers"].values[0]

    # Ensure "Papers abandoned" column exists and is a list
    if "Papers abandoned" not in users_df.columns:
        users_df["Papers abandoned"] = "[]"
    users_df["Papers abandoned"] = users_df["Papers abandoned"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else []
    )
    papers_abandoned = users_df.loc[users_df["userID"] == user_id, "Papers abandoned"].values[0]

    # Calculate remaining re-starts
    max_abandonments = 2
    remaining_restarts = max_abandonments - len(papers_abandoned)

    # Get the last paper in progress
    temp_file_name = user_row["Paper in progress"].values[0] if not user_row.empty else None

    # Get paper title
    paper_meta = get_paper_metadata_by_pmid(pmid, str(PAPERS_CSV_PATH))
    paper_title = f"<i>{paper_meta['Title']}</i>" if paper_meta and paper_meta.get("Title") else f"<i>{pmid}</i>"

    # Dummy values for protocols, solutions, annotated (replace with real logic if available)
    protocols = "N"
    solutions = "M"
    annotated = "Q"

    # Use interchangeable processed text
    processed_text = resume["paper_in_progress"]["detail"].format(
        paper_title=paper_title,
        protocols=protocols,
        solutions=solutions,
        annotated=annotated,
        num_abandoned=len(papers_abandoned),
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
            # Add the current paper's PMID to the "Papers abandoned" list
            if pmid not in papers_abandoned:
                papers_abandoned.append(pmid)
                users_df.loc[users_df["userID"] == user_id, "Papers abandoned"] = str(papers_abandoned)
                # Clear the "Paper in progress" column for the user
                users_df.loc[users_df["userID"] == user_id, "Paper in progress"] = None
                # Save the updated users_table back to the file
                users_df.to_excel(USERS_TABLE_PATH, index=False)

            # Clear the "paper_in_progress" cookie by setting it to an empty value
            cookies["paper_in_progress"] = ""
            cookies.save()  # Save the updated cookies

            # Clear the session storage for "Paper in progress"
            if "paper_in_progress" in st.session_state:
                del st.session_state["paper_in_progress"]

            # Redirect to the "Pick a new paper" page
            st.switch_page("pages/2_pick_paper.py")
else:
    st.error("No user logged in. Please log in to continue.")