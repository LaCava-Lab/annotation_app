import uuid
import streamlit as st
from streamlit_cookies_manager import CookieManager
from src.database import fetch_fulltext_by_pmid, add_completed_paper, clear_paper_in_progress, fetch_doi_by_pmid, \
fetch_user_info, set_abandon_limit, abandon_paper, save_session_state, fetch_paper_info,save_annotations_to_db
from src.subpage import Subpage
from src.various import get_pmid, handle_redirects, get_token, get_user_key, fetch_and_prepare_paper_data, \
load_state_from_backend, handle_auth_error, send_to_thanks_no_PI_exp
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

pmid = get_pmid(cookies)  # Fetch the PMID
# Redirect to pick paper if no paper in progress

def format_paper_metadata(paper_meta):
    title = paper_meta.get("Title", "Unknown Title")
    abstract = paper_meta.get("Abstract", "")
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
    doi_link = paper_meta.get("DOI_URL", "")
    if doi_link and not doi_link.startswith("http"):
        doi_link = f"https://doi.org/{doi_link}"
    if not doi_link:
        doi_link = None


    return title, authors_str, metadata_line, doi_link, abstract

token = get_token(cookies)
success, paper_meta = fetch_paper_info(pmid, token)
if not success:
    handle_auth_error(cookies)
    st.error("Could not fetch paper info.")
    st.stop()

if "paper_metadata_picker" not in st.session_state:
    title, authors_str, metadata_line, doi_link, abstract = format_paper_metadata(paper_meta)
    st.session_state.paper_metadata_picker = {
        "title": title,
        "authors_str": authors_str,
        "metadata_line": metadata_line,
        "doi_link": doi_link,
        "abstract": abstract,
    }

if not pmid:
    st.error("No paper in progress. Please pick a paper to annotate.")
    st.switch_page("pages/2_pick_paper.py")

