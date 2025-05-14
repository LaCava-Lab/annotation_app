import streamlit as st
import pandas as pd
import ast
from pathlib import Path
from time import sleep
from streamlit_cookies_manager import CookieManager
from src.various import get_pmid
from src.various import handle_redirects

# Define the base directory as the parent directory of this script
base_dir = Path(__file__).resolve().parent.parent 

# Define file paths relative to the root directory
data_file = base_dir / "AWS_S3" / "users_table.xlsx"
papers_table = base_dir / "AWS_S3" / "papers_table.xlsx"

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

st.title("Welcome Back!")

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
    
    # if len(papers_completed) == no_papers:
    #     st.write("You have completed all your papers. Would you like to complete more?")
        
    #     # Display "Yes" and "No" buttons horizontally
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         if st.button("Yes"):
    #             st.switch_page("pages/2_pick_paper.py")
    #     with col2:
    #         if st.button("No"):
    #             st.switch_page("pages/7_thanks.py")
    # else:
    #     if not user_row.empty:
    #         # Get the last paper in progress
    #         temp_file_name = user_row["Paper in progress"].values[0]
    #         # Provide options to continue or select a new paper
    #         if not pd.isna(temp_file_name):
    #             paper_details = papers_df[papers_df["PMID"] == temp_file_name]
    #             columns_to_hide = ["status_1", "user_1", "status_2", "user_2"]
    #             paper_details_display = paper_details.drop(columns=columns_to_hide, errors="ignore")

    #             if not paper_details.empty:
    #                 # Display the details of the paper
    #                 st.write("Your last paper:")
    #                 st.dataframe(paper_details_display)
    #             else:
    #                 st.warning("No matching paper found in the papers table!")

    #             if st.button("Continue annotating"):
    #                 st.switch_page("pages/4_question_cascade.py")
    #             elif st.button("Choose a new paper"):
    #                 st.switch_page("pages/2_pick_paper.py")
    #         else:
    #             # If no temp_file_name, move on to the next paper they selected
    #             st.switch_page("pages/4_question_cascade.py")
    #             import streamlit as st

# paper title is Paper + extracted PMID
paper_title = "Paper " + pmid
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

# Calculate remaining re-starts
max_abandonments = 2
remaining_restarts = max_abandonments - len(papers_abandoned)

# Update the note with the remaining re-starts
st.markdown(f"""
    <div style='border: 1px solid #444; padding: 20px; border-radius: 8px'>
        We see that you have already started annotating <b>{paper_title}</b>. You have identified <b>{protocols}</b> protocols and <b>{solutions}</b> solutions in it, and you have already annotated in detail <b>{annotated}</b> of these solutions.
        <br><br>
        To continue annotating this paper, press <b>"Continue annotation"</b> below.
        <br><br>
        Even though we do not encourage it, if you have really changed your mind about the paper you chose to annotate, then press <b>"Start new annotation"</b>.
        Please note, we only allow each annotator a maximum of two "abandoned" papers. The "Start new annotation" button will be disabled once you reach this limit.
        <br><br>
        <b>You currently have {remaining_restarts} re-starts remaining.</b>
    </div>
    """, unsafe_allow_html=True)

st.write("")
spacer, col1, big_gap, col2, spacer2 = st.columns([1, 2, 1.5, 2, 1])

with col1:
    if st.button("Continue annotation", type="primary"):
        st.switch_page("pages/5_detail_picker.py")   
with col2:
    if st.button("Start new annotation", disabled=(remaining_restarts <= 0)):
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
        if "Paper in progress" in st.session_state:
            del st.session_state["Paper in progress"]

        # Redirect to the "Pick a new paper" page
        st.switch_page("pages/2_pick_paper.py")