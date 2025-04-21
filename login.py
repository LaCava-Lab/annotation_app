import streamlit as st
import pandas as pd
from src.various import evaluate_userID, evaluate_email
from st_pages import hide_pages
import ast
from time import sleep


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
    else:
        # Validate the User ID format
        if not evaluate_userID(unique_id):
            st.error("Invalid User ID format. Please try again.")
        else:
            # Check if the email and User ID match in the database
            user_row = users_df[(users_df["e-mail"] == email) & (users_df["userID"] == unique_id)]

            if user_row.empty:
                st.write("First-time user, welcome!")
                new_user = pd.DataFrame({
                    "e-mail": [email], 
                    "userID": [unique_id],
                    "No.Papers": [0],
                    "Papers completed": [None], 
                    "Paper in progress": [None]
                    # Add any other columns that exist in users_table
                })
                # Add the new user to the existing DataFrame
                users_df = pd.concat([users_df, new_user], ignore_index=True)
                # Save the updated DataFrame back to the file
                users_df.to_excel("AWS_S3/users_table.xlsx", index=False)
                st.success("Your account has been created successfully!")

                # Save session state
                st.session_state.logged_in = True
                st.session_state["userID"] = unique_id
                sleep(1)
                # Move on to pick papers
                st.switch_page("pages/2_pick_paper.py")
            else:
                # Returing user, save session state
                st.session_state.logged_in = True
                st.success("Logged in successfully!")
                st.session_state["userID"] = unique_id
                sleep(1)
                # Move on to resume annotating
                st.switch_page("pages/1_resume.py")