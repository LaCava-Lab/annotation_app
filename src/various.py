from streamlit_cookies_manager import CookieManager
import streamlit as st
import pandas as pd
import requests
import re
import json
import random

# Path to folder with JSON papers
JSON_FOLDER = "Full_text_jsons"

# Path to the users table
USERS_TABLE_PATH = r"AWS_S3/users_table.xlsx"

BACKEND_URL = "http://localhost:3000"

def get_token(cookies=None):
    if cookies:
        return cookies.get("token") or st.session_state.get("token")
    return st.session_state.get("token")

def get_user_email():
    return st.session_state.get("userID")

def fetch_user_info(cookies=None):
    user_email = get_user_email()
    token = get_token(cookies)
    if not user_email or not token:
        st.error("Not authenticated. Please log in again.")
        st.stop()
    try:
        resp = requests.get(
            f"{BACKEND_URL}/users/me",
            params={"email": user_email},
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error("Could not fetch user info from backend.")
            st.stop()
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        st.stop()

def fetch_paper_info(pmid, cookies=None):
    token = get_token(cookies)
    try:
        resp = requests.get(
            f"{BACKEND_URL}/papers/{pmid}",
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            return None
    except Exception as e:
        return None

def abandon_paper(user_email, pmid, cookies=None):
    token = get_token(cookies)
    try:
        resp = requests.post(
            f"{BACKEND_URL}/users/add_abandoned",
            json={"email": user_email, "pmid": pmid},
            cookies={"token": token},
            timeout=10
        )
        return resp.status_code == 200
    except Exception as e:
        return False

def clear_paper_in_progress(user_email, cookies=None):
    token = get_token(cookies)
    try:
        resp = requests.post(
            f"{BACKEND_URL}/users/set_current_pmid",
            json={"email": user_email, "pmid": None},
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            st.session_state["paper_in_progress"] = None
            cookies["paper_in_progress"] = ""
            cookies.save()
            return True
        else:
            st.error("Failed to clear paper in progress in the database.")
            return False
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        return False

def add_completed_paper(user_email, pmid, cookies=None):
    token = get_token(cookies)
    try:
        resp = requests.post(
            f"{BACKEND_URL}/users/add_completed",
            json={"email": user_email, "pmid": pmid},
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code != 200:
            st.error("Failed to add completed paper in the database.")
            return False
        return True
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        return False

def update_paper_in_progress(user_email, pmid, cookies):
    token = get_token(cookies)
    try:
        resp = requests.post(
            f"{BACKEND_URL}/users/set_current_pmid",
            json={"email": user_email, "pmid": pmid},
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            st.session_state["paper_in_progress"] = pmid
            cookies["paper_in_progress"] = pmid
            cookies.save()
        else:
            st.error("Failed to update paper in progress in the database.")
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")

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

def get_pmid(cookies: CookieManager, redir: bool = True) -> str:
    # Check if PMID is in session state
    if "paper_in_progress" in st.session_state:
        return st.session_state["paper_in_progress"]

    # Check if PMID is in cookies
    pmid_from_cookies = cookies.get("paper_in_progress")
    if pmid_from_cookies:
        st.session_state["paper_in_progress"] = pmid_from_cookies
        return pmid_from_cookies

    # Check the backend database for the user's current paper in progress
    user_email = st.session_state.get("userID")
    token = cookies.get("token") or st.session_state.get("token")
    BACKEND_URL = "http://localhost:3000"
    if user_email and token:
        try:
            resp = requests.get(
                f"{BACKEND_URL}/users/me",
                params={"email": user_email},
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
    if "userID" not in st.session_state:
        st.session_state["userID"] = cookies.get("userID", None)

    if not st.session_state.logged_in:
        st.set_option("client.showSidebarNavigation", False)
        st.switch_page("login.py")

def save_state_to_cookies(cookies):
    cookies["cards"] = json.dumps(st.session_state.get("cards", []))
    cookies["current_page"] = json.dumps(st.session_state.get("current_page", {}))
    cookies["pages"] = json.dumps(st.session_state.get("pages", []))
    cookies["active_solution_btn"] = json.dumps(st.session_state.get("active_solution_btn", {}))

def load_state_from_cookies(cookies):
    if "cards" not in st.session_state and "cards" in cookies and cookies["cards"]:
        st.session_state["cards"] = json.loads(cookies["cards"])
    if "current_page" not in st.session_state and "current_page" in cookies and cookies["current_page"]:
        st.session_state["current_page"] = json.loads(cookies["current_page"])
    if "pages" not in st.session_state and "pages" in cookies and cookies["pages"]:
        st.session_state["pages"] = json.loads(cookies["pages"])
    if "active_solution_btn" not in st.session_state and "active_solution_btn" in cookies and cookies["active_solution_btn"]:
        st.session_state["active_solution_btn"] = json.loads(cookies["active_solution_btn"])

def check_tag(tag):
    if 'non-PI' in tag:
        return "non-PI"
    else:
        return "PI"

def load_paper_metadata(token, papers_completed, papers_abandoned):
    import requests
    try:
        resp = requests.get(
            f"{BACKEND_URL}/papers",
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            papers = resp.json()
            result = []
            for paper in papers:
                pmid = paper.get("PMID")
                if pmid and (pmid in papers_completed or pmid in papers_abandoned):
                    continue  # Skip papers that are already completed or abandoned
                authors = paper.get("Authors", [])
                if isinstance(authors, list):
                    authors_str = ", ".join(authors)
                else:
                    authors_str = str(authors)
                fpage = paper.get("FPage", "N/A")
                lpage = paper.get("LPage", "N/A")
                pages = f"{fpage}-{lpage}" if fpage != "N/A" and lpage != "N/A" else "N/A"
                result.append({
                    "title": paper.get("Title", ""),
                    "authors": authors_str,
                    "volume": paper.get("Volume", "?"),
                    "issue": paper.get("Issue", "?"),
                    "pages": pages,
                    "year": paper.get("Year", "?"),
                    "doi": paper.get("DOI_URL", ""),
                    "link": paper.get("DOI_URL", ""),
                    "filename": pmid,
                    "pmid": pmid
                })
            return result
        else:
            st.error(f"Failed to fetch papers: {resp.text}")
            st.stop()
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        st.stop()

def fetch_paper_by_pmid(pmid, token):
    import requests
    try:
        resp = requests.get(
            f"{BACKEND_URL}/papers",
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            papers = resp.json()
            for paper in papers:
                if str(paper.get("PMID")) == str(pmid):
                    return paper
            st.error(f"Paper with PMID {pmid} not found.")
            st.stop()
        else:
            st.error(f"Failed to fetch papers: {resp.text}")
            st.stop()
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        st.stop()

def fetch_fulltext_by_pmid(pmid, cookies=None):
    """
    Fetch the full text for a given PMID from the backend.
    Returns the full text JSON or None if not found.
    """
    token = get_token(cookies)
    try:
        resp = requests.get(
            f"{BACKEND_URL}/fulltext",
            params={"filename": pmid},
            cookies={"token": token},
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
        else:
            return None
    except Exception as e:
        return None
