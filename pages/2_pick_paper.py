import streamlit as st
import random
from process_interchange import pick_paper
from src.various import get_token, get_pmid, fetch_user_info, handle_redirects, load_paper_metadata
from streamlit_cookies_manager import CookieManager

st.set_page_config(page_title=pick_paper["title"], layout="wide", initial_sidebar_state="collapsed")
st.title(pick_paper["title"])

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

# Fetch user info from backend
user_info = fetch_user_info(cookies)
# Get pmid to see if a paper is in progress
pmid = get_pmid(cookies)
if pmid:
    st.switch_page("pages/1_resume.py")

papers_completed = user_info.get("CompletedPMIDs", []) or []
papers_abandoned = user_info.get("AbandonedPMIDs", []) or []

token = get_token(cookies)
all_papers = load_paper_metadata(token, papers_completed, papers_abandoned)

st.markdown(pick_paper["detail"])

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
        # Save the selected paper's metadata in session state
        selected_paper = next(paper for paper in st.session_state.paper_choices if paper["filename"] == st.session_state.selected_option)

        # Set selected paper in session state and cookies
        pmid = selected_paper["pmid"]

        st.session_state["selected_paper"] = pmid
        cookies["selected_paper"] = pmid
        cookies.save()
        st.switch_page(pick_paper["buttons"][0]["page_link"])
        
with col3:
    st.button(pick_paper["buttons"][1]["text"], type="secondary", key="refresh_button", on_click=refresh_paper_list)