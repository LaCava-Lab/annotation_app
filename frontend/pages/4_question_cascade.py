import streamlit as st
from process_interchange import question_cascade
from streamlit_cookies_manager import CookieManager
from src.various import handle_redirects, get_selected_paper, get_token, get_user_key, handle_auth_error
from src.database import fetch_paper_info, update_paper_in_progress, save_session_state, update_session_status, add_completed_paper

# Set page config
st.set_page_config(page_title=question_cascade["title"], layout="wide", initial_sidebar_state="collapsed")

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")
if not cookies.ready():
    st.stop()

handle_redirects(cookies)

def format_paper_metadata(paper_meta):
    title = paper_meta.get("Title", "Unknown Title")
    authors = paper_meta.get("Authors", [])
    authors_str = ", ".join(authors) if isinstance(authors, list) else str(authors)
    metadata_line = ""
    if paper_meta.get("Issue") and str(paper_meta["Issue"]).strip().lower() != "nan":
        metadata_line += f"**Issue:** {paper_meta['Issue']}, "
    if paper_meta.get("Volume") and str(paper_meta["Volume"]).strip().lower() != "nan":
        metadata_line += f"**Volume:** {paper_meta['Volume']}, "
    fpage = paper_meta.get("FPage")
    lpage = paper_meta.get("LPage")
    if (
        fpage and lpage and
        str(fpage).strip().lower() != "nan" and
        str(lpage).strip().lower() != "nan"
    ):
        metadata_line += f"**Pages:** {fpage}-{lpage}, "
    year = paper_meta.get("Year")
    if year and str(year).strip().lower() != "nan":
        metadata_line += f"**Year:** {year}, "
    if metadata_line.endswith(", "):
        metadata_line = metadata_line[:-2]
    pmcid = paper_meta.get("PMCID", "") or paper_meta.get("pmcid", "")
    pmc_link = ""
    if pmcid and str(pmcid).strip().upper().startswith("PMC"):
        pmc_link = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"
    if pmc_link:
        fulltext_link = pmc_link
    else:
        doi_link = paper_meta.get("DOI_URL", "")
        if doi_link and not doi_link.startswith("http"):
            doi_link = f"https://doi.org/{doi_link}"
        fulltext_link = doi_link if doi_link else None
    return title, authors_str, metadata_line, fulltext_link

pmid = get_selected_paper(cookies)
if pmid is None:
    st.error("No paper selected. Please select a paper to annotate.")
    st.switch_page("pages/2_pick_paper.py")

token = get_token(cookies)
success, paper_meta = fetch_paper_info(pmid, token)
if not success:
    handle_auth_error(cookies)
    st.error("Could not fetch paper info.")
    st.stop()

title, authors_str, metadata_line, fulltext_link = format_paper_metadata(paper_meta)

# Display paper metadata
st.markdown(f"""
    <div style="margin-top: -50px;">
        <h3>You have selected to annotate the paper:</h3>
        <strong>{authors_str}</strong>, <em>{title}</em>
    </div>
""", unsafe_allow_html=True)
if metadata_line:
    st.markdown(metadata_line)

