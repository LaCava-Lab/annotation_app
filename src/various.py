from streamlit_cookies_manager import CookieManager
import streamlit as st
import pandas as pd

# Path to folder with JSON papers
JSON_FOLDER = "Full_text_jsons"

# Path to the users table
USERS_TABLE_PATH = r"AWS_S3/users_table.xlsx"

def evaluate_userID_format(userid):
    if not userid.isdigit():
        return "PIN must contain only digits."

    if len(userid) <= 3:
        return "PIN must be longer than 3 digits."

    return None  # Means it's valid

def evaluate_userID(userid):
    '''
    userid is a string of digits 0-9, of variable length

    > n: papers (2)
    Test IDs (min, max): 111219, 9991971

    > n: papers (9)
    Test IDs (min, max): 111996, 9998964
    '''
    # userid should be all numbers and no letters
    try:
        float(userid)
    except:
        return False

    # userid should encode an integer value (number of papers n) ranging from 2 to 9.
    m = float(userid[:3])
    [a, b, c] = [float(no) for no in userid[:3]]
    s = a+b+c
    e = float(userid[3:])
    try:
        n = (e + s)/m
    except:
        return False
    if (n == int(n)) and (n in list(range(2,10))):
        return True
    else:
        return False

def evaluate_email(email):
    import re

    academic_email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    return re.fullmatch(academic_email_pattern, email)

def get_pmid(cookies: CookieManager, redir: bool = True) -> str:
    import requests

    # Check if PMID is in session state
    if "paper_in_progress" in st.session_state:
        return st.session_state["paper_in_progress"]

    # Check if PMID is in cookies
    pmid_from_cookies = cookies.get("paper_in_progress")
    if pmid_from_cookies:
        st.session_state["paper_in_progress"] = pmid_from_cookies
        return pmid_from_cookies

    # Check the backend database for the user's current paper in progress
    user_key = st.session_state.get("userKey") or cookies.get("userKey")
    token = cookies.get("token") or st.session_state.get("token")
    BACKEND_URL = "http://localhost:3000"
    if user_key and token:
        try:
            resp = requests.get(
                f"{BACKEND_URL}/users/me",
                params={"userKey": user_key},
                cookies={"token": token},
                timeout=10
            )
            if resp.status_code == 200:
                user = resp.json()
                pmid_from_db = user.get("CurrentPMID")
                print(f"PMID from backend: {pmid_from_db}")
                if pmid_from_db:
                    st.session_state["paper_in_progress"] = pmid_from_db
                    cookies["paper_in_progress"] = pmid_from_db
                    cookies.save()
                    return pmid_from_db
            # else: do nothing, will redirect below
        except Exception as e:
            st.error(f"Error fetching PMID from backend: {e}")

    # If PMID is not found anywhere
    if redir:
        st.set_option("client.showSidebarNavigation", True)
        st.switch_page("pages/2_pick_paper.py")
        st.stop()

    return None

def get_selected_paper(cookies : CookieManager):
    # Check if selected paper is in session state
    if "selected_paper" in st.session_state:
        return st.session_state["selected_paper"]

    # Check if selected paper is in cookies
    selected_paper_from_cookies = cookies.get("selected_paper")
    if selected_paper_from_cookies:
        st.session_state["selected_paper"] = selected_paper_from_cookies
        return selected_paper_from_cookies

    # If not found, return None
    return None

def handle_redirects(cookies : CookieManager):
    # Check cookies for session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = cookies.get("logged_in", False)
    if "userKey" not in st.session_state:
        st.session_state["userKey"] = cookies.get("userKey", None)

    if not st.session_state.logged_in:
        st.set_option("client.showSidebarNavigation", False)
        st.switch_page("login.py")

# Helper to get token
def get_token(cookies : CookieManager):
    return cookies.get("token") or st.session_state.get("token")

# Helper to get user key
def get_user_key(cookies : CookieManager):
    return st.session_state.get("userKey") or cookies.get("userKey")
