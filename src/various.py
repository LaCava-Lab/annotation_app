from streamlit_cookies_manager import CookieManager
import streamlit as st
import pandas as pd

# Path to folder with JSON papers
JSON_FOLDER = "Full_text_jsons"

# Path to the users table
USERS_TABLE_PATH = "AWS_S3\\users_table.xlsx"

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
	#userid should be all numbers and no letters
	try:
		float(userid)
	except:
		return False

	#userid should encode an integer value (number of papers n) ranging from 2 to 9.
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

# Function to fetch the PMID
def get_pmid(cookies : CookieManager) -> str:
    # Check if PMID is in session state
    if "paper_in_progress" in st.session_state:
        return st.session_state["paper_in_progress"]

    # Check if PMID is in cookies
    pmid_from_cookies = cookies.get("paper_in_progress")
    if pmid_from_cookies:
        st.session_state["paper_in_progress"] = pmid_from_cookies
        return pmid_from_cookies

    # Check the users table for the "Paper in progress" column
    user_id = st.session_state.get("userID")
    if user_id:
        try:
            users_df = pd.read_excel(USERS_TABLE_PATH)
            user_row = users_df[users_df["userID"] == user_id]
            if not user_row.empty:
                pmid_from_table = user_row["Paper in progress"].values[0]
                if pd.notna(pmid_from_table):
                    # Ensure the value is treated as a string
                    pmid_from_table = str(int(pmid_from_table))
                    st.session_state["paper_in_progress"] = pmid_from_table
                    cookies["paper_in_progress"] = pmid_from_table
                    cookies.save()
                    return pmid_from_table
        except Exception as e:
            st.error(f"Error fetching PMID from users table: {e}")

    # If PMID is not found anywhere
    st.switch_page("pages/2_pick_paper.py")
    st.stop()

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
    if "userID" not in st.session_state:
        st.session_state["userID"] = cookies.get("userID", None)

    if not st.session_state.logged_in:
        st.set_option("client.showSidebarNavigation", False)
        st.switch_page("pages/0_login.py")