# Description
st.markdown("###")
col1, col2, col3 = st.columns([0.5, 3, 0.5])
with col2:
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: -100px; margin-top: -40px;">
            {question_cascade["description"]}
        </div>
    """, unsafe_allow_html=True)

# "Go to full-text paper" button
st.markdown("###")
col1, col2, col3 = st.columns([1.5, 1, 1])
with col2:
    if fulltext_link:
        st.link_button(question_cascade["go_to_fulltext"], fulltext_link)
    else:
        st.warning(question_cascade["doi_warning"])

# Questionnaire
st.markdown(question_cascade["questionnaire_title"])

answers = {}

# Define column widths and indentation for each question
col_widths = [
    [1, 200],  # Q1
    [1, 60],   # Q1a
    [1, 50],   # Q1b
    [1, 50],   # Q1c
    None,      # Q2
    None       # Q3
]
indents = [
    0,   # Q1
    20,  # Q1a
    20,  # Q1b
    20,  # Q1c
    0,   # Q2
    0    # Q3
]

for idx, q in enumerate(question_cascade["questions"]):
    label = q["label"]
    col_width = col_widths[idx] if idx < len(col_widths) else None
    indent = indents[idx] if idx < len(indents) else 0

    # Skip questions 1a, 1b, 1c if the first question (idx 0) is answered "NO"
    if idx in [1, 2, 3] and answers.get("q0") == "NO":
        # Set default empty values for skipped questions
        answers[f"q{idx}"] = ""
        continue

    st.markdown(
        f'<div style="padding-left: {indent}px; margin-bottom: 10px;">{label}</div>',
        unsafe_allow_html=True
    )

    if col_width:
        col1, col2 = st.columns(col_width)
        with col1:
            st.markdown("")
        with col2:
            if q["type"] == "radio":
                answers[f"q{idx}"] = st.radio(
                    "", options=q["options"], horizontal=True, key=f"q{idx}_radio", label_visibility="collapsed"
                )
            elif q["type"] == "text_input":
                answers[f"q{idx}"] = st.text_input(
                    "", placeholder=q.get("placeholder", ""), key=f"q{idx}_text", label_visibility="collapsed"
                )
            elif q["type"] == "selectbox":
                answers[f"q{idx}"] = st.selectbox(
                    "", q["options"], key=f"q{idx}_select", label_visibility="collapsed"
                )
    else:
        if q["type"] == "radio":
            answers[f"q{idx}"] = st.radio(
                "", options=q["options"], horizontal=True, key=f"q{idx}_radio", label_visibility="collapsed"
            )
        elif q["type"] == "text_input":
            answers[f"q{idx}"] = st.text_input(
                "", placeholder=q.get("placeholder", ""), key=f"q{idx}_text", label_visibility="collapsed"
            )
        elif q["type"] == "selectbox":
            answers[f"q{idx}"] = st.selectbox(
                "", q["options"], key=f"q{idx}_select", label_visibility="collapsed"
            )
    st.markdown("")  # spacing

# Validation - different logic for YES vs NO answers
if answers.get("q0") == "NO":
    # For NO answer, only need Q1, Q2, Q3 (skip 1a, 1b, 1c)
    all_filled = (
        answers["q0"] is not None and
        answers["q4"] is not None and
        answers["q5"] is not None
    )
else:
    # For YES answer, need all fields including 1a, 1b, 1c
    all_filled = (
        answers["q0"] is not None and
        answers["q1"].strip() != "" and
        answers["q2"] is not None and
        answers["q3"] is not None and
        answers["q4"] is not None and
        answers["q5"] is not None
    )

col1, col2, col3 = st.columns([1.5, 1, 1])
with col1:
    if st.button(question_cascade["pick_another"], type="secondary", key="pick_another_button"):
        st.session_state["selected_paper"] = None
        cookies["selected_paper"] = None
        st.switch_page("pages/2_pick_paper.py")
with col2:
    st.button(
        question_cascade["confirm_paper"],
        type="primary",
        key="confirm_paper_button",
        disabled=not all_filled
    )
    if all_filled and st.session_state.get("confirm_paper_button"):
        st.set_option("client.showSidebarNavigation", False)
        user_key = get_user_key(cookies)
        
        # Handle different flows based on Q1 answer
        if answers.get("q0") == "NO":
            # Negative flow: don't update paper in progress, create negative session, go to thanks
            question_answers = {
                "q1": answers["q0"],
                "q1a": "",  # Empty for skipped questions
                "q1b": "",
                "q1c": "",
                "q2": answers["q4"],
                "q3": answers["q5"]
            }
            
            # Create session state with negative status
            save_session_state(user_key, pmid, {}, token, question_answers)
            
            # Update session status to negative (this should be done after save_session_state creates it)
            update_session_status(user_key, pmid, "negative", token)
            
            # Add paper to completed papers array (even for negative papers)
            add_completed_paper(user_key, pmid)
            
            # Set completed paper for thanks page
            cookies["completed_paper"] = pmid
            st.session_state["completed_paper"] = pmid
            
            st.switch_page("pages/7_thanks.py")
        else:
            # Positive flow: normal annotation process
            update_paper_in_progress(user_key, pmid, token)
            
            # Create question answers dictionary
            question_answers = {
                "q1": answers["q0"],
                "q1a": answers["q1"],
                "q1b": answers["q2"],
                "q1c": answers["q3"],
                "q2": answers["q4"],
                "q3": answers["q5"]
            }
            
            # Create initial session state in backend with question answers
            save_session_state(user_key, pmid, {}, token, question_answers)
            st.switch_page("pages/5_detail_picker.py")