import streamlit as st
import pandas as pd
from src.various import evaluate_userID, evaluate_email, evaluate_userID_format
from st_pages import hide_pages
import ast
from time import sleep
import os
from datetime import datetime

# Hide sidebar
st.set_page_config(initial_sidebar_state="collapsed")

# Load dataframes (local path for now)
data_table = "AWS_S3/users_table.xlsx"
papers_table = "AWS_S3/papers_table.xlsx"

if "logged_in" in st.session_state and st.session_state.logged_in:
    try:
        users_df = pd.read_excel(data_table)
        user_row = users_df[users_df["userID"] == st.session_state["userID"]]
        temp_file_name = user_row["Paper in progress"].values[0]

        if not pd.isna(temp_file_name):
            st.switch_page("pages/1_resume.py")
        else:
            st.switch_page("pages/2_pick_paper.py")
    except Exception as e:
        st.error(f"Error loading user data: {e}")
        st.stop()

st.set_option("client.showSidebarNavigation", False)

# Handle first-load refresh issue
if "has_rerun" not in st.session_state:
    st.session_state.has_rerun = True
    st.rerun()

st.title("Welcome")
st.text("Welcome to the Annotation App. Please enter your E-Mail and PIN to continue.")

email = st.text_input("E-Mail")
unique_id = st.text_input("PIN")

if st.button("Log in", type="primary"):
    try:
        # File missing/corrupt
        if not os.path.exists(data_table):
            st.error("User database not found.")
            st.stop()

        users_df = pd.read_excel(data_table)
    except Exception as e:
        st.error(f"Error reading user database: {e}")
        st.stop()

    try:
        # Preprocess columns
        if "e-mail" not in users_df.columns or "userID" not in users_df.columns:
            st.error("User database is missing required columns.")
            st.stop()

        users_df["e-mail"] = users_df["e-mail"].astype(str).str.strip().str.lower()
        users_df["userID"] = users_df["userID"].astype(str).str.strip()
    except Exception as e:
        st.error(f"Error processing user data: {e}")
        st.stop()

    # Preprocess user inputs
    email = email.strip().lower()

    # Validate the email format
    if not evaluate_email(email):
        st.switch_page("pages/8_error_page.py")

    error_message = evaluate_userID_format(unique_id)
    if error_message:
        st.switch_page("pages/8_error_page.py")

    if not evaluate_userID(unique_id):
        st.switch_page("pages/8_error_page.py")

    # Lookup user
    try:
        user_row = users_df[(users_df["e-mail"] == email) & (users_df["userID"] == unique_id)]
    except Exception as e:
        st.error(f"Error validating user credentials: {e}")
        st.stop()

    if user_row.empty:
        st.switch_page("pages/8_error_page.py")
    else:
        try:
            st.session_state.logged_in = True
            st.session_state["userID"] = unique_id
            st.success("Logged in successfully!")

            today_str = datetime.now().strftime("%Y-%m-%d")
            user_index = user_row.index[0]
            timestamp_columns = [col for col in users_df.columns if col.startswith("tmpstmp")]
            user_dates = users_df.loc[user_index, timestamp_columns].dropna().astype(str).tolist()

            if today_str not in user_dates:
                for col in timestamp_columns:
                    if pd.isna(users_df.at[user_index, col]):
                        users_df.at[user_index, col] = today_str
                        break
                else:
                    new_col = f"tmpstmp{len(timestamp_columns)+1}"
                    users_df[new_col] = None
                    users_df.at[user_index, new_col] = today_str

            users_df.to_excel(data_table, index=False)

            sleep(1)
            temp_file_name = user_row["Paper in progress"].values[0]
            st.set_option("client.showSidebarNavigation", True)

            if not pd.isna(temp_file_name):
                st.switch_page("pages/1_resume.py")
            else:
                st.switch_page("pages/2_pick_paper.py")

        except Exception as e:
            st.error(f"Unexpected error during login: {e}")