import streamlit as st

# Hide sidebar
st.set_page_config(initial_sidebar_state="collapsed")
st.set_option("client.showSidebarNavigation", False)

from src.various import get_pmid
from streamlit_cookies_manager import CookieManager
from src.database import login_user, signup_user

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

# Check cookies for session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = cookies.get("logged_in", False)
if "userKey" not in st.session_state:
    st.session_state["userKey"] = cookies.get("userKey", None)
if "token" not in st.session_state:
    st.session_state["token"] = cookies.get("token", None)

# Redirection logic
try:
    if st.session_state.logged_in:
        pmid = get_pmid(cookies)
        st.set_option("client.showSidebarNavigation", True)
        if pmid:
            st.switch_page("pages/1_resume.py")
        else:
            st.switch_page("pages/2_pick_paper.py")
except Exception as e:
    st.error(f"Redirection error: {e}")
    st.stop()

st.title("Welcome")
st.text("Welcome to the Annotation App. Please enter your E-Mail and PIN to continue.")

email = st.text_input("E-Mail")
pin = st.text_input("PIN", type="password")

if st.button("Log in", type="primary"):
    if not email or not pin:
        st.error("Please enter both email and PIN.")
        st.stop()
    success, result = login_user(email, pin)
    if success:
        token = result["token"]
        user_key = result["userKey"]
        # Save token and login state in cookies and session state
        st.session_state.logged_in = True
        st.session_state["userKey"] = user_key
        st.session_state["token"] = token
        cookies["logged_in"] = True
        cookies["userKey"] = user_key
        cookies["token"] = token
        cookies.save()

        st.success("Logged in successfully!")
        st.set_option("client.showSidebarNavigation", True)

        pmid = get_pmid(cookies)
        print(f"DEBUG: Retrieved PMID: {pmid}")
        if pmid:
            st.switch_page("pages/1_resume.py")
        else:
            st.switch_page("pages/2_pick_paper.py")
    else:
        st.error(result)

st.write("---")
st.write("Don't have an account? Sign up below:")

signup_email = st.text_input("Sign-up E-Mail", key="signup_email")
signup_pin = st.text_input("Sign-up PIN", type="password", key="signup_pin")

if st.button("Sign up", type="secondary"):
    if not signup_email or not signup_pin:
        st.error("Please enter both email and PIN for sign-up.")
        st.stop()
    success, msg = signup_user(signup_email, signup_pin)
    if success:
        st.success(msg)
    else:
        st.error(msg)
        
if st.session_state.get("logged_in"):
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state["userKey"] = None
        st.session_state["token"] = None
        cookies["logged_in"] = False
        cookies["userKey"] = ""
        cookies["token"] = ""
        cookies.save()
        st.rerun()