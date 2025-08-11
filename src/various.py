from streamlit_cookies_manager import CookieManager
import streamlit as st
import pandas as pd
import random
from src.database import fetch_all_papers, fetch_session_state

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
    BACKEND_URL = "https://seal-app-c5ety.ondigitalocean.app"
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

def handle_auth_error(cookies : CookieManager):
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    # Set logged_in to False
    st.session_state.logged_in = False
    # Clear all relevant cookies
    if cookies is not None:
        for k in [
            "logged_in", "userKey", "token",
            "paper_in_progress", "selected_paper"
        ]:
            cookies[k] = ""
        cookies["logged_in"] = False
        cookies.save()
    # Hide sidebar and redirect to login
    st.set_option("client.showSidebarNavigation", False)
    st.switch_page("login.py")
    st.stop()

def handle_redirects(cookies : CookieManager):
    # Check cookies for session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = cookies.get("logged_in", False)
    if "userKey" not in st.session_state:
        st.session_state["userKey"] = cookies.get("userKey", None)

    token = cookies.get("token") or st.session_state.get("token")
    if not st.session_state.logged_in or not token:
        st.set_option("client.showSidebarNavigation", False)
        st.session_state.logged_in = False
        cookies["logged_in"] = False
        st.switch_page("login.py")
        st.stop()

    # Check if token has not expired
    import requests
    BACKEND_URL = "https://seal-app-c5ety.ondigitalocean.app"
    try:
        resp = requests.get(
            f"{BACKEND_URL}/users/me",
            params={"userKey": st.session_state["userKey"]},
            cookies={"token": token},
            timeout=5
        )
        if resp.status_code == 401 or resp.status_code == 403:
            # Token is invalid/expired
            st.session_state.logged_in = False
            cookies["logged_in"] = False
            cookies["token"] = ""
            cookies.save()
            st.set_option("client.showSidebarNavigation", False)
            st.switch_page("login.py")
            st.stop()
    except Exception as e:
        st.error(f"Error checking authentication: {e}")
        st.set_option("client.showSidebarNavigation", False)
        st.session_state.logged_in = False
        cookies["logged_in"] = False
        st.switch_page("login.py")
        st.stop()

# Helper to get token
def get_token(cookies : CookieManager):
    return cookies.get("token") or st.session_state.get("token")

# Helper to get user key
def get_user_key(cookies : CookieManager):
    return st.session_state.get("userKey") or cookies.get("userKey")

# -- Paper picker helper functions --

@st.cache_data
def load_paper_metadata(_cookies, papers_completed, papers_abandoned):
    token = get_token(_cookies)
    if not token:
        st.error("Not authenticated. Please log in again.")
        st.stop()
    success, papers = fetch_all_papers(token)
    if not success:
        st.error(papers)
        handle_auth_error(_cookies)
        st.stop()
    result = []
    for paper in papers:
        pmid = paper.get("PMID")
        if pmid and (pmid in papers_completed or pmid in papers_abandoned):
            continue  # Skip papers that are already completed or abandoned

        # Authors: handle as string or list
        authors = paper.get("Authors", [])
        if isinstance(authors, list):
            authors_str = ", ".join(authors)
        else:
            authors_str = str(authors)

        # Journal, Issue, Volume, Pages
        journal = paper.get("Journal", None)
        issue = paper.get("Issue", None)
        volume = paper.get("Volume", None)
        pages = paper.get('Pages')

        result.append({
            "title": paper.get("Title", ""),
            "authors": authors_str,
            "journal": journal,
            "issue": issue,
            "volume": volume,
            "pages": pages,
            "year": paper.get("Year", "?"),
            "doi": paper.get("DOI_URL", ""),
            "link": paper.get("DOI_URL", ""),
            "filename": pmid,
            "pmid": pmid,
            "abstract": paper.get('Abstract', "")
        })
    return result

# Function to refresh paper list
def refresh_paper_list(all_papers):
    num_to_select = min(5, len(all_papers))
    if num_to_select < 5:
        st.warning("Not enough papers available to display 5 options.")
    st.session_state.paper_choices = random.sample(all_papers, k=num_to_select)
    st.session_state.selected_option = None
    # Clear checkbox states
    for k in ["a", "b", "c", "d", "e"]:
        if k in st.session_state:
            del st.session_state[k]

