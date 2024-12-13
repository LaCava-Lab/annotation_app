import streamlit as st
import pandas as pd
import ast
from pathlib import Path
from time import sleep

# Define the base directory as the parent directory of this script
base_dir = Path(__file__).resolve().parent.parent 

# Define file paths relative to the root directory
data_file = base_dir / "AWS_S3" / "users_table.xlsx"
papers_table = base_dir / "AWS_S3" / "papers_table.xlsx"

st.title("Welcome Back!")

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
    papers_completed = user_row["Papers completed"] = user_row["Papers completed"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else []
    )
    no_papers = user_row["No.Papers"].values[0]

    if len(papers_completed) == no_papers:
        st.write("You have completed all your papers. Would you like to complete more?")
        if st.button("Yes"):
            st.switch_page("pages/2_pick_paper.py")
        elif st.button("No"):
            st.switch_page("pages/7_thanks.py")
    else:
        if not user_row.empty:
            # Get the last paper in progress
            temp_file_name = user_row["Paper in progress"].values[0]
            # Provide options to continue or select a new paper
            if not pd.isna(temp_file_name):
                paper_details = papers_df[papers_df["PMID"] == temp_file_name]
                columns_to_hide = ["status_1", "user_1", "status_2", "user_2"]
                paper_details_display = paper_details.drop(columns=columns_to_hide, errors="ignore")

                if not paper_details.empty:
                    # Display the details of the paper
                    st.write("Your last paper:")
                    st.dataframe(paper_details_display)
                else:
                    st.warning("No matching paper found in the papers table!")

                if st.button("Continue annotating"):
                    st.switch_page("pages/3_browse_paper.py")
                elif st.button("Choose a new paper"):
                    st.switch_page("pages/2_pick_paper.py")
            else:
                # If no temp_file_name, move on to the next paper they selected
                st.switch_page("pages/3_browse_paper.py")