import streamlit as st
import uuid
import pandas as pd
import json
import os
from streamlit_cookies_manager import CookieManager
from text_highlighter import text_highlighter
from st_components.TableSelect import TableSelect
from src.various import get_pmid, handle_redirects
from st_components.BreadCrumbs import BreadCrumbs

# Set page config
st.set_page_config(initial_sidebar_state="expanded", page_title="Paper Annotation", layout="wide")
st.set_option("client.showSidebarNavigation", False)

# Initialize the cookie manager
cookies = CookieManager(prefix="annotation_app_")

if not cookies.ready():
    st.stop()

handle_redirects(cookies)

# Path to the folder containing JSON files
JSON_FOLDER = "Full_text_jsons"

# Path to the users table
USERS_TABLE_PATH = "AWS_S3\\users_table.xlsx"


# Function to load the selected paper's JSON file based on the PMID
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


# Fetch the PMID
pmid = get_pmid(cookies)

# Load the selected paper's JSON file
if "paper_data" not in st.session_state:
    raw = load_paper_by_pmid(pmid)
    doc = raw[0]["documents"][0]
    all_data = []
    doi_link = None  # Initialize DOI link
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
    st.session_state["paper_data"] = df
    st.session_state["tab_names"] = df["section_type"].unique().tolist()  # Extract unique tab names
    st.session_state["doi_link"] = doi_link  # Save the DOI link in session state

# Sidebar
st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            min-width: 370px;
        }
    </style>
    <style>
        .block-container {
            padding-top: 4rem;
        }
    </style>
