import streamlit as st
import pandas as pd
import ast
from pathlib import Path
from time import sleep
from process_interchange import resume
from streamlit_cookies_manager import CookieManager
from src.various import get_pmid
from src.various import handle_redirects
import os
import json

# Define the base directory as the parent directory of this script
base_dir = Path(__file__).resolve().parent.parent 

# Define file paths relative to the root directory
data_file = base_dir / "AWS_S3" / "users_table.xlsx"
papers_table = base_dir / "AWS_S3" / "papers_table.xlsx"

st.title(resume["title"])

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

# Fetch the PMID
pmid = get_pmid(cookies)

# # Check if user is logged in
if "userID" in st.session_state:
    user_id = st.session_state["userID"]
    users_df = pd.read_excel(data_file)
    papers_df = pd.read_excel(papers_table)

    # Preprocess columns
    users_df["userID"] = users_df["userID"].astype(str).str.strip()
    user_id = str(st.session_state["userID"]).strip()

    user_row = users_df[users_df["userID"] == user_id]

    # Convert "Papers completed" to a list of strings
    users_df.loc[users_df["userID"] == user_id, "Papers completed"] = users_df.loc[users_df["userID"] == user_id, "Papers completed"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else []
    )
    papers_completed = users_df.loc[users_df["userID"] == user_id, "Papers completed"].values[0]
    no_papers = user_row["No.Papers"].values[0]
    
    #if len(papers_completed) == no_papers:
    #    st.write(resume["paper_completed"]["detail"])
    #    if st.button(resume["paper_completed"]["buttons"][0]["text"]):
    #        st.switch_page(resume["paper_completed"]["buttons"][0]["page_link"])
    #    elif st.button(resume["paper_completed"]["buttons"][1]["text"]):
    #        st.switch_page(resume["paper_completed"]["buttons"][1]["page_link"])
    #else:
    #    if not user_row.empty:
    #        # Get the last paper in progress
    #        temp_file_name = user_row["Paper in progress"].values[0]
    #        # Provide options to continue or select a new paper
    #        if not pd.isna(temp_file_name):
    #            paper_details = papers_df[papers_df["PMID"] == temp_file_name]
    #            columns_to_hide = ["status_1", "user_1", "status_2", "user_2"]
    #            paper_details_display = paper_details.drop(columns=columns_to_hide, errors="ignore")
    #
    #            if not paper_details.empty:
    #                # Display the details of the paper
    #                st.write(resume["paper_not_completed"]["detail"])
    #                st.dataframe(paper_details_display)
    #            else:
    #                st.warning(resume["paper_not_completed"]["warning"])
    #
    #            if st.button(resume["paper_not_completed"]["buttons"][0]["text"]):
    #                st.switch_page(resume["paper_not_completed"]["buttons"][0]["page_link"])
    #            elif st.button(resume["paper_not_completed"]["buttons"][1]["text"]):
    #                st.switch_page(resume["paper_not_completed"]["buttons"][1]["page_link"])
    #        else:
    #            # If no temp_file_name, move on to the next paper they selected
    #            st.switch_page(resume["other"]["no_temp_file_name"])

# Extracting the title of paper
JSON_FOLDER = base_dir / "Full_text_jsons"
paper_name = pmid  # fallback

for filename in os.listdir(JSON_FOLDER):
    if filename.endswith(".json"):
        with open(os.path.join(JSON_FOLDER, filename), "r", encoding="utf-8") as f:
            raw = json.load(f)
            doc = raw[0]["documents"][0]
            front = doc["passages"][0]
            meta = front["infons"]
            extracted_pmid = meta.get("article-id_pmid", None)
            if extracted_pmid == pmid:
                paper_name = front["text"]
                break

paper_title = f"<i>{paper_name}</i>"
protocols = "N"
solutions = "M"
annotated = "Q"

# Ensure "Papers abandoned" column exists and initialize it if missing
if "Papers abandoned" not in users_df.columns:
    users_df["Papers abandoned"] = "[]"

# Fetch the user's abandoned papers
users_df["Papers abandoned"] = users_df["Papers abandoned"].apply(
    lambda x: ast.literal_eval(x) if isinstance(x, str) else []
)
papers_abandoned = users_df.loc[users_df["userID"] == user_id, "Papers abandoned"].values[0]

# Calculate remaining re-starts and number of abandonments
num_abandoned = len(papers_abandoned)
max_abandonments = 2
remaining_restarts = max_abandonments - num_abandoned

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
        # Add the current paper's PMID to the "Papers abandoned" list
        if pmid not in papers_abandoned:
            papers_abandoned.append(pmid)
            users_df.loc[users_df["userID"] == user_id, "Papers abandoned"] = str(papers_abandoned)

            # Clear the "Paper in progress" column for the user
            users_df.loc[users_df["userID"] == user_id, "Paper in progress"] = None

            # Save the updated users_table back to the file
            users_df.to_excel(data_file, index=False)

        # Clear the "paper_in_progress" cookie by setting it to an empty value
        cookies["paper_in_progress"] = ""
        cookies.save()  # Save the updated cookies

        # Clear the session storage for "Paper in progress"
        if "paper_in_progress" in st.session_state:
            del st.session_state["paper_in_progress"]

        # Redirect to the "Pick a new paper" page
        st.switch_page("pages/2_pick_paper.py")
