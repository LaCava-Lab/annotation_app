import streamlit as st
import pandas as pd
from src.various import evaluate_userID, evaluate_email, evaluate_userID_format
from st_pages import hide_pages
import ast
from time import sleep
import os
from datetime import datetime

# Load dataframes (local path for now)
data_table = "AWS_S3/users_table.xlsx"
papers_table = "AWS_S3/papers_table.xlsx"

# Hide sidebar
st.set_option("client.showSidebarNavigation", False)

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
        st.error("Invalid email format. Please enter a valid academic email address.")
        st.stop()
    
    error_message = evaluate_userID_format(unique_id)
    if error_message:
        st.error(error_message)
        st.stop()

    # Validate the user ID format
    if not evaluate_userID(unique_id):
        st.error("Invalid PIN. Please try again.")
        st.stop()

    # Lookup user
    try:
        user_row = users_df[(users_df["e-mail"] == email) & (users_df["userID"] == unique_id)]
    except Exception as e:
        st.error(f"Error validating user credentials: {e}")
        st.stop()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_row.empty:
        st.write("First-time user, welcome!")
        try:
            new_user = pd.DataFrame({
                "e-mail": [email],
                "userID": [unique_id],
                "No.Papers": [0],
                "Papers completed": [None],
                "Paper in progress": [None],
                "Last Login": [current_time]
            })

            # Add the new user to the existing DataFrame
            users_df = pd.concat([users_df, new_user], ignore_index=True)
            # Save the updated DataFrame back to the file
            users_df.to_excel(data_table, index=False)
            st.success("Your account has been created successfully!")

            # Save session state
            st.session_state.logged_in = True
            st.session_state["userID"] = unique_id
            sleep(1)
            # Move on to pick papers
            st.switch_page("pages/2_pick_paper.py")
        except Exception as e:
            st.error(f"Failed to create new user: {e}")
    else:
        # Returing user, save session state
        try:
            st.session_state.logged_in = True
            st.session_state["userID"] = unique_id
            st.success("Logged in successfully!")

            # Update the login timestamp
            users_df.loc[
                (users_df["userID"] == unique_id) & (users_df["e-mail"] == email),
                "Last Login"
            ] = current_time
            users_df.to_excel(data_table, index=False)

            sleep(1)
            temp_file_name = user_row["Paper in progress"].values[0]
            if not pd.isna(temp_file_name):
                # Move on to resume annotating
                st.switch_page("pages/1_resume.py")
            else:
                # Move on to pick papers
                st.switch_page("pages/2_pick_paper.py")
        except Exception as e:
            st.error(f"Unexpected error during login: {e}")