""", unsafe_allow_html=True)


def colored_card(title, subtitle, bg_color="#1f77b4", text_color="#ffffff", key=None):
    if key is None:
        key = str(uuid.uuid4())  # Generate unique key if none provided

    container_id = f"card-{key}"

    st.markdown(f"""
                <div id="{container_id}" style="
                background: linear-gradient(135deg, {bg_color}, #333333);
                padding: 1.5rem;
                border-radius: 1.25rem;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                                color: {text_color};
                font-family: 'Segoe UI', sans-serif;
                margin: 1rem 0;
                ">
                <div style="font-size: 1.5rem; font-weight: 600; margin-bottom: 0.3rem;">
                                {title}
                </div>
                <div style="font-size: 1rem; font-weight: 400; opacity: 0.85;">
                                {subtitle}
                </div>
                </div>
        """, unsafe_allow_html=True)


# Functions to load paper text + labels
@st.cache_data
def get_tab_body(tab_name):
    df = st.session_state["paper_data"]
    tmp = df[df.section_type == tab_name]
    return tmp['text'].str.cat(sep="\n\n") if not tmp.empty else "No content available for this section."


@st.cache_data
def get_labels():
    return [
        ("buffer", "pink"),
        ("pH", "lightsalmon"),
        ("salt", "lightblue"),
        ("detergent", "yellow"),
        ("chelating", "orange"),
        ("inhibitors", "violet"),
        ("other", "lightgrey")
    ]


if "pages" not in st.session_state:
    st.session_state.links = [
        {"label": "Experiment Picker"},
        {"label": "Solution Picker"},
        {"label": "Experiment Details"},
        {"label": "Solution Details"},
    ]
    st.session_state.pages = [
        {"index": i + 1, "label": link["label"], "visited": 0}
        for i, link in enumerate(st.session_state.links)
    ]
    st.session_state.current_page = {"page": st.session_state.links[0], "index": 0}
    st.session_state.pages[0]["visited"] = 1

if "cards" not in st.session_state:
    st.session_state["cards"] = [[], [], [], []]
if "active_solution_btn" not in st.session_state:
    st.session_state["active_solution_btn"] = {}

# func to change page
def changePage(index):
    st.session_state.current_page = {
        "page": st.session_state.links[index],
        "index": index
    }
    st.session_state.pages[index]["visited"] = 1
    st.rerun()


def next():
    if st.session_state.current_page["index"] < len(st.session_state.links) - 1:
        changePage(st.session_state.current_page["index"] + 1)


def prev():
    if st.session_state.current_page["index"] > 0:
        changePage(st.session_state.current_page["index"] - 1)


def save():
    pass


pageSelected = BreadCrumbs(st.session_state.links, st.session_state.current_page["page"], pages=st.session_state.pages)


# for i, link in enumerate(st.session_state.links):
#     if link["label"] == pageSelected:
#         st.session_state.current_page = {
#             "page": st.session_state.links[i],
#             "index": i
#         }
#         break

def check_tag(tag):
    if 'non-PI' in item['tag']:
        return "non-PI"
    else:
        return "PI"


def displayTextHighlighter(labels, index):
    # Main app: Tabs + Highlighting
    # Dynamically load tab names from session state
    tab_names = st.session_state.get("tab_names", ["Unknown"])
    tabs = st.tabs(tab_names)
    results = []

    for i, (name, tab) in enumerate(zip(tab_names, tabs)):
        annotations = []
        if (len(st.session_state["cards"][st.session_state.current_page["index"]]) > 0):
            annotations = st.session_state["cards"][st.session_state.current_page["index"]][i]

        # print(st.session_state["cards"][st.session_state.current_page["index"]][i],i)
        with tab:
            result = text_highlighter(
                text=get_tab_body(name),
                labels=labels,
                text_height=400,
                annotations=annotations,
                key=f"text_highlighter_{name}_{index}"  # Assign a unique key for each tab
            )

            results.append(result)
    return results


if st.session_state.current_page["page"]["label"] == st.session_state.links[0]["label"]:
    st.title(st.session_state.links[0]["label"])
    labels = [
        ("PI experiment", "#6290C3"),
        ("non-PI experiment", "#F25757")
    ]
    st.session_state["cards"][0] = displayTextHighlighter(labels, 0)
elif st.session_state.current_page["page"]["label"] == st.session_state.links[1]["label"]:
    st.title(st.session_state.links[1]["label"])
    labels = [("PI experiment", "#6290C3"),
              ("non-PI experiment", "#F25757")]
        # if st.session_state["active_solution_btn"] != None and st.session_state["active_solution_btn"]["type"] == "non-PI":
        #     labels = [("non-PI experiment", "#F25757")]
    print(st.session_state["active_solution_btn"])
    st.session_state["cards"][1] = displayTextHighlighter(labels, 1)
elif st.session_state.current_page["page"]["label"] == st.session_state.links[2]["label"]:
    st.title(st.session_state.links[2]["label"])
    labels = [
        ("Select", "#82645E"),
    ]
    st.session_state["cards"][2] = displayTextHighlighter(labels, 2)
elif st.session_state.current_page["page"]["label"] == st.session_state.links[3]["label"]:
    st.title(st.session_state.links[3]["label"])
    labels = [
        ("Buffer", "#F68E5F"),
        ("pH", "#56876D"),
        ("Salt", "#F9C784"),
        ("Detergent", "#007FFF"),
        ("Chelating", "#7D83FF"),
        ("Other", "#8898AA"),
    ]
    st.session_state["cards"][3] = displayTextHighlighter(labels, 3)
# elif st.session_state.current_page["page"]["label"] == st.session_state.links[4]["label"]:
#     st.title(st.session_state.links[4]["label"])
else:
    st.title("")

with st.sidebar:
    # Use the DOI link dynamically
    st.title("Paper Annotation")

    if st.session_state.current_page["page"]["label"] == st.session_state.links[0]["label"]:
        st.subheader("Step 1/4 : Identify experiments (names)")
        st.markdown(
            "Identify all the experimental methods used in the paper and determine if they contain any steps that **preserve protein interactions (PIs) with any other type of molecule, in cell-free systems, without use of cross-linking**. We are not interested in identifying methods that are exclusively computational.")
    elif st.session_state.current_page["page"]["label"] == st.session_state.links[1]["label"]:
        st.subheader("Step 2/4 : Identify solutions (names)")
        st.markdown(
            "For each of the laboratory experiments that you identified in the previous step, select the solution names used in distinct steps of the experimental protocol. If the solution is intended to **preserve protein interactions (PIs) with any other type of molecule, in cell-free systems, without use of cross-linking**, thet it should be classified as \"PI\", and as \"non-PI\" otherwise, like before. An experiment that has been labeled as \"non-PI\" cannot contain \"PI\" solutions, but the opposite is possible.")
    elif st.session_state.current_page["page"]["label"] == st.session_state.links[2]["label"]:
        st.subheader("Step 3/4 : Experiment details")
        st.markdown(
            "For each of the PI laboratory experiments that you identified in the first step, find the details we ask  below. For each selected question you will need to find the answer in the text of the paper (\"Select\" button). In the case the information is split in multiple locations in the paper, then you can append more text to your current selection by pressing the \"Add to selection\" button, repeating as many times as necessary. The \"Select\" button is reset when you move on to the next question.")
    elif st.session_state.current_page["page"]["label"] == st.session_state.links[3]["label"]:
        st.subheader("Step 4/4 : Solution composition")
        st.markdown(
            "For each of the PI solutions that you identified in the second step, find their detailed composition in the text after selecting the right button for the type of chemical. If the composition of a solution used in the experiments is not described in detail but instead is offered as a reference to previous work, then select that reference in-text withe the corresponding button selected.  ")
    else:
        st.title("")

    doi_link = st.session_state.get("doi_link")
    if doi_link:
        st.link_button("Go to full-text paper", doi_link, use_container_width=True)
    else:
        st.write("DOI link not available for this paper.")

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

    if st.session_state.current_page["page"]["label"] == st.session_state.links[0]["label"]:
        header = {
            "column_1": "Experiment name",
            "column_2": "Type"
        }
        for tab_index, tab_results in enumerate(st.session_state["cards"][0]):
            for i, item in enumerate(tab_results):
                colored_card(
                    title=f"{item['tag']}",
                    subtitle=item['text'],
                    bg_color=item['color']
                )
    elif st.session_state.current_page["page"]["label"] == st.session_state.links[1]["label"]:
        # print(st.session_state.cards)
        buttons = []
        for tab_index, tab_results in enumerate(st.session_state["cards"][0]):
            for i, item in enumerate(tab_results):
                details = {
                    "index": i,
                    "name": item["text"],
                    "type": check_tag(item["tag"]),
                    "background_color": "#6290C3" if check_tag(item["tag"]) == "PI" else "#F25757",
                    "text_color": "white"
                }
                buttons.append(details)
        header = {
            "column_1": "Experiment > Solution",
            "column_2": "Type"
        }
        st.session_state["active_solution_btn"] = TableSelect(header, buttons, 2, key=st.session_state.links[1]["label"])
        # for tab_index, tab_results in enumerate(st.session_state["cards"][1]):
        #     for i, item in enumerate(tab_results):
        #         full_type = table + " solution"
        #         if full_type == item['tag']:
        #             colored_card(
        #                 title=f"{item['tag']}",
        #                 subtitle=item['text'],
        #                 bg_color=item['color']
        #             )
        #         elif table == "":
        #             colored_card(
        #                 title=f"{item['tag']}",
        #                 subtitle=item['text'],
        #                 bg_color=item['color']
        #             )

    elif st.session_state.current_page["page"]["label"] == st.session_state.links[2]["label"]:
        st.title(st.session_state.links[2]["label"])

    elif st.session_state.current_page["page"]["label"] == st.session_state.links[3]["label"]:
        st.title(st.session_state.links[3]["label"])
    # elif st.session_state.current_page["page"]["label"] == st.session_state.links[4]["label"]:
    #     st.title(st.session_state.links[4]["label"])
    else:
        st.title("")
