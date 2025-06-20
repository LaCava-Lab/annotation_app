import os
import json
import pandas as pd
import streamlit as st
from src.subpage import Subpage
from src.various import get_pmid, handle_redirects, get_token, get_user_key, fetch_and_prepare_paper_data, load_state_from_backend
from src.database import fetch_fulltext_by_pmid, add_completed_paper, clear_paper_in_progress, fetch_doi_by_pmid, fetch_user_info, set_abandon_limit, abandon_paper, save_session_state, fetch_session_state
from streamlit_cookies_manager import CookieManager
from st_components.BreadCrumbs import BreadCrumbs

# CONFIG
st.set_page_config(initial_sidebar_state="expanded", page_title="Paper Annotation", layout="wide")
st.set_option("client.showSidebarNavigation", False)
st.markdown("""
    <style>
        [data-testid="stSidebarCollapseButton"] {
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 9999;
            background-color: transparent;
            }
        [data-testid="stSidebarHeader"] {
            height: 0px;
            padding: 10px;
        }
        [data-testid="stSidebarNav"] {
            display: none;
        }
        [data-testid="stSidebarUserContent"] {
            padding-top: 0px;
        }
        [data-testid="stSidebarUserContent"] h1 {
            padding-top: 0px;
        }
        [data-testid="stSidebar"] {
            min-width: 370px;
        }
    </style>
    """, unsafe_allow_html=True)

# COOKIES
cookies = CookieManager(prefix="annotation_app_")

if not cookies.ready():
    st.stop()

handle_redirects(cookies)

pmid = get_pmid(cookies) # Fetch the PMID
# Redirect to pick paper if no paper in progress
if not pmid:
    st.error("No paper in progress. Please pick a paper to annotate.")
    st.switch_page("pages/2_pick_paper.py")

if "paper_data" not in st.session_state:
    df, tab_names, doi_link = fetch_and_prepare_paper_data(
        pmid, cookies, fetch_fulltext_by_pmid, fetch_doi_by_pmid
    )
    st.session_state["paper_data"] = df
    st.session_state["tab_names"] = tab_names
    st.session_state["doi_link"] = doi_link

paper_data = st.session_state["paper_data"]
tab_names = st.session_state["tab_names"]
doi_link = st.session_state["doi_link"]

# PAGES INFO
if "subpages" not in st.session_state:
    st.session_state.subpages = [
        {"label": "Experiment Picker",
         "sidebar_content": {
             "subtitle": "Step 1/4 : Identify experiments (names)",
             "description": "Identify all the experimental methods used in the paper and determine if they contain any steps that **preserve protein interactions (PIs) with any other type of molecule, in cell-free systems, without use of cross-linking**. We are not interested in identifying methods that are exclusively computational.",
             "widget": "CARDS"
         },
         "selections": [],
         "highlighter_labels":[
             ("PI experiment", "#6290C3"),
             ("non-PI experiment", "#F25757")
         ],
         "coffee_break": False,
         "coffee_break_display": False,
         "index": 1,
         "visited": 0},
        {"label": "Solution Picker",
         "sidebar_content": {
             "subtitle": "Step 2/4 : Identify solutions (names)",
             "description": "For each of the laboratory experiments that you identified in the previous step, select the solution names used in distinct steps of the experimental protocol. If the solution is intended to **preserve protein interactions (PIs) with any other type of molecule, in cell-free systems, without use of cross-linking**, thet it should be classified as \"PI\", and as \"non-PI\" otherwise, like before. An experiment that has been labeled as \"non-PI\" cannot contain \"PI\" solutions, but the opposite is possible.",
             "widget": "CARDS_SELECT"
         },
         "selections": [],
         "experiments": {},
         "highlighter_labels":[
             ("PI experiment", "#6290C3"),
             ("non-PI experiment", "#F25757")
         ],
         "coffee_break": True,
         "coffee_break_display": False,
         "index": 2,
         "visited": 0},
        {"label": "Experiment Details",
         "sidebar_content": {
             "subtitle": "Step 3/4 : Experiment details",
             "description": "For each of the PI laboratory experiments that you identified in the first step, find the details we ask  below. For each selected question you will need to find the answer in the text of the paper (\"Select\" button). In the case the information is split in multiple locations in the paper, then you can append more text to your current selection by pressing the \"Add to selection\" button, repeating as many times as necessary. The \"Select\" button is reset when you move on to the next question.",
             "widget": ""
         },
         "selections": [],
         "highlighter_labels":[
            ("Select", "#82645E"),
         ],
         "coffee_break": True,
         "coffee_break_display": False,
         "index": 3,
         "visited": 0},
        {"label": "Solution Details",
         "sidebar_content": {
             "subtitle": "Step 4/4 : Solution composition",
             "description": "For each of the PI solutions that you identified in the second step, find their detailed composition in the text after selecting the right button for the type of chemical. If the composition of a solution used in the experiments is not described in detail but instead is offered as a reference to previous work, then select that reference in-text withe the corresponding button selected.",
             "widget": ""
         },
         "selections": [],
         "highlighter_labels":[
             ("Buffer", "#F68E5F"),
             ("pH", "#56876D"),
             ("Salt", "#F9C784"),
             ("Detergent", "#007FFF"),
             ("Chelating", "#7D83FF"),
             ("Other", "#8898AA"),
         ],
         "coffee_break": True,
         "coffee_break_display": False,
         "index": 4,
         "visited": 0},
    ]
    st.session_state.current_page = {"subpage": st.session_state.subpages[0], "index": 0}
    st.session_state.subpages[0]["visited"] = 1
    st.session_state.active_experiment_widget = {}

