import streamlit as st
import random
import requests
from process_interchange import pick_paper
from src.various import get_pmid, handle_redirects
from streamlit_cookies_manager import CookieManager

st.set_page_config(page_title=pick_paper["title"], layout="wide", initial_sidebar_state="collapsed")
st.title(pick_paper["title"])

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

BACKEND_URL = "http://localhost:3000"

pmid = get_pmid(cookies, redir=False)
if pmid:
    st.switch_page("pages/1_resume.py")
    st.stop()
    
def get_token():
    return cookies.get("token") or st.session_state.get("token")

def get_user_email():
    # Adjust this if you use UserKey or UserEmail for login
    return st.session_state.get("userID")

# Fetch user info from backend
def fetch_user_info():
    user_email = get_user_email()
    token = get_token()
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

# Fetch completed and abandoned PMIDs for the current user
user_info = fetch_user_info()
papers_completed = user_info.get("CompletedPMIDs", []) or []
papers_abandoned = user_info.get("AbandonedPMIDs", []) or []

# Loads the metadata from backend via HTTP
@st.cache_data
def load_paper_metadata():
    token = get_token()
    if not token:
        st.error("Not authenticated. Please log in again.")
        st.stop()
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

                # Authors: handle as string or list
                authors = paper.get("Authors", [])
                if isinstance(authors, list):
                    authors_str = ", ".join(authors)
                else:
                    authors_str = str(authors)

                # Pages
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
                    "filename": pmid,  # Use PMID as filename identifier
                    "pmid": pmid
                })
            return result
        else:
            st.error(f"Failed to fetch papers: {resp.text}")
            st.stop()
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
        st.stop()

st.markdown(pick_paper["detail"])

all_papers = load_paper_metadata()

# Function to refresh paper list
def refresh_paper_list():
    num_to_select = min(5, len(all_papers))
    if num_to_select < 5:
        st.warning("Not enough papers available to display 5 options.")
    st.session_state.paper_choices = random.sample(all_papers, k=num_to_select)
    st.session_state.selected_option = None
    # Clear checkbox states
    for k in ["a", "b", "c", "d", "e"]:
        if k in st.session_state:
            del st.session_state[k]

# Initialize session state for paper choices
if "paper_choices" not in st.session_state:
    refresh_paper_list()

# Initialize session state for selected option
def select(option, key):
    if st.session_state.selected_option == option:
        st.session_state.selected_option = None
        st.session_state[key] = False
    else:
        st.session_state.selected_option = option
        for k in ["a", "b", "c", "d", "e"]:
            if k != key:
                st.session_state[k] = False

# Display the 5 random papers
for i, paper in enumerate(st.session_state.paper_choices):
    key = chr(ord("a") + i)
    label = (
        f"**{paper['authors']}**, "
        f"*{paper['title']}* "
        f"({paper['year']})\n\n"
    )

    # Dynamically construct the metadata parts
    metadata_parts = []
    if paper.get('issue', '?') != "?":
        metadata_parts.append(f"**Issue:** {paper['issue']}")
    if paper.get('volume', '?') != "?":
        metadata_parts.append(f"**Volume:** {paper['volume']}")
    if paper.get('pages', 'N/A') != "N/A":
        metadata_parts.append(f"**Pages:** {paper['pages']}")

    # Join metadata parts with a comma
    if metadata_parts:
        label += ", ".join(metadata_parts) + "\n\n"

    # Always use a proper DOI link
    doi_link = paper.get("link", "")
    if doi_link and not doi_link.startswith("http"):
        doi_link = f"https://doi.org/{doi_link}"
    if doi_link:
        label += f"[**Link**]({doi_link})"

    st.checkbox(label, key=key, value=st.session_state.get(key, False),
                on_change=select, args=(paper["filename"], key))

# Navigation buttons
col2, col3 = st.columns([6, 6])
with col2:
    if st.button(pick_paper["buttons"][0]["text"], type="primary", key="go_button", disabled=not st.session_state.selected_option):
        # Save the selected paper's metadata in session state
        selected_paper = next(paper for paper in st.session_state.paper_choices if paper["filename"] == st.session_state.selected_option)

        # Use the pmid directly (no local file access)
        pmid = selected_paper["pmid"]

        st.session_state["selected_paper"] = pmid
        cookies["selected_paper"] = pmid
        cookies.save()
        st.switch_page(pick_paper["buttons"][0]["page_link"])
        
with col3:
    st.button(pick_paper["buttons"][1]["text"], type="secondary", key="refresh_button", on_click=refresh_paper_list)