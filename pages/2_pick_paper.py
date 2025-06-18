import streamlit as st
from process_interchange import pick_paper
from src.various import get_pmid, handle_redirects, get_token, get_user_key, load_paper_metadata, refresh_paper_list
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

st.markdown(
    f"<div style='font-size:1.3em; margin-top: -0.8em; padding-bottom:32px'>{pick_paper['detail']}</div>",
    unsafe_allow_html=True
)

all_papers = load_paper_metadata(cookies, papers_completed, papers_abandoned)

# Initialize session state for paper choices
if "paper_choices" not in st.session_state:
    refresh_paper_list(all_papers)

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
        f"*{paper['authors']}*, "
        f"**{paper['title']}** "
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
    st.button(
        pick_paper["buttons"][1]["text"],
        type="secondary",
        key="refresh_button",
        on_click=lambda: refresh_paper_list(all_papers)
    )