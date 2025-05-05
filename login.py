import streamlit as st
import pandas as pd
from src.various import evaluate_userID, evaluate_email
from st_pages import hide_pages
import ast
from time import sleep
from src.error_page import show_error_page  # ✅ NEW: import error page

# Session state flag to control error display
if "show_error" not in st.session_state:
    st.session_state.show_error = False

# If login previously failed, show error page and stop further code
if st.session_state.show_error:
    show_error_page()
    st.stop()


# Load dataframes (local path for now)
data_table = "AWS_S3/users_table.xlsx"
papers_table = "AWS_S3/papers_table.xlsx"

#Hide sidebar
st.set_option("client.showSidebarNavigation", False)

st.title("Login")

email = st.text_input("Enter your .edu email:")
unique_id = st.text_input("Enter your user ID:")

if st.button("Log in", type="primary"):
    users_df = pd.read_excel(data_table)
    # Preprocess columns
    users_df["e-mail"] = users_df["e-mail"].str.strip().str.lower()
    users_df["userID"] = users_df["userID"].astype(str).str.strip()

    # Preprocess user inputs
    email = email.strip().lower()

    # Validate the email format
    if not evaluate_email(email):
        st.error("Invalid email format. Please enter a valid academic email address.")
        st.session_state.show_error = True
        st.experimental_rerun()
    else:
        # Validate the User ID format
        if not evaluate_userID(unique_id):
            st.error("Invalid User ID format. Please try again.")
            st.session_state.show_error = True
            st.experimental_rerun()
        else:
            # Check if the email and User ID match in the database
            user_row = users_df[(users_df["e-mail"] == email) & (users_df["userID"] == unique_id)]

            if user_row.empty:
                st.session_state.show_error = True
                st.experimental_rerun()

            else:
                # Returing user, save session state
                st.session_state.logged_in = True
                st.success("Logged in successfully!")
                st.session_state["userID"] = unique_id
                sleep(1)
                # Move on to resume annotating
                st.switch_page("pages/1_resume.py")
