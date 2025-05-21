import streamlit as st
import pandas as pd
import ast
from pathlib import Path
from time import sleep
from process_interchange import resume

# Define the base directory as the parent directory of this script
base_dir = Path(__file__).resolve().parent.parent 

# Define file paths relative to the root directory
data_file = base_dir / "AWS_S3" / "users_table.xlsx"
papers_table = base_dir / "AWS_S3" / "papers_table.xlsx"
st.title(resume["title"])

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

    if len(papers_completed) == no_papers:
        st.write(resume["paper_completed"]["detail"])
        if st.button(resume["paper_completed"]["buttons"][0]["text"]):
            st.switch_page(resume["paper_completed"]["buttons"][0]["page_link"])
        elif st.button(resume["paper_completed"]["buttons"][1]["text"]):
            st.switch_page(resume["paper_completed"]["buttons"][1]["page_link"])
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
                    st.write(resume["paper_not_completed"]["detail"])
                    st.dataframe(paper_details_display)
                else:
                    st.warning(resume["paper_not_completed"]["warning"])

                if st.button(resume["paper_not_completed"]["buttons"][0]["text"]):
                    st.switch_page(resume["paper_not_completed"]["buttons"][0]["page_link"])
                elif st.button(resume["paper_not_completed"]["buttons"][1]["text"]):
                    st.switch_page(resume["paper_not_completed"]["buttons"][1]["page_link"])
            else:
                # If no temp_file_name, move on to the next paper they selected
                st.switch_page(resume["other"]["no_temp_file_name"])

paper_title = "Paper XXXXXXXX"
protocols = "N"
solutions = "M"
annotated = "Q"

processed_text = resume["paper_in_progress"]["detail"].format(
    paper_title=paper_title,
    protocols=protocols,
    solutions=solutions,
    annotated=annotated
)

st.markdown(
    f"<div style='border: 1px solid #444; padding: 20px; border-radius: 8px'>{processed_text}</div>",
    unsafe_allow_html=True
)

st.write("")
spacer, col1, big_gap, col2, spacer2 = st.columns([1, 2, 1.5, 2, 1])

with col1:
    st.button(resume["paper_in_progress"]["buttons"][0]["text"], type="primary")
with col2:
    st.button(resume["paper_in_progress"]["buttons"][1]["text"], disabled=False)