def fetch_and_prepare_paper_data(pmid, cookies, fetch_fulltext_by_pmid, fetch_doi_by_pmid):
    """
    Fetches fulltext and DOI for a paper by PMID, normalizes, and returns (df, tab_names, doi_link).
    """
    def normalize_section_name(section):
        s = section.strip().upper()
        if "INTRO" in s:
            return "INTRODUCTION"
        if "METHOD" in s:
            return "METHODS"
        if "RESULT" in s:
            return "RESULTS"
        if "DISCUSS" in s:
            return "DISCUSSION"
        if "SUPPL" in s:
            return "SUPPLEMENTARY"
        if "CONCL" in s:
            return "CONCLUSION"
        return section.strip()

    token = get_token(cookies)
    raw = fetch_fulltext_by_pmid(pmid, token)
    if not raw:
        st.error("Failed to fetch fulltext data for this paper.")
        handle_auth_error(cookies)

    df = pd.DataFrame(raw)
    if df.empty:
        st.error("No fulltext data available for this paper.")
        st.stop()
    df = df[df["TextValue"].notnull() & (df["TextValue"].str.strip() != "")]
    df = df.rename(columns={"TextValue": "text"})
    df = df[~df["Section"].str.upper().isin(["ISSUE", "FIG"])]
    df["section_type"] = df["Section"].apply(normalize_section_name)
    tab_names = df["section_type"].drop_duplicates().tolist()
    doi_link = fetch_doi_by_pmid(pmid, token)
    if doi_link and not str(doi_link).startswith("http"):
        doi_link = f"https://doi.org/{doi_link}"
    return df, tab_names, doi_link

def load_state_from_backend(cookies, pmid):
    if not st.session_state.get("backend_loaded", False):
        user_key = get_user_key(cookies)
        token = get_token(cookies)
        backend_state = fetch_session_state(user_key, pmid, token)
        if backend_state:
            for key in ["subpages", "current_page"]:
                if key in backend_state:
                    st.session_state[key] = backend_state[key]
            st.session_state["backend_loaded"] = True

def get_user_progress(cookies, pmid):

    """
    Fetches user progress data from the backend for the given PMID.
    Returns a tuple of (num_protocols, num_solutions, num_annotated) to display in resume page.
    """

    def is_details_annotated(details):
        # Check for default values
        if not details:
            return False
        if (
            details.get("ph") == "0"
            and details.get("temp") == "0"
            and details.get("time") == "0–5 min"
            and details.get("composition_name") == "Solution details not listed: reference paper"
            and details.get("composition_selections") == []
            and details.get("composition_chems") == []
        ):
            return False
        return True
    
    user_key = get_user_key(cookies)
    token = get_token(cookies)
    backend_state = fetch_session_state(user_key, pmid, token)
    if not backend_state:
        return 0, 0, 0

    subpages = backend_state.get("subpages", [])
    experiments = []

    for subpage in reversed(subpages):
        exp_struct = subpage.get("experiments", [])
        if isinstance(exp_struct, list) and exp_struct:
            experiments = exp_struct
            break
        elif isinstance(exp_struct, dict):
            for tab in exp_struct.values():
                if tab:
                    experiments.extend(tab)
            if experiments:
                break

    num_protocols = len(experiments)
    num_solutions = 0
    num_annotated = 0

    for exp in experiments:
        solutions = exp.get("solutions", [])
        for sol in solutions:
            if not isinstance(sol, dict):
                continue
            num_solutions += 1
            details = sol.get("details")
            if is_details_annotated(details):
                num_annotated += 1

    return num_protocols, num_solutions, num_annotated

def send_to_thanks_no_PI_exp(cookies,pmid,add_completed_paper,clear_paper_in_progress,save_annotations_to_db):
    st.session_state["completed_paper"] = pmid
    cookies["completed_paper"] = pmid

    if "selected_paper" in st.session_state:
        del st.session_state["selected_paper"]
    cookies["selected_paper"] = ""

    if "paper_in_progress" in st.session_state:
        del st.session_state["paper_in_progress"]
    cookies["paper_in_progress"] = ""
    cookies.save()

    user_key = get_user_key(cookies)
    token = get_token(cookies)
    if user_key:
        # Only clear after add_completed_paper succeeds
        if add_completed_paper(user_key, pmid):
            clear_paper_in_progress(user_key, token)

    if "pages" in st.session_state:
        del st.session_state["pages"]
    if "current_page" in st.session_state:
        del st.session_state["current_page"]

    save_annotations_to_db(st.session_state, user_key, pmid, token)

    st.switch_page("pages/7_thanks.py")