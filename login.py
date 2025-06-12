import streamlit as st

# Hide sidebar
st.set_page_config(initial_sidebar_state="collapsed")
st.set_option("client.showSidebarNavigation", False)

import requests
from src.various import get_pmid
from streamlit_cookies_manager import CookieManager

BACKEND_URL = "http://localhost:3000"

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

# Check cookies for session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = cookies.get("logged_in", False)
if "userID" not in st.session_state:
    st.session_state["userID"] = cookies.get("userID", None)
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

    try:
        # Send login request to backend
        resp = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"UserEmail": email.strip(), "UserPIN": pin.strip()},
            timeout=10
        )
        if resp.status_code == 200:
            # Extract token and userID from response
            token = resp.cookies.get("token") or resp.json().get("token")
            user_id = resp.json().get("userID") or email.strip()
            if not token:
                st.error("Login failed: No token received.")
                st.stop()

            # Save token and login state in cookies and session state
            st.session_state.logged_in = True
            st.session_state["userID"] = user_id
            st.session_state["token"] = token
            cookies["logged_in"] = True
            cookies["userID"] = user_id
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
            try:
                msg = resp.json().get("error") or resp.json().get("message") or "Login failed."
            except Exception:
                msg = "Login failed."
            st.error(msg)
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")

st.write("---")
st.write("Don't have an account? Sign up below:")

signup_email = st.text_input("Sign-up E-Mail", key="signup_email")
signup_pin = st.text_input("Sign-up PIN", type="password", key="signup_pin")

if st.button("Sign up", type="secondary"):
    if not signup_email or not signup_pin:
        st.error("Please enter both email and PIN for sign-up.")
        st.stop()
    try:
        resp = requests.post(
            f"{BACKEND_URL}/auth/signup",
            json={"UserEmail": signup_email.strip(), "UserPIN": signup_pin.strip()},
            timeout=10
        )
        if resp.status_code == 201:
            st.success("Account created! Please log in above.")
        else:
            try:
                msg = resp.json().get("error") or resp.json().get("message") or "Sign-up failed."
            except Exception:
                msg = "Sign-up failed."
            st.error(msg)
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")

# Optionally, add a logout button for testing
if st.session_state.get("logged_in"):
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.session_state["userID"] = None
        st.session_state["token"] = None
        cookies["logged_in"] = False
        cookies["userID"] = ""
        cookies["token"] = ""
        cookies.save()
        st.rerun()