load_state_from_backend(cookies, pmid)

subpages_data = []
for i,subpage in enumerate(st.session_state.subpages):
    label = subpage["label"]
    sidebar_content = subpage["sidebar_content"]
    coffee_break = subpage["coffee_break"]
    coffee_break_display = subpage["coffee_break_display"]
    selections = subpage["selections"]
    highlighter_labels = subpage["highlighter_labels"]
    index = subpage["index"]

    if "experiments" in subpage:

        if st.session_state.active_experiment_widget:
            exp = st.session_state.active_experiment_widget
            absolute_index = exp.get("absolute_index")
            list = subpage["experiments"].get(exp.get("section"))
            if list:
                selections = list[absolute_index]["solutions"]

    subpages_data.append(Subpage(index,label, doi_link, paper_data, sidebar_content, selections, highlighter_labels, coffee_break,coffee_break_display))

    if "experiments" in subpage:
        subpages_data[i].assign_experiments(subpage["experiments"])

page = subpages_data[st.session_state.current_page["index"]]

# func to change page
def changePage(index):
    st.session_state.current_page = {
        "page": st.session_state.links[index],
        "index": index
    }
    st.session_state.pages[index]["visited"] = 1
    save()
    st.rerun()

def next():
    if st.session_state.current_page["index"] <= len(st.session_state.subpages) - 1:
        index = st.session_state.current_page["index"]

        if st.session_state.subpages[index]["coffee_break"] and not st.session_state.subpages[index]["coffee_break_display"]:
            st.session_state.subpages[index]["coffee_break_display"] = True
            st.rerun()
        elif st.session_state.subpages[index]["coffee_break"] and st.session_state.subpages[index]["coffee_break_display"]:
            st.session_state.subpages[index]["coffee_break_display"] = False
            if st.session_state.current_page["index"] < len(st.session_state.subpages) - 1:
                changePage(index + 1)
        else:
            if st.session_state.current_page["index"] < len(st.session_state.subpages) - 1:
                changePage(index + 1)

def prev():
    for page in st.session_state.subpages:
        page["coffee_break_display"] = False

    if st.session_state.current_page["index"] > 0:
        changePage(st.session_state.current_page["index"] - 1)

def save():
    index = st.session_state.current_page["index"]

    #SAVE SELECTIONS
    st.session_state.subpages[index]["selections"] = page.selections

    #SAVE EXPERIMENTS
    if index < len(st.session_state.subpages) - 1:
        next_page_index = index + 1
        if "experiments" in st.session_state.subpages[next_page_index]:
            experiments = {
                tab_name: [
                    {**item,
                     "solutions": [],
                     "section": tab_name,
                     "type": page.check_tag(item["tag"]),
                     "absolute_index" :sum(len(page.selections[k]) for k in range(i)) + j,
                     "background_color": "#6290C3" if page.check_tag(item["tag"]) == "PI" else "#F25757",
                     "text_color": "white"}
                    for j, item in enumerate(page.selections[i])
                ]
                for i, tab_name in enumerate(tab_names)
            }
            st.session_state.subpages[next_page_index]["experiments"] = experiments

    # Persist the session state to the backend
    user_key = get_user_key(cookies)
    pmid = get_pmid(cookies)
    token = get_token(cookies)
    session_state_to_save = {
        "subpages": st.session_state.get("subpages", []),
        "current_page": st.session_state.get("current_page", {}),
        # ADD MORE KEYS IF NEEDED
    }
    save_session_state(user_key, pmid, session_state_to_save, token)
    
pageSelected = BreadCrumbs(st.session_state.current_page["subpage"], pages=st.session_state.subpages)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# UI CODE
# MAIN PAGE

#ACTIVE LABELS BASED ON EXPERIMENT TYPE
if "active_experiment" not in st.session_state:
    st.session_state.active_experiment = ""
active_experiment = st.session_state.active_experiment
index = st.session_state.current_page["index"]
labels = st.session_state.subpages[index]["highlighter_labels"]

### display main subpage
if not page.coffee_break_display:
    if st.session_state.active_experiment == "non-PI" and page.index == 2:
        page.update_labels_type([labels[1]])
        page.main_page(tab_names)
    else:
        page.update_labels_type(labels)
        page.main_page(tab_names)
else:
    page.main_page()
    page.display_coffee_break_nav_buttons(
        index, pmid, cookies,
        prev, save, next,
        get_user_key, get_token, add_completed_paper, clear_paper_in_progress
    )

page.display_abandon_paper_button(
    index, pmid, cookies,
    prev, save, next,
    get_user_key, get_token, add_completed_paper, clear_paper_in_progress, fetch_user_info, set_abandon_limit, abandon_paper
)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# UI CODE
# SIDEBAR (only when not in coffee break)
if not page.coffee_break_display:
    with st.sidebar:
        st.title("Paper Annotation")
    page.sidebar_info()
    with st.sidebar:
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            if st.button("Prev", use_container_width=True):
                prev()

        with col2:
            if st.button("Save", use_container_width=True):
                save()

        with col3:
            if st.button("Save & Next", use_container_width=True):
                save()
                next()


    page.active_experiment = st.session_state.active_experiment_widget

    st.session_state.active_experiment = page.sidebar_widget()

    # print(st.session_state.subpages[page.index - 1].get("experiments"))
    # print(st.session_state)

    # reload solutions in experiments
    if page.active_experiment != st.session_state.active_experiment_widget:
        st.rerun()

    # reload state if current labels are not synced
    if active_experiment != st.session_state.active_experiment:
        st.rerun()