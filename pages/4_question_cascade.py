import streamlit as st
from process_interchange import question_cascade
from streamlit_cookies_manager import CookieManager
from src.various import handle_redirects, get_selected_paper, get_token, update_paper_in_progress, fetch_paper_by_pmid

# Set page config
st.set_page_config(page_title="Questionnaire", layout="wide", initial_sidebar_state="collapsed")

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

pmid = get_selected_paper(cookies)
if pmid is None:
    st.error("No paper selected. Please select a paper to annotate.")
    st.switch_page("pages/2_pick_paper.py")

token = get_token(cookies)
paper_meta = fetch_paper_by_pmid(pmid, token)

title = paper_meta.get("Title", "Unknown Title")
authors = paper_meta.get("Authors", [])
if isinstance(authors, list):
    authors_str = ", ".join(authors)
else:
    authors_str = str(authors)

metadata_parts = []
if paper_meta.get("Issue", "?") != "?":
    metadata_parts.append(f"**Issue:** {paper_meta['Issue']}")
if paper_meta.get("Volume", "?") != "?":
    metadata_parts.append(f"**Volume:** {paper_meta['Volume']}")
fpage = paper_meta.get("FPage", "N/A")
lpage = paper_meta.get("LPage", "N/A")
if fpage != "N/A" and lpage != "N/A":
    metadata_parts.append(f"**Pages:** {fpage}-{lpage}")
year = paper_meta.get("Year", "?")
if year != "?":
    metadata_parts.append(f"**Year:** {year}")

# DOI link handling
doi_link = paper_meta.get("DOI_URL", "")
if doi_link and not doi_link.startswith("http"):
    doi_link = f"https://doi.org/{doi_link}"
if not doi_link:
    doi_link = None

# Display paper metadata
st.markdown(f"""
    <div style="margin-top: -50px;">
        <h3>You have selected to annotate the paper:</h3>
        <strong>{authors_str}</strong>, <em>{title}</em>
    </div>
""", unsafe_allow_html=True)
if metadata_parts:
    st.markdown(", ".join(metadata_parts))

# Description
st.markdown("###")
col1, col2, col3 = st.columns([0.5, 3, 0.5])
with col2:
    st.markdown("""
        <div style="text-align: center; margin-bottom: -100px; margin-top: -40px;">
            Use the link to the full-text paper to scan through it and then answer the quick questionnaire below. 
            In this stage, you can go back through the "Pick another" button and change the paper as many times as you want. 
            You will be allowed to abandon a "Confirmed Paper" later only twice. 
            If you are happy with your selection, press "Confirm paper" to proceed to annotating your current selection.
        </div>
    """, unsafe_allow_html=True)

# "Go to full-text paper" button
st.markdown("###")
col1, col2, col3 = st.columns([1.5, 1, 1])
with col2:
    if doi_link:
        st.link_button("Go to full-text paper", doi_link)
    else:
        st.warning("DOI link not available for this paper.")

# Questionnaire
st.markdown("### Questionnaire")

st.markdown('<div>1. Is the paper describing wet lab experiments that aim to understand protein interactions?</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 200])
with col1:
    st.markdown("")
with col2:
    q1 = st.radio("Question 1", options=["YES", "NO"], horizontal=True, key="q1_radio", label_visibility="collapsed")

st.markdown('<div style="padding-left: 20px; margin-bottom: 10px;">1a. What is the main method the authors use to understand protein interactions?</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 60])
with col1:
    st.markdown("")
with col2:
    q1a = st.text_input("Sub-question 1a", placeholder="Enter the main method here", key="q1a_text", label_visibility="collapsed")

st.markdown('<div style="padding-left: 20px;">1b. Is this method preserving protein interactions in a cell-free system (e.g., whole cell extracts)?</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 50])
with col1:
    st.markdown("")
with col2:
    q1b = st.radio("Sub-question 1b", options=["YES", "NO"], horizontal=True, key="q1b_radio", label_visibility="collapsed")

st.markdown('<div style="padding-left: 20px;">1c. Is this method using any type of cross-linking to preserve protein interactions?</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 50])
with col1:
    st.markdown("")
with col2:
    q1c = st.radio("Sub-question 1c", options=["YES", "NO"], horizontal=True, key="q1c_radio", label_visibility="collapsed")

st.markdown('<div style="margin-bottom: 10px;">2. What is your level of familiarity with the topic of this paper?</div>', unsafe_allow_html=True)
q2 = st.selectbox("Question 2", ["Basic", "Course", "MSc research", "PhD field", "PhD research", "Expert"], key="q2_select", label_visibility="collapsed")

st.markdown('<div style="margin-bottom: 10px;">3. What is your level of familiarity with the methods and experiments in this paper?</div>', unsafe_allow_html=True)
q3 = st.selectbox("Question 3", ["Basic", "Course", "MSc research", "PhD field", "PhD research", "Expert"], key="q3_select", label_visibility="collapsed")

st.markdown("""
    <div style="margin-top: -20px;">
    </div>
""", unsafe_allow_html=True)

all_filled = (
    q1 is not None and
    q1a.strip() != "" and
    q1b is not None and
    q1c is not None and
    q2 is not None and
    q3 is not None
)

col1, col2, col3 = st.columns([1.5, 1, 1])
with col1:
    if st.button("Pick another paper", type="secondary", key="pick_another_button"):
        st.session_state["selected_paper"] = None
        cookies["selected_paper"] = None
        st.switch_page("pages/2_pick_paper.py")
with col2:
    st.button(
        "Confirm paper",
        type="primary",
        key="confirm_paper_button",
        disabled=not all_filled
    )
    if all_filled and st.session_state.get("confirm_paper_button"):
        st.set_option("client.showSidebarNavigation", False)
        # Use user email for backend update
        user_email = st.session_state.get("userID")
        update_paper_in_progress(user_email, pmid, cookies)
        st.switch_page("pages/5_detail_picker.py")