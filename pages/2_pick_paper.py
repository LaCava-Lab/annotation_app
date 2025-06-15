import streamlit as st
import random
from process_interchange import pick_paper
from src.various import get_pmid, handle_redirects, get_token, get_user_key
from streamlit_cookies_manager import CookieManager
from src.database import fetch_user_info, fetch_all_papers

st.set_page_config(page_title=pick_paper["title"], layout="wide", initial_sidebar_state="collapsed")
st.title(pick_paper["title"])

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

pmid = get_pmid(cookies, redir=False)
if pmid:
    st.switch_page("pages/1_resume.py")
    st.stop()

# Fetch user info from backend
user_key = get_user_key(cookies)
token = get_token(cookies)

if not user_key or not token:
    st.error("Not authenticated. Please log in again.")
    st.stop()

success, user_info = fetch_user_info(user_key, token)
if not success:
    st.error(user_info)
    st.stop()

papers_completed = user_info.get("CompletedPMIDs", []) or []
papers_abandoned = user_info.get("AbandonedPMIDs", []) or []

# Loads the metadata from backend via HTTP
@st.cache_data
def load_paper_metadata():
    token = get_token(cookies)
    if not token:
        st.error("Not authenticated. Please log in again.")
        st.stop()
    success, papers = fetch_all_papers(token)
    if not success:
        st.error(papers)
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
            "pmid": pmid
        })
    return result

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

for i, paper in enumerate(st.session_state.paper_choices):
    key = chr(ord("a") + i)
    label = (
        f"**{paper['authors']}**, "
        f"*{paper['title']}* "
        f"({paper['year']})\n\n"
    )

    # Add Journal, Issue, Volume in order if present
    if paper.get('journal'):
        label += f"**Journal:** {paper['journal']}, "
    if paper.get('issue'):
        label += f"**Issue:** {paper['issue']}, "
    if paper.get('volume'):
        label += f"**Volume:** {paper['volume']}, "

    # Only add Pages if not "nan"
    pages = paper.get('pages')
    if pages and str(pages).strip().lower() != "nan":
        label += f"**Pages:** {pages}, "

    # Remove trailing comma and space
    if label.endswith(", "):
        label = label[:-2]
    label += "\n\n"

    # DOI Link extraction
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
        # Reset navigation/session state for new annotation
        for key in ["pages", "current_page", "cards", "active_solution_btn"]:
            if key in st.session_state:
                del st.session_state[key]
            if key in cookies:
                cookies[key] = ""
        # Save the selected paper's metadata in session state
        selected_paper = next(paper for paper in st.session_state.paper_choices if paper["filename"] == st.session_state.selected_option)
        pmid = selected_paper["pmid"]
        st.session_state["selected_paper"] = pmid
        cookies["selected_paper"] = pmid
        cookies.save()
        st.switch_page(pick_paper["buttons"][0]["page_link"])
        
with col3:
    st.button(pick_paper["buttons"][1]["text"], type="secondary", key="refresh_button", on_click=refresh_paper_list)