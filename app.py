import streamlit as st
import pandas as pd

st.set_page_config(page_title="Paper Annotation", layout="wide", initial_sidebar_state="collapsed")

from streamlit_cookies_manager import CookieManager

data_table = "AWS_S3/users_table.xlsx"

# Initialize the cookie manager
cookies = CookieManager(
    prefix="annotation_app_",  # Prefix for your app's cookies
)
if not cookies.ready():
    st.stop()

# Check cookies for session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = cookies.get("logged_in", False)
if "userID" not in st.session_state:
    st.session_state["userID"] = cookies.get("userID", None)

if st.session_state.logged_in:
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

st.switch_page("pages/0_login.py")

