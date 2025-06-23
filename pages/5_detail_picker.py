import os
import json
import pandas as pd
import streamlit as st
from subpage import Subpage
from src.various import get_pmid, handle_redirects
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

# PAPER INFO
JSON_FOLDER = "Full_text_jsons" # Path to the folder containing JSON files
USERS_TABLE_PATH = r"AWS_S3/users_table.xlsx" # Path to the users table
pmid = get_pmid(cookies) # Fetch the PMID
doi_link = None # Initialize DOI link
paper_data = None
tab_names = None

def load_paper_by_pmid(pmid):
    for filename in os.listdir(JSON_FOLDER):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(JSON_FOLDER, filename), "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    # Check if the PMID matches
                    doc = raw[0]["documents"][0]
                    front = doc["passages"][0]  # Front matter
                    meta = front["infons"]
                    extracted_pmid = meta.get("article-id_pmid", None)
                    if extracted_pmid == pmid:
                        return raw
            except Exception as e:
                st.error(f"Error reading file {filename}: {e}")
    st.error(f"No JSON file found for PMID: {pmid}")
    st.stop()

if True: # Load the selected paper's JSON file
    raw = load_paper_by_pmid(pmid)
    doc = raw[0]["documents"][0]
    all_data = []
    for passage in doc["passages"]:
        section_type = passage["infons"].get("section_type", "Unknown")
        text = passage.get("text", "")
        all_data.append({
            "section_type": section_type,
            "text": text
        })
        # Extract DOI link from the metadata
        if "article-id_doi" in passage["infons"]:
            doi_link = f"https://doi.org/{passage['infons']['article-id_doi']}"
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    # Filter out sections that do not need to be annotated
    df = df[~df["section_type"].isin(["TITLE", "REF", "SUPPL", "AUTH_CONT", "COMP_INT", "ACK_FUND"])]
    paper_data = df
    tab_names = df["section_type"].unique().tolist()  # Extract unique tab names

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
             "widget": "EXPERIMENT_DETAILS"
         },
         "selections": [],
         "experiments": {},
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
             "widget": "SOLUTION_DETAILS"
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
    # st.session_state.current_page = {"subpage": st.session_state.subpages[2], "index": 2}
    # st.session_state.subpages[2]["visited"] = 1
    # st.session_state.active_experiment_widget = {}

    st.session_state.current_page = {"subpage": st.session_state.subpages[0], "index": 0}
    st.session_state.subpages[0]["visited"] = 1
    st.session_state.active_experiment_widget = {}
    st.session_state.select_type = ""
    st.session_state.current_bait = {
        "name": {},
        "tag": {},
        "species": {}
    }
    st.session_state.current_interactor = {
        "name": {},
        "species": {}
    }

subpages_data = []
for i,subpage in enumerate(st.session_state.subpages):
    label = subpage["label"]
    sidebar_content = subpage["sidebar_content"]
    coffee_break = subpage["coffee_break"]
    coffee_break_display = subpage["coffee_break_display"]
    selections = subpage["selections"]
    highlighter_labels = subpage["highlighter_labels"]
    index = subpage["index"]

    if "experiments" in subpage and index == 2:

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
        "subpage": st.session_state.subpages[index],
        "index": index
    }
    st.session_state.subpages[index]["visited"] = 1
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
        if "experiments" in st.session_state.subpages[next_page_index] and index == 0:
            experiments = {
                tab_name: [
                    {**item,
                     "solutions": item.get("solutions", []),
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
        if "experiments" in st.session_state.subpages[next_page_index] and index == 1:
            experiments = [{
                **item,
                "baits": item.get("baits", []),
                "solutions": [{
                    **inner_item
                } for inner_sublist in item["solutions"] for inner_item in inner_sublist]
            } for sublist in st.session_state.subpages[index]["experiments"].values() for item in sublist]
            st.session_state.subpages[next_page_index]["experiments"] = experiments

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
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Save", use_container_width=True):
            save()
    with col2:
        if st.button("Save & next", use_container_width=True):
            save()
            next()

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
    page.select_type = st.session_state.select_type

    st.session_state.active_experiment = page.sidebar_widget()

    # print(st.session_state.subpages[page.index - 1].get("experiments"))
    # print(st.session_state)

    # reload select
    if page.select_type != st.session_state.select_type:
        st.rerun()

    # reload solutions in experiments
    if page.active_experiment != st.session_state.active_experiment_widget:
        st.rerun()

    # reload state if current labels are not synced
    if active_experiment != st.session_state.active_experiment:
        st.rerun()