if "paper_data" not in st.session_state:
    df, tab_names, doi_link = fetch_and_prepare_paper_data(
        pmid, cookies, fetch_fulltext_by_pmid, fetch_doi_by_pmid
    )

    seen = set()
    unique_tab_names = []
    for x in tab_names:
        key = x.upper()
        if key not in seen:
            seen.add(key)
            unique_tab_names.append(key)  # already uppercased

    st.session_state["paper_data"] = df
    st.session_state["tab_names"] = unique_tab_names
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
         "highlighter_labels": [
             ("PI Experiment", "#6290C3"),
             ("non-PI Experiment", "#F25757")
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
         "highlighter_labels": [
             ("PI Solution", "#6290C3"),
             ("non-PI Solution", "#F25757")
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
         "highlighter_labels": [
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
         "experiments": {},
         "highlighter_labels": [
             ("Buffer", "#F68E5F"),
             ("Salt", "#F9C784"),
             ("Detergent", "#007FFF"),
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
    st.session_state.active_solution_widget = {}
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

    st.session_state.select_type_composition = ""

    st.session_state.details_listed = {
        "name": {},
        "quantity": {},
        "unit": {}
    }

if "current_page" not in st.session_state:
    st.session_state.current_page = {"subpage": st.session_state.subpages[0], "index": 0}
    st.session_state.subpages[0]["visited"] = 1

load_state_from_backend(cookies, pmid)

subpages_data = []
for i, subpage in enumerate(st.session_state.subpages):
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
    if "experiments" in subpage and index == 4:
        if st.session_state.active_solution_widget:
            selections = st.session_state.active_solution_widget["details"]["composition_selections"]

    subpages_data.append(
        Subpage(index, label, doi_link, paper_data, sidebar_content, selections, highlighter_labels, coffee_break,
                coffee_break_display))

    if "experiments" in subpage:
        subpages_data[i].assign_experiments(subpage["experiments"])

page = subpages_data[st.session_state.current_page["index"]]


# func to change page
def check_has_pi_exp(experiments):
    pi_experiments = [exp for exp in experiments if exp.get("tag") == "PI Experiment"]
    if len(pi_experiments) > 0:
        return True
    else:
        return False

def check_only_non_pi_exp(experiments):
    non_pi_experiments = [exp for exp in experiments if exp.get("tag") == "non-PI Experiment"]

    if len(non_pi_experiments) > 0 and not check_has_pi_exp(experiments):
        return True
    else:
        return False

def check_no_exp(experiments):
    if len(experiments) == 0:
        return True
    else:
        return False

@st.dialog("Are you sure?")
def finish_paper():
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("No", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("Yes", use_container_width=True):
            send_to_thanks_no_PI_exp(cookies,pmid,add_completed_paper,clear_paper_in_progress,save_annotations_to_db)

def reload():
    st.rerun()


def changePage(index):
    st.session_state.current_page = {
        "subpage": st.session_state.subpages[index],
        "index": index
    }
    st.session_state.subpages[index]["visited"] = 1
    st.rerun()


def next():
    index = st.session_state.current_page["index"]

    if index == 0:
        experiments = [
            item
            for i in range(len(tab_names))
            for item in page.selections[i]
        ]

        if check_no_exp(experiments):
            return

        if check_only_non_pi_exp(experiments):
            finish_paper()
            return

    if index == 1:
        experiments = [
            item
            for i in tab_names
            for item in st.session_state.subpages[index]["experiments"].get(i,{})
        ]
        # st.write(experiments)
        pi_exp = [exp for exp in experiments if exp.get("tag") == "PI Experiment"]

        if len(pi_exp) == 0:
            return

        for exp in pi_exp:
            # st.write(exp["solutions"])

            if len(exp["solutions"]) == 0:
                return
            else:
                exp_solutions = [
                    item
                    for i in range(len(tab_names))
                    for item in exp["solutions"][i]
                ]

                if len(exp_solutions) == 0:
                    return

                pi_solutions = [sol for sol in exp_solutions if sol.get("tag") == "PI Solution"]

                if len(pi_solutions) == 0:
                    return

    if st.session_state.current_page["index"] <= len(st.session_state.subpages) - 1:
        if st.session_state.subpages[index]["coffee_break"] and not st.session_state.subpages[index][
            "coffee_break_display"]:
            st.session_state.subpages[index]["coffee_break_display"] = True
            st.rerun()
        elif st.session_state.subpages[index]["coffee_break"] and st.session_state.subpages[index][
            "coffee_break_display"]:
            st.session_state.subpages[index]["coffee_break_display"] = False
            if st.session_state.current_page["index"] < len(st.session_state.subpages) - 1:
                changePage(index + 1)
        else:
            if st.session_state.current_page["index"] < len(st.session_state.subpages) - 1:
                changePage(index + 1)


def prev():
    index = st.session_state.current_page["index"]
    # If currently displaying a coffee break, just hide it and stay on the same page
    if st.session_state.subpages[index]["coffee_break"] and st.session_state.subpages[index]["coffee_break_display"]:
        st.session_state.subpages[index]["coffee_break_display"] = False
        st.rerun()

    # Otherwise, go to the previous page
    for page in st.session_state.subpages:
        page["coffee_break_display"] = False

    if index > 0:
        changePage(index - 1)


def save():
    index = st.session_state.current_page["index"]
    next_page_index = index + 1

    # SAVE COFFEE BREAKS
    if st.session_state.subpages[index]["coffee_break"] and st.session_state.subpages[index]["coffee_break_display"]:
        page.saveCoffeeBreak()

    # SAVE SELECTIONS
    st.session_state.subpages[index]["selections"] = page.selections

    # SAVE EXPERIMENTS
    if index < len(st.session_state.subpages) - 1:
        if "experiments" in st.session_state.subpages[next_page_index] and index == 0:
            experiments = {
                tab_name: [{
                    "uuid": str(uuid.uuid4()),
                    **item,
                    "solutions": item.get("solutions", []),
                    "section": tab_name,
                    "type": page.check_tag(item["tag"]),
                    "alt_exp_text": None,
                    "absolute_index": sum(len(page.selections[k]) for k in range(i)) + j,
                    "background_color": "#6290C3" if page.check_tag(item["tag"]) == "PI" else "#F25757",
                    "text_color": "white"}
                    for j, item in enumerate(page.selections[i])
                ]
                for i, tab_name in enumerate(tab_names)
            }
            st.session_state.subpages[next_page_index]["experiments"] = experiments
        if "experiments" in st.session_state.subpages[next_page_index] and index == 1:
            #add uuid for each solution
            for section_name, experiments in page.experiments.items():
                for experiment in experiments:
                    for solution_list in experiment.get("solutions", []):
                        for solution in solution_list:
                            solution["uuid"] = str(uuid.uuid4())
                            
            experiments = [{
                **item,
                "baits": item.get("baits", []),
                "solutions": [{
                    **inner_item,
                } for inner_sublist in item["solutions"] for inner_item in inner_sublist]
            } for sublist in st.session_state.subpages[index]["experiments"].values() for item in sublist]
            st.session_state.subpages[next_page_index]["experiments"] = experiments

    if index < len(st.session_state.subpages) and index == 2:
        if "experiments" in st.session_state.subpages[next_page_index]:
            experiments = [{
                **exp,
                "solutions": [{
                    **sol,
                    "details": {
                        "ph": "0",
                        "temp": "0",
                        "time": "0–5 min",
                        "composition_name": "Solution details not listed: reference paper",
                        "composition_selections": [],
                        "composition_chems": []
                    }
                } for sol in exp["solutions"]]
            } for exp in st.session_state.subpages[index]["experiments"]]
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

# ACTIVE LABELS BASED ON EXPERIMENT TYPE
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
    elif st.session_state.select_type != "composition_listed" and page.index == 4:
        page.update_labels_type(st.session_state.subpages[index - 1]["highlighter_labels"])
        page.main_page(tab_names)
    else:
        page.update_labels_type(labels)
        page.main_page(tab_names)
else:
    page.main_page()
    page.display_coffee_break_nav_buttons(
        index, pmid, cookies,
        prev, save, next, reload,
        get_user_key, get_token, add_completed_paper, clear_paper_in_progress
    )

page.display_abandon_paper_button(
    index, pmid, cookies,
    prev, save, next,
    get_user_key, get_token, add_completed_paper, clear_paper_in_progress, fetch_user_info, set_abandon_limit,
    abandon_paper
)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# UI CODE
# SIDEBAR (only when not in coffee break)
if not page.coffee_break_display:
    with st.sidebar:
        st.title("Paper Annotation")
    page.sidebar_info()
    with st.sidebar:
        if st.session_state.current_page["index"] != 0:
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

        if st.session_state.current_page["index"] == 0:
            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("Save", use_container_width=True):
                    save()

            with col2:
                if st.button("Save & Next", use_container_width=True):
                    save()
                    next()

    page.active_experiment = st.session_state.active_experiment_widget
    page.active_solution = st.session_state.active_solution_widget
    page.select_type = st.session_state.select_type
    page.select_type_composition = st.session_state.select_type_composition

    st.session_state.active_experiment = page.sidebar_widget()

    # print(st.session_state.subpages[page.index - 1].get("experiments"))
    # print(st.session_state)
    # st.write(st.session_state["subpages"][0])

    # reload select
    if page.select_type != st.session_state.select_type:
        st.rerun()

    if page.select_type_composition != st.session_state.select_type_composition:
        st.rerun()

    # reload solutions in experiments
    if page.active_experiment != st.session_state.active_experiment_widget:
        st.rerun()

    # reload solutions in experiments
    if page.active_solution != st.session_state.active_solution_widget:
        st.rerun()

    # reload state if current labels are not synced
    if active_experiment != st.session_state.active_experiment:
        st.rerun()
