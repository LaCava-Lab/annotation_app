import streamlit as st
from st_pages import get_nav_from_toml, hide_pages
import pandas as pd


nav = get_nav_from_toml(".streamlit/pages.toml")
pg = st.navigation(nav)

data_table = "AWS_S3/users_table.xlsx"
papers_table = "AWS_S3/papers_table.xlsx"

st.title("Restart OR Finish")

# Check if user is logged in
if "user_id" in st.session_state:
    user_id = st.session_state["user_id"]

    # Load the users table
    users_df = pd.read_excel(data_table)
    user_row = users_df[users_df["userID"] == user_id]

    #     if st.button("Request more papers"):
    #         # Redirect to pick a new paper
    # else:
    #     # Redirect to restart or continue annotating